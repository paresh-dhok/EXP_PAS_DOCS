"""Multi-date Sentinel-2 bare-soil composite: 3x3 window stats for up to 12 Mar-May 2024 scenes per location.
Resumable: results are written to composite_parts/ in chunks; rerunning skips finished pairs."""
import time
from functools import lru_cache
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import mgrs
import numpy as np
import pandas as pd
import requests
import shapely
from pyproj import Transformer
from pystac_client import Client
from requests.adapters import HTTPAdapter
from shapely.geometry import shape

OUT_DIR = Path(r"D:\SEM 7\CAPSTONE\DATA\slusi\Start")
FINAL   = OUT_DIR / "mh_final_dataset.parquet"
SCENES  = OUT_DIR / "comp_scenes_2024MarMay.parquet"
TASKS   = OUT_DIR / "comp_tasks.parquet"
PARTS   = OUT_DIR / "composite_parts"
PARTS.mkdir(exist_ok=True)

START, END = "2024-03-01", "2024-05-31"
MAX_DATES, WORKERS, CHUNK = 12, 16, 5000
STAC_URL  = "https://planetarycomputer.microsoft.com/api/stac/v1"
STATS_API = "https://planetarycomputer.microsoft.com/api/data/v1/item/statistics"
ASSETS = ["B01","B02","B03","B04","B05","B06","B07","B08","B8A","B09","B11","B12","SCL","AOT","WVP"]
HALF = 15

session = requests.Session()
session.mount("https://", HTTPAdapter(pool_connections=32, pool_maxsize=32))


def scene_tile(item):
    return item.properties.get("s2:mgrs_tile") or item.id.split("_")[5][1:]


@lru_cache(maxsize=None)
def to_utm(epsg):
    return Transformer.from_crs(4326, epsg, always_xy=True)


