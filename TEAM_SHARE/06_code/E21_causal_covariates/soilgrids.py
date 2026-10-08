# SoilGrids v2 (250 m): clay, sand, silt, cec, soc, phh2o, nitrogen, bdod, cfvo at 0-5 and 5-15 cm (point sample)
import sys,time; sys.path.insert(0,__file__.rsplit('/',1)[0]); from geo import *
import rasterio, pyproj
from concurrent.futures import ThreadPoolExecutor
t0=time.time(); pts=points(); lon,lat=pts.longitude.to_numpy(),pts.latitude.to_numpy()
V=["clay","sand","silt","cec","soc","phh2o","nitrogen","bdod","cfvo"]; DEP=["0-5cm","5-15cm"]
def one(job):
    v,d=job
    for a in range(5):
        try:
            with rasterio.open(f"/vsicurl/https://files.isric.org/soilgrids/latest/data/{v}/{v}_{d}_mean.vrt") as s:
                x,y=pyproj.Transformer.from_crs("EPSG:4326",s.crs,always_xy=True).transform(lon,lat)
                c,r=~s.transform*(x,y); r=np.floor(r).astype(int); c=np.floor(c).astype(int)
                r0,r1,c0,c1=r.min(),r.max()+1,c.min(),c.max()+1
                arr=s.read(1,window=rasterio.windows.Window(c0,r0,c1-c0,r1-r0)).astype("float32")
                vals=arr[r-r0,c-c0]; vals[vals==s.nodata]=np.nan
                print(v,d,f"{time.time()-t0:.0f}s",flush=True); return f"sg_{v}_{d.replace('-','_')}",vals
        except Exception as e: err=e; time.sleep(10)
    print("FAIL",v,d,err,flush=True); return f"sg_{v}_{d}",np.full(len(pts),np.nan)
out=pd.DataFrame({"id":pts.id})
with ThreadPoolExecutor(6) as ex:
    for k,vals in ex.map(one,[(v,d) for v in V for d in DEP]): out[k]=vals
out.to_parquet(OUT+"/f_soilgrids.parquet",index=False); print(out.describe().T.round(2)); print("done",f"{time.time()-t0:.0f}s")
