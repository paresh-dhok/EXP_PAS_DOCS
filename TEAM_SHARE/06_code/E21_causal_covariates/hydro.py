# Hydrology terrain from Copernicus GLO-90 over Maharashtra (+0.3 deg buffer): TWI, HAND, flow acc, dist to stream, curvature
import sys,time; sys.path.insert(0,__file__.rsplit('/',1)[0]); from geo import *
import rasterio
from rasterio.merge import merge
from scipy import ndimage
t0=time.time(); cat=catalog()
items=list(cat.search(collections=["cop-dem-glo-90"],bbox=[72.1,15.1,81.5,22.6]).items()); print("dem tiles",len(items),flush=True)
from dl import get
os.makedirs(OUT+"/dem",exist_ok=True)
from concurrent.futures import ThreadPoolExecutor
paths=list(ThreadPoolExecutor(8).map(lambda it: get(href(it,"data"),OUT+"/dem/"+it.id+".tif"),items))
print("downloaded",f"{time.time()-t0:.0f}s",flush=True)
srcs=[rasterio.open(q) for q in paths]
dem,tr=merge(srcs,bounds=(72.1,15.1,81.5,22.6),nodata=-32767); dem=dem[0].astype("float32"); prof=srcs[0].profile
dem[dem<=-1000]=np.nan; print("mosaic",dem.shape,f"{time.time()-t0:.0f}s",flush=True)
dem_f=np.where(np.isnan(dem),0,dem).astype("float32")   # sea/nodata -> 0 m
path=OUT+"/dem90_mh.tif"
with rasterio.open(path,"w",driver="GTiff",height=dem_f.shape[0],width=dem_f.shape[1],count=1,dtype="float32",crs="EPSG:4326",transform=tr,nodata=-9999) as d: d.write(dem_f,1)
np.in1d = np.isin  # numpy>=2.4 removed in1d; pysheds still calls it
from pysheds.grid import Grid
grid=Grid.from_raster(path); r=grid.read_raster(path)
r=grid.fill_pits(r); r=grid.fill_depressions(r); r=grid.resolve_flats(r); print("conditioned",f"{time.time()-t0:.0f}s",flush=True)
fdir=grid.flowdir(r); acc=grid.accumulation(fdir); print("acc",f"{time.time()-t0:.0f}s",flush=True)
STREAM=1000  # cells (~8 km2 at 90 m)
hand=grid.compute_hand(fdir,r,acc>STREAM); print("hand",f"{time.time()-t0:.0f}s",flush=True)
acc=np.asarray(acc,dtype="float64"); hand=np.asarray(hand,dtype="float32")
# metric cell sizes
ny,nx=dem_f.shape; lat=tr.f+tr.e*(np.arange(ny)+0.5)
dy=abs(tr.e)*110574.0; dx=(tr.a*111320.0*np.cos(np.deg2rad(lat)))[:,None]
z=dem_f.astype("float64")
gy,gx=np.gradient(z); gy=gy/dy; gx=gx/dx   # dz/drow, dz/dcol
slope=np.arctan(np.hypot(gx,gy))
area=(acc+1)*(dx*dy); width=np.sqrt(dx*dy)
twi=np.log(area/width/np.maximum(np.tan(slope),1e-3)).astype("float32")
# curvature (Zevenbergen-Thorne style from second derivatives)
zyy,zyx=np.gradient(gy); zxy,zxx=np.gradient(gx); zyy/=dy; zxx=zxx/dx; zxy=zxy/dy
p2=gx**2+gy**2+1e-12
prof_c=(-(zxx*gx**2+2*zxy*gx*gy+zyy*gy**2)/p2).astype("float32")
plan_c=(-(zxx*gy**2-2*zxy*gx*gy+zyy*gx**2)/p2).astype("float32")
stream=acc>STREAM
dist=ndimage.distance_transform_edt(~stream,sampling=(dy,float(np.mean(dx)))).astype("float32")
pts=points(); inv=~tr; c,rw=inv*(pts.longitude.to_numpy(),pts.latitude.to_numpy()); rw=rw.astype(int); c=c.astype(int)
def at(a): return a[rw,c]
def mean3(a): return ndimage.uniform_filter(a.astype("float32"),3)[rw,c]
out=pd.DataFrame({"id":pts.id,"twi":mean3(twi),"flow_acc_log":np.log1p(at(acc)),"hand":at(hand),"dist_stream":at(dist),
                  "curv_prof":mean3(prof_c),"curv_plan":mean3(plan_c)})
out.to_parquet(OUT+"/f_hydro.parquet",index=False); print(out.describe().T.round(3)); print("done",f"{time.time()-t0:.0f}s")
