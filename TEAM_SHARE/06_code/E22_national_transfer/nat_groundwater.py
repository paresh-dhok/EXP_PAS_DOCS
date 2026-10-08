# CGWB 2019-21 stations, all-India: IDW of 8 nearest (log space) + distance to nearest station
import sys,os; sys.path.insert(0,os.path.dirname(__file__)); from natcommon import *
from scipy.spatial import cKDTree
g=pd.read_csv(HOME+"features/cgwb_gwq_stations.csv",dtype=str)
for c in ["latitude","longitude","EC","NO3","K","Na","Cl","HCO3","pH"]: g[c]=pd.to_numeric(g[c],errors="coerce")
g=g[g.latitude.between(6,37.5)&g.longitude.between(68,97.5)&g.EC.notna()&g.K.notna()]; print("stations",len(g),flush=True)
xy=lambda lo,la: np.c_[lo*111320*np.cos(np.deg2rad(la)),la*110574]
P=points(); d,i=cKDTree(xy(g.longitude.to_numpy(),g.latitude.to_numpy())).query(xy(P.lon.to_numpy(),P.lat.to_numpy()),k=8); w=1/np.maximum(d,100)
out=pd.DataFrame({"id":P.id,"gw_dist_nearest":d[:,0]})
for c in ["EC","NO3","K","Na","Cl","HCO3","pH"]:
    v=g[c].to_numpy()[i]; v=np.log1p(np.clip(v,0,None)) if c!="pH" else v; m=~np.isnan(v)
    out[f"gw_{c}"]=(np.where(m,v,0)*w).sum(1)/np.where(m,w,0).sum(1)
save(out,"groundwater")
