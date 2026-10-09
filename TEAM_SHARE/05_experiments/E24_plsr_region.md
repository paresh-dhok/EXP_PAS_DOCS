# E24 — Partial least squares regression (PLSR), region-wise

**Date:** 2026-10-09
**Notebook:** cell run on 2026-10-09
**Results:** `results/24_plsr_region.csv` (R², RMSE, MAE and median number of components per region × input set × nutrient)
**Data:** model table, 17,273 locations + climate; region-wise protocol (10 km spatial CV, 5 folds, inside each region)

## Hypothesis (recorded before running)
PLSR scores about the same as Ridge (E23), because both are linear methods designed for correlated inputs, and well
below Random Forest. The best number of components is small.

## Setup
- `PLSRegression(n_components=k, scale=True)`; target log1p, predictions back-transformed with expm1 and clipped to the
  range of the training-fold target values (as in E23).
- Number of components chosen from {1, 2, 3, 5, 8, 12, 16, 20} by lowest mean squared error in an inner
  `GroupKFold(3)` on the training blocks; the model is then refitted on all training data of the fold.
- Input sets: **41 inputs** and **41 + elev + climate** (48). Run time 39 s.

## Results — mean R² over the 5 regions (spatial 10 km)

| Input set | Model | N | P | K | OC |
|---|---|---|---|---|---|
| 41 inputs | RandomForest (E18) | **0.137** | **0.107** | **0.042** | **0.092** |
| | Ridge (E23) | 0.035 | 0.047 | −0.000 | 0.016 |
| | **PLSR** | 0.027 | 0.044 | −0.006 | 0.011 |
| 41 + elev + climate | RandomForest (E18) | **0.400** | **0.269** | **0.194** | **0.269** |
| | Ridge (E23) | 0.215 | 0.152 | 0.067 | 0.146 |
| | **PLSR** | 0.162 | 0.124 | 0.070 | 0.100 |

PLSR per region, 41 inputs (R²):

| Region | N | P | K | OC |
|---|---|---|---|---|
| Vidarbha | 0.021 | −0.026 | **0.231** | −0.017 |
| Marathwada | 0.074 | 0.156 | −0.015 | 0.000 |
| North MH | −0.012 | −0.015 | −0.074 | 0.022 |
| Western MH | 0.082 | 0.150 | −0.039 | 0.028 |
| Konkan | −0.031 | −0.046 | −0.132 | 0.022 |

Median number of components chosen: 41 inputs — N 5, P 5, K 3, OC 3; 41 + elev + climate — N 12, P 12, K 8, OC 12.

## Interpretation
1. **Hypothesis confirmed for the 41 inputs:** PLSR ≈ Ridge (differences ≤ 0.01) and both are near zero, far below
   Random Forest. Only 3–5 components are needed, i.e. the 33 satellite features carry few independent directions.
2. With elevation + climate, PLSR is **below Ridge** (N 0.162 vs 0.215, OC 0.100 vs 0.146). Compressing the inputs into
   components loses part of the information in the few climate and elevation variables.
3. The pattern per region matches E23: K in Vidarbha (0.231) and P in Marathwada and Western MH (≈ 0.15) are the only
   cells with clear linear signal.
4. PLSR, the standard method in soil spectroscopy, gives no advantage here: broad-band Sentinel-2 composites do not
   contain the fine spectral structure that PLSR exploits in laboratory spectra.

## Caveats
- Single seed; component grid is coarse; inner tuning uses 3 grouped folds.
