# Copernicus GLO-90: elev, slope, TPI (~500 m, ~2 km), roughness, per 1-deg tile with 0.1-deg buffer, all-India points
import sys,os,time; sys.path.insert(0,os.path.dirname(__file__)); from natcommon import *
import rasterio
from rasterio.merge import merge
from scipy import ndimage
from concurrent.futures import ThreadPoolExecutor
t0=time.time(); P=points(); lon,lat=P.lon.to_numpy(),P.lat.to_numpy()
cells=sorted(set(zip(np.floor(lon).astype(int),np.floor(lat).astype(int)))); print("1-deg cells with points",len(cells),flush=True)
cat=catalog(); items=list(cat.search(collections=["cop-dem-glo-90"],bbox=BBOX).items()); print("dem items",len(items),flush=True)
os.makedirs(CACHE+"dem90",exist_ok=True)
import requests
def get(it):
    dst=CACHE+"dem90/"+it.id+".tif"
    if not os.path.exists(dst):
        for a in range(5):
            try:
                with requests.get(href(it,"data"),stream=True,timeout=300) as q:
                    q.raise_for_status(); open(dst+".part","wb").writelines(q.iter_content(2**22))
                os.rename(dst+".part",dst); break
            except Exception as e: time.sleep(10)
    return dst
paths=list(ThreadPoolExecutor(12).map(get,items)); print("downloaded",f"{time.time()-t0:.0f}s",flush=True)
idx={}
for p in paths:
    with rasterio.open(p) as s: b=s.bounds; idx[(int(round(b.left)),int(round(b.bottom)))]=p
cols={k:np.full(len(P),np.nan,dtype="float32") for k in ["elev","slope","tpi_500m","tpi_2km","rough_270m"]}
cx,cy=np.floor(lon).astype(int),np.floor(lat).astype(int)
def do(cell):
    x0,y0=cell; nb=[idx[(x,y)] for x in (x0-1,x0,x0+1) for y in (y0-1,y0,y0+1) if (x,y) in idx]
    if (x0,y0) not in idx: return
    srcs=[rasterio.open(p) for p in nb]
    dem,tr=merge(srcs,bounds=(x0-0.1,y0-0.1,x0+1.1,y0+1.1),nodata=-32767); [s.close() for s in srcs]
    z=dem[0].astype("float32"); z[z<-1000]=np.nan
    dy=abs(tr.e)*110574; dx=tr.a*111320*np.cos(np.deg2rad(y0+0.5))
    gy,gx=np.gradient(np.nan_to_num(z)); slope=np.degrees(np.arctan(np.hypot(gx/dx,gy/dy)))
    zz=np.nan_to_num(z)
    t5=zz-ndimage.uniform_filter(zz,11); t2=zz-ndimage.uniform_filter(zz,45); rg=ndimage.generic_filter(zz,np.ptp,3) if False else ndimage.maximum_filter(zz,3)-ndimage.minimum_filter(zz,3)
    m=np.where((cx==x0)&(cy==y0))[0]; c,r=~tr*(lon[m],lat[m]); r=np.clip(r.astype(int),0,z.shape[0]-1); c=np.clip(c.astype(int),0,z.shape[1]-1)
    for k,a in [("elev",z),("slope",slope),("tpi_500m",t5),("tpi_2km",t2),("rough_270m",rg)]: cols[k][m]=a[r,c]
with ThreadPoolExecutor(12) as ex:
    for n,_ in enumerate(ex.map(do,cells)):
        if n%100==0: print(n,f"{time.time()-t0:.0f}s",flush=True)
out=pd.DataFrame({"id":P.id,**cols}); save(out,"terrain")
