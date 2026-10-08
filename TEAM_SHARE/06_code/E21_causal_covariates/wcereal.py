# ESA WorldCereal 2021 (10 m): irrigation (rabi = wintercereals season, kharif = maize-main season) + temporary crops, AEZs over MH only
import sys,time,os,json,urllib.request,zipfile,shutil; sys.path.insert(0,__file__.rsplit('/',1)[0]); from geo import *
import fsspec, rasterio, pyproj
from rasterio.windows import Window
t0=time.time(); pts=points(); AEZ=("28107_","28122_","34119_")
r=json.load(urllib.request.urlopen("https://zenodo.org/api/records/7875104")); fl={f["key"]:f["links"]["self"] for f in r["files"]}
PROD={"irr_rabi":"WorldCereal_2021_tc-wintercereals_irrigation_classification.zip",
      "irr_kharif":"WorldCereal_2021_tc-maize-main_irrigation_classification.zip",
      "tempcrop":"WorldCereal_2021_tc-annual_temporarycrops_classification.zip"}
tmp=OUT+"/wc_tmp"; os.makedirs(tmp,exist_ok=True)
lon,lat=pts.longitude.to_numpy(),pts.latitude.to_numpy()
out=pd.DataFrame({"id":pts.id})
for name,zipname in PROD.items():
    z=zipfile.ZipFile(fsspec.open(fl[zipname],block_size=2**22).open())
    mem=[n for n in z.namelist() if os.path.basename(n).startswith(AEZ)]; print(name,mem,flush=True)
    pt=np.full(len(pts),np.nan); fr=np.full(len(pts),np.nan)
    for m in mem:
        dst=os.path.join(tmp,os.path.basename(m))
        from dl import zip_member
        zip_member(fl[zipname],z.getinfo(m),dst)
        print(" got",m,os.path.getsize(dst)//2**20,"MB",f"{time.time()-t0:.0f}s",flush=True)
        with rasterio.open(dst) as s:
            x,y=pyproj.Transformer.from_crs("EPSG:4326",s.crs,always_xy=True).transform(lon,lat)
            c,rr=~s.transform*(x,y); rr=np.floor(rr).astype(int); c=np.floor(c).astype(int)
            res=abs(s.transform.a); k=int(round(500/res)) if s.crs.is_projected else 50
            for i in np.where((rr>=k)&(rr<s.height-k)&(c>=k)&(c<s.width-k)&np.isnan(pt))[0]:
                w=s.read(1,window=Window(c[i]-k,rr[i]-k,2*k+1,2*k+1))
                v=w[(w!=255)&(w!=0)] if s.nodata is None else w[w!=s.nodata]
                ctr=w[k-1:k+2,k-1:k+2].ravel()
                pos=100 if name!="tempcrop" else 100
                pt[i]=np.mean(ctr==pos) if ctr.size else np.nan
                fr[i]=np.mean(w==pos)
            print("  vals",np.unique(s.read(1,window=Window(0,0,2000,2000)),return_counts=True),flush=True)
        os.remove(dst)
    out[f"wc_{name}_pt"]=pt; out[f"wc_{name}_frac1km"]=fr
out.to_parquet(OUT+"/f_wcereal.parquet",index=False); print(out.describe().T.round(3)); print("done",f"{time.time()-t0:.0f}s")
