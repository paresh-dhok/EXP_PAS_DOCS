# MODIS MOD13Q1 (Terra) 250 m, Jun 2019 - May 2024, all-India points; running per-point season maxima / annual stats (no full time series kept)
import sys,os,time,threading; sys.path.insert(0,os.path.dirname(__file__)); from natcommon import *
import rasterio, pyproj
from concurrent.futures import ThreadPoolExecutor
t0=time.time(); P=points(); lon,lat=P.lon.to_numpy(),P.lat.to_numpy(); N=len(P)
items=[i for i in catalog().search(collections=["modis-13Q1-061"],bbox=BBOX,datetime="2019-06-01/2024-05-31").items() if i.id.startswith("MOD13Q1")]
print("items",len(items),flush=True)
sin=pyproj.CRS.from_proj4("+proj=sinu +lon_0=0 +x_0=0 +y_0=0 +R=6371007.181 +units=m +no_defs")
X,Y=pyproj.Transformer.from_crs("EPSG:4326",sin,always_xy=True).transform(lon,lat)
smax=np.full((N,5,3),np.nan,dtype="float32"); amax=np.full((N,5),np.nan,dtype="float32"); amin=amax.copy(); asum=np.zeros((N,5),"float32"); acnt=np.zeros((N,5),"int16")
lock=threading.Lock()
def do(it):
    dt=pd.Timestamp(it.properties.get("start_datetime") or it.datetime).tz_localize(None); mo=dt.month
    ay=(dt.year if mo>=6 else dt.year-1)-2019
    if not 0<=ay<5: return 0
    se={7:0,8:0,9:0,10:0,11:1,12:1,1:1,2:1,3:2,4:2,5:2}.get(mo)
    for a in range(4):
        try:
            with rasterio.open(href(it,"250m_16_days_NDVI")) as s, rasterio.open(href(it,"250m_16_days_pixel_reliability")) as q:
                c,r=~s.transform*(X,Y); m=(r>=0)&(r<s.height)&(c>=0)&(c<s.width)
                if not m.any(): return 0
                i=np.where(m)[0]; r=r[m].astype(int); c=c[m].astype(int)
                v=s.read(1)[r,c].astype("float32")/10000; qq=q.read(1)[r,c]; v[(qq>1)|(v<-0.2)]=np.nan
            ok=~np.isnan(v); i,v=i[ok],v[ok]
            with lock:
                if se is not None: smax[i,ay,se]=np.fmax(smax[i,ay,se],v)
                amax[i,ay]=np.fmax(amax[i,ay],v); amin[i,ay]=np.fmin(amin[i,ay],v); asum[i,ay]+=v; acnt[i,ay]+=1
            return len(i)
        except Exception as e: err=e; time.sleep(10)
    print("FAIL",it.id,err,flush=True); return 0
with ThreadPoolExecutor(10) as ex:
    for n,k in enumerate(ex.map(do,items)):
        if n%100==0: print(n,f"{time.time()-t0:.0f}s",flush=True)
out=pd.DataFrame({"id":P.id})
for j,se in enumerate(["kharif","rabi","zaid"]):
    out[f"ndvi_{se}_max"]=np.nanmean(smax[:,:,j],axis=1); out[f"green_{se}_freq"]=np.nanmean(np.where(np.isnan(smax[:,:,j]),np.nan,smax[:,:,j]>0.4),axis=1)
g=smax>0.4; out["n_seasons_green"]=np.nanmean(g.sum(2),axis=1)
out["irrig_proxy"]=np.nanmean((smax[:,:,1]>0.4)|(smax[:,:,2]>0.4),axis=1)
am=asum/np.maximum(acnt,1); am[acnt==0]=np.nan
out["ndvi_amp"]=np.nanmean(amax-amin,axis=1); out["ndvi_mean"]=np.nanmean(am,axis=1); out["ndvi_interannual_sd"]=np.nanstd(am,axis=1)
save(out,"ndvi")
