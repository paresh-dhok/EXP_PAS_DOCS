# Location baseline done properly: IDW mean of k nearest TRAINING locations (log space), same schemes/folds as nat_model.py.
# Also the history-prior design: XGB on [prior, pH, EC] and [prior, pH, EC, causal].
import sys,os,glob,time; sys.path.insert(0,os.path.dirname(__file__)); from natcommon import *
import xgboost as xgb
from scipy.spatial import cKDTree
from sklearn.model_selection import GroupKFold
from sklearn.metrics import r2_score
t0=time.time(); T=["N","P","K","OC"]; K=25
D=pd.read_parquet(HOME+"national/india_locations.parquet").merge(pd.read_parquet(OUT+"zones_kmeans20.parquet"),on="id")
CAUSAL=[]
for f in sorted(glob.glob(OUT+"n_*.parquet")):
    if "ndvi" in f and os.environ.get("NO_NDVI"): continue
    x=pd.read_parquet(f); cols=[c for c in x.columns if c!="id" and x[c].notna().mean()>0.5 and x[c].nunique()>1]
    D=D.merge(x[["id"]+cols],on="id",how="left"); CAUSAL+=cols
x=D.lon.to_numpy()*111320*np.cos(np.deg2rad(D.lat.to_numpy())); y=D.lat.to_numpy()*110574; XY=np.c_[x,y]
blk=lambda km: pd.Series([f"{a}_{b}" for a,b in zip((x//(km*1000)).astype(int),(y//(km*1000)).astype(int))]).factorize()[0]
SCHEMES={"blk10":(blk(10),5),"blk100":(blk(100),5),"state":(D.sid.factorize()[0],10),"zone":(D.zone.to_numpy(),10)}
LOG=np.log1p(D[T].to_numpy())
def prior(tr_idx,q_idx,exclude_self):
    tree=cKDTree(XY[tr_idx]); d,i=tree.query(XY[q_idx],k=K+1 if exclude_self else K)
    if exclude_self: d,i=d[:,1:],i[:,1:]
    w=1/np.maximum(d,30.0); return (LOG[tr_idx][i]*w[:,:,None]).sum(1)/w.sum(1)[:,None], d[:,0]
P=dict(n_estimators=400,max_depth=6,learning_rate=0.05,subsample=0.8,colsample_bytree=0.8,min_child_weight=20,tree_method="hist",device="cuda",random_state=42)
rows=[]; resf=OUT+os.environ.get("RESNAME","nat_knn_results.csv")
for sname,(grp,k) in SCHEMES.items():
    oof={s:np.zeros((len(D),4)) for s in ["knn_loc","knn+onsite","knn+onsite+causal"]}; dist=np.zeros(len(D))
    for a,b in GroupKFold(n_splits=k,shuffle=True,random_state=42).split(D,groups=grp):
        pr_tr,_=prior(a,a,True); pr_te,dd=prior(a,b,False); dist[b]=dd
        oof["knn_loc"][b]=np.expm1(pr_te)
        for j,t in enumerate(T):
            for s,extra in [("knn+onsite",["pH","EC"]),("knn+onsite+causal",["pH","EC"]+CAUSAL)]:
                Xa=np.c_[pr_tr[:,j],D[extra].to_numpy("float32")[a]]; Xb=np.c_[pr_te[:,j],D[extra].to_numpy("float32")[b]]
                oof[s][b,j]=np.expm1(xgb.XGBRegressor(**P).fit(Xa,LOG[a,j]).predict(Xb))
        print(sname,"fold done",f"{time.time()-t0:.0f}s",flush=True)
    for s,o in oof.items():
        for j,t in enumerate(T):
            yv=D[t].to_numpy()
            within=[r2_score(yv[grp==g],o[grp==g,j]) for g in np.unique(grp) if (grp==g).sum()>=500] if sname in ("state","zone") else []
            rows.append(dict(scheme=sname,set=s,target=t,R2=r2_score(yv,o[:,j]),R2_within_heldout_mean=np.mean(within) if within else np.nan,median_dist_to_train_km=np.median(dist)/1000))
            print(f"{sname:<7} {s:<20} {t:<3} R2={rows[-1]['R2']:.3f} within={rows[-1]['R2_within_heldout_mean']:.3f} medDist={rows[-1]['median_dist_to_train_km']:.1f}km",flush=True)
    pd.DataFrame(rows).to_csv(resf,index=False)
print("done",f"{time.time()-t0:.0f}s")
