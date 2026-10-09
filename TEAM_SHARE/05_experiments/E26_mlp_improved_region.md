# E26 — Improved neural network (ensemble, quantile-transformed inputs, tuned regularisation), region-wise

**Date:** 2026-10-09
**Notebook:** cell run on 2026-10-09
**Results:** `results/26_mlp_improved_region.csv`; all 13 models in `results/26_all_models_region.csv`
**Data:** model table, 17,273 locations + climate; region-wise protocol (10 km spatial CV, 5 folds, inside each region)

## Why
The first network (E25) was near or below zero for K and OC with the 41 inputs. A negative R² means worse than predicting
the regional mean, which points to instability and overfitting rather than a lack of capacity. Four changes were made,
all using training data only.

## Hypothesis (recorded before running)
The improved network is ≥ the E25 network for every nutrient, its mean R² is ≥ 0 for all four nutrients, and it stays
below Random Forest.

## Setup
| Change | E25 | E26 |
|---|---|---|
| Input scaling | `StandardScaler` | `QuantileTransformer(n_quantiles=200, output_distribution="normal")` |
| Network | (64, 32), alpha 0.01 | (32, 16), alpha tuned |
| Regularisation | fixed | alpha ∈ {0.01, 0.1, 1.0}, chosen by inner `GroupKFold(3)` on the training blocks (one network, seed 42) |
| Prediction | one network | **average of 5 networks** (seeds 42, 7, 13, 99, 2024) trained with the chosen alpha |

Unchanged: `MLPRegressor`, ReLU, learning rate 0.001, batch size 64, early stopping on a random 15 % of the training fold
(patience 20), target log1p then standardised with training-fold mean and SD, predictions clipped to the training-fold
range, outer folds `GroupKFold(5, shuffle=True, random_state=42)` (identical to E18–E25). 40 jobs in parallel; run time 191 s.

## Results — mean R² over the 5 regions (spatial 10 km)

| Input set | Model | N | P | K | OC |
|---|---|---|---|---|---|
| 41 inputs | RandomForest (E18) | **0.137** | **0.107** | **0.042** | **0.092** |
| | **MLP improved (E26)** | 0.118 | 0.092 | **0.042** | 0.069 |
| | MLP (E25) | 0.061 | 0.070 | −0.008 | 0.011 |
| | Ridge (E23) | 0.035 | 0.047 | −0.000 | 0.016 |
| 41 + elev + climate | RandomForest (E18) | **0.400** | **0.269** | **0.194** | **0.269** |
| | **MLP improved (E26)** | 0.335 | 0.178 | 0.140 | 0.176 |
| | MLP (E25) | 0.226 | 0.152 | 0.057 | 0.117 |
| | Ridge (E23) | 0.215 | 0.152 | 0.067 | 0.146 |

Improved MLP per region, 41 inputs (R²):

| Region | N | P | K | OC |
|---|---|---|---|---|
| Vidarbha | 0.169 | 0.032 | 0.261 | 0.052 |
| Marathwada | 0.093 | 0.231 | 0.016 | 0.012 |
| North MH | 0.006 | 0.024 | −0.024 | 0.103 |
| Western MH | 0.203 | 0.133 | −0.040 | 0.139 |
| Konkan | 0.121 | 0.039 | −0.003 | 0.039 |

Chosen alpha: 1.0 (the largest value offered) in the median of every input set and nutrient.

Position among all 13 models (41 inputs, mean N): Random Forest 0.137, Cubist 0.129, Extra Trees 0.125,
**MLP improved 0.118**, SVR 0.117, KNN 0.072, MLP (E25) 0.061, linear models 0.02–0.04.
The improved network beats Random Forest in 7 of the 20 region × nutrient cells (e.g. Vidarbha N +0.019, K +0.022;
Marathwada P +0.020).

## Interpretation
1. **Hypothesis confirmed.** The improved network is better than E25 for every nutrient and both input sets, its mean R²
   is positive for all four nutrients, and it stays at or below Random Forest on average (equal for K).
2. **The gain is large for a neural network:** N 0.061 → 0.118 and OC 0.011 → 0.069 with the 41 inputs; N 0.226 → 0.335
   with elevation + climate. It moves from 7th to 4th place, level with SVR and close to Extra Trees.
3. **The first network's weakness was instability and overfitting, not the method.** Averaging five networks,
   removing extreme input values and stronger regularisation account for the gain.
4. **Three cells remain slightly negative** (K in North MH, Western MH and Konkan), as for most other models.
5. Even after tuning, the neural network does not exceed the tree ensembles. The conclusion of E18–E25 stands:
   the inputs limit accuracy more than the algorithm.

## Caveats
- **The chosen alpha is at the upper edge of the grid (1.0)**, so stronger regularisation (e.g. 3 or 10) was not tested
  and might do slightly better.
- One architecture; ensemble seeds fixed; no search over learning rate or depth.
- The improved network received tuning and ensembling that the other models did not (Random Forest, Cubist, SVR and KNN
  are untuned). For a like-for-like table, the other models should be tuned in the same way, or the comparison should
  state which models were tuned.
