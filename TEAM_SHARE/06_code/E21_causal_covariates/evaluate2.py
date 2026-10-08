# Follow-up: (a) score SoilGrids + WorldCereal, (b) each group's gain ON TOP OF base_41 + lon/lat (field information beyond location)
import sys,glob,os,time; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import common
common.D=os.environ.get("REPO_TS",common.D); common.FEATDIR=os.environ.get("FEATDIR",common.FEATDIR)
from common import *
t0=time.time(); data,groups=load(); FD=common.FEATDIR
GROUPS={}
for f in sorted(glob.glob(FD+"f_*.parquet")):
    g=os.path.basename(f)[2:-8]; x=pd.read_parquet(f)
    cols=[c for c in x.columns if c!="id" and x[c].notna().mean()>0.5 and x[c].nunique()>1]
    data=data.merge(x[["id"]+cols],on="id",how="left"); GROUPS[g]=cols
print({g:len(c) for g,c in GROUPS.items()},len(data),flush=True)
ALL=[c for cs in GROUPS.values() for c in cs]; LL=["longitude","latitude"]
sets={"base_41":FEATS,"base+soilgrids":FEATS+GROUPS["soilgrids"],"base+wcereal":FEATS+GROUPS["wcereal"],"base+ALL12":FEATS+ALL,
      "base+ALL12-minus-groundwater":FEATS+[c for c in ALL if c not in GROUPS["groundwater"]],
      "diag:base+lonlat":FEATS+LL}
for g,cs in GROUPS.items(): sets[f"diag:base+lonlat+{g}"]=FEATS+LL+cs
sets["diag:base+lonlat+ALL12"]=FEATS+LL+ALL
res=[]
for name,cols in sets.items():
    r=evaluate_region_wise(data,groups,cols,name); res.append(r)
    print(f"{name:<34} N {r[r.target=='N'].R2.mean():.3f} P {r[r.target=='P'].R2.mean():.3f} K {r[r.target=='K'].R2.mean():.3f} OC {r[r.target=='OC'].R2.mean():.3f}  ({time.time()-t0:.0f}s)",flush=True)
    pd.concat(res).to_csv(FD+"eval2_results.csv",index=False)
print("done",f"{time.time()-t0:.0f}s")
