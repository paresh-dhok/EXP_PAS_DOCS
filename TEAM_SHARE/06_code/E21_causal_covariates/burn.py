# MODIS MCD64A1 burned area (500 m) 2015-2023: months burned at pixel and within 3x3 (1.5 km)
import sys,time; sys.path.insert(0,__file__.rsplit('/',1)[0]); from geo import *
import rasterio, pyproj
from rasterio.windows import Window
from concurrent.futures import ThreadPoolExecutor
t0=time.time(); cat=catalog(); pts=points()
items=list(cat.search(collections=["modis-64A1-061"],bbox=BBOX,datetime="2015-01-01/2023-12-31").items()); print("items",len(items),flush=True)
lon,lat=pts.longitude.to_numpy(),pts.latitude.to_numpy()
def do(it):
    for a in range(4):
        try:
            with rasterio.open(href(it,"Burn_Date")) as s:
                x,y=pyproj.Transformer.from_crs("EPSG:4326",s.crs,always_xy=True).transform(lon,lat)
                c,r=~s.transform*(x,y); r=np.floor(r).astype(int); c=np.floor(c).astype(int)
                m=(r>=1)&(r<s.height-1)&(c>=1)&(c<s.width-1)
                if not m.any(): return None
                a_=s.read(1)>0
                from scipy import ndimage
                nb=ndimage.maximum_filter(a_,3)
                return pd.DataFrame({"i":np.where(m)[0],"b":a_[r[m],c[m]],"b3":nb[r[m],c[m]]})
        except Exception as e:
            err=e; time.sleep(5)
    print("FAIL",it.id,err,flush=True); return None
with ThreadPoolExecutor(8) as ex: res=[x for x in ex.map(do,items) if x is not None]
d=pd.concat(res).groupby("i")[["b","b3"]].sum().rename(columns={"b":"burn_months","b3":"burn_months_1500m"})
d=d.reindex(range(len(pts))).fillna(0); d.insert(0,"id",pts.id.values)
d.to_parquet(OUT+"/f_burn.parquet",index=False); print(d.describe().T.round(3)); print("done",f"{time.time()-t0:.0f}s")
