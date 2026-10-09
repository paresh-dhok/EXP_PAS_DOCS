# E25 — Neural network (MLP), region-wise, and the full 12-model comparison

**Date:** 2026-10-09
**Notebook:** cell run on 2026-10-09
**Results:** `results/25_mlp_region.csv` (MLP), `results/25_all_models_region.csv` (all 12 models from E18, E23, E24, E25)
**Data:** model table, 17,273 locations + climate; region-wise protocol (10 km spatial CV, 5 folds, inside each region)

## Hypothesis (recorded before running)
The neural network lands between the linear models and Random Forest: it can learn non-linear relationships, but on
small tabular data (about 2,000–5,000 locations per region) it stays below tree ensembles. With elevation + climate it
gains more than the linear models did, but stays below the trees.

## Setup
- `MLPRegressor(hidden_layer_sizes=(64, 32), activation="relu", alpha=0.01, learning_rate_init=0.001, batch_size=64,
  max_iter=500, early_stopping=True, validation_fraction=0.15, n_iter_no_change=20, random_state=42)`.
- Inputs standardised inside each fold; target log1p then standardised (`TransformedTargetRegressor`); predictions
  back-transformed and clipped to the range of the training-fold target values (as in E23, E24).
- Early stopping uses a random 15 % of the training fold (never the test fold). No hyperparameter search.
- Input sets: **41 inputs** and **41 + elev + climate** (48). Run time 146 s; median 38 epochs before stopping.

## Results — all 12 models, mean R² over the 5 regions (spatial 10 km)

41 inputs:

| Rank | Model | N | P | K | OC | Source |
|---|---|---|---|---|---|---|
| 1 | **Random Forest** | **0.137** | **0.107** | 0.042 | **0.092** | E18 |
| 2 | Cubist | 0.129 | 0.088 | **0.053** | 0.053 | E18 |
| 3 | Extra Trees | 0.125 | 0.077 | 0.036 | 0.079 | E18 |
| 4 | SVR | 0.117 | 0.070 | 0.022 | 0.022 | E18 |
| 5 | KNN | 0.072 | 0.036 | 0.015 | 0.019 | E18 |
| 6 | **MLP** | 0.061 | 0.070 | −0.008 | 0.011 | E25 |
| 7 | ElasticNet | 0.036 | 0.036 | −0.012 | 0.006 | E23 |
| 8 | Ridge | 0.035 | 0.047 | −0.000 | 0.016 | E23 |
| 9 | Lasso | 0.035 | 0.035 | −0.012 | 0.007 | E23 |
| 10 | PLSR | 0.027 | 0.044 | −0.006 | 0.011 | E24 |
| 11 | Linear regression | 0.023 | 0.054 | −0.016 | 0.008 | E23 |
| 12 | Decision tree | −0.054 | 0.042 | −0.142 | −0.077 | E18 |

41 + elev + climate:

| Rank | Model | N | P | K | OC |
|---|---|---|---|---|---|
| 1 | **Cubist** | **0.416** | **0.287** | 0.183 | 0.231 |
| 2 | **Random Forest** | 0.400 | 0.269 | **0.194** | **0.269** |
| 3 | Extra Trees | 0.391 | 0.249 | 0.180 | 0.250 |
| 4 | SVR | 0.285 | 0.155 | 0.089 | 0.122 |
| 5 | Decision tree | 0.248 | 0.164 | 0.023 | 0.096 |
| 6 | **MLP** | 0.226 | 0.152 | 0.057 | 0.117 |
| 7 | Linear regression | 0.225 | 0.157 | 0.067 | 0.117 |
| 8 | KNN | 0.224 | 0.123 | 0.070 | 0.093 |
| 9 | Lasso | 0.218 | 0.150 | 0.060 | 0.136 |
| 10 | Ridge | 0.215 | 0.152 | 0.067 | 0.146 |
| 11 | ElasticNet | 0.209 | 0.146 | 0.064 | 0.137 |
| 12 | PLSR | 0.162 | 0.124 | 0.070 | 0.100 |

MLP per region, 41 inputs (R²):

| Region | N | P | K | OC |
|---|---|---|---|---|
| Vidarbha | 0.075 | 0.006 | **0.220** | −0.020 |
| Marathwada | 0.094 | 0.175 | −0.020 | −0.005 |
| North MH | −0.039 | 0.019 | −0.047 | 0.060 |
| Western MH | 0.140 | 0.129 | −0.089 | 0.074 |
| Konkan | 0.034 | 0.020 | −0.106 | −0.052 |

## Interpretation
1. **First part of the hypothesis confirmed for N and P only.** With the 41 inputs the MLP (N 0.061, P 0.070) is above
   the linear models (N ≈ 0.035) and below Random Forest (0.137, 0.107). For K and OC it is at the level of the linear
   models (≈ 0).
2. **Second part not confirmed.** With elevation + climate the MLP (N 0.226) gains no more than linear regression
   (0.225) and stays far below the tree ensembles (0.39–0.42). This small network does not form the detailed
   position map that trees build from elevation and climate.
3. **Overall ranking under the region-wise protocol** (12 models): tree ensembles and Cubist > SVR > KNN ≈ MLP >
   linear models and PLSR > single decision tree. The ranking of the top three is the same for both input sets.
4. **The algorithm matters less than the inputs.** Across all 12 models with the 41 inputs, mean N ranges from −0.05 to
   0.14. Adding elevation + climate moves the best models to about 0.40.
5. P and K remain ≤ 0.11 and ≤ 0.05 for every model with the 41 inputs.

## Caveats
- One network architecture and one seed; no hyperparameter search. Neural networks are sensitive to initialisation,
  so individual cells may shift by a few hundredths.
- The boosting family (XGBoost, LightGBM, CatBoost) and stacking are not yet run under this protocol
  (a preliminary statewide XGBoost run was slightly above Random Forest).
