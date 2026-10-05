# E16 — Is climate acting as location? (region-wise diagnostic)

**Date:** 2026-10-05
**Notebook:** cell run on 2026-10-05, after E15
**Results:** `results/16_climate_vs_location_check.csv`
**Data:** model table (17,273) + climate (D11); region-wise spatial CV (10 km blocks, 5 folds inside each region)

## Question (recorded before running)
E15 showed a large gain from climate inside regions. The climate grid is a smooth 4 km surface, so climate values may
encode position within a region. If a model with only longitude/latitude scores about the same as one with only climate,
climate is acting mainly as location. If climate scores clearly higher, it carries information of its own.
Longitude/latitude are used here **only as a diagnostic**, not as candidate model inputs.

## Setup
Same Random Forest as E14/E15 (300 trees, min_samples_leaf 3, max_features 0.33, seed 42, log1p target).

| Set | Inputs |
|---|---|
| lonlat_only (diagnostic) | longitude, latitude |
| climate_only | 6 climate features |
| base_41 + lonlat (diagnostic) | 41 inputs + longitude, latitude |
| base_41 + climate | 41 inputs + 6 climate (same as E15 `plus_climate`) |

## Results (R²)
Mean over the 5 regions:

| Set | N | P | K | OC |
|---|---|---|---|---|
| **lonlat_only (diagnostic)** | **0.486** | **0.333** | **0.242** | **0.333** |
| climate_only | 0.373 | 0.285 | 0.188 | 0.253 |
| base_41 + lonlat (diagnostic) | 0.434 | 0.295 | 0.219 | 0.302 |
| base_41 + climate | 0.387 | 0.260 | 0.179 | 0.246 |

Per region:

| Region | Set | N | P | K | OC |
|---|---|---|---|---|---|
| Vidarbha | lonlat_only | 0.373 | 0.245 | 0.519 | 0.383 |
| | climate_only | 0.297 | 0.207 | 0.480 | 0.209 |
| | base_41 + lonlat | 0.346 | 0.185 | 0.452 | 0.236 |
| | base_41 + climate | 0.319 | 0.181 | 0.447 | 0.189 |
| Marathwada | lonlat_only | 0.551 | 0.504 | 0.255 | 0.096 |
| | climate_only | 0.454 | **0.562** | 0.216 | **0.125** |
| | base_41 + lonlat | 0.522 | 0.485 | 0.252 | 0.103 |
| | base_41 + climate | 0.445 | 0.525 | 0.197 | 0.127 |
| North MH | lonlat_only | 0.408 | 0.411 | 0.347 | 0.382 |
| | climate_only | 0.332 | 0.278 | 0.204 | 0.320 |
| | base_41 + lonlat | 0.345 | 0.292 | 0.309 | 0.362 |
| | base_41 + climate | 0.309 | 0.221 | 0.235 | 0.315 |
| Western MH | lonlat_only | 0.553 | 0.425 | 0.006 | 0.576 |
| | climate_only | 0.418 | 0.366 | −0.009 | 0.439 |
| | base_41 + lonlat | 0.485 | 0.419 | −0.009 | 0.565 |
| | base_41 + climate | 0.425 | 0.330 | −0.015 | 0.439 |
| Konkan | lonlat_only | 0.546 | 0.079 | 0.084 | 0.228 |
| | climate_only | 0.367 | 0.013 | 0.050 | 0.171 |
| | base_41 + lonlat | 0.472 | 0.095 | 0.091 | 0.243 |
| | base_41 + climate | 0.437 | 0.042 | 0.031 | 0.161 |

## Interpretation
1. **Coordinates alone beat climate alone in 18 of 20 region × nutrient cases** (exceptions: Marathwada P and OC).
   On average, climate-only reaches about 75–85 % of the coordinates-only score.
   **Climate is acting mainly as a smoothed version of location**, not as independent information.
2. **Coordinates alone also beat every model with the 41 field features.** Adding the 41 features to coordinates
   lowers the mean score (N 0.486 → 0.434), and adding them to climate raises it only slightly (N 0.373 → 0.387).
   Inside regions, the predictable variation is almost entirely **spatial pattern**: nearby fields have similar lab
   values (real soil geography and/or laboratory/district patterns). The satellite, terrain and pH/EC inputs add little beyond it.
3. This is consistent with the earlier statewide findings: GPS alone N 0.65 (E02), district average ≈ any model (E03),
   ≈ 0 within-district skill from field features (E04–E06).
4. Under the rule "no location inputs", **climate should be treated like coordinates**. The large gain in E15 does not
   come from information measured at the field.

## Decision needed
Whether climate (and elevation) are allowed as model inputs. The evidence says they work mainly as location proxies.
