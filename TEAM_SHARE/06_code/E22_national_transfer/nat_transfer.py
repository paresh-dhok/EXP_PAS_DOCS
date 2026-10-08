# National transfer test (final). Same schemes/folds as nat_model.py / nat_knn.py; faster XGB (300 trees, 400k-row training subsample per fold).
# Sets: causal | onsite+causal | knn_loc | knn+onsite | knn+onsite+causal ; ablation: knn+onsite+causal minus each group (zone scheme)
import sys,os,glob,time; sys.path.insert(0,os.path.dirname(__file__)); from natcommon import *
import xgboost as xgb
from scipy.spatial import cKDTree
from sklearn.model_selection import GroupKFold
from sklearn.metrics import r2_score
t0=time.time(); T=["N","P","K","OC"]; K=25; NSUB=400_000; rng=np.random.default_rng(42)
D=pd.read_parquet(HOME+"national/india_locations.parquet").merge(pd.read_parquet(OUT+"zones_kmeans20.parquet"),on="id")
GROUPS={}
for f in sorted(glob.glob(OUT+"n_*.parquet")):
    g=os.path.basename(f)[2:-8]; x=pd.read_parquet(f); cols=[c for c in x.columns if c!="id" and x[c].notna().mean()>0.5 and x[c].nunique()>1]
    D=D.merge(x[["id"]+cols],on="id",how="left"); GROUPS[g]=cols
CAUSAL=[c for cs in GROUPS.values() for c in cs]; print({g:len(c) for g,c in GROUPS.items()},len(D),flush=True)
x=D.lon.to_numpy()*111320*np.cos(np.deg2rad(D.lat.to_numpy())); y=D.lat.to_numpy()*110574; XY=np.c_[x,y]
blk=lambda km: pd.Series([f"{a}_{b}" for a,b in zip((x//(km*1000)).astype(int),(y//(km*1000)).astype(int))]).factorize()[0]
SCHEMES={"blk10":(blk(10),5),"blk100":(blk(100),5),"state":(D.sid.factorize()[0],10),"zone":(D.zone.to_numpy(),10)}
only=os.environ.get("SCHEMES"); SCHEMES={k:v for k,v in SCHEMES.items() if not only or k in only.split(",")}
LOG=np.log1p(D[T].to_numpy()); ON=D[["pH","EC"]].to_numpy("float32"); CA=D[CAUSAL].to_numpy("float32")
def prior(tr,q,self_):
    d,i=cKDTree(XY[tr]).query(XY[q],k=K+1 if self_ else K,workers=-1)
    if self_: d,i=d[:,1:],i[:,1:]
    w=1/np.maximum(d,30.0); return (LOG[tr][i]*w[:,:,None]).sum(1)/w.sum(1)[:,None], d[:,0]
P=dict(n_estimators=300,max_depth=8,learning_rate=0.1,subsample=0.8,colsample_bytree=0.8,min_child_weight=20,tree_method="hist",device="cuda",random_state=42)
def fit_pred(Xa,ya,Xb):
    s=rng.choice(len(Xa),min(NSUB,len(Xa)),replace=False)
    return np.expm1(xgb.XGBRegressor(**P).fit(Xa[s],ya[s]).predict(Xb))
rows=[]; resf=OUT+"nat_transfer_results.csv"
for sname,(grp,k) in SCHEMES.items():
    sets=["causal","onsite+causal","knn_loc","knn+onsite","knn+onsite+causal"]+([f"knn+onsite+causal-minus-{g}" for g in GROUPS] if sname=="zone" else [])
    oof={s:np.zeros((len(D),4)) for s in sets}; dist=np.zeros(len(D))
    for fi,(a,b) in enumerate(GroupKFold(n_splits=k,shuffle=True,random_state=42).split(D,groups=grp)):
        pa,_=prior(a,a,True); pb,dd=prior(a,b,False); dist[b]=dd; oof["knn_loc"][b]=np.expm1(pb)
        for j in range(4):
            feats={"causal":(CA[a],CA[b]),"onsite+causal":(np.c_[ON[a],CA[a]],np.c_[ON[b],CA[b]]),
                   "knn+onsite":(np.c_[pa[:,j],ON[a]],np.c_[pb[:,j],ON[b]]),
                   "knn+onsite+causal":(np.c_[pa[:,j],ON[a],CA[a]],np.c_[pb[:,j],ON[b],CA[b]])}
            for g in GROUPS:
                if f"knn+onsite+causal-minus-{g}" in oof:
                    keep=[ci for ci,c in enumerate(CAUSAL) if c not in GROUPS[g]]
                    feats[f"knn+onsite+causal-minus-{g}"]=(np.c_[pa[:,j],ON[a],CA[a][:,keep]],np.c_[pb[:,j],ON[b],CA[b][:,keep]])
            for s,(Xa,Xb) in feats.items(): oof[s][b,j]=fit_pred(Xa,LOG[a,j],Xb)
        print(sname,"fold",fi+1,"/",k,f"{time.time()-t0:.0f}s",flush=True)
    for s,o in oof.items():
        for j,t in enumerate(T):
            yv=D[t].to_numpy()
            within=[r2_score(yv[grp==g],o[grp==g,j]) for g in np.unique(grp) if (grp==g).sum()>=500] if sname in ("state","zone") else []
            rows.append(dict(scheme=sname,set=s,target=t,R2=r2_score(yv,o[:,j]),R2_within_heldout_mean=np.mean(within) if within else np.nan,
                             median_dist_to_train_km=np.median(dist)/1000))
            print(f"{sname:<7} {s:<40} {t:<3} R2={rows[-1]['R2']:.3f} within={rows[-1]['R2_within_heldout_mean']:.3f} medDist={rows[-1]['median_dist_to_train_km']:.0f}km",flush=True)
    pd.DataFrame(rows).to_csv(resf,index=False)
print("done",f"{time.time()-t0:.0f}s")
