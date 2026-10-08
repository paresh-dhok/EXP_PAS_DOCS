# E22: is the held-out-state failure a per-state (lab) offset?  Leave-states-out models + m local calibration samples per held-out state.
import sys,os,glob,time; sys.path.insert(0,os.path.dirname(__file__)); from natcommon import *
import xgboost as xgb
from scipy.spatial import cKDTree
from scipy.stats import spearmanr
from sklearn.model_selection import GroupKFold
from sklearn.metrics import r2_score
t0=time.time(); T=["N","P","K","OC"]; K=25; NSUB=400_000; rng=np.random.default_rng(42)
D=pd.read_parquet(HOME+"national/india_locations.parquet")
GROUPS={}
for f in sorted(glob.glob(OUT+"n_*.parquet")):
    g=os.path.basename(f)[2:-8]; x=pd.read_parquet(f); cols=[c for c in x.columns if c!="id" and x[c].notna().mean()>0.5 and x[c].nunique()>1]
    D=D.merge(x[["id"]+cols],on="id",how="left"); GROUPS[g]=cols
CAUSAL=[c for cs in GROUPS.values() for c in cs]
XY=np.c_[D.lon.to_numpy()*111320*np.cos(np.deg2rad(D.lat.to_numpy())),D.lat.to_numpy()*110574]
LOG=np.log1p(D[T].to_numpy()); ON=D[["pH","EC"]].to_numpy("float32"); CA=D[CAUSAL].to_numpy("float32")
st=D.sid.to_numpy(); grp=D.sid.factorize()[0]
P=dict(n_estimators=300,max_depth=8,learning_rate=0.1,subsample=0.8,colsample_bytree=0.8,min_child_weight=20,tree_method="hist",device="cuda",random_state=42)
def fit_pred(Xa,ya,Xb):
    s=rng.choice(len(Xa),min(NSUB,len(Xa)),replace=False); return xgb.XGBRegressor(**P).fit(Xa[s],ya[s]).predict(Xb)
def prior(tr,q,self_):
    d,i=cKDTree(XY[tr]).query(XY[q],k=K+1 if self_ else K,workers=-1)
    if self_: d,i=d[:,1:],i[:,1:]
    w=1/np.maximum(d,30.0); return (LOG[tr][i]*w[:,:,None]).sum(1)/w.sum(1)[:,None]
oofp=OUT+"nat_calib_oof.parquet"
if os.path.exists(oofp): O=pd.read_parquet(oofp); print("loaded OOF",flush=True)
else:
    O=pd.DataFrame({"id":D.id,"sid":st})
    sets=["causal","onsite+causal","knn+onsite+causal"]; arr={s:np.zeros((len(D),4)) for s in sets}
    for fi,(a,b) in enumerate(GroupKFold(n_splits=10,shuffle=True,random_state=42).split(D,groups=grp)):
        pa,pb=prior(a,a,True),prior(a,b,False)
        for j in range(4):
            arr["causal"][b,j]=fit_pred(CA[a],LOG[a,j],CA[b])
            arr["onsite+causal"][b,j]=fit_pred(np.c_[ON[a],CA[a]],LOG[a,j],np.c_[ON[b],CA[b]])
            arr["knn+onsite+causal"][b,j]=fit_pred(np.c_[pa[:,j],ON[a],CA[a]],LOG[a,j],np.c_[pb[:,j],ON[b],CA[b]])
        print("fold",fi+1,f"{time.time()-t0:.0f}s",flush=True)
    for s,v in arr.items():
        for j,t in enumerate(T): O[f"{s}|{t}"]=v[:,j]
    O.to_parquet(oofp,index=False)
# ---- calibration with m local samples per held-out state (states with >= 2000 locations so that m=500 leaves enough test points)
states=[s for s,n in pd.Series(st).value_counts().items() if n>=2000]; print("states evaluated",len(states),flush=True)
rows=[]
for m in [0,10,20,50,100,200,500,"oracle"]:
    for draw in range(1 if m in (0,"oracle") else 3):
        r=np.random.default_rng(1000+draw); test_mask=np.zeros(len(D),bool); preds={}
        cal_idx={}
        for s in states:
            idx=np.where(st==s)[0]
            cal=r.choice(idx,m,replace=False) if isinstance(m,int) and m>0 else np.array([],int)
            cal_idx[s]=cal; tm=np.setdiff1d(idx,cal); test_mask[tm]=True
        for setname in ["causal","onsite+causal","knn+onsite+causal","local_only"]:
            for j,t in enumerate(T):
                yv=LOG[:,j]; out=np.full(len(D),np.nan); out_lin=np.full(len(D),np.nan)
                for s in states:
                    idx=np.where(st==s)[0]; cal=cal_idx[s]; tm=np.setdiff1d(idx,cal)
                    if setname=="local_only":
                        if len(cal)<5: continue
                        d,i=cKDTree(XY[cal]).query(XY[tm],k=min(K,len(cal))); d=np.atleast_2d(d); i=np.atleast_2d(i)
                        if d.shape[0]!=len(tm): d,i=d.T,i.T
                        w=1/np.maximum(d,30.0); out[tm]=(yv[cal][i]*w).sum(1)/w.sum(1); continue
                    p=O[f"{setname}|{t}"].to_numpy()
                    if m=="oracle": off=np.mean(yv[idx]-p[idx])
                    elif len(cal)==0: off=0.0
                    else: off=np.mean(yv[cal]-p[cal])
                    out[tm]=p[tm]+off
                    if isinstance(m,int) and m>=50:
                        A=np.c_[np.ones(len(cal)),p[cal]]; coef=np.linalg.lstsq(A,yv[cal],rcond=None)[0]; out_lin[tm]=coef[0]+coef[1]*p[tm]
                for cname,o in [("offset",out),("linear",out_lin)]:
                    ok=test_mask&~np.isnan(o)
                    if ok.sum()<1000: continue
                    yt=D[t].to_numpy()
                    ws=[r2_score(yt[ok&(st==s)],np.expm1(o[ok&(st==s)])) for s in states if (ok&(st==s)).sum()>=200]
                    sp=[spearmanr(yt[ok&(st==s)],o[ok&(st==s)]).statistic for s in states if (ok&(st==s)).sum()>=200]
                    rows.append(dict(m=str(m),draw=draw,set=setname,correction=cname,target=t,R2=r2_score(yt[ok],np.expm1(o[ok])),
                                     R2_within_state_mean=np.mean(ws),spearman_within_state_mean=np.mean(sp),n_test=int(ok.sum())))
    print("m",m,"done",f"{time.time()-t0:.0f}s",flush=True)
R=pd.DataFrame(rows); R.to_csv(OUT+"nat_calib_results.csv",index=False)
S=R.groupby(["set","correction","m","target"])[["R2","R2_within_state_mean","spearman_within_state_mean"]].mean().round(3)
print(S.to_string()); print("done",f"{time.time()-t0:.0f}s")
