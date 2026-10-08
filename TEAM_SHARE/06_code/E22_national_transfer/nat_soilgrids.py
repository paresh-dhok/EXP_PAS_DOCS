# SoilGrids v2 250 m, India window per layer, sampled at all points
import sys,os,time; sys.path.insert(0,os.path.dirname(__file__)); from natcommon import *
import rasterio, pyproj
from rasterio.windows import Window
t0=time.time(); P=points(); lon,lat=P.lon.to_numpy(),P.lat.to_numpy(); out=pd.DataFrame({"id":P.id})
for v in ["clay","sand","silt","cec","soc","phh2o","nitrogen","bdod","cfvo"]:
    for d in ["0-5cm","5-15cm"]:
        for a in range(5):
            try:
                with rasterio.open(f"/vsicurl/https://files.isric.org/soilgrids/latest/data/{v}/{v}_{d}_mean.vrt") as s:
                    x,y=pyproj.Transformer.from_crs("EPSG:4326",s.crs,always_xy=True).transform(lon,lat)
                    c,r=~s.transform*(x,y); r=np.floor(r).astype(int); c=np.floor(c).astype(int)
                    r0,c0=r.min(),c.min(); arr=s.read(1,window=Window(c0,r0,c.max()-c0+1,r.max()-r0+1)).astype("float32")
                    val=arr[r-r0,c-c0]; val[val==s.nodata]=np.nan; out[f"sg_{v}_{d.replace('-','_')}"]=val; del arr
                break
            except Exception as e: print("retry",v,d,e,flush=True); time.sleep(20)
        print(v,d,f"{time.time()-t0:.0f}s",flush=True)
save(out,"soilgrids")
