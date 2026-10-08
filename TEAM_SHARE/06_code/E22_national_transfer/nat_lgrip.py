# LGRIP30 (30 m, ~2015): class at point + irrigated / rainfed fraction in ~1 km cells, all-India
import sys,os,time,requests; sys.path.insert(0,os.path.dirname(__file__)); from natcommon import *
import rasterio
t0=time.time(); P=points(); lon,lat=P.lon.to_numpy(),P.lat.to_numpy()
tok=[l.split("=",1)[1].strip().strip('"\'') for l in open(HOME+".env") if l.startswith("earthdata_token")][0]
es=requests.get("https://cmr.earthdata.nasa.gov/search/granules.json",params={"short_name":"LGRIP30","bounding_box":",".join(map(str,BBOX)),"page_size":100},timeout=60).json()["feed"]["entry"]
urls=[[l["href"] for l in e["links"] if l["href"].endswith(".tif")][0] for e in es]; print("tiles",len(urls),flush=True)
cls=np.full(len(P),np.nan,dtype="float32"); irr=cls.copy(); rain=cls.copy(); B=33  # 33 px ~ 1 km block
for u in urls:
    dst=CACHE+u.rsplit("/",1)[1]
    for a_ in range(8):
        if os.path.exists(dst): break
        try:
            with requests.get(u,headers={"Authorization":f"Bearer {tok}"},stream=True,timeout=600) as q:
                q.raise_for_status(); open(dst+".part","wb").writelines(q.iter_content(2**22))
            os.rename(dst+".part",dst)
        except Exception as e: print("retry",a_,type(e).__name__,flush=True); time.sleep(20*(a_+1))
    with rasterio.open(dst) as s:
        c,r=~s.transform*(lon,lat); r=np.floor(r).astype(int); c=np.floor(c).astype(int)
        m=(r>=0)&(r<s.height)&(c>=0)&(c<s.width)&np.isnan(cls)
        if not m.any(): continue
        a=s.read(1); H,W=(a.shape[0]//B)*B,(a.shape[1]//B)*B
        cls[m]=a[r[m],c[m]]
        blk=lambda v:(a[:H,:W]==v).reshape(H//B,B,W//B,B).mean(axis=(1,3),dtype="float32")
        bi,br=blk(2),blk(3); rr=np.clip(r[m]//B,0,bi.shape[0]-1); cc=np.clip(c[m]//B,0,bi.shape[1]-1)
        irr[m]=bi[rr,cc]; rain[m]=br[rr,cc]; del a,bi,br
    print(os.path.basename(dst),int(m.sum()),f"{time.time()-t0:.0f}s",flush=True)
save(pd.DataFrame({"id":P.id,"lgrip_class_pt":cls,"lgrip_irr_1km":irr,"lgrip_rain_1km":rain}),"lgrip")
