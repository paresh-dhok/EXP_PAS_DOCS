# D11 — Climate features (TerraClimate)

**Date:** 2026-10-05
**Notebook:** cell run on 2026-10-05
**Output:** `mh_climate.parquet` (17,620 rows: id + 6 features)
**New packages:** `zarr` 3.4.0, `adlfs` 2026.8.0 (installed 2026-10-05)

## Objective
Add long-term climate covariates, which most high-accuracy studies in the literature survey used
(IBM 2020, Mundada & Jain 2025, several Chinese SOC studies).

## Source
**TerraClimate** on Microsoft Planetary Computer (STAC collection `terraclimate`, Zarr store `az://cpdata/terraclimate.zarr`):
monthly climate, about 4 km (1/24°) grid, 1958–2021.

## Method
- Opened through the `zarr-abfs` asset (Azure route, `adlfs`). The `zarr-https` asset failed with HTTP 403, because zarr
  appends the metadata path after the access token in the URL.
- Maharashtra box lat 15.4–22.3, lon 72.4–81.1; period **2011-01 to 2020-12 (10-year average)**.
  A 30-year normal with 8 variables was planned but dropped: the data is stored in 12-month × 1024 × 1024 blocks,
  so one variable-year took about 50 s, i.e. 3+ hours in total.
- Value at each field = nearest grid cell.

| Feature | Definition |
|---|---|
| `ppt_annual` | mean monthly precipitation × 12 (mm/year) |
| `ppt_monsoon` | mean June–September monthly precipitation × 4 (mm) |
| `tmax_mean`, `tmin_mean` | mean monthly maximum / minimum temperature (°C) |
| `tmean` | (tmax_mean + tmin_mean) / 2 |
| `def_annual` | mean monthly climatic water deficit × 12 (mm/year) |

## Results
815 s; 17,620 of 17,620 sites; 0 missing values.

| | min | median | max |
|---|---|---|---|
| ppt_annual (mm) | 503.3 | 962.1 | 5,223.4 |
| ppt_monsoon (mm) | 320.1 | 831.7 | 5,005.3 |
| tmax_mean (°C) | 26.4 | 33.0 | 35.4 |
| tmin_mean (°C) | 17.3 | 20.7 | 24.4 |
| tmean (°C) | 22.1 | 27.0 | 28.6 |
| def_annual (mm) | 569.4 | 967.7 | 1,160.5 |

The values are plausible: the Marathwada rain shadow is ~500 mm, the Konkan coast and Western Ghats exceed 5,000 mm.

## Notes
- Climate varies smoothly across the state and very sharply across the Western Ghats, so these features partly act as
  **location**, even more than elevation. They must be evaluated with and without, like elevation (E14).
- At 4 km resolution, neighbouring fields share the same climate values; climate cannot separate fields within a few km.
