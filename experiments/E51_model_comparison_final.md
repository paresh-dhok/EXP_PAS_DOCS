# E51 — Final setup: five models, random 70/30 vs spatial 10 km

**Date:** 2026-10-14
**Notebook:** cell run on 2026-10-14 (after E50)
**Results:** `results/51_model_comparison_final.csv` (model × nutrient × test: R², RMSE, MAE, seconds)
**Replaces E44 for the paper** (E44 included Raigad).

## Setup
As E44 (same five models and settings, predictions clipped to the training range), on the final data: 32,096 samples
(Raigad excluded), 39 inputs + 4 neighbourhood features, statewide. Random 70/30 and 10 km spatial CV.
Run time 2.8 min; CPU seconds: RF 823, MLP 75, LightGBM 47, KNN 46, ridge 5.
The cell was **not** test-run before it was given; LightGBM row identical to E49.

## Results — R²

| Model | Random: N | P | K | OC | Spatial 10 km: N | P | K | OC |
|---|---|---|---|---|---|---|---|---|
| Linear (ridge) | 0.700 | 0.598 | 0.552 | 0.699 | 0.355 | 0.349 | 0.315 | 0.566 |
| KNN | 0.649 | 0.556 | 0.514 | 0.675 | 0.326 | 0.350 | 0.301 | 0.560 |
| MLP | 0.701 | 0.603 | 0.550 | 0.695 | 0.351 | 0.342 | 0.320 | 0.561 |
| Random Forest | **0.713** | **0.616** | **0.571** | **0.708** | 0.391 | 0.390 | 0.348 | **0.591** |
| LightGBM | 0.706 | 0.614 | 0.564 | 0.701 | **0.393** | **0.396** | **0.352** | 0.578 |

RMSE, random 70/30 (N / P / K / OC): ridge 55.6 / 15.37 / 166.9 / 0.216; KNN 60.1 / 16.16 / 173.8 / 0.224;
MLP 55.5 / 15.29 / 167.3 / 0.217; RF 54.4 / 15.03 / 163.3 / 0.213; LightGBM 55.0 / 15.08 / 164.6 / 0.215.
RMSE, spatial 10 km: ridge 79.1 / 19.96 / 206.0 / 0.262; KNN 80.8 / 19.94 / 208.1 / 0.264; MLP 79.3 / 20.06 /
205.3 / 0.264; RF 76.8 / 19.32 / 201.0 / 0.254; LightGBM 76.7 / 19.22 / 200.4 / 0.258.

R² drop, random → spatial 10 km:

| Model | N | P | K | OC |
|---|---|---|---|---|
| Linear (ridge) | 0.345 | 0.250 | 0.237 | 0.133 |
| KNN | 0.323 | 0.206 | 0.213 | 0.115 |
| MLP | 0.350 | 0.261 | 0.230 | 0.134 |
| Random Forest | 0.321 | 0.226 | 0.224 | 0.117 |
| LightGBM | 0.313 | 0.218 | 0.212 | 0.123 |

## Interpretation
1. **The drop is the same for every model:** N 0.31–0.35, P 0.21–0.26, K 0.21–0.24, OC 0.12–0.13. The validation
   design, not the algorithm, decides the reported accuracy.
2. **Spread between models is small:** random 0.65–0.71 (N), spatial 0.33–0.39 (N). Random Forest and LightGBM lead
   (within 0.01, i.e. seed noise, E35); the tree ensembles are 0.03–0.04 better than ridge and MLP under spatial CV.
3. LightGBM matches Random Forest at about 1/18 of the computing time (47 vs 823 CPU s) and is the base model.
4. Ridge regression stays close to the tree models (random N 0.700 vs 0.713): most of the information is in the
   neighbourhood features, which enter the model almost linearly.

## Caveats
One seed, one split; untuned settings (RF 100 trees).
