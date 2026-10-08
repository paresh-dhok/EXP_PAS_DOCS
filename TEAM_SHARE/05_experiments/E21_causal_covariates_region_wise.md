# E21 — Causal-driver covariates under the region-wise protocol

**Date:** 2026-10-07 → 2026-10-08
**Code:** `06_code/E21_causal_covariates/` (one extraction script per feature group; `evaluate.py`, `evaluate2.py`, `locenc.py`)
**Results:** `04_results/21_causal_covariates_region_wise.csv`, `04_results/21_location_encoding.csv`
**New data:** `03_satellite_and_terrain/mh_feat_<group>.parquet` (one file per group, 17,620 rows, joined on `id`);
`03_satellite_and_terrain/cgwb_gwq_stations_2019_2021.csv` (CGWB groundwater quality, station level)
**Background:** `07_research/causal_drivers_and_datasets.md` (driver → dataset survey)

## Question (recorded before running)
The 41 field inputs explain little within regions (mean N 0.137, OC 0.092), and coordinates alone do much better
(E16: N 0.486). The literature names management and landscape drivers that act at field to landscape scale:
irrigation, cropping intensity, land cover / distance to settlement, toposequence position, flooding, burning,
groundwater chemistry, soil texture. **Do covariates for these drivers add information about a field that
location does not already carry?**
Expected: small gains from the field-scale groups; larger gains from smooth regional surfaces (SoilGrids,
groundwater interpolation) that would act as location, as climate did in E16.

## Setup
- Protocol exactly as `REGION_WISE_PROTOCOL.md`: 5 regions, 10 km blocks, `GroupKFold(5, shuffle=True, random_state=42)`,
  Random Forest (300 trees, min_samples_leaf 3, max_features 0.33), log1p/expm1 target, 17,273 locations.
  The reference table (§7) was reproduced to ±0.001 on two machines before running.
- Missing values handled natively by the Random Forest (scikit-learn 1.9). Columns with > 50 % missing or constant were dropped.

| Group | Source | Resolution / period | Cols | Driver |
|---|---|---|---|---|
| `ndvi` | MODIS MOD13Q1 NDVI (Planetary Computer) | 250 m, Jun 2019 – May 2024 | 11 | season maxima (kharif/rabi/zaid), seasons per year, irrigation proxy, amplitude |
| `lgrip` | LGRIP30 v001 (USGS, NASA Earthdata) | 30 m, nominal 2015 | 5 | irrigated / rainfed cropland, at point and within 500 m / 1 km |
| `wcereal` | ESA WorldCereal 2021 (Zenodo 7875105, AEZs 28107/28122/34119) | 10 m, 2021 | 6 | irrigation in winter-cereal and maize seasons, temporary crops |
| `iolulc` | Impact Observatory annual LULC v02 | 10 m, 2017–2023 | 8 | years as crop / built / trees / bare / rangeland / water, number of changes |
| `worldcover` | ESA WorldCover 2021 | 10 m | 21 | class fractions within 0.5 / 1 / 2 km, distance to built-up |
| `hydro` | Copernicus GLO-90 + pysheds | 90 m | 6 | TWI, flow accumulation, HAND, distance to stream, curvature |
| `water` | JRC Global Surface Water v1.4 | 30 m, 1984–2021 | 6 | water occurrence at point / 500 m / 1 km, distance to water |
| `s1` | Sentinel-1 RTC (Planetary Computer), read at ~80 m | Jul–Oct 2023, Mar–Apr 2024 | 11 | VV/VH medians and SD, flood frequency, kharif–dry difference |
| `groundwater` | CGWB station tables 2019–2021 (pubs 293–295), 5,232 stations incl. 1,266 in MH | IDW of 8 nearest, ~9 km station spacing | 8 | K, NO3, EC, Na, Cl, HCO3, pH, distance to nearest station |
| `soilgrids` | SoilGrids v2 (ISRIC) | 250 m | 18 | clay, sand, silt, CEC, SOC, pH, N, bulk density, coarse fragments; 0–5 and 5–15 cm |
| `burn` | MODIS MCD64A1 burned area | 500 m, 2015–2023 | 2 | months burned at point / within 1.5 km |

Diagnostics (longitude/latitude used **only** as diagnostics, never as candidate inputs):
- `base + lonlat` and `base + lonlat + <group>`: a gain that survives once coordinates are present is field information; a gain that disappears was location.
- **Location encoding**: R² of predicting longitude and latitude from the group alone (same RF and folds, inside each region). Near 1 = the group is effectively a map of position.
- Stability: `base_41`, `base+ALL`, `base+lonlat`, `base+lonlat+ALL` repeated with seeds 7, 13, 99, 2024 (RF seed only; folds fixed).

## Results (mean R² over the 5 regions, seed 42)

