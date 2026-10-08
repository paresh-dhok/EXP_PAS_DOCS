# All-India SHC -> independent locations, mirroring Paresh's D02 (repeated GPS) + D07 limits + D08 de-clustering (30 m, drop >10, merge 2-10)
# Differences from the MH pipeline (by design): no date / season / satellite filter, so undated and older-cycle records are kept.
import pandas as pd, numpy as np, shapely, time, json
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
t0=time.time(); OUT=__file__.rsplit('/',1)[0]+"/"
SRC="/Users/mihirmohite/Downloads/TEAM_SHARE/01_source_data/SLUSI_SHC_all_india.parquet"
SOIL=["N","P","K","OC","pH","EC"]; MICRO=["S","Zn","Fe","Cu","Mn","B"]
df=pd.read_parquet(SRC,columns=["id","sid","did","cycle","date","geometry"]+SOIL+MICRO)
log={"raw":len(df)}
for c in SOIL+MICRO: df[c]=pd.to_numeric(df[c],errors="coerce")
p=shapely.from_wkb(df.geometry.values); df["lon"]=shapely.get_x(p); df["lat"]=shapely.get_y(p)
df["date"]=pd.to_datetime(df.date,format="%m/%d/%y, %I:%M %p",errors="coerce")
df.loc[~df.date.dt.year.between(2014,2025),"date"]=pd.NaT
df=df[df.lon.between(68,98)&df.lat.between(6,37.5)]; log["inside_india_bbox"]=len(df)
lim=(df.N.between(20,1500)&df.P.between(1,300)&df.K.between(20,3000)&(df.OC>0.02)&(df.OC<=5)&df.pH.between(3.5,10.5)&(df.EC>0.005)&(df.EC<=10))
df=df[lim].copy(); log["plausible_values"]=len(df)
# D02: records sharing an exact GPS point. Identical soil values = copy -> keep one; different values -> drop all
df["gkey"]=df.geometry
g=df.groupby("gkey")
n=g.N.transform("size"); nvar=g[SOIL].transform("nunique").max(axis=1)
rep=df[n>1]; rep[["id","sid","did","cycle","date","lon","lat"]+SOIL].to_parquet(OUT+"repeated_gps_records.parquet",index=False)  # kept aside for year-on-year work
keep=(n==1)|(nvar==1)
df=df[keep].drop_duplicates("gkey").drop(columns=["gkey","geometry"]); log["after_repeated_gps_rule"]=len(df)
log["repeated_gps_records_set_aside"]=int((n>1).sum())
# D08: 30 m clusters
x=df.lon.to_numpy()*111320*np.cos(np.deg2rad(df.lat.to_numpy())); y=df.lat.to_numpy()*110574
tree=cKDTree(np.c_[x,y]); pairs=tree.query_pairs(30,output_type="ndarray"); print("pairs",len(pairs),f"{time.time()-t0:.0f}s",flush=True)
m=len(df); A=coo_matrix((np.ones(len(pairs)),(pairs[:,0],pairs[:,1])),shape=(m,m))
nc,lab=connected_components(A,directed=False); df["cl"]=lab
size=df.groupby("cl").cl.transform("size"); df["cl_size"]=size
log["isolated"]=int((size==1).sum()); log["in_clusters_2_10"]=int(size.between(2,10).sum()); log["in_clusters_gt10"]=int((size>10).sum())
log["clusters_gt10"]=int(df.loc[size>10,"cl"].nunique()); log["largest_cluster"]=int(size.max())
df=df[size<=10]
agg={c:"median" for c in ["lon","lat"]+SOIL+MICRO}
agg.update({"id":lambda s:"|".join(s),"sid":lambda s:s.mode().iat[0],"did":lambda s:s.mode().iat[0],
            "cycle":lambda s:"|".join(sorted(set(s.dropna()))),"date":"min"})
single=df[df.cl_size==1].copy(); single["ids_merged"]=single.id; single["n_merged"]=1; single["cycles"]=single.cycle
multi=df[df.cl_size>1].groupby("cl").agg(agg).reset_index(drop=True)
multi["n_merged"]=multi.id.str.count(r"\|")+1; multi["ids_merged"]=multi.id; multi["cycles"]=multi.cycle; multi["id"]=multi.id.str.split("|").str[0]
cols=["id","ids_merged","n_merged","sid","did","cycles","date","lon","lat"]+SOIL+MICRO
loc=pd.concat([single[cols],multi[cols]],ignore_index=True); log["locations_after_merge"]=len(loc)
# remove locations still < 30 m apart after merging
x=loc.lon.to_numpy()*111320*np.cos(np.deg2rad(loc.lat.to_numpy())); y=loc.lat.to_numpy()*110574
pr=cKDTree(np.c_[x,y]).query_pairs(30,output_type="ndarray"); bad=np.unique(pr.ravel())
loc=loc.drop(index=bad).reset_index(drop=True); log["still_close_removed"]=int(len(bad)); log["final_locations"]=len(loc)
loc["has_date"]=loc.date.notna()
loc.to_parquet(OUT+"india_locations.parquet",index=False)
log["by_state"]=loc.groupby("sid").size().sort_values(ascending=False).to_dict()
log["merged_size_dist"]=loc.n_merged.value_counts().sort_index().to_dict()
json.dump(log,open(OUT+"india_locations_log.json","w"),indent=1,default=int)
print(json.dumps({k:v for k,v in log.items() if k!="by_state"},indent=1,default=int)); print("done",f"{time.time()-t0:.0f}s")
