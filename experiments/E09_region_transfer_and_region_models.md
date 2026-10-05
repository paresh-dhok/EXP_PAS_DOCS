# E09 — Region transfer and region-specific models

**Date:** 2026-10-05
**Notebook:** two cells run on 2026-10-05, after the short setup cell (load saved files)
**Results:** `results/09_region_transfer.csv` (part A), `results/09_region_models.csv` (part B)
**Data:** model table, 17,273 locations (final + terrain + composite)

## Question / hypothesis (recorded before running)
Maharashtra's regions have different soils: Konkan has acidic red laterite, while the other four regions are mostly
Deccan black soil (Vertisol). Hypotheses:
1. Models will transfer poorly to and from Konkan (negative R² likely); transfer between the four Deccan regions will be moderate.
2. A model trained only on a region will predict that region better than one statewide model, at least in Konkan.

## Regions
Administrative divisions, from `mh_candidates.parquet` (`region`). **Used only to split the data, never as a model input.**

| Region | Locations | Median N | Median P | Median K | Median OC % | Median pH |
|---|---|---|---|---|---|---|
| North MH | 5,373 | 191.8 | 17.4 | 308.9 | 0.49 | 7.70 |
| Marathwada | 3,838 | 179.0 | 11.9 | 443.8 | 0.38 | 7.89 |
| Vidarbha | 3,561 | 175.6 | 17.0 | 400.0 | 0.44 | 7.60 |
| Western MH | 2,729 | 191.9 | 21.1 | 358.4 | 0.39 | 7.60 |
| Konkan | 1,772 | **395.3** | 15.1 | 426.8 | **1.20** | **6.44** |

## Setup
- Features: the no-location set = composite 12 bands + 16 indices + 5 temporal std + pH, EC + 7 terrain (42).
- Model: `RandomForestRegressor(n_estimators=300, min_samples_leaf=3, max_features=0.33, random_state=42)` with a
  log1p/expm1 target transform. No tuning.
- Metrics computed **inside the test region**: R², RMSE, bias = mean(prediction) − mean(true).

**Part A — transfer (`09_region_transfer.csv`)**
- *Leave one region out:* train on 4 regions, predict the 5th.
- *Train on one region, test on each other region:* a 5 × 5 table. The diagonal = spatial CV (10 km blocks, 5 folds) inside the region.

**Part B — region model vs statewide model (`09_region_models.csv`)**
- *Region model:* trained and tested only inside the region (spatial CV, 10 km blocks, 5 folds).
- *Statewide model:* spatial CV on all 17,273 locations; its out-of-fold predictions are scored only on the region's locations.
- Both are scored on the same locations.

## Results — Part A

Leave one region out, R² in the unseen region:

| Test region | N | P | K | OC |
|---|---|---|---|---|
| Vidarbha | −0.069 | −0.164 | −0.069 | −0.878 |
| Marathwada | −0.647 | −0.099 | −0.280 | −1.759 |
| North MH | −0.353 | −0.157 | −0.596 | −0.178 |
| Western MH | 0.012 | −0.253 | −0.103 | −0.382 |
| Konkan | −0.828 | −0.071 | −0.499 | −1.190 |

Leave one region out, bias (prediction mean − true mean):

| Test region | N | P | K | OC |
|---|---|---|---|---|
| Vidarbha | 15.14 | −5.56 | −138.67 | 0.09 |
| Marathwada | −40.01 | 4.98 | −77.34 | 0.16 |
| North MH | −25.96 | −4.15 | 91.11 | −0.11 |
| Western MH | −12.57 | −18.91 | −67.86 | 0.16 |
| Konkan | **−286.54** | −7.31 | **−254.07** | **−0.75** |

Train on one region (rows), test on another (columns); diagonal = spatial CV inside the region. R²:

N
| train \ test | Vidarbha | Marathwada | North MH | Western MH | Konkan |
|---|---|---|---|---|---|
| Vidarbha | **0.177** | −0.407 | −0.472 | −0.093 | −1.000 |
| Marathwada | −0.088 | **0.236** | −0.219 | −0.311 | −0.706 |
| North MH | 0.022 | −0.060 | **0.082** | 0.041 | −0.700 |
| Western MH | −1.402 | −2.819 | −2.833 | **0.365** | −1.521 |
| Konkan | −3.176 | −5.662 | −8.133 | −1.666 | **0.204** |

P
| train \ test | Vidarbha | Marathwada | North MH | Western MH | Konkan |
|---|---|---|---|---|---|
| Vidarbha | **0.054** | −0.176 | −0.139 | −0.236 | −0.140 |
| Marathwada | −0.250 | **0.252** | −0.160 | −0.371 | −0.165 |
| North MH | −0.146 | −0.175 | **0.104** | −0.185 | −0.045 |
| Western MH | −0.417 | −0.161 | −0.294 | **0.240** | −0.431 |
| Konkan | −0.012 | −0.180 | −0.049 | −0.172 | **−0.001** |

