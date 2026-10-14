# E53 — Input ablation on the final setup: what Sentinel-2 and the neighbourhood features add

**Date:** 2026-10-14
**Notebook:** cell run on 2026-10-14 (after E52)
**Results:** `results/53_input_ablation.csv` (input set × nutrient × test: R², RMSE, MAE, bias, RPIQ)

## Why
Desk-rejection check for a remote-sensing journal: does Sentinel-2 add accuracy, and is the model more than an
interpolation of nearby samples?

## Setup
Final setup (32,096 samples, Raigad excluded; statewide LightGBM, E36 settings). Five input sets, random 70/30 and
10 km spatial CV. Neighbourhood features as in E42 (training samples only). Run time 0.2 min.

## Results — R²

| Inputs | Random: N | P | K | OC | Spatial 10 km: N | P | K | OC |
|---|---|---|---|---|---|---|---|---|
| Full (39 inputs + neighbourhood) | 0.706 | 0.614 | 0.564 | 0.701 | 0.393 | 0.396 | 0.352 | 0.578 |
| Without Sentinel-2 (11 + neighbourhood) | 0.710 | 0.616 | 0.568 | 0.703 | 0.390 | 0.381 | 0.357 | 0.578 |
| Without neighbourhood (39 inputs) | 0.613 | 0.529 | 0.498 | 0.680 | 0.326 | 0.359 | 0.312 | 0.557 |
| Neighbourhood only (4) | 0.694 | 0.590 | 0.548 | 0.686 | 0.333 | 0.367 | 0.288 | 0.533 |
| Sentinel-2 + pH, EC only (30) | 0.168 | 0.121 | 0.161 | 0.324 | 0.036 | 0.033 | 0.049 | 0.201 |

RMSE, random 70/30 (N / P / K / OC): full 55.0 / 15.08 / 164.6 / 0.215; without Sentinel-2 54.6 / 15.03 / 163.8 /
0.214; without neighbourhood 63.1 / 16.65 / 176.6 / 0.223; neighbourhood only 56.1 / 15.53 / 167.7 / 0.220;
Sentinel-2 + pH, EC 92.6 / 22.73 / 228.4 / 0.323.

## Interpretation
1. **Sentinel-2 adds no accuracy once location, climate and neighbourhood context are present.** Removing all 28
   Sentinel-2 inputs changes R² by −0.004 to +0.015 (random: slightly *better* without; spatial: P −0.015, others
   within ±0.005). The 11–13 % SHAP share of Sentinel-2 (E52) is credit taken from correlated inputs, not added
   information.
2. **On its own, bare-soil Sentinel-2 (+ pH, EC) explains little:** random R² 0.12–0.32, spatial 0.03–0.20. OC is the
   only nutrient with some signal (0.32 random, 0.20 spatial) — consistent with darker soils being richer in OC.
3. **Under random splitting the model is close to interpolation:** neighbourhood features alone reach 0.69 / 0.59 /
   0.55 / 0.69, within 0.01–0.02 of the full model.
4. **Under spatial testing the other inputs matter more:** the full model beats neighbourhood-only by 0.03–0.06
   (N 0.393 vs 0.333, K 0.352 vs 0.288, OC 0.578 vs 0.533). Climate and coordinates carry information when the
   nearest samples are far away.
5. Consequence for the paper: do not claim that Sentinel-2 improves the predictions. The correct statement is that
   date-matched bare-soil Sentinel-2 reflectance carries a weak signal on its own (mainly for OC) and adds nothing
   beyond location, climate and nearby measurements.

## Caveats
One seed, one split; Sentinel-2 used as single-date 3×3 medians (the multi-date composite exists only for the
de-clustered locations and was not tested here).
