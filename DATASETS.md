# Data files in this repository

Every `.parquet` file in the top-level folder, what it contains, how it was made and when to use it.
Parquet is a compressed table format; load any file with `pandas.read_parquet("file.parquet")`.

**If you only want to train models, you need four files:**
`mh_final_dataset.parquet` + `mh_composite.parquet` + `mh_terrain.parquet` (+ `mh_candidates.parquet` for the region).
The exact loading code is in [`TEAM_SHARE/REGION_WISE_PROTOCOL.md`](TEAM_SHARE/REGION_WISE_PROTOCOL.md).

All files are joined by the column **`id`** (the Soil Health Card sample id, e.g. `27_485_shc_2024-25.1923`:
state code 27 = Maharashtra, district code 485 = Nanded).

## Overview

| File | Rows | Columns | Stage | Use for modelling? |
|---|---|---|---|---|
| [`maharashtra_raw.parquet`](#maharashtra_rawparquet) | 355,562 | 46 | Source soil data, Maharashtra | No (raw) |
| [`mh_candidates.parquet`](#mh_candidatesparquet) | 91,818 | 51 | Samples eligible for satellite matching | Only for `region` |
| [`mh_scenes.parquet`](#mh_scenesparquet) | 2,666 | 5 | Satellite scenes found | No (lookup) |
| [`mh_pairs.parquet`](#mh_pairsparquet) | 151,831 | 10 | Sample–scene matches | No (lookup) |
| [`mh_s2_3x3.parquet`](#mh_s2_3x3parquet) | 61,617 | 36 | Raw single-date satellite download | No (raw) |
| [`mh_model_dataset.parquet`](#mh_model_datasetparquet) | 33,877 | 44 | Clean samples, **still clustered** | Only to study clustering / noise |
| [**`mh_final_dataset.parquet`**](#mh_final_datasetparquet) | **17,620** | 44 | **Final de-clustered locations** | **Yes: targets, pH, EC** |
| [`comp_scenes_2024MarMay.parquet`](#comp_scenes_2024marmayparquet) | 1,377 | 5 | Scenes for the composite | No (lookup) |
| [`comp_tasks.parquet`](#comp_tasksparquet) | 211,440 | 7 | Location–scene list for the composite | No (lookup) |
| [`composite_parts/`](#composite_parts-43-files) | 211,440 | 36 | Raw multi-date satellite download | No (raw) |
| [**`mh_composite.parquet`**](#mh_compositeparquet) | **17,273** | 35 | **Multi-date satellite features** | **Yes: 33 satellite inputs** |
| [**`mh_terrain.parquet`**](#mh_terrainparquet) | **17,620** | 8 | **Terrain features** | **Yes: 6 terrain inputs** (`elev` excluded) |
| [`mh_climate.parquet`](#mh_climateparquet) | 17,620 | 7 | Climate features | Only as a labelled "spatial context" test |
| [`pilot_1000*.parquet`](#pilot-files) | — | — | Early 1,000-sample pilot | No (history) |

How the files follow from each other:

```
SLUSI all-India file (5.18 M records, not in the repo: 223 MB)
  └─ maharashtra_raw            355,562   Maharashtra only
       └─ mh_candidates          91,818   own GPS point, valid date, Jan–Jun, numeric N/P/K
            ├─ mh_scenes          2,666   Sentinel-2 scenes for these samples
            └─ mh_pairs         151,831   sample–scene pairs within ±3 days
                 └─ mh_s2_3x3    61,617   3×3 window values downloaded for the pairs
                      └─ mh_model_dataset   33,877   all 9 pixels bare soil, impossible values removed (clustered)
                           └─ mh_final_dataset   17,620   fake-GPS clusters removed, near-duplicates merged
                                ├─ mh_terrain     17,620   terrain at each location
                                ├─ mh_climate     17,620   climate at each location
                                └─ comp_scenes / comp_tasks / composite_parts  →  mh_composite   17,273
```

---

## Soil data

### `maharashtra_raw.parquet`
**355,562 rows × 46 columns · 16 MB**

All Soil Health Card records of Maharashtra, taken unchanged from the all-India SLUSI Soil Health data
(filter: `sid == "27"`). Nothing was cleaned or added.

- **All columns are text**, including the numbers; convert with `pd.to_numeric(..., errors="coerce")`.
- `geometry` is the GPS point in binary WKB format. Decode with `shapely.from_wkb`; x = longitude, y = latitude.

| Column(s) | Meaning |
|---|---|
| `id` | Sample id: `<state>_<district>_shc_<cycle>.<number>` |
| `sid`, `did` | State code (27) and district code (466–500, 665) |
| `cycle` | Soil Health Card cycle, e.g. `2023-24` |
| `date` | Sampling date as text, e.g. `7/23/24, 12:00 AM` (format `%m/%d/%y, %I:%M %p`); missing for about 30 % of records |
| `N`, `P`, `K` | Plant-available nitrogen, phosphorus, potassium (kg/ha) |
| `OC` | Organic carbon (%) |
| `pH`, `EC` | Soil pH and electrical conductivity (dS/m) |
| `S`, `Zn`, `Fe`, `Cu`, `Mn`, `B` | Secondary and micronutrients |
| `geometry` | GPS point of the sample (WKB) |
| `surveyNo`, `address`, `village_1`, `computedID` | Plot / address text fields (partly filled) |
| `VILLAGE`, `MANDAL`, `DISTRICT`, `BLOCK`, `TEHSIL`, `STATE`, … | Location name fields from other states' formats; **empty for Maharashtra** |

Contains raw errors (negative values, zeros, decimal mistakes such as pH 6,982) and GPS points shared by many records.
See `experiments/D01`, `D02`.

### `mh_candidates.parquet`
**91,818 rows × 51 columns · 7.7 MB**

Samples that can be matched to a satellite image. A record is kept if it is the **only record at its GPS point**, has a
valid date, lies inside Maharashtra, has numeric N, P, K, and was **sampled January–June** (bare-soil season).

The 46 original columns (still text) plus 5 added columns:

| Added column | Meaning |
|---|---|
| `longitude`, `latitude` | Decoded GPS coordinates (degrees) |
| `sample_date` | Parsed sampling date |
| `region` | One of 5 regions: Vidarbha, Marathwada, North MH, Western MH, Konkan (from the district code) |
| `mgrs_tile` | Sentinel-2 tile name containing the point, e.g. `43QGB` |

**Use:** the `region` column, for region-wise experiments (join on `id`). See `experiments/D03`, `D05`.

### `mh_model_dataset.parquet`
**33,877 rows × 44 columns · 6.5 MB — clean but still CLUSTERED**

One row per soil sample that has a fully bare-soil satellite window, after removing impossible soil values and
impossible reflectances. **Many rows are within 30 m of each other** (placeholder GPS), so this file is **not** for
honest model testing. Use it to study the clustering, the noise ceiling, or the effect of de-clustering.

| Column(s) | Meaning |
|---|---|
| `id`, `sample_date`, `longitude`, `latitude` | Sample identity and position |
| `N`, `P`, `K`, `OC`, `pH`, `EC` | Lab values, numeric, within the cleaning limits |
| `sentinel_scene_id`, `sentinel_datetime`, `date_difference_days` | The Sentinel-2 scene used and its distance in days from sampling (−3 … +3) |
| `B01` … `B12`, `B8A` | Single-date reflectance (0–1), median of the 3×3 pixel window |
| `AOT`, `WVP` | Aerosol optical thickness; water vapour (cm) |
| `NDVI` … `R_B6B5` | 16 spectral indices computed from the single-date reflectance |
| `n_within_30m` | Number of other samples within 30 m |

Cleaning limits: N 20–1500, P 1–300, K 20–3000 kg/ha; OC 0–5 %; pH 3.5–10.5; EC 0–10 dS/m; reflectance in (0, 1].
(The later steps also apply OC > 0.02 and EC > 0.005, leaving 33,842.) See `experiments/D07`.

### `mh_final_dataset.parquet`
**17,620 rows × 44 columns · 4.3 MB — FINAL, DE-CLUSTERED. Use this for modelling.**

One row per **independent location**. Built from `mh_model_dataset` by dropping clusters of more than 10 samples within
30 m (placeholder GPS) and merging clusters of 2–10 samples into one location (median of all values).

| Column(s) | Meaning |
|---|---|
| `id` | Id of the location (the first sample id of the cluster) |
| `ids_merged` | All sample ids merged into this location, separated by `;` |
| `n_merged` | Number of samples merged (1 = isolated sample; 2–10 = merged) |
| `sample_date` | Sampling date (earliest of the merged samples); all in January–May 2024 |
| `longitude`, `latitude` | Position — **used only to build test folds, never as a model input** |
| **`N`, `P`, `K`, `OC`** | **Targets** (kg/ha, kg/ha, kg/ha, %) |
| **`pH`, `EC`** | **Model inputs** (lab values standing in for the field sensor) |
| `sentinel_scene_id`, `date_difference_days` | Scene used for the single-date values |
| `B01` … `B12`, `AOT`, `WVP`, `NDVI` … `R_B6B5` | Single-date reflectance and indices (not part of the final 41 inputs) |

See `experiments/D08`.

---

## Satellite data (Sentinel-2 L2A, from Microsoft Planetary Computer)

### `mh_scenes.parquet`
**2,666 rows × 5 columns** — every Sentinel-2 scene found for the candidates (one search per tile, no cloud filter).

| Column | Meaning |
|---|---|
| `sentinel_scene_id` | Scene name, e.g. `S2B_MSIL2A_20240724T051659_R062_T43QGB_…` |
| `mgrs_tile` | Tile of the scene |
| `sentinel_datetime` | Acquisition time (UTC) |
| `scene_cloud_cover` | Cloud cover of the whole scene (%) |
| `footprint` | Outline of the area with valid data (WKB polygon) |

### `mh_pairs.parquet`
**151,831 rows × 10 columns** — every sample–scene pair where the scene is within **±3 days** of sampling and the point
lies inside the scene's valid-data area.

Columns: `id`, `sample_date`, `longitude`, `latitude`, `mgrs_tile`, `region`, `sentinel_scene_id`, `sentinel_datetime`,
`scene_cloud_cover`, `date_difference_days` (scene date − sampling date).

### `mh_s2_3x3.parquet`
**61,617 rows × 36 columns — raw single-date download, values are raw digital numbers (DN), not reflectance.**

For each extracted pair, the statistics of the exact 3×3 pixel window (30 m × 30 m) around the sample.

| Column(s) | Meaning |
|---|---|
| `id`, `sentinel_scene_id` | The pair |
| `status` | `ok`, or the failure reason (285 failed with a server error) |
| `B01` … `B12`, `AOT`, `WVP` | **Median DN** of the window. Reflectance = (DN − 1000) / 10000; AOT, WVP = DN / 1000 |
| `n_B01` … `n_WVP` | Number of pixels used (9 for 10 m and 20 m bands; 1–4 for the 60 m bands B01, B09) |
| `SCL` | Median scene-classification code of the window |
| `SCL_major`, `SCL_min`, `SCL_max` | Most common, lowest and highest class in the window. **5 = bare soil**; all three = 5 means all 9 pixels are bare |

See `experiments/D04`, `D06`.

### `comp_scenes_2024MarMay.parquet`
**1,377 rows × 5 columns** — scenes from **1 March to 31 May 2024** used for the multi-date composite.
Same columns as `mh_scenes.parquet`.

### `comp_tasks.parquet`
**211,440 rows × 7 columns** — for each of the 17,620 final locations, the **12 least-cloudy scenes** chosen for the
composite. Columns: `id`, `longitude`, `latitude`, `mgrs_tile`, `sentinel_scene_id`, `sentinel_datetime`, `scene_cloud_cover`.

### `composite_parts/` (43 files)
**211,440 rows in total × 36 columns — raw multi-date download (DN).**

The same 3×3 window statistics as `mh_s2_3x3.parquet`, but for every location on up to 12 dates. Same columns.
242 rows failed (server error). Use these files to build a different kind of composite (for example the date with the
highest bare-soil index, or a percentile instead of the median).

### `mh_composite.parquet`
**17,273 rows × 35 columns · 4.3 MB — the satellite inputs of the final model.**

For each location, the **median reflectance over all dates on which all 9 pixels were bare soil** (March–May 2024).
Only locations with at least 3 such dates are included (347 locations have no composite).

| Column(s) | Meaning |
|---|---|
| `id` | Location id |
| `c_B01` … `c_B12`, `c_B8A` | Median reflectance per band (0–1) — 12 columns |
| `c_NDVI`, `c_SAVI`, `c_NBR2`, `c_NDMI`, `c_NDWI`, `c_BSI`, `c_NDRE`, `c_CI`, `c_BI`, `c_RI`, `c_R_B4B2`, `c_R_B11B12`, `c_R_B12B8`, `c_R_B11B8`, `c_R_B7B5`, `c_R_B6B5` | 16 indices computed from the median reflectances |
| `c_std_NDVI`, `c_std_BSI`, `c_std_NDMI`, `c_std_B11`, `c_std_B12` | How much the value varied between dates (standard deviation) |
| `c_n_dates` | Number of bare-soil dates used (3–12, median 12) — not a model input |

Index formulas are in `TEAM_SHARE/README.md` (section 3). See `experiments/D10`.

---

## Terrain and climate

### `mh_terrain.parquet`
**17,620 rows × 8 columns** — from the Copernicus 30 m elevation model.

| Column | Meaning |
|---|---|
| `id` | Location id |
| `elev` | Elevation (m). **Not used in the final 41 inputs** (it mostly encodes the region) |
| `slope` | Slope (degrees) |
| `tpi_150m`, `tpi_500m`, `tpi_1km` | Topographic position: elevation minus the mean elevation within 150 m / 500 m / 1 km. Positive = higher than surroundings |
| `rough_90m` | Local roughness (standard deviation of elevation in a 3×3 window) |
| `relpos_2km` | Position between the lowest (0) and highest (1) point within about 2 km |

See `experiments/D09`.

### `mh_climate.parquet`
**17,620 rows × 7 columns** — from TerraClimate (about 4 km grid), **averages of 2011–2020**.

| Column | Meaning |
|---|---|
| `id` | Location id |
| `ppt_annual` | Mean yearly rainfall (mm) |
| `ppt_monsoon` | Mean June–September rainfall (mm) |
| `tmax_mean`, `tmin_mean`, `tmean` | Mean monthly maximum, minimum and average temperature (°C) |
| `def_annual` | Mean yearly climatic water deficit (mm) |

**Caution:** climate acts mainly as a stand-in for location (experiments `E15`, `E16`). Do not use it as a normal model
input; if tested, report results with and without it. See `experiments/D11`.

---

## Pilot files
Early 1,000-sample test of the download method (28 September 2026). Kept for the record; not used in modelling.

| File | Rows | Content |
|---|---|---|
| `pilot_1000.parquet` | 1,000 | Random sample of eligible records (seed 42): original columns + `longitude`, `latitude`, `sample_date`, `mgrs_tile` |
| `pilot_1000_scenes.parquet` | 1,031 | Scenes with < 10 % cloud for the pilot; includes the full catalogue record (`item_json`) |
| `pilot_1000_matches.parquet` | 667 | Sample–scene pairs within ±3 days |
| `pilot_1000_s2_raw.parquet` | 500 | **Single-pixel** DN values per pair (not the 3×3 window) |

See `experiments/D03`.

---

## The final model inputs (41) and where each comes from

| Group | Columns | File |
|---|---|---|
| Sensor (2) | `pH`, `EC` | `mh_final_dataset.parquet` |
| Satellite composite (33) | 12 `c_B*` + 16 `c_` indices + 5 `c_std_*` | `mh_composite.parquet` |
| Terrain (6) | `slope`, `tpi_150m`, `tpi_500m`, `tpi_1km`, `rough_90m`, `relpos_2km` | `mh_terrain.parquet` |
| **Targets** | `N`, `P`, `K`, `OC` | `mh_final_dataset.parquet` |
| Region (for splitting only) | `region` | `mh_candidates.parquet` |

Joining the first three files on `id` gives the **model table of 17,273 locations**.

Not in this repository: the all-India source file `SLUSI_SHC_all_india.parquet` (5,182,371 records, 223 MB), which is
over GitHub's file-size limit.
