# Recompute NDVI season features from the saved MODIS time series, full crop years Jun 2019 - May 2024 only
import sys; sys.path.insert(0,'.'); from geo import *
pts=points(); ts=pd.read_parquet(OUT+"/modis_ndvi_ts.parquet")
m=ts.date.dt.month; ts["agyear"]=np.where(m>=6,ts.date.dt.year,ts.date.dt.year-1); ts=ts[ts.agyear.between(2019,2023)].copy(); m=ts.date.dt.month
ts["season"]=np.select([m.isin([7,8,9,10]),m.isin([11,12,1,2]),m.isin([3,4,5])],["kharif","rabi","zaid"],"other")
s=ts[ts.season!="other"].groupby(["i","agyear","season"]).ndvi.max().unstack("season")
f=pd.DataFrame(index=s.index.get_level_values(0).unique())
for se in ["kharif","rabi","zaid"]:
    f[f"ndvi_{se}_max"]=s[se].groupby(level=0).mean(); f[f"green_{se}_freq"]=(s[se]>0.4).groupby(level=0).mean()
f["n_seasons_green"]=(s>0.4).sum(axis=1).groupby(level=0).mean()
f["irrig_proxy"]=((s["rabi"]>0.4)|(s["zaid"]>0.4)).groupby(level=0).mean()
ann=ts.groupby(["i","agyear"]).ndvi.agg(["max","min","mean"])
f["ndvi_amp"]=(ann["max"]-ann["min"]).groupby(level=0).mean(); f["ndvi_mean"]=ann["mean"].groupby(level=0).mean(); f["ndvi_interannual_sd"]=ann["mean"].groupby(level=0).std()
f=f.reindex(range(len(pts))); f.insert(0,"id",pts.id.values); f.to_parquet(OUT+"/f_ndvi.parquet",index=False)
print(f.describe().T.round(3)[["count","min","50%","max"]])
