# E30 — Stacked ensemble, region-wise

**Date:** 2026-10-09
**Notebook:** cell run on 2026-10-09 (part 2 of the three-part cell)
**Results:** `results/30_stacking_region.csv` (Stack, SimpleAverage and the 6 base models per region × input set ×
nutrient; mean stacking weights in the `w_*` columns of the Stack rows)
**Data:** model table, 17,273 locations + climate; region-wise protocol (10 km spatial CV, 5 folds, inside each region)

## Hypothesis (recorded before running)
The stack gains at most +0.01–0.02 over the best single model.

## Setup
- Base models (fixed settings): Random Forest (100 trees, max_features 0.33, leaf 5), Extra Trees (300 trees,
  max_features 0.5, leaf 3), XGBoost (400 trees, lr 0.03, depth 4, min_child_weight 10), LightGBM (400 trees, lr 0.03,
  7 leaves, min_child_samples 40), SVR (RBF, C 1, epsilon 0.3, standardised), Ridge (RidgeCV, standardised).
- In every outer fold: base-model predictions for the training locations are produced with an inner `GroupKFold(3)` on
  the training blocks; a non-negative linear regression (`LinearRegression(positive=True)`) is fitted on those
  predictions; the base models are refitted on the whole training fold and combined with the learned weights on the
  test fold. The test fold is never used for the weights.
- `SimpleAverage` = unweighted mean of the 6 base models.
- Predictions clipped to the training-fold target range. Outer folds identical to E18–E29. 40 jobs, run time 6.2 min.

## Results — mean R² over the 5 regions (spatial 10 km)

| Model | 41 inputs: N | P | K | OC | + elev + climate: N | P | K | OC |
|---|---|---|---|---|---|---|---|---|
| **Stack** | **0.152** | 0.101 | 0.042 | 0.086 | **0.432** | **0.273** | 0.191 | **0.268** |
| SimpleAverage | 0.146 | 0.102 | **0.047** | **0.091** | 0.391 | 0.243 | 0.175 | 0.251 |
| XGBoost (base) | 0.145 | 0.117 | 0.037 | 0.088 | 0.391 | 0.255 | 0.171 | 0.250 |
| LightGBM (base) | 0.144 | **0.118** | 0.038 | 0.085 | 0.383 | 0.241 | 0.169 | 0.239 |
| Extra Trees (base) | 0.133 | 0.088 | 0.038 | 0.087 | 0.415 | 0.272 | **0.196** | 0.267 |
| Random Forest (base) | 0.133 | 0.103 | 0.040 | **0.091** | 0.394 | 0.261 | 0.186 | 0.262 |
| SVR (base) | 0.120 | 0.074 | 0.023 | 0.032 | 0.289 | 0.161 | 0.094 | 0.130 |
| Ridge (base) | 0.030 | 0.054 | −0.006 | 0.018 | 0.227 | 0.158 | 0.069 | 0.135 |

Stack minus the best single tuned model of E29 (41 inputs): N +0.007, P −0.018, K −0.013, OC −0.009.

Mean stacking weights (41 inputs):

| Nutrient | RF | ET | XGBoost | LightGBM | SVR | Ridge |
|---|---|---|---|---|---|---|
| N | 0.09 | 0.13 | 0.32 | 0.18 | 0.15 | 0.05 |
| P | 0.32 | 0.13 | 0.22 | 0.12 | 0.09 | 0.02 |
| K | 0.25 | 0.14 | 0.11 | 0.10 | 0.10 | 0.10 |
| OC | 0.16 | 0.15 | 0.21 | 0.14 | 0.11 | 0.03 |

## Interpretation
1. **Hypothesis confirmed; the gain is at the low end or absent.** With the 41 inputs the stack is +0.007 above the
   best single model for N and below it for P, K and OC. With elevation + climate it is +0.007 above the best tuned
   single model for N (0.432 vs Cubist 0.425) and not above it for P and K.
2. **The simple unweighted average is as good as the learned stack** with the 41 inputs (better for K and OC).
   Learning weights adds nothing when all base models carry the same weak signal.
3. **Combining models does not raise the ceiling.** The base models make largely the same errors, so there is little
   independent information to combine. This is consistent with E18–E29: the inputs, not the algorithm, limit accuracy.
4. The weights are spread over all base models, with no dominant model; they change from nutrient to nutrient.

## Caveats
- Base models at fixed settings (not the per-fold tuned settings of E27/E29); Cubist, CatBoost and the neural network
  are not in the stack.
- Linear meta-model only; single seed.
