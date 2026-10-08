# LGRIP30 (USGS, 30 m, nominal 2015): irrigated / rainfed cropland at point (3x3 majority) + irrigated/rainfed fractions within 500 m and 1 km
import sys,time,os,requests; sys.path.insert(0,__file__.rsplit('/',1)[0]); from geo import *
import rasterio
from rasterio.windows import Window
t0=time.time(); pts=points(); lon,lat=pts.longitude.to_numpy(),pts.latitude.to_numpy()
tok=[l.split("=",1)[1].strip().strip('"\'') for l in open("/Users/mihirmohite/Downloads/TEAM_SHARE/.env") if l.startswith("earthdata_token")][0]
r=requests.get("https://cmr.earthdata.nasa.gov/search/granules.json",params={"short_name":"LGRIP30","bounding_box":"72.4,15.4,81.2,22.3","page_size":50},timeout=60).json()
urls=[[l["href"] for l in e["links"] if l["href"].endswith(".tif")][0] for e in r["feed"]["entry"]]
os.makedirs(OUT+"/lgrip",exist_ok=True); paths=[]
for u in urls:
    dst=OUT+"/lgrip/"+u.rsplit("/",1)[1]
    if not os.path.exists(dst):
        with requests.get(u,headers={"Authorization":f"Bearer {tok}"},stream=True,timeout=300) as q:
            q.raise_for_status()
            with open(dst+".part","wb") as o:
                for ch in q.iter_content(2**22): o.write(ch)
        os.rename(dst+".part",dst)
    print("got",os.path.basename(dst),os.path.getsize(dst)//2**20,"MB",f"{time.time()-t0:.0f}s",flush=True); paths.append(dst)
# legend check
with rasterio.open(paths[0]) as s: print("crs",s.crs,"res",s.res,"tags",s.tags(), "sample vals",np.unique(s.read(1,window=Window(15000,15000,2000,2000)),return_counts=True),flush=True)
out=pd.DataFrame({"id":pts.id}); cols={k:np.full(len(pts),np.nan) for k in ["lgrip_class_pt","lgrip_irr_500m","lgrip_rain_500m","lgrip_irr_1km","lgrip_rain_1km"]}
for p in paths:
    with rasterio.open(p) as s:
        c,rw=~s.transform*(lon,lat); rw=np.floor(rw).astype(int); c=np.floor(c).astype(int)
        k1=int(round(1000/30)); k5=int(round(500/30))
        idx=np.where((rw>=k1)&(rw<s.height-k1)&(c>=k1)&(c<s.width-k1)&np.isnan(cols["lgrip_class_pt"]))[0]
        for i in idx:
            w=s.read(1,window=Window(c[i]-k1,rw[i]-k1,2*k1+1,2*k1+1))
            ctr=w[k1-1:k1+2,k1-1:k1+2].ravel(); cols["lgrip_class_pt"][i]=np.bincount(ctr,minlength=4).argmax()
            inner=w[k1-k5:k1+k5+1,k1-k5:k1+k5+1]
            cols["lgrip_irr_500m"][i]=(inner==2).mean(); cols["lgrip_rain_500m"][i]=(inner==3).mean()
            cols["lgrip_irr_1km"][i]=(w==2).mean(); cols["lgrip_rain_1km"][i]=(w==3).mean()
        print(os.path.basename(p),len(idx),"points",f"{time.time()-t0:.0f}s",flush=True)
for k,v in cols.items(): out[k]=v
out.to_parquet(OUT+"/f_lgrip.parquet",index=False); print(out.describe().T.round(3)); print(out.lgrip_class_pt.value_counts()); print("done",f"{time.time()-t0:.0f}s")
