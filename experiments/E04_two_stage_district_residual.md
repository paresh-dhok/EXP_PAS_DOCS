# E04 — Two-stage model: district average + RF on the within-district deviation

**Date:** 2026-09-30
**Notebook:** `new.ipynb` cell 27
**Results:** `results/04_two_stage_district_residual.csv`
**Data:** 17,620 locations

## Question (before running)
After removing the district effect, do Sentinel-2 and/or pH/EC explain why one field differs from its district's average?

## Setup
For each spatial fold (10 km blocks, 5 folds, seed 42):
1. **Stage 1:** the district mean of log1p(y), computed from the training folds only.
2. **Stage 2:** `RandomForestRegressor(n_estimators=200, min_samples_leaf=5, max_features=1.0, random_state=42)`
   trained on the deviation log1p(y) − district mean.
3. Prediction = expm1(district mean + predicted deviation).

Metrics:
- `R2_district_only`: stage 1 alone
- `R2_two_stage`: final prediction, original scale
- **`R2_within_district`**: R² of the predicted vs true deviation (log scale). 0 means no field-level skill.

Stage-2 feature sets: A_satellite (28), B_sensor_pH_EC (2), C_fusion (30), D_fusion_plus_GPS (32).

## Results
District-only baseline: N 0.624, P 0.379, K 0.373, OC 0.609.

| Stage 2 features | Two-stage N | P | K | OC |
|---|---|---|---|---|
| A_satellite | 0.617 | 0.380 | 0.363 | 0.602 |
| B_sensor_pH_EC | 0.607 | 0.370 | 0.333 | 0.591 |
| C_fusion | 0.617 | 0.387 | 0.364 | 0.608 |
| D_fusion_plus_GPS | **0.660** | **0.410** | **0.385** | **0.619** |

| Stage 2 features | **Within-district** N | P | K | OC |
|---|---|---|---|---|
| A_satellite | −0.015 | −0.018 | −0.019 | −0.019 |
| B_sensor_pH_EC | −0.055 | −0.067 | −0.091 | −0.069 |
| C_fusion | −0.008 | −0.012 | −0.015 | −0.006 |
| D_fusion_plus_GPS | **0.118** | 0.061 | 0.017 | 0.035 |

## Interpretation
- **Within a district, neither the satellite nor pH/EC explains field-to-field differences** (all ≈ 0 or slightly negative).
- Only GPS adds some within-district skill (N 0.12): nutrients also vary smoothly inside districts.
- This explains E01: pH/EC's statewide R² (N 0.17) came from the *regional* co-variation of pH and N, which disappears inside a district.
- Possible reasons, listed for the report:
  1. Available N, P and K have no direct spectral signature in broad-band Sentinel-2.
  2. In black Vertisols the dark colour comes from clay mineralogy, not OC, and OC varies over a narrow range.
  3. SHC label noise (lab differences, composite sampling, GPS recorded where the sampler stood).

## Status
Uses location (district stage, set D also GPS). Diagnostic only. Best two-stage results: N 0.660, P 0.410, K 0.385, OC 0.619.
