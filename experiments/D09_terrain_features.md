# D09 — Terrain features (Copernicus DEM GLO-30)

**Date:** 2026-09-30
**Notebook:** `new.ipynb` cell 28
**Output:** `mh_terrain.parquet` (17,620 rows: id + 7 features)

## Objective
Add field-specific landscape covariates. Terrain differs between fields within the same district, and the literature
reports it as useful for OC and nutrients.

## Method
- STAC collection `cop-dem-glo-30` (Planetary Computer), signed with `planetary_computer.sign_inplace`.
- 60 DEM tiles (1° × 1°, ~30 m) intersecting the sites' bounding box. Each tile is read **once** in full
  (4 tiles in parallel), and the features are computed locally.
- Pixel size in metres: dx = |a| · 111,320 · cos(tile-centre lat), dy = |e| · 110,574.
- Sampled at the pixel containing each site (`rowcol`), with edges handled by `mode="nearest"`.

| Feature | Definition |
|---|---|
| elev | elevation (m) |
| slope | degrees, from `np.gradient` |
| tpi_150m / tpi_500m / tpi_1km | elevation − mean elevation in a 5 / 17 / 33-pixel window |
| rough_90m | std of elevation in a 3×3 window |
| relpos_2km | (z − min) / (max − min) in a 67-pixel (~2 km) window; 0 = valley bottom, 1 = ridge top |

Not computed: the topographic wetness index (needs flow accumulation).

## Results
1,072 s; **17,620 of 17,620 sites**, 0 missing, 0 non-finite.

| | min | 1 % | 50 % | 99 % | max |
|---|---|---|---|---|---|
| elev (m) | 0.00 | 7.13 | 402.16 | 820.91 | 1,284.99 |
| slope (°) | 0.00 | 0.14 | 1.38 | 12.11 | 35.91 |
| tpi_150m | −9.06 | −3.36 | 0.01 | 2.96 | 12.76 |
| tpi_500m | −37.29 | −12.05 | 0.01 | 10.15 | 49.93 |
| tpi_1km | −67.16 | −23.82 | −0.10 | 17.77 | 100.24 |
| rough_90m | 0.00 | 0.14 | 0.65 | 5.17 | 16.55 |
| relpos_2km | 0.00 | 0.04 | 0.41 | 0.88 | 1.00 |

## Notes
- The values are plausible: the Konkan coast is near 0 m, the Deccan plateau is ~400 m, and the Western Ghats reach ~1,300 m.
- **Elevation partly encodes region** (Konkan low, plateau high), so it acts partly as a location proxy. Results should
  also be reported without elevation where location inputs are excluded.
- Used in E05 and E06.
