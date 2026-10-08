# Impact Observatory annual LULC v02 (10 m) 2017-2023: years as crop / built / trees / bare at point (3x3 majority)
import sys,time; sys.path.insert(0,__file__.rsplit('/',1)[0]); from geo import *
import rasterio, pyproj
from rasterio.windows import Window
from concurrent.futures import ThreadPoolExecutor
t0=time.time(); cat=catalog(); pts=points()
items=list(cat.search(collections=["io-lulc-annual-v02"],bbox=BBOX).items()); print("items",len(items),flush=True)
lon,lat=pts.longitude.to_numpy(),pts.latitude.to_numpy()
def do(it):
    for a in range(4):
        try:
            with rasterio.open(href(it,"data")) as s:
                x,y=pyproj.Transformer.from_crs("EPSG:4326",s.crs,always_xy=True).transform(lon,lat)
                c,r=~s.transform*(x,y); r=np.floor(r).astype(int); c=np.floor(c).astype(int)
                m=(r>=1)&(r<s.height-1)&(c>=1)&(c<s.width-1)
                if not m.any(): return None
                idx=np.where(m)[0]; vals=[]
                # read per point 3x3 (points are sparse; group would read huge windows)
                for i in idx:
                    v=s.read(1,window=Window(c[i]-1,r[i]-1,3,3)).ravel()
                    vals.append(np.bincount(v,minlength=12).argmax())
                yr=pd.Timestamp(it.properties.get("start_datetime") or it.datetime).year
                return pd.DataFrame({"i":idx,"year":yr,"cls":vals})
        except Exception as e:
            err=e; time.sleep(5)
    print("FAIL",it.id,err,flush=True); return None
with ThreadPoolExecutor(12) as ex: res=[x for x in ex.map(do,items) if x is not None]
d=pd.concat(res).drop_duplicates(["i","year"])
p=d.pivot(index="i",columns="year",values="cls")
f=pd.DataFrame(index=p.index)
for code,name in {5:"crop",7:"built",2:"trees",8:"bare",11:"range",1:"water"}.items(): f[f"io_{name}_years"]=(p==code).sum(axis=1)
f["io_n_years"]=p.notna().sum(axis=1); f["io_changes"]=(p.diff(axis=1).fillna(0)!=0).sum(axis=1)
f=f.reindex(range(len(pts))); f.insert(0,"id",pts.id.values)
f.to_parquet(OUT+"/f_iolulc.parquet",index=False); print(f.describe().T.round(3)); print("done",f"{time.time()-t0:.0f}s")
