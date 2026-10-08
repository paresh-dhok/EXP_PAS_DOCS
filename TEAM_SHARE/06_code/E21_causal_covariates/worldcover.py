# ESA WorldCover 2021 (10 m): land-cover fractions within 500 m/1 km/2 km, built-up fraction, distance to built-up
import sys,time,threading; sys.path.insert(0,__file__.rsplit('/',1)[0]); from geo import *
import rasterio
from rasterio.windows import Window
from concurrent.futures import ThreadPoolExecutor
t0=time.time(); cat=catalog(); pts=points()
items=[i for i in cat.search(collections=["esa-worldcover"],bbox=BBOX).items() if "2021" in i.id]; print("tiles",len(items),flush=True)
bnds=[(it, it.bbox) for it in items]
def tile_for(lon,lat):
    for it,b in bnds:
        if b[0]<=lon<b[2] and b[1]<=lat<b[3]: return it
CL={10:"tree",20:"shrub",30:"grass",40:"crop",50:"built",60:"bare",80:"water",90:"wetland"}
tl=threading.local()
def ds(it):
    d=getattr(tl,"d",{}); tl.d=d
    if it.id not in d: d[it.id]=rasterio.open(href(it,"map"))
    return d[it.id]
R=200  # 2 km at 10 m
yy,xx=np.mgrid[-R:R+1,-R:R+1]; rr=np.hypot(yy,xx)*10
def one(k):
    lon,lat=pts.longitude[k],pts.latitude[k]; it=tile_for(lon,lat)
    for a in range(4):
        try:
            s=ds(it); c,r=~s.transform*(lon,lat); r=int(r); c=int(c)
            win=Window(c-R,r-R,2*R+1,2*R+1); m=s.read(1,window=win,boundless=True,fill_value=0)
            row={"wc_class_pt":int(m[R,R])}
            for rad in [500,1000,2000]:
                mm=m[rr<=rad]; v=mm[mm>0]; n=max(len(v),1)
                for code,name in CL.items():
                    if rad==2000 and name not in ("built","crop","tree"): continue
                    row[f"wc_{name}_{rad}m"]=(v==code).sum()/n
            b=rr[m==50]; row["dist_built"]=float(b.min()) if len(b) else 2500.0
            return row
        except Exception as e:
            tl.d={}; time.sleep(3); err=e
    print("FAIL",k,err,flush=True); return {}
rows=[None]*len(pts)
with ThreadPoolExecutor(16) as ex:
    for n,(k,row) in enumerate(zip(range(len(pts)),ex.map(one,range(len(pts))))):
        rows[k]=row
        if n%2000==0: print(n,f"{time.time()-t0:.0f}s",flush=True)
out=pd.DataFrame(rows); out.insert(0,"id",pts.id.values)
out.to_parquet(OUT+"/f_worldcover.parquet",index=False); print(out.describe().T.round(3)); print("done",f"{time.time()-t0:.0f}s")
