# E45 — Sensitivity of the headline model to pH and EC measurement error

**Date:** 2026-10-14
**Notebook:** cell run on 2026-10-14 (after E44, reuses its data and functions)
**Results:** `results/45_ph_ec_noise.csv` (nutrient × test × scenario: R², RMSE)

## Why
The model uses laboratory pH and EC from the Soil Health Card. In practice these would come from a field sensor
(e.g. JXBS-3001: pH accuracy ±0.3). A reviewer will ask how much accuracy is lost with sensor-grade values.

The cell was **not** test-run before it was given (user's request). Check passed: the "lab values" row reproduces E42
exactly (N 0.812 random, 0.661 spatial).

## Setup
- Headline setup: statewide LightGBM (E36 settings), clustered `mh_model_dataset` (33,877), 39 inputs + 4
  neighbourhood features.
- The model is trained on laboratory values; noise is added to the **test** pH and EC only (field use of a model
  trained on lab data): pH + N(0, σ), EC × (1 + N(0, r)), EC floored at 0.001. Levels (σ pH, r EC):
  (0.15, 10 %), (0.30, 20 %) ≈ sensor specification, (0.50, 40 %).
- Worst case: model retrained without pH and EC.
- Tests: random 70/30 and 10 km spatial CV. Run time 0.2 min.

## Results — R²

| Scenario | Random: N | P | K | OC | Spatial 10 km: N | P | K | OC |
|---|---|---|---|---|---|---|---|---|
| Lab values (no noise) | 0.812 | 0.606 | 0.551 | 0.712 | 0.661 | 0.375 | 0.308 | 0.537 |
| pH ±0.15, EC ±10 % | 0.813 | 0.604 | 0.551 | 0.712 | 0.661 | 0.374 | 0.307 | 0.537 |
| pH ±0.3, EC ±20 % (sensor spec) | 0.811 | 0.595 | 0.551 | 0.711 | 0.661 | 0.373 | 0.306 | 0.537 |
| pH ±0.5, EC ±40 % | 0.811 | 0.595 | 0.546 | 0.711 | 0.661 | 0.371 | 0.303 | 0.536 |
| Retrained without pH, EC | 0.809 | 0.594 | 0.550 | 0.712 | 0.662 | 0.376 | 0.305 | 0.534 |

RMSE changes by at most 1.4 % (P, random, 15.41 → 15.65).

## Interpretation
1. **The headline model is robust to sensor-grade pH/EC error:** at the sensor specification R² drops by ≤ 0.011
   (P, random); all other changes are ≤ 0.002.
2. **But pH and EC contribute almost nothing once location, climate and neighbourhood context are present:**
   without them R² changes by ≤ 0.012 (P) and is otherwise within ±0.003. This differs from the earlier models without
   location inputs (E37: pH + EC added about 0.07 to the 39-input models without coordinates; E31: pH and EC were the
   top inputs in the 41-input set). The information in pH and EC overlaps with what the neighbouring samples and the
   position already supply.
3. Consequence for the paper: write "robust to sensor-grade measurement error", but do **not** claim that pH and EC
   are among the most important inputs of the headline model (check with SHAP, E46).
4. Consequence for the capstone: in this model a pH/EC sensor does not improve N, P, K, OC prediction; its value
   is the pH and EC readings themselves.

## Caveats
One seed, one split, one noise draw per scenario; Gaussian noise is a simplification of real sensor error
(bias and drift not modelled).
