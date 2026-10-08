# National transfer test: does a set of causal covariates predict SHC N/P/K/OC in territory the model never saw,
# where coordinates cannot extrapolate?  XGBoost (GPU), log1p targets, out-of-fold R2 on original scale.
import sys,os,glob,time,json; sys.path.insert(0,os.path.dirname(__file__)); from natcommon import *
import xgboost as xgb
from sklearn.model_selection import GroupKFold
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import r2_score
t0=time.time(); T=["N","P","K","OC"]
D=pd.read_parquet(HOME+"national/india_locations.parquet")
GROUPS={}
for f in sorted(glob.glob(OUT+"n_*.parquet")):
    g=os.path.basename(f)[2:-8]; x=pd.read_parquet(f); cols=[c for c in x.columns if c!="id" and x[c].notna().mean()>0.5 and x[c].nunique()>1]
    D=D.merge(x[["id"]+cols],on="id",how="left"); GROUPS[g]=cols
print({g:len(c) for g,c in GROUPS.items()},len(D),flush=True)
ONSITE=["pH","EC"]; LL=["lon","lat"]; CAUSAL=[c for cs in GROUPS.values() for c in cs]
# ---- grouping schemes (all based on location / environment, never used as inputs)
x=D.lon.to_numpy()*111320*np.cos(np.deg2rad(D.lat.to_numpy())); y=D.lat.to_numpy()*110574
blk=lambda km: pd.Series([f"{a}_{b}" for a,b in zip((x//(km*1000)).astype(int),(y//(km*1000)).astype(int))]).factorize()[0]
ZV=[c for c in ["ppt_annual","ppt_monsoon","tmean","def_annual","elev","sg_clay_0_5cm","sg_sand_0_5cm","sg_phh2o_0_5cm"] if c in D]
Z=D[ZV].fillna(D[ZV].median()); km=KMeans(20,random_state=42,n_init=4).fit(StandardScaler().fit_transform(Z))
D["zone"]=km.labels_; D[["id","zone"]].to_parquet(OUT+"zones_kmeans20.parquet",index=False)
print("zone vars",ZV,"sizes",np.bincount(km.labels_).tolist(),flush=True)
SCHEMES={"blk10":(blk(10),5),"blk100":(blk(100),5),"state":(D.sid.factorize()[0],10),"zone":(D.zone.to_numpy(),10)}
SETS={"onsite":ONSITE,"causal":CAUSAL,"onsite+causal":ONSITE+CAUSAL,"lonlat":LL,"onsite+lonlat":ONSITE+LL,"onsite+causal+lonlat":ONSITE+CAUSAL+LL}
for g,cs in GROUPS.items(): SETS[f"onsite+causal-minus-{g}"]=ONSITE+[c for c in CAUSAL if c not in cs]
only=os.environ.get("SETS"); 
if only: SETS={k:v for k,v in SETS.items() if k in only.split(",")}
P=dict(n_estimators=600,max_depth=8,learning_rate=0.05,subsample=0.8,colsample_bytree=0.8,min_child_weight=20,tree_method="hist",device="cuda",random_state=42)
rows=[]; resf=OUT+os.environ.get("RESNAME","nat_model_results.csv")
for sname,(grp,k) in SCHEMES.items():
    folds=list(GroupKFold(n_splits=k,shuffle=True,random_state=42).split(D,groups=grp))
    for setname,cols in SETS.items():
        if setname.startswith("onsite+causal-minus") and sname not in ("blk100","zone"): continue
        X=D[cols].to_numpy("float32")
        for t in T:
            yv=D[t].to_numpy(); oof=np.zeros(len(D))
            for a,b in folds:
                m=xgb.XGBRegressor(**P).fit(X[a],np.log1p(yv[a])); oof[b]=np.expm1(m.predict(X[b]))
            # pooled R2, and mean R2 within held-out groups (state / zone) with >=500 points
            within=[r2_score(yv[grp==gv],oof[grp==gv]) for gv in np.unique(grp) if (grp==gv).sum()>=500] if sname in ("state","zone") else []
            rows.append(dict(scheme=sname,set=setname,target=t,R2=r2_score(yv,oof),R2_within_heldout_mean=np.mean(within) if within else np.nan,n=len(D)))
            print(f"{sname:<7} {setname:<34} {t:<3} R2={rows[-1]['R2']:.3f} within={rows[-1]['R2_within_heldout_mean']:.3f} ({time.time()-t0:.0f}s)",flush=True)
        pd.DataFrame(rows).to_csv(resf,index=False)
print("done",f"{time.time()-t0:.0f}s")
