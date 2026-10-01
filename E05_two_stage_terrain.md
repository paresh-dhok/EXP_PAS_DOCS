# E05 — Two-stage model with terrain features

**Date:** 2026-09-30
**Notebook:** `new.ipynb` cell 29
**Results:** `results/05_two_stage_terrain.csv`
**Data:** 17,620 locations + `mh_terrain.parquet` (D09)

## Hypothesis (before running)
Terrain (slope, valley/ridge position, roughness) differs between fields in the same district and controls erosion and
the accumulation of soil and water. It may supply the field-level signal that the spectra lacked.

## Setup
Same two-stage procedure as E04 (district mean from training folds + RF 200 trees, min_samples_leaf 5,
max_features 1.0, seed 42; 10 km spatial blocks, 5 folds).

| Stage 2 set | Features |
|---|---|
| T_terrain | 7 terrain features |
| C_fusion | 28 satellite + pH, EC (reference) |
| CT_fusion_terrain | C + 7 terrain |
| DT_fusion_terrain_GPS | CT + longitude, latitude |

## Results
| Set | Two-stage N | P | K | OC |
|---|---|---|---|---|
| T_terrain | 0.618 | 0.355 | 0.357 | 0.589 |
| C_fusion | 0.617 | 0.387 | 0.364 | 0.608 |
| CT_fusion_terrain | 0.636 | 0.379 | 0.376 | 0.610 |
| DT_fusion_terrain_GPS | **0.667** | **0.403** | **0.391** | **0.620** |

| Set | **Within-district** N | P | K | OC |
|---|---|---|---|---|
| T_terrain | −0.036 | −0.067 | −0.040 | −0.050 |
| C_fusion | −0.008 | −0.012 | −0.015 | −0.006 |
| CT_fusion_terrain | **0.039** | 0.002 | 0.003 | 0.008 |
| DT_fusion_terrain_GPS | 0.123 | 0.058 | 0.022 | 0.038 |

## Interpretation
- Terrain **alone** explains nothing at field level.
- **Terrain combined with the spectra gives N its first positive field-level signal** (0.039). The model uses interactions
  (e.g. a valley position combined with a soil colour). P, K and OC remain ≈ 0.
- The best overall results barely change (N 0.667, P 0.403, K 0.391, OC 0.620).
- This raised the question of whether field-level differences in SHC data are predictable at all, or mostly noise → E07.

## Status
Uses location (district stage). Diagnostic. The field-only (no-location) version of "satellite + pH/EC + terrain" **has not been run yet**.