| Set | N | P | K | OC |
|---|---|---|---|---|
| base_41 (reference) | 0.137 | 0.107 | 0.042 | 0.092 |
| + ndvi | 0.156 | 0.123 | 0.073 | 0.122 |
| + worldcover | 0.152 | 0.127 | 0.060 | 0.103 |
| + iolulc | 0.149 | 0.108 | 0.060 | 0.098 |
| + lgrip | 0.146 | 0.119 | 0.044 | 0.119 |
| + s1 | 0.143 | 0.117 | 0.041 | 0.101 |
| + water / hydro / burn | 0.130–0.138 | 0.103–0.108 | 0.040–0.042 | 0.084–0.094 |
| + wcereal | 0.242 | 0.184 | 0.114 | 0.142 |
| + soilgrids | 0.310 | 0.201 | 0.171 | 0.216 |
| + groundwater | 0.330 | 0.210 | 0.153 | 0.247 |
| + all 11 groups | **0.390** | **0.260** | **0.224** | **0.294** |
| + all 11 groups except groundwater | 0.334 | 0.236 | 0.193 | 0.252 |
| *diag:* lon/lat only | 0.486 | 0.333 | 0.242 | 0.333 |
| *diag:* base + lon/lat | 0.434 | 0.295 | 0.219 | 0.302 |
| *diag:* base + lon/lat + all 11 groups | 0.441 | 0.298 | 0.251 | 0.341 |

Gain of each group **on top of base + lon/lat** (N / P / K / OC): groundwater +.006/+.009/+.022/+.043;
soilgrids +.012/.000/+.018/+.015; wcereal +.019/+.009/+.016/+.009; every other group between −.014 and +.005.

Location encoding (mean R² for lon and lat, inside regions): soilgrids 0.81, groundwater 0.74, base_41 0.51,
wcereal 0.42, worldcover 0.37, ndvi 0.30, iolulc 0.18, s1 0.16, lgrip 0.15, hydro 0.09, burn ≈ 0, water ≈ 0.

Seed stability: standard deviation across 5 seeds 0.001–0.003 for every set and nutrient.

## Interpretation
1. **The covariates roughly triple the region-wise scores (N 0.137 → 0.390, K 0.042 → 0.224), but the gain is
   almost all location.** The groups that help most (SoilGrids, groundwater, WorldCereal) are the ones that encode
   position most strongly (location-encoding R² 0.42–0.81). Once coordinates are in the model, adding all 11 groups
   changes N by +0.007 and P by +0.003.
2. **The field-scale management groups add +0.01–0.03 without coordinates and nothing with them.** Irrigation (LGRIP30,
   NDVI seasons), cropping history, land cover / distance to settlement, radar, hydrology, surface water and burning
   do not explain field-to-field differences that location does not. This agrees with E19: within 1–2 km, fields
   differ about as much as repeat samples, so field-scale signal is buried in measurement noise.
3. **The only gain beyond location is small and specific: K +0.03 and OC +0.04**, mostly from groundwater chemistry and
   SoilGrids. These may carry some real information (irrigation-water K; texture) that a coordinate model cannot form,
   but the size is at the level of fold-to-fold variation (E14, ±0.02).
4. **Useful reading for the next step:** with all groups and **no** coordinates, the model reaches 80–90 % of the
   coordinates-only score using physical variables. Within a region both are interpolation, so coordinates win. The
   question that can separate them is **transfer to unseen territory**, where coordinates cannot extrapolate but
   causal covariates might (being run on the all-India data; see below).

## Caveats
- Only the RF seed was varied; the fold assignment is fixed. Differences < 0.02 are within E14's run-to-run range.
- Year mismatch: covariates span 2015–2024 (groundwater 2019–21, LGRIP30 ≈ 2015, WorldCereal 2021) vs 2024 samples.
- LGRIP30 labels 63 % of these fields irrigated (27 % rainfed); this looks high for Maharashtra and was not validated.
  WorldCereal irrigation exists only within its cereal masks and is mapped per AEZ, so its values carry AEZ seams.
- Sentinel-1 was read at ~80 m (8× decimation) to limit download volume.
- Not covered: lithology (GSI Bhukosh unreachable), crop type (no labels), canals, salinity maps, night lights.
  The Reis Ely et al. 2025 BNF raster was rejected: its crop layers spread each country's total evenly over cropland,
  so it carries no within-India variation.

## Decision / next step
- No new group is added to the 41 field inputs for the Maharashtra region-wise models.
- The all-India transfer test (1,334,556 de-clustered locations, built with the D02/D07/D08 rules and no date filter)
  compares on-site + causal covariates against coordinates under 10 km blocks, 100 km blocks, held-out states and
  held-out data-driven agro-ecological zones.