K
| train \ test | Vidarbha | Marathwada | North MH | Western MH | Konkan |
|---|---|---|---|---|---|
| Vidarbha | **0.275** | −1.481 | −3.590 | −2.055 | −0.347 |
| Marathwada | −0.092 | **0.062** | −1.047 | −0.023 | −0.004 |
| North MH | −0.264 | −1.006 | **0.117** | −0.359 | −0.530 |
| Western MH | −0.118 | −0.322 | −0.268 | **−0.037** | −0.214 |
| Konkan | −0.309 | −0.831 | −0.206 | −0.197 | **0.025** |

OC
| train \ test | Vidarbha | Marathwada | North MH | Western MH | Konkan |
|---|---|---|---|---|---|
| Vidarbha | **0.150** | −3.291 | 0.087 | −0.561 | −1.415 |
| Marathwada | −0.114 | **0.052** | −0.196 | −0.039 | −1.328 |
| North MH | −0.012 | −4.326 | **0.213** | −0.901 | −0.883 |
| Western MH | −0.004 | −0.340 | −0.123 | **0.258** | −1.245 |
| Konkan | −8.028 | −35.887 | −2.975 | −8.562 | **0.134** |

## Results — Part B (same locations, spatial CV)

R²:

| Region | Model | N | P | K | OC |
|---|---|---|---|---|---|
| Vidarbha | **region** | **0.177** | **0.054** | **0.275** | **0.150** |
| | statewide | 0.158 | −0.017 | 0.090 | −0.017 |
| Marathwada | **region** | **0.236** | **0.252** | **0.062** | **0.052** |
| | statewide | −0.044 | 0.235 | −0.069 | −0.275 |
| North MH | **region** | **0.082** | **0.104** | **0.117** | **0.213** |
| | statewide | −0.002 | −0.007 | 0.075 | 0.012 |
| Western MH | **region** | **0.365** | **0.240** | **−0.037** | **0.258** |
| | statewide | 0.265 | 0.099 | −0.051 | 0.174 |
| Konkan | **region** | **0.204** | **−0.001** | **0.025** | **0.134** |
| | statewide | 0.131 | −0.027 | −0.010 | −0.044 |

RMSE:

| Region | Model | N | P | K | OC |
|---|---|---|---|---|---|
| Vidarbha | region | 87.8 | 17.95 | 292.3 | 0.242 |
| | statewide | 88.9 | 18.61 | 327.5 | 0.264 |
| Marathwada | region | 61.4 | 12.60 | 176.9 | 0.135 |
| | statewide | 71.8 | 12.74 | 188.9 | 0.157 |
| North MH | region | 60.3 | 20.81 | 134.4 | 0.311 |
| | statewide | 63.0 | 22.07 | 137.6 | 0.349 |
| Western MH | region | 96.8 | 36.19 | 233.7 | 0.249 |
| | statewide | 104.1 | 39.40 | 235.3 | 0.262 |
| Konkan | region | 281.4 | 28.87 | 358.4 | 0.636 |
| | statewide | 294.0 | 29.23 | 364.6 | 0.699 |

## Interpretation
1. **Models do not transfer to an unseen region.** Leave-one-region-out R² is negative in 19 of 20 cases. The bias shows
   the reason for Konkan: a model trained on Deccan black soils predicts Konkan N 287 kg/ha, K 254 kg/ha and OC 0.75 %
   too low. It carries black-soil levels into laterite soil.
2. **Transfer also fails between the four Deccan regions**, which was more than hypothesised (hypothesis 1 confirmed and
   exceeded). Almost every off-diagonal cell is negative. The relationship between features and nutrients differs by region,
   possibly also because of laboratory differences between regions. A Konkan-trained model is catastrophic elsewhere
   (OC −35.9 in Marathwada).
3. **Region-specific models beat the single statewide model in all 20 region × nutrient cases**, on both R² and RMSE
   (hypothesis 2 confirmed, not only in Konkan). Inside its region, the statewide model is often ≈ 0 or negative
   (e.g. Marathwada OC −0.275, Vidarbha OC −0.017), whereas region models reach up to N 0.365 (Western MH),
   P 0.252 (Marathwada), K 0.275 (Vidarbha) and OC 0.258 (Western MH).
4. **The statewide R² (N 0.409, OC 0.370) mostly comes from telling regions apart.** Inside a single region, the same
   statewide model explains little.
5. Region R² measures variation inside one region, which includes differences between its districts. It is therefore
   not comparable to the within-district R² of E04–E06.

## Caveats
- Choosing a region-specific model uses the region (a coarse location) to select the model. It is reported as a finding
  about soil zones. It must be stated clearly in the paper that the region is used to choose the model, not as a feature.
- Region sizes differ (1,772 to 5,373 locations), so Konkan models train on much less data.
- Single seed (42), no tuning.

## Use in the paper
- A transfer matrix figure (heat map of R², 5 × 5 per nutrient) showing that models are region-bound.
- A region vs statewide comparison table.
- Practical message: a soil-prediction model for Maharashtra should be built per soil zone, and should not be used in a
  zone it was not trained on.
- Vidarbha focus: K R² 0.275 with a Vidarbha-only model vs 0.090 for the statewide model on the same fields.
