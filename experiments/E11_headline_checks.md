# E11 — Checks on the headline no-location result

**Date:** 2026-10-05
**Notebook:** cell run on 2026-10-05
**Results:** `results/11_headline_checks.csv`
**Data:** model table, 17,273 locations; 10 km blocks (1,554) and 50 km blocks (150)

## Question (recorded before running)
E08 gave the best no-location result: composite + pH/EC + terrain, N 0.409, P 0.108, K 0.116, OC 0.370 (10 km spatial CV).
Before using it as the headline:
- (a) Does it depend on elevation, which partly encodes region (Konkan low, plateau high)?
- (b) Does it hold with stricter 50 km blocks?
- (c) Which feature group causes it: the composite, the terrain, or pH/EC?

## Setup
Same model as E08/E09: `RandomForestRegressor(n_estimators=300, min_samples_leaf=3, max_features=0.33, random_state=42)`
with a log1p/expm1 target transform. Statewide spatial CV, 5 folds (`GroupKFold(shuffle=True, random_state=42)`), pooled
out-of-fold R². No location inputs in any set.

| Set | Features | Count |
|---|---|---|
| full_comp_pHEC_terrain | composite (33) + pH, EC + terrain (7) | 42 |
| no_elevation | as full, without `elev` | 41 |
| comp_pHEC_no_terrain | composite + pH, EC | 35 |
| terrain_pHEC_no_satellite | terrain + pH, EC | 9 |
| single_date_pHEC_terrain | single-date 12 bands + 16 indices + pH, EC + terrain | 37 |
| comp_only | composite | 33 |
| terrain_only | terrain | 7 |

## Results (R²)
| Set | Blocks | N | P | K | OC |
|---|---|---|---|---|---|
| full_comp_pHEC_terrain | 10 km | **0.409** | **0.108** | **0.116** | **0.370** |
| full_comp_pHEC_terrain | 50 km | 0.230 | 0.038 | 0.062 | 0.337 |
| no_elevation | 10 km | 0.272 | 0.041 | 0.055 | 0.291 |
| no_elevation | 50 km | 0.163 | 0.004 | 0.018 | 0.251 |
| comp_pHEC_no_terrain | 10 km | 0.225 | 0.034 | 0.054 | 0.280 |
| terrain_pHEC_no_satellite | 10 km | 0.385 | 0.083 | 0.084 | 0.358 |
| single_date_pHEC_terrain | 10 km | 0.404 | 0.089 | 0.096 | 0.356 |
| comp_only | 10 km | 0.071 | −0.012 | 0.008 | 0.169 |
| terrain_only | 10 km | 0.334 | 0.012 | 0.020 | 0.276 |

The full set at 10 km reproduces E08 exactly (0.409 / 0.108 / 0.116 / 0.370).

## Interpretation
1. **Terrain drives most of the headline, not the satellite.** Terrain + pH/EC without any satellite data reaches
   N 0.385 and OC 0.358, i.e. 94 % and 97 % of the full model. Adding the composite raises N by only 0.024 and OC by 0.012.
2. **Elevation in particular.** Removing `elev` alone lowers N from 0.409 to 0.272, P from 0.108 to 0.041, K from 0.116
   to 0.055 and OC from 0.370 to 0.291. Elevation separates regions, so it acts largely as a location proxy (question a: yes).
3. **With 50 km blocks, N drops sharply (0.409 → 0.230) but OC holds (0.370 → 0.337)** (question b: partly).
   N relies more on short-range spatial similarity.
4. **The composite adds little once terrain is present:** single date + terrain gives N 0.404 and OC 0.356, almost the same as
   composite + terrain. On its own, the composite is better than the single date for OC (0.169 here vs 0.085 for single-date
   satellite only in E01).
5. **OC is the most robust target.** It stays between 0.25 and 0.37 in every set that includes terrain or pH/EC,
   including the strictest one (no elevation, 50 km: 0.251). P and K fall to ≈ 0 under the strictest test.
6. **Strictest honest result** (no elevation, 50 km blocks, no location): **N 0.163, P 0.004, K 0.018, OC 0.251.**

## Decision needed
Whether `elev` is accepted as an input. It is a physical property of the field (standard in digital soil mapping),
but it largely acts as regional location. The two options are to report the full set with this caveat, or to make the
no-elevation set the main feature set. The algorithm comparison should use the same choice.
