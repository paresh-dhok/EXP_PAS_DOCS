# E40 — Statewide base model: full metrics and measured-vs-predicted figure

**Date:** 2026-10-14
**Notebook:** cell run on 2026-10-14 (directly after E39, reuses its data and functions)
**Results:** `results/40_statewide_base_model_metrics.csv`, `results/40_measured_vs_predicted.png`

## Why
The paper's base model is one statewide LightGBM on all 33,877 clean samples (E39). This cell gives its full metric
set for the random 70/30 split (train and test) and for 10 km spatial CV, plus the paper figure.

No blind hypothesis: the cell was test-run before it was given (identical numbers).

## Setup
As E39: clustered `mh_model_dataset` (33,877), 39 inputs (single-date bands + indices, pH, EC, elevation, climate,
longitude, latitude), LightGBM fixed settings, log1p target. RPIQ = (Q3 − Q1) of measured / RMSE.

## Results

| Test | Metric | N (kg/ha) | P (kg/ha) | K (kg/ha) | OC (%) |
|---|---|---|---|---|---|
| Random 70/30 test (n = 10,164) | R² | **0.774** | **0.499** | **0.465** | **0.686** |
| | RMSE | 74.8 | 17.39 | 190.7 | 0.234 |
| | MAE | 45.7 | 7.64 | 118.2 | 0.143 |
| | bias | −10.7 | −2.70 | −34.2 | −0.013 |
| | RPIQ | 1.36 | 0.70 | 1.47 | 1.20 |
| Spatial 10 km CV (n = 33,877) | R² | 0.598 | 0.334 | 0.256 | 0.543 |
| | RMSE | 100.7 | 20.12 | 223.3 | 0.287 |
| | MAE | 58.7 | 9.40 | 140.7 | 0.173 |
| | RPIQ | 1.01 | 0.60 | 1.28 | 0.98 |
| Random 70/30 train (n = 23,713) | R² | 0.807 | 0.577 | 0.544 | 0.750 |

## Interpretation
1. Train R² is only 0.03–0.08 above test R²: the model does not overfit.
2. Spatial CV lowers R² by 0.15–0.24 and raises RMSE by 16–35 %.
3. The figure shows the high values being under-predicted under spatial CV (P and K most clearly); bias is negative
   throughout (log-target back-transform pulls predictions toward the median).
4. A tight group of samples at N ≈ 900 kg/ha is predicted well in both tests. It looks like repeated values from one
   lab or district; check before claiming that high N is predicted well.

## Caveats
One seed, one split. Same input caveats as E39.
