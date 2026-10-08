import os, numpy as np, pandas as pd
os.environ.setdefault("GDAL_HTTP_MAX_RETRY","5"); os.environ.setdefault("GDAL_HTTP_RETRY_DELAY","2")
os.environ.setdefault("GDAL_DISABLE_READDIR_ON_OPEN","EMPTY_DIR"); os.environ.setdefault("CPL_VSIL_CURL_ALLOWED_EXTENSIONS",".tif,.TIF,.tiff,.vrt")
import pystac_client, planetary_computer as pc
HOME=os.path.expanduser("~/agrosense_soil/")
OUT=HOME+"national/features/"; os.makedirs(OUT,exist_ok=True)
CACHE=HOME+"cache/"; os.makedirs(CACHE,exist_ok=True)
BBOX=[68.0,6.5,97.5,37.2]
def points():
    p=pd.read_parquet(HOME+"national/india_locations.parquet",columns=["id","lon","lat"])
    return p.reset_index(drop=True)
def catalog(): return pystac_client.Client.open("https://planetarycomputer.microsoft.com/api/stac/v1")
def href(item,asset): return pc.sign(item.assets[asset].href)
def save(df,name):
    df.to_parquet(OUT+f"n_{name}.parquet",index=False); print(df.describe().T.round(3).to_string(),flush=True)
