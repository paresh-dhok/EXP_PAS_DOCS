# E39 — Validation design: random 70/30 vs spatial CV, statewide vs region-wise, clustered vs de-clustered

**Date:** 2026-10-14
**Notebook:** cell run on 2026-10-14
**Results:** `results/39_validation_design.csv` (per dataset × scope × nutrient: R² random 70/30, R² spatial 10 km)

## Why
After the faculty meeting of 2026-10-09 the paper is framed around one base model and the effect of the validation
design: a random 70/30 split (as most published studies use) against spatial CV. The question is which design choice
(de-clustering, statewide vs region-wise model, random vs spatial test) moves the reported accuracy, and by how much.

No blind hypothesis: the cell was test-run before it was given, and the numbers below are identical to that test run.

## Setup
- **Datasets:** clustered `mh_model_dataset` (33,877 samples, placeholder-GPS clusters kept) and de-clustered
  `mh_final_dataset` (17,620 locations). Both use the single-date bands, so the clustered set needs no new extraction.
- **Inputs (39):** 12 single-date bands + 16 indices + pH, EC + elevation + 6 climate + longitude, latitude.
  Elevation and climate for clustered samples are taken from the nearest de-clustered location
  (median distance 3 m, 95 % within 751 m; climate is ~km scale).
- **Model:** LightGBM, fixed settings as in E36; target log1p standardised.
- **Scopes:** one statewide model, and one model per region (mean of 5 regions reported).
- **Tests:** one random 70/30 split (`random_state=42`) and 5-fold spatial CV on 10 km blocks. Run time 0.3 min.

## Results — R²

| Data | Scope | Test | N | P | K | OC |
|---|---|---|---|---|---|---|
| Clustered 33,877 | Statewide | Random 70/30 | **0.774** | **0.499** | **0.465** | **0.686** |
| Clustered 33,877 | Statewide | Spatial 10 km | 0.598 | 0.334 | 0.256 | 0.543 |
| Clustered 33,877 | Mean of regions | Random 70/30 | 0.614 | 0.535 | 0.448 | 0.523 |
| Clustered 33,877 | Mean of regions | Spatial 10 km | 0.433 | 0.327 | 0.216 | 0.304 |
| De-clustered 17,620 | Statewide | Random 70/30 | 0.749 | 0.484 | 0.413 | 0.682 |
| De-clustered 17,620 | Statewide | Spatial 10 km | 0.596 | 0.349 | 0.288 | 0.565 |
| De-clustered 17,620 | Mean of regions | Random 70/30 | 0.630 | 0.540 | 0.374 | 0.454 |
| De-clustered 17,620 | Mean of regions | Spatial 10 km | 0.461 | 0.320 | 0.200 | 0.322 |

## Interpretation
1. **De-clustering hardly changes R²** (statewide random N 0.774 vs 0.749; spatial 0.598 vs 0.596). Keeping the
   clustered samples does not inflate the result much, so the full 33,877 samples can be the main dataset.
2. **The largest effect is the test design.** Statewide, random 70/30 → spatial CV lowers R² by 0.15–0.24
   (N 0.774 → 0.598, K 0.465 → 0.256).
3. **Statewide models score higher than region-wise models** for N and OC (random N 0.774 vs 0.614; OC 0.686 vs
   0.523): the statewide model also learns the large differences between regions.
4. The headline for the paper is the statewide random 70/30 result, always reported next to the spatial-CV result.

## Caveats
- One seed and one split (E35: seed SD ≈ 0.01 for means).
- Elevation and climate for clustered samples are borrowed from the nearest de-clustered location.
- Single-date bands, not the multi-date composite (the composite exists only for de-clustered locations).
