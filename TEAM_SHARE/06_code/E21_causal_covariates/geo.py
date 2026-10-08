import os, numpy as np, pandas as pd
import pystac_client, planetary_computer as pc
os.environ.setdefault("GDAL_HTTP_MAX_RETRY","5"); os.environ.setdefault("GDAL_HTTP_RETRY_DELAY","2")
os.environ.setdefault("GDAL_DISABLE_READDIR_ON_OPEN","EMPTY_DIR"); os.environ.setdefault("CPL_VSIL_CURL_ALLOWED_EXTENSIONS",".tif,.TIF,.tiff,.vrt")
D="/Users/mihirmohite/Downloads/EXP_PAS_DOCS/TEAM_SHARE/"
OUT=os.path.join(os.path.dirname(__file__),"out")
BBOX=[72.4,15.4,81.2,22.3]
def points():
    p=pd.read_parquet(D+"02_datasets/mh_final_dataset.parquet",columns=["id","longitude","latitude"])
    return p.reset_index(drop=True)
def catalog():
    return pystac_client.Client.open("https://planetarycomputer.microsoft.com/api/stac/v1")
def href(item,asset):
    return pc.sign(item.assets[asset].href)
