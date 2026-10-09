# E23 — Linear models, region-wise (linear regression, Ridge, Lasso, ElasticNet)

**Date:** 2026-10-09
**Notebook:** cell run on 2026-10-09 (after the short setup cell)
**Results:** `results/23_linear_models_region.csv` (R², RMSE, MAE per region × input set × model × nutrient)
**Data:** model table, 17,273 locations + climate; region-wise protocol (10 km spatial CV, 5 folds, inside each region)

## Hypothesis (recorded before running)
1. All four linear models score below Random Forest (E18, 41 inputs: N 0.137, P 0.107, K 0.042, OC 0.092).
2. Ridge, Lasso and ElasticNet are close to plain linear regression, slightly better where inputs are strongly correlated.
3. With elevation + climate added, linear models gain less than the tree models did, because a straight-line model
   cannot turn elevation and climate into a map of position.

## Setup
- Pipeline: `StandardScaler` (fitted on the training folds) + model. Target: log1p; predictions back-transformed with expm1.
- **Predictions clipped to the range of the training-fold target values**, so that a linear extrapolation on unusual inputs
  cannot produce extreme values after back-transformation.
- Tuning inside the training folds only, with an inner `GroupKFold(3)` on the training blocks:
  - Ridge: `RidgeCV`, 25 alphas from 10⁻³ to 10³
  - Lasso: `LassoCV`, 40 alphas, max_iter 5000
  - ElasticNet: `ElasticNetCV`, l1_ratio ∈ {0.2, 0.5, 0.8}, 30 alphas, max_iter 5000
- Input sets: **41 inputs** and **41 + elev + climate** (48). Seed 42.
- Run time 826 s. (scikit-learn 1.7.2 printed a deprecation warning for `n_alphas`; it does not affect results.)

## Results — mean R² over the 5 regions (spatial 10 km)

41 inputs:

| Model | N | P | K | OC |
|---|---|---|---|---|
| RandomForest (E18) | **0.137** | **0.107** | 0.042 | **0.092** |
| Cubist (E18) | 0.129 | 0.088 | **0.053** | 0.053 |
| ElasticNet | 0.036 | 0.036 | −0.012 | 0.006 |
| Ridge | 0.035 | 0.047 | −0.000 | 0.016 |
| Lasso | 0.035 | 0.035 | −0.012 | 0.007 |
| Linear | 0.023 | 0.054 | −0.016 | 0.008 |

41 + elev + climate:

| Model | N | P | K | OC |
|---|---|---|---|---|
| Cubist (E18) | **0.416** | **0.287** | 0.183 | 0.231 |
| RandomForest (E18) | 0.400 | 0.269 | **0.194** | **0.269** |
| Linear | 0.225 | 0.157 | 0.067 | 0.117 |
| Lasso | 0.218 | 0.150 | 0.060 | 0.136 |
| Ridge | 0.215 | 0.152 | 0.067 | 0.146 |
| ElasticNet | 0.209 | 0.146 | 0.064 | 0.137 |

Best linear model per region and nutrient, 41 inputs (R²):

| Region | N | P | K | OC |
|---|---|---|---|---|
| Vidarbha | 0.038 | −0.014 | **0.231** | −0.005 |
| Marathwada | 0.087 | 0.155 | −0.010 | 0.003 |
| North MH | −0.007 | −0.005 | −0.046 | 0.028 |
| Western MH | 0.101 | 0.157 | −0.046 | 0.036 |
| Konkan | −0.022 | −0.016 | −0.129 | 0.028 |

## Interpretation
1. **Hypothesis 1 confirmed.** With the 41 field inputs, linear models explain almost nothing (N ≤ 0.036, K and OC ≈ 0),
   clearly below Random Forest and Cubist. The weak relationships that exist are not linear.
2. **Hypothesis 2 confirmed.** The four linear models differ by at most about 0.02; regularisation and tuning change little.
3. **Hypothesis 3 confirmed.** Adding elevation + climate raises linear models to N ≈ 0.22, about half of what the tree
   models reach (0.40–0.42). Trees can combine these smooth variables into a detailed map of position; a linear model
   can only fit a plane.
4. One exception: **K in Vidarbha reaches 0.231 with a linear model**, almost the same as Random Forest (0.239) and Cubist
   (0.269). The K relationship there is close to linear (E-data check: strongest single correlation 0.55).
5. Ranking so far under the region-wise protocol: Random Forest ≈ Cubist > Extra Trees > SVR > KNN > linear models > single tree.

## Caveats
- Single seed; inner tuning uses 3 grouped folds.
- Clipping to the training range affects only extreme predictions; without it, individual folds can give very negative R².
