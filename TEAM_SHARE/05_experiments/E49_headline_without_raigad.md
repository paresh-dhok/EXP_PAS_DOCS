# E49 — Final headline model (without Raigad): all metrics and Figure 1

**Date:** 2026-10-14
**Notebook:** cell run on 2026-10-14 (after E48)
**Results:** `results/49_headline_metrics.csv`, `results/49_measured_vs_predicted.png`
**Replaces E40 as the paper's main table and figure.**

## Decision behind it
After E47/E48 (Raigad, 5.3 % of samples, carries 61 % of the N variance; median N 872 kg/ha vs about 195 statewide)
Raigad district (491) is excluded from the paper's dataset, with one stated sentence of justification.

The cell was **not** test-run before it was given (user's request). Check passed: random 70/30 test R² identical to E48.

## Setup
- Data: clustered `mh_model_dataset` without Raigad: **32,096 samples**.
- Inputs: 39 (12 bands, 16 indices, pH, EC, elevation, 6 climate, longitude, latitude) + 4 neighbourhood features
  (10 nearest training samples; training rows exclude themselves; no test values used).
- Model: statewide LightGBM (E36 settings), log1p target standardised.
- Tests: random 70/30 (`random_state=42`) and 5-fold spatial CV on 10 km blocks. Run time 0.2 min.

## Results

| Test | Metric | N (kg/ha) | P (kg/ha) | K (kg/ha) | OC (%) |
|---|---|---|---|---|---|
| Random 70/30 test (n = 9,629) | R² | **0.706** | **0.614** | **0.564** | **0.701** |
| | RMSE | 55.0 | 15.08 | 164.6 | 0.215 |
| | MAE | 34.6 | 6.49 | 101.6 | 0.126 |
| | bias | −7.4 | −1.70 | −25.0 | −0.010 |
| | RPIQ | 1.69 | 0.77 | 1.72 | 1.17 |
| Spatial 10 km CV (n = 32,096) | R² | **0.393** | **0.396** | **0.352** | **0.578** |
| | RMSE | 76.7 | 19.22 | 200.4 | 0.258 |
| | MAE | 45.9 | 8.80 | 127.7 | 0.153 |
| | bias | −10.0 | −2.76 | −35.1 | −0.032 |
| | RPIQ | 1.21 | 0.62 | 1.44 | 0.97 |
| Random 70/30 train (n = 22,467) | R² | 0.748 | 0.735 | 0.649 | 0.794 |

## Interpretation
1. Random 70/30: R² 0.56–0.71; spatial 10 km: 0.35–0.58. The validation design costs 0.31 (N), 0.22 (P), 0.21 (K),
   0.12 (OC).
2. Train vs test gap 0.04–0.12: no strong overfitting.
3. MAE is 15 % (N), 29 % (P), 23 % (K), 22 % (OC) of the mean values (N ≈ 231, P ≈ 22.7, K ≈ 433, OC ≈ 0.57,
   means of the full dataset): moderate errors, suitable for low/medium/high screening.
4. The figure no longer shows the Raigad block. Under spatial CV high values are under-predicted (all nutrients),
   and P shows a horizontal band near 20 kg/ha (the model falls back towards the typical value).

## Caveats
One seed, one split.
