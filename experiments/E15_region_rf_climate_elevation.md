# E15 — Region-wise Random Forest with climate and elevation

**Date:** 2026-10-05
**Notebook:** cell run on 2026-10-05
**Results:** `results/15_region_rf_climate_elevation.csv`
**Data:** model table (17,273 locations) + `mh_climate.parquet` (D11); region-wise protocol (spatial CV, 10 km blocks, 5 folds inside each region)

## Hypothesis (recorded before running)
Climate raises R² inside regions, most in Western MH and Konkan, which have the largest rainfall gradients (Ghats vs plateau).
Elevation + climate together gives the highest scores, but both partly carry location.

## Setup
- Model: `RandomForestRegressor(n_estimators=300, min_samples_leaf=3, max_features=0.33, random_state=42)`, log1p/expm1 target. No tuning.
- Climate features (6): `ppt_annual`, `ppt_monsoon`, `tmax_mean`, `tmin_mean`, `tmean`, `def_annual`.

| Set | Inputs | Count |
|---|---|---|
| base_41 | final 41 inputs | 41 |
| plus_elev | + `elev` | 42 |
| plus_climate | + 6 climate | 47 |
| plus_elev_climate | + `elev` + 6 climate | 48 |

## Results (R², region-wise spatial CV)
| Region | Set | N | P | K | OC |
|---|---|---|---|---|---|
| Vidarbha | base_41 | 0.150 | 0.025 | 0.239 | 0.060 |
| | plus_elev | 0.184 | 0.054 | 0.274 | 0.148 |
| | plus_climate | 0.319 | 0.181 | 0.447 | 0.189 |
| | plus_elev_climate | **0.331** | **0.193** | **0.453** | **0.262** |
| Marathwada | base_41 | 0.134 | 0.211 | 0.014 | 0.020 |
| | plus_elev | 0.236 | 0.249 | 0.059 | 0.053 |
| | plus_climate | 0.445 | 0.525 | 0.197 | 0.127 |
| | plus_elev_climate | **0.447** | **0.530** | **0.213** | **0.127** |
| North MH | base_41 | 0.042 | 0.046 | 0.009 | 0.112 |
| | plus_elev | 0.081 | 0.102 | 0.120 | 0.212 |
| | plus_climate | 0.309 | 0.221 | 0.235 | 0.315 |
| | plus_elev_climate | **0.332** | **0.250** | **0.271** | **0.332** |
| Western MH | base_41 | 0.216 | 0.230 | −0.030 | 0.177 |
| | plus_elev | 0.364 | 0.242 | −0.037 | 0.265 |
| | plus_climate | 0.425 | 0.330 | **−0.015** | 0.439 |
| | plus_elev_climate | **0.447** | **0.339** | −0.019 | **0.443** |
| Konkan | base_41 | 0.141 | 0.022 | −0.022 | 0.089 |
| | plus_elev | 0.209 | −0.003 | 0.017 | 0.122 |
| | plus_climate | 0.437 | **0.042** | 0.031 | 0.161 |
| | plus_elev_climate | **0.445** | 0.036 | **0.050** | **0.182** |

Mean over the 5 regions:

| Set | N | P | K | OC |
|---|---|---|---|---|
| base_41 | 0.137 | 0.107 | 0.042 | 0.092 |
| plus_elev | 0.215 | 0.129 | 0.087 | 0.160 |
| plus_climate | 0.387 | 0.260 | 0.179 | 0.246 |
| plus_elev_climate | **0.400** | **0.269** | **0.194** | **0.269** |

## Interpretation
1. **Climate gives a very large gain inside every region.** The 5-region mean roughly triples for N (0.137 → 0.387),
   more than doubles for P (0.107 → 0.260) and OC (0.092 → 0.246), and quadruples for K (0.042 → 0.179).
   Best cells: Marathwada P 0.530 and N 0.447, Vidarbha K 0.453, Western MH OC 0.443.
2. The hypothesis is only partly confirmed: the gain is large in **all** regions, not mainly in Western MH and Konkan.
   The largest relative gains are in Marathwada and North MH.
3. Elevation adds little once climate is present (mean N 0.387 → 0.400); the two carry overlapping information.
4. **Caution — climate may act as location.** The climate grid is 4 km and the climate surface is smooth, so the climate
   values effectively encode position within a region (similar to latitude/longitude). Earlier, GPS alone predicted N with
   R² 0.65 statewide (E02), and district averages matched any model (E03). The gain from climate may therefore partly be
   spatial interpolation of laboratory/district patterns rather than a climate effect on soil. This experiment cannot
   separate the two.

## Open check
Compare, inside each region, (a) longitude/latitude only, (b) climate only, (c) base_41 + longitude/latitude.
If climate-only ≈ coordinates-only, climate is acting mainly as location. Optionally also test with 50 km blocks inside regions.
