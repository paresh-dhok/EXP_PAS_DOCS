# E44 — Five models on the headline setup: random 70/30 vs spatial 10 km

**Date:** 2026-10-14
**Notebook:** cell run on 2026-10-14 (after E43, reuses its data and functions)
**Results:** `results/44_model_comparison.csv` (model × nutrient × test: R², RMSE, MAE, seconds)

## Why
A reviewer will ask whether the drop from random to spatial validation is specific to LightGBM. This compares five
common model families on exactly the same inputs and tests. Models chosen to mirror Gupta & Patil (2026: KNN, MLP,
LightGBM) plus the two most common baselines (linear regression, Random Forest).

The cell was **not** test-run before it was given (user's request).

## Setup
- Data and inputs as E42: statewide, clustered `mh_model_dataset` (33,877), 39 inputs + 4 neighbourhood features
  (10 nearest training samples, no leakage). Target log1p standardised; predictions clipped to the training range.
- Models: Ridge (alpha 1, standardised inputs); KNN (k = 15, distance-weighted, standardised); MLP (64-32, alpha
  1e-3, early stopping, standardised); Random Forest (100 trees, min_samples_leaf 5, max_features 0.33);
  LightGBM (E36 settings). Seed 42.
- Tests: random 70/30 and 5-fold spatial CV on 10 km blocks. Run time 3.3 min; CPU seconds: RF 964, MLP 104,
  KNN 53, LightGBM 52, Ridge 5.

## Results — R²

| Model | Random: N | P | K | OC | Spatial 10 km: N | P | K | OC |
|---|---|---|---|---|---|---|---|---|
| Linear (ridge) | 0.801 | 0.595 | 0.538 | 0.707 | 0.643 | 0.330 | 0.294 | 0.522 |
| KNN | 0.772 | 0.553 | 0.498 | 0.682 | 0.620 | 0.334 | 0.256 | 0.517 |
| MLP | 0.799 | 0.597 | 0.539 | 0.701 | 0.654 | 0.344 | 0.294 | 0.512 |
| Random Forest | **0.813** | **0.609** | **0.558** | **0.719** | 0.655 | 0.373 | **0.314** | **0.546** |
| LightGBM | 0.812 | 0.606 | 0.551 | 0.712 | **0.661** | **0.375** | 0.308 | 0.537 |

RMSE, random 70/30 (N / P / K / OC): ridge 70.3 / 15.62 / 177.2 / 0.226; KNN 75.3 / 16.42 / 184.8 / 0.236;
MLP 70.6 / 15.58 / 177.0 / 0.229; RF 68.1 / 15.35 / 173.4 / 0.221; LightGBM 68.3 / 15.41 / 174.7 / 0.224.
RMSE, spatial 10 km: ridge 95.0 / 20.18 / 217.4 / 0.294; KNN 97.9 / 20.11 / 223.2 / 0.295; MLP 93.4 / 19.97 /
217.4 / 0.297; RF 93.3 / 19.52 / 214.4 / 0.286; LightGBM 92.5 / 19.49 / 215.4 / 0.289.

R² drop, random → spatial 10 km:

| Model | N | P | K | OC |
|---|---|---|---|---|
| Linear (ridge) | 0.158 | 0.265 | 0.244 | 0.185 |
| KNN | 0.151 | 0.219 | 0.241 | 0.166 |
| MLP | 0.145 | 0.253 | 0.245 | 0.190 |
| Random Forest | 0.158 | 0.236 | 0.244 | 0.174 |
| LightGBM | 0.151 | 0.231 | 0.244 | 0.175 |

## Interpretation
1. **The drop is the same for every model:** 0.15–0.16 (N), 0.22–0.27 (P), 0.24–0.25 (K), 0.17–0.19 (OC).
   It is a property of the validation design, not of the algorithm.
2. **The models are close:** Random Forest and LightGBM lead (within 0.01 of each other; E35: seed SD ≈ 0.01),
   MLP and ridge are 0.01–0.03 behind, KNN is last. The choice of validation changes R² about ten times more than the
   choice of model.
3. **Ridge regression is almost as good as the tree models** (random N 0.801 vs 0.813). With neighbourhood features
   the problem is close to linear: the neighbour mean carries most of the information.
4. LightGBM gives Random-Forest accuracy at about 1/18 of the computing time (52 vs 964 CPU s), which supports
   keeping it as the base model.

## Caveats
One seed, one split; models at fixed, untuned settings (RF reduced to 100 trees for speed).
