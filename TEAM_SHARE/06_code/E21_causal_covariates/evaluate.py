# Region-wise protocol (TEAM_SHARE/REGION_WISE_PROTOCOL.md, RF reference model) applied to base_41 + new feature groups
import sys,glob,os,time; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); from common import *
from sklearn.ensemble import RandomForestRegressor
t0=time.time(); data,groups=load()
GROUPS={}
for f in sorted(glob.glob(FEATDIR+"out/f_*.parquet")):
    g=os.path.basename(f)[2:-8]; x=pd.read_parquet(f)
    cols=[c for c in x.columns if c!="id" and x[c].notna().mean()>0.5 and x[c].nunique()>1]
    data=data.merge(x[["id"]+cols],on="id",how="left"); GROUPS[g]=cols
print({g:len(c) for g,c in GROUPS.items()},len(data),flush=True)
ALL=[c for cs in GROUPS.values() for c in cs]; LL=["longitude","latitude"]
sets={"base_41":FEATS}
for g,cs in GROUPS.items(): sets[f"base+{g}"]=FEATS+cs
sets["base+ALL"]=FEATS+ALL
for g,cs in GROUPS.items(): sets[f"base+ALL-minus-{g}"]=FEATS+[c for c in ALL if c not in cs]
sets["ALL_new_only"]=ALL; sets["pHEC+ALL_new"]=["pH","EC"]+ALL
sets["diag:lonlat_only"]=LL; sets["diag:base+lonlat"]=FEATS+LL; sets["diag:base+lonlat+ALL"]=FEATS+LL+ALL
res=[]
def show(r,name): print(f"{name:<30} N {r[r.target=='N'].R2.mean():.3f} P {r[r.target=='P'].R2.mean():.3f} K {r[r.target=='K'].R2.mean():.3f} OC {r[r.target=='OC'].R2.mean():.3f}  ({time.time()-t0:.0f}s)",flush=True)
for name,cols in sets.items():
    r=evaluate_region_wise(data,groups,cols,name); res.append(r); show(r,name)
pd.concat(res).to_csv(FEATDIR+"out/eval_results.csv",index=False)
for seed in [7,13,99,2024]:
    for name in ["base_41","base+ALL","diag:base+lonlat","diag:base+lonlat+ALL"]:
        res.append(evaluate_region_wise(data,groups,sets[name],name,seed=seed))
    pd.concat(res).to_csv(FEATDIR+"out/eval_results.csv",index=False); print("seed",seed,"done",flush=True)
# location-encoding score: how well each group predicts lon/lat inside a region (same spatial CV)
cv=GroupKFold(n_splits=5,shuffle=True,random_state=42); loc=[]
for g,cs in list(GROUPS.items())+[("base_41",FEATS)]:
    for reg in REGIONS:
        idx=np.where(data.region==reg)[0]; sub=data.iloc[idx]; gg=groups[idx]
        for tgt in LL:
            y=sub[tgt].to_numpy(); oof=np.zeros(len(sub))
            for a,b in cv.split(sub,y,gg):
                oof[b]=RandomForestRegressor(n_estimators=200,min_samples_leaf=3,max_features=0.33,n_jobs=-1,random_state=42).fit(sub[cs].iloc[a],y[a]).predict(sub[cs].iloc[b])
            loc.append(dict(group=g,region=reg,coord=tgt,R2=r2_score(y,oof)))
L=pd.DataFrame(loc); L.to_csv(FEATDIR+"out/location_encoding.csv",index=False)
print(L.groupby("group").R2.mean().round(3)); print("done",f"{time.time()-t0:.0f}s")