def window_feature_utm(tile, lon, lat):
    epsg = 32600 + int(tile[:2])
    x, y = to_utm(epsg).transform(lon, lat)
    cx, cy = np.floor(x / 10) * 10 + 5, np.floor(y / 10) * 10 + 5
    ring = [[cx + dx, cy + dy] for dx, dy in
            [(-HALF, -HALF), (HALF, -HALF), (HALF, HALF), (-HALF, HALF), (-HALF, -HALF)]]
    return epsg, {"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [ring]}}


def fetch_window(row):
    epsg, feat = window_feature_utm(row.mgrs_tile, row.longitude, row.latitude)
    params = ([("collection", "sentinel-2-l2a"), ("item", row.sentinel_scene_id)]
              + [("assets", a) for a in ASSETS]
              + [("coord_crs", f"EPSG:{epsg}"), ("dst_crs", f"EPSG:{epsg}"), ("width", 3), ("height", 3)])
    base = {"id": row.id, "sentinel_scene_id": row.sentinel_scene_id}
    last = ""
    for attempt in range(3):
        try:
            r = session.post(STATS_API, params=params, json=feat, timeout=(10, 30))
            if r.status_code == 200:
                j = r.json()
                stats = (j.get("properties") or j["features"][0]["properties"])["statistics"]
                out = {**base, "status": "ok"}
                for name, s in stats.items():
                    a = name.split("_")[0]
                    out[a] = s["median"]
                    out[f"n_{a}"] = s["count"]
                    if a == "SCL":
                        out.update(SCL_major=s["majority"], SCL_min=s["min"], SCL_max=s["max"])
                return out
            last = f"http {r.status_code}"
            if r.status_code not in (429, 500, 502, 503, 504):
                break
        except requests.RequestException as e:
            last = type(e).__name__
        time.sleep(2 * 2 ** attempt)
    return {**base, "status": f"failed: {last}"}


def find_scenes(loc):
    if SCENES.exists():
        return pd.read_parquet(SCENES)
    catalog, rows = Client.open(STAC_URL), []
    for k, (tile, t) in enumerate(loc.groupby("mgrs_tile"), 1):
        bbox = [t.longitude.min(), t.latitude.min(), t.longitude.max(), t.latitude.max()]
        for attempt in range(5):
            try:
                items = list(catalog.search(collections=["sentinel-2-l2a"], bbox=bbox,
                                            datetime=f"{START}/{END}", limit=1000).items())
                break
            except Exception as e:
                print(f"  {tile}: {type(e).__name__}, retry")
                time.sleep(5 * 2 ** attempt)
        else:
            raise RuntimeError(f"STAC search failed for {tile}")
        for it in items:
            if scene_tile(it) == tile:
                rows.append({"sentinel_scene_id": it.id, "mgrs_tile": tile,
                             "sentinel_datetime": pd.Timestamp(it.datetime).tz_convert(None),
                             "scene_cloud_cover": it.properties.get("eo:cloud_cover"),
                             "footprint": shapely.to_wkb(shape(it.geometry))})
        if k % 10 == 0:
            print(f"  searched {k} tiles, {len(rows):,} scenes")
        time.sleep(0.25)
    sc = pd.DataFrame(rows).drop_duplicates("sentinel_scene_id")
    sc.to_parquet(SCENES, index=False)
    return sc


def build_tasks(loc, sc):
    if TASKS.exists():
        return pd.read_parquet(TASKS)
    fp = dict(zip(sc.sentinel_scene_id, shapely.from_wkb(sc.footprint)))
    meta = sc.drop(columns="footprint")
    parts = []
    for tile, t in loc.groupby("mgrs_tile"):
        mm = t.merge(meta[meta.mgrs_tile == tile], on="mgrs_tile")
        if len(mm):
            mm = mm[[shapely.contains_xy(fp[s], lo, la)
                     for s, lo, la in zip(mm.sentinel_scene_id, mm.longitude, mm.latitude)]]
            parts.append(mm)
    tasks = (pd.concat(parts).sort_values(["id", "scene_cloud_cover", "sentinel_datetime"])
               .groupby("id").head(MAX_DATES).reset_index(drop=True))
    tasks.to_parquet(TASKS, index=False)
    return tasks


def main():
    loc = pd.read_parquet(FINAL, columns=["id", "longitude", "latitude"])
    m = mgrs.MGRS()
    loc["mgrs_tile"] = [m.toMGRS(la, lo, MGRSPrecision=0) for lo, la in zip(loc.longitude, loc.latitude)]
    print(f"Locations: {len(loc):,} | tiles: {loc.mgrs_tile.nunique()}")

    sc = find_scenes(loc)
    print(f"Scenes {START}..{END}: {len(sc):,}")
    tasks = build_tasks(loc, sc)
    print(f"Tasks: {len(tasks):,} | locations covered: {tasks.id.nunique():,} | "
          f"dates per location: {tasks.groupby('id').size().describe()[['min', '50%', 'max']].to_dict()}")

    done = set()
    for f in PARTS.glob("*.parquet"):
        d = pd.read_parquet(f, columns=["id", "sentinel_scene_id"])
        done |= set(zip(d.id, d.sentinel_scene_id))
    todo = tasks[[k not in done for k in zip(tasks.id, tasks.sentinel_scene_id)]]
    print(f"Already done: {len(done):,} | to fetch: {len(todo):,} | ETA at 19/s: {len(todo) / 19 / 3600:.1f} h\n")

    t0, n = time.time(), 0
    ex = ThreadPoolExecutor(max_workers=WORKERS)
    try:
        for s in range(0, len(todo), CHUNK):
            part = todo.iloc[s:s + CHUNK]
            futs = [ex.submit(fetch_window, row) for row in part.itertuples(index=False)]
            res = pd.DataFrame([f.result() for f in as_completed(futs)])
            res.to_parquet(PARTS / f"part_{int(time.time())}_{s:07d}.parquet", index=False)
            n += len(part)
            rate = n / (time.time() - t0)
            print(f"{n:,}/{len(todo):,} | {rate:.1f}/s | ETA {(len(todo) - n) / rate / 60:.0f} min | "
                  f"failed in chunk: {(res.status != 'ok').sum()} | "
                  f"all-bare in chunk: {((res.get('SCL_min') == 5) & (res.get('SCL_max') == 5)).sum():,}",
                  flush=True)
    except KeyboardInterrupt:
        print("Stopped. Finished chunks are saved; rerun to continue.")
    finally:
        ex.shutdown(wait=False, cancel_futures=True)
    print("Done.")


if __name__ == "__main__":
    main()
