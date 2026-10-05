# E03 — District-average baseline and feature-dilution test

**Date:** 2026-09-30
**Notebook:** `new.ipynb` cell 26
**Results:** `results/03_diagnostics_district_dilution.csv`
**Data:** 17,620 locations; district = second field of `id` (e.g. `27_485_…` → 485)

## Questions (before running)
1. Is the GPS effect mainly **district / lab level**? If simply predicting the district's average gives an R² close to
   GPS-only, the regional effect dominates.
2. Was "more features = worse" in E02 a **feature-dilution artefact** (each split sees only 33 % of the features, so
   longitude and latitude are rarely considered)?

## Setup
- **District average (no ML):** for each spatial fold, the mean of log1p(target) per district is computed **from the
  training folds only**. A test sample gets its district's mean (the global training mean if the district is unseen),
  back-transformed with expm1.
- **RF with all features per split:** `max_features=1.0`, 300 trees, min_samples_leaf 3, log target, seed 42.
- Validation: spatial 10 km blocks, 5 folds.

## Results (R²)
| Model | N | P | K | OC |
|---|---|---|---|---|
| **District average (no ML)** | 0.624 | **0.379** | **0.373** | **0.609** |
| RF all-features, GPS only | **0.663** | 0.359 | 0.279 | 0.573 |
| RF all-features, pH/EC + GPS | 0.651 | 0.377 | 0.321 | 0.587 |
| RF all-features, satellite + pH/EC + GPS | 0.642 | 0.378 | 0.314 | 0.572 |

## Interpretation
- **A plain district average matches or beats every Random Forest.** Most of the predictable variation in the SHC values
  is **between districts**. That is partly real soil geography and probably partly lab differences (each district's
  samples are analysed by its own lab).
- With all features per split, the full model recovered from 0.576 to 0.642 for N. So E02's ranking was partly a dilution
  artefact: the satellite is not harmful, it simply adds almost nothing beyond location.
- New research question: **can the satellite and sensor explain field-to-field differences *within* a district?** → E04.

## Status
Uses location (district, GPS). Diagnostic only.
