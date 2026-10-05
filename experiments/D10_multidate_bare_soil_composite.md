# D10 — Multi-date bare-soil composite (Mar–May 2024)

**Dates:** script written and started on 2026-09-30; download completed and composite built on 2026-10-01
**Code:** `Start\s2_composite.py` (download, run in a terminal) + notebook setup cell (build; this cell was not
yet saved to disk when this file was written)
**Outputs:** `comp_scenes_2024MarMay.parquet`, `comp_tasks.parquet`, `composite_parts\*.parquet` (43 files), **`mh_composite.parquet`**

## Hypothesis (stated before running)
A single-date observation is affected by one-day conditions (moisture after rain, crust, haze, roughness). A median over
many bare-soil dates gives a more stable soil signal. The literature (Belgium, Germany, France SOC studies) reports
that multi-date bare-soil composites beat single dates, especially for OC.

## Download design (`s2_composite.py`)
- Locations: the 17,620 final locations, each with its own MGRS tile (50 tiles).
- Window: **2024-03-01 to 2024-05-31** (peak fallow: rabi harvested, kharif not yet sown).
- One STAC search per tile with no cloud filter. Only scenes of the location's own tile with the point inside the footprint are kept.
  **1,377 scenes.**
- Up to **12 scenes per location, least cloudy first** (`MAX_DATES = 12`). Every location had ≥ 12 scenes available.
- **211,440 requests.** The same exact UTM 3×3 statistics request as D04. 16 workers, timeout (10, 30) s, 3 attempts.
- Saved in chunks of 5,000 (`composite_parts/`). Resumable: the run was interrupted twice and resumed with no loss.

## Download results
| Item | Value |
|---|---|
| Requests | 211,440, no duplicates |
| OK | 211,198 |
| Failed (HTTP 500) | 242 (0.1 %) |
| Speed | ~19–23 requests/s |
| All-9-bare share per chunk | ~78–94 % |

## Composite construction
1. Keep observations with status OK, **SCL min = max = 5**, complete window (n_B04 = n_B11 = 9).
2. Reflectance = (DN − 1000) / 10000. Keep only observations with all bands in (0, 1].
   **185,946 bare-soil observations.**
3. Per location: **median reflectance per band** across dates (`c_B01` … `c_B12`) and the number of bare dates (`c_n_dates`).
4. Temporal variability: std across dates of NDVI, BSI, NDMI, B11 and B12 (`c_std_*`).
5. Keep locations with **≥ 3 bare dates** (a 1–2 date "composite" is not a composite).
6. 16 indices recomputed from the median reflectances (`c_NDVI` …).

## Results
| Item | Value |
|---|---|
| Locations with ≥ 1 bare date | 17,559 |
| **Composite locations (≥ 3 bare dates)** | **17,273** |
| Bare dates per location | min 3, median 12, mean 10.7, max 12 |
| Locations with all 12 dates bare | 10,201 |
| Model table (final + terrain + composite) | 17,273 locations, 1,554 spatial blocks (10 km), 0 non-finite features |

Correlation between single-date and composite reflectance for the same band:
B02 0.634 | B04 0.732 | B08 0.723 | B11 0.850 | B12 0.826.

## Interpretation
The moderate correlation (0.63–0.85) shows that the single-date values were noticeably affected by one-day conditions.
The composite is a different, more stable measurement. Its predictive value was tested in E06.
