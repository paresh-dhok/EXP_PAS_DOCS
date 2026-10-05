# D04 — Extraction method and exact 3×3 window

**Date:** 2026-09-28
**Notebook:** `new.ipynb` cells 9, 12, 13

## Objective
Find an extraction method that is orders of magnitude faster than D00 (8.4 min/scene), and obtain a **3×3 pixel median**
instead of a single pixel (GPS error of ~5–10 m and field heterogeneity make a single pixel unreliable).

## Test 1 — single pixel, two methods (cell 9, 5 random pilot pairs, 15 assets each)
| Method | Time | Per pair |
|---|---|---|
| A: rasterio on signed COGs, tuned GDAL settings, 1-pixel window, 16 threads | 14.5 s | 2.9 s |
| **B: Planetary Computer data API `/item/point/{lon},{lat}`, 1 request per pair (server reads the pixels)** | 6.0 s | **1.2 s** (sequential) |

The values were **identical** for both methods. Pairs 1 and 4 returned all zeros (SCL 0), which led to the footprint filter in D03.

GDAL settings used: `GDAL_DISABLE_READDIR_ON_OPEN=EMPTY_DIR`, `CPL_VSIL_CURL_ALLOWED_EXTENSIONS=.tif`,
`GDAL_HTTP_MERGE_CONSECUTIVE_RANGES=YES`, `GDAL_HTTP_MULTIPLEX=YES`, `GDAL_HTTP_VERSION=2`, `VSI_CACHE=TRUE`.

## Test 2 — 3×3 statistics, lon/lat box (cell 12, 20 SCL=5 pairs)
- Endpoint: `POST /api/data/v1/item/statistics` with a 30 m × 30 m GeoJSON polygon in lon/lat.
- 0.26 s per pair (4 workers), all OK.
- **Problem:** the pixel count per window was 12–20 and **identical for 10 m, 20 m and 60 m bands**. The server
  reprojected everything to its own lat/lon grid and counted partially covered edge pixels. That is not a clean 3×3. **Rejected.**

## Test 3 — exact 3×3 in native UTM (cell 13, same 20 pairs)
- UTM EPSG = 32600 + zone (from the MGRS tile, northern hemisphere).
- The point is transformed to UTM. The centre of the 10 m pixel containing it is
  `cx = floor(x/10)*10 + 5`, `cy = floor(y/10)*10 + 5`. The box is centre ± 15 m (exactly 3×3 pixels at 10 m).
- Request parameters: `coord_crs=EPSG:326xx`, `dst_crs=EPSG:326xx`, `width=3`, `height=3`.
- Returned per band: `median`, `count`; for SCL also `majority`, `min`, `max`.

| Check | Result |
|---|---|
| Pixels per window, B04 (10 m) | 9 (min = max = 9) |
| Pixels per window, B11 (20 m), SCL | 9 (resampled to the 10 m grid by nearest neighbour) |
| Pixels per window, B01 (60 m) | 1–4 (real 60 m pixels touched by the 30 m box) |
| All 9 pixels bare (SCL min = max = 5) | 18 of 20 |
| Majority bare (SCL majority = 5) | 20 of 20 |
| **B04 3×3 median: API vs rasterio direct read of the native 3×3 window** | **20 of 20 identical** |

## Decision
**Method for all further extraction: data-API statistics, exact UTM-aligned 3×3 window, one request per sample–scene pair.**
It is verified identical to a direct read of the image file.
