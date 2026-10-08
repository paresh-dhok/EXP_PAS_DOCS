# Sentinel-1 RTC (PC), kharif Jul-Oct 2023 and dry Mar-Apr 2024, read at ~80 m (8x decimation): VV/VH stats, flood frequency
import sys,time; sys.path.insert(0,__file__.rsplit('/',1)[0]); from geo import *
import rasterio, pyproj
from rasterio.enums import Resampling
from concurrent.futures import ThreadPoolExecutor
t0=time.time(); cat=catalog(); pts=points(); lon,lat=pts.longitude.to_numpy(),pts.latitude.to_numpy()
items=[]
for dt in ["2023-07-01/2023-10-31","2024-03-01/2024-04-30"]:
    items+=list(cat.search(collections=["sentinel-1-rtc"],bbox=BBOX,datetime=dt).items())
print("items",len(items),flush=True)
DEC=8
def do(it):
    for a in range(4):
        try:
            res=[]
            for band in ["vv","vh"]:
                with rasterio.open(href(it,band)) as s:
                    x,y=pyproj.Transformer.from_crs("EPSG:4326",s.crs,always_xy=True).transform(lon,lat)
                    c,r=~s.transform*(x,y); m=(r>=0)&(r<s.height)&(c>=0)&(c<s.width)
                    if not m.any(): return None
                    H,W=s.height//DEC,s.width//DEC
                    arr=s.read(1,out_shape=(H,W),resampling=Resampling.average).astype("float32")
                    rr=np.clip((r[m]/DEC).astype(int),0,H-1); cc=np.clip((c[m]/DEC).astype(int),0,W-1)
                    v=arr[rr,cc]; v[(v<=0)|~np.isfinite(v)]=np.nan
                    res.append(10*np.log10(v))
            return pd.DataFrame({"i":np.where(m)[0],"date":pd.Timestamp(it.datetime).tz_localize(None),"vv":res[0],"vh":res[1]})
        except Exception as e: err=e; time.sleep(10)
    print("FAIL",it.id,err,flush=True); return None
recs=[]
with ThreadPoolExecutor(6) as ex:
    for n,r in enumerate(ex.map(do,items)):
        if r is not None: recs.append(r)
        if n%20==0: print(n,f"{time.time()-t0:.0f}s",flush=True)
ts=pd.concat(recs).dropna(); ts.to_parquet(OUT+"/s1_ts.parquet",index=False)
ts["season"]=np.where(ts.date.dt.year==2023,"kharif","dry")
g=ts.groupby(["i","season"])
f=pd.concat({"vv_med":g.vv.median(),"vh_med":g.vh.median(),"vh_sd":g.vh.std(),"vv_min":g.vv.min(),
             "flood_freq":g.vv.apply(lambda s:(s<-18).mean())},axis=1).unstack("season")
f.columns=[f"s1_{a}_{b}" for a,b in f.columns]
f["s1_vh_kharif_minus_dry"]=f["s1_vh_med_kharif"]-f["s1_vh_med_dry"]
f=f.reindex(range(len(pts))); f.insert(0,"id",pts.id.values)
f.to_parquet(OUT+"/f_s1.parquet",index=False); print(f.describe().T.round(2)); print("done",f"{time.time()-t0:.0f}s")
