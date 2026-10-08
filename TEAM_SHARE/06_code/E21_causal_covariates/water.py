# JRC Global Surface Water occurrence (30 m) -> occurrence at point, within 500 m / 1 km, distance to water
import sys,time; sys.path.insert(0,__file__.rsplit('/',1)[0]); from geo import *
import rasterio
from rasterio.merge import merge
from scipy import ndimage
t0=time.time(); cat=catalog(); pts=points()
items=list(cat.search(collections=["jrc-gsw"],bbox=BBOX).items()); print("tiles",len(items),[i.id for i in items],flush=True)
srcs=[rasterio.open(href(it,"occurrence")) for it in items]
occ,tr=merge(srcs,bounds=(72.3,15.3,81.3,22.4),nodata=255); occ=occ[0]; print("mosaic",occ.shape,f"{time.time()-t0:.0f}s",flush=True)
occ=np.where(occ==255,0,occ).astype("uint8")
inv=~tr; c,r=inv*(pts.longitude.to_numpy(),pts.latitude.to_numpy()); r=r.astype(int); c=c.astype(int)
lat=pts.latitude.to_numpy(); px=abs(tr.e)*110574  # ~30 m
out=pd.DataFrame({"id":pts.id})
out["gsw_occ_pt"]=ndimage.uniform_filter(occ.astype("float32"),3)[r,c]
for rad in [500,1000]:
    k=int(round(rad/px)); 
    out[f"gsw_occ_max_{rad}m"]=ndimage.maximum_filter(occ,size=2*k+1)[r,c]
    out[f"gsw_ever_frac_{rad}m"]=ndimage.uniform_filter((occ>0).astype("float32"),size=2*k+1)[r,c]
# distance to water (occurrence>=10) on 90 m grid
w=ndimage.maximum_filter(occ>=10,size=3)[::3,::3]
d=ndimage.distance_transform_edt(~w,sampling=(px*3,px*3*np.cos(np.deg2rad(19)))).astype("float32")
out["dist_water"]=d[r//3,c//3]
out.to_parquet(OUT+"/f_water.parquet",index=False); print(out.describe().T.round(3)); print("done",f"{time.time()-t0:.0f}s")
