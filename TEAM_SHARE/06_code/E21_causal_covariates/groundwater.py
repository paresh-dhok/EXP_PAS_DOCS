# CGWB groundwater quality (2019-2021 station tables, Maharashtra + neighbours within 50 km) -> IDW of 8 nearest stations (log space) + distance to nearest station
import sys; sys.path.insert(0,__file__.rsplit('/',1)[0]); from geo import *
from scipy.spatial import cKDTree
g=pd.read_csv(OUT+"/cgwb/cgwb_gwq_stations.csv",dtype=str)
for c in ["latitude","longitude","EC","NO3","K","Na","Cl","HCO3","pH"]: g[c]=pd.to_numeric(g[c],errors="coerce")
g=g[g.latitude.between(14.5,23)&g.longitude.between(71.5,82)&g.EC.notna()&g.K.notna()]
print("stations used:",len(g),g.state.value_counts().head(8).to_dict())
xy=lambda lo,la: np.c_[lo*111320*np.cos(np.deg2rad(la)),la*110574]
T=cKDTree(xy(g.longitude.to_numpy(),g.latitude.to_numpy())); pts=points()
d,i=T.query(xy(pts.longitude.to_numpy(),pts.latitude.to_numpy()),k=8); w=1/np.maximum(d,100)
out=pd.DataFrame({"id":pts.id,"gw_dist_nearest":d[:,0]})
for c in ["EC","NO3","K","Na","Cl","HCO3","pH"]:
    v=g[c].to_numpy()[i]; v=np.log1p(np.clip(v,0,None)) if c!="pH" else v
    m=~np.isnan(v); out[f"gw_{c}"]=(np.where(m,v,0)*w).sum(1)/np.where(m,w,0).sum(1)
out.to_parquet(OUT+"/f_groundwater.parquet",index=False); print(out.describe().T.round(3))
