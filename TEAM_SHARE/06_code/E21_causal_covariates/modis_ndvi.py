# MODIS MOD13Q1 250 m NDVI, Jun 2019 - May 2024, sampled at points -> seasonal / irrigation proxy features
import sys,time; sys.path.insert(0,__file__.rsplit('/',1)[0]); from geo import *
import rasterio, pyproj
from rasterio.windows import Window
from concurrent.futures import ThreadPoolExecutor
t0=time.time(); cat=catalog(); pts=points()
items=list(cat.search(collections=["modis-13Q1-061"],bbox=BBOX,datetime="2019-06-01/2024-05-31").items())
print("items",len(items),flush=True)
lon,lat=pts.longitude.to_numpy(),pts.latitude.to_numpy()
recs=[]
def do(it):
    for k in range(4):
        try:
            with rasterio.open(href(it,"250m_16_days_NDVI")) as s, rasterio.open(href(it,"250m_16_days_pixel_reliability")) as q:
                x,y=pyproj.Transformer.from_crs("EPSG:4326",s.crs,always_xy=True).transform(lon,lat)
                c,r=~s.transform*(x,y); r=np.floor(r).astype(int); c=np.floor(c).astype(int)
                m=(r>=0)&(r<s.height)&(c>=0)&(c<s.width)
                if not m.any(): return None
                r0,r1,c0,c1=r[m].min(),r[m].max()+1,c[m].min(),c[m].max()+1
                w=Window(c0,r0,c1-c0,r1-r0)
                nd=s.read(1,window=w)[r[m]-r0,c[m]-c0].astype("float32"); qq=q.read(1,window=w)[r[m]-r0,c[m]-c0]
                nd[(qq>1)|(nd<-2000)]=np.nan
                return pd.DataFrame({"i":np.where(m)[0],"date":pd.Timestamp(it.datetime or it.properties["start_datetime"]).tz_localize(None),"ndvi":nd/10000})
        except Exception as e:
            err=e; time.sleep(5)
    print("FAIL",it.id,err,flush=True); return None
with ThreadPoolExecutor(8) as ex:
    for n,res in enumerate(ex.map(do,items)):
        if res is not None: recs.append(res)
        if n%50==0: print(n,f"{time.time()-t0:.0f}s",flush=True)
ts=pd.concat(recs); ts.to_parquet(OUT+"/modis_ndvi_ts.parquet",index=False)
m=ts.date.dt.month; ts["agyear"]=np.where(m>=6,ts.date.dt.year,ts.date.dt.year-1)
ts["season"]=np.select([m.isin([7,8,9,10]),m.isin([11,12,1,2]),m.isin([3,4,5])],["kharif","rabi","zaid"],"other")
s=ts[ts.season!="other"].groupby(["i","agyear","season"]).ndvi.max().unstack("season")
f=pd.DataFrame(index=s.index.get_level_values(0).unique())
for se in ["kharif","rabi","zaid"]:
    f[f"ndvi_{se}_max"]=s[se].groupby(level=0).mean()
    f[f"green_{se}_freq"]=(s[se]>0.4).groupby(level=0).mean()      # share of years green in season
f["n_seasons_green"]=(s>0.4).sum(axis=1).groupby(level=0).mean()  # cropping intensity proxy
f["irrig_proxy"]=((s["rabi"]>0.4)|(s["zaid"]>0.4)).groupby(level=0).mean()  # green outside monsoon
ann=ts.groupby(["i","agyear"]).ndvi.agg(["max","min","mean"])
f["ndvi_amp"]=(ann["max"]-ann["min"]).groupby(level=0).mean(); f["ndvi_mean"]=ann["mean"].groupby(level=0).mean()
f["ndvi_interannual_sd"]=ann["mean"].groupby(level=0).std()
f=f.reindex(range(len(pts))); f.insert(0,"id",pts.id.values)
f.to_parquet(OUT+"/f_ndvi.parquet",index=False); print(f.describe().T.round(3)); print("done",f"{time.time()-t0:.0f}s")
