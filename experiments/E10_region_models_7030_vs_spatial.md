# E10 — Region models: random 70/30 split vs spatial CV

**Date:** 2026-10-05
**Notebook:** cell run on 2026-10-05, after the E09 cells
**Results:** `results/10_region_models_7030_vs_spatial.csv`
**Data:** model table, 17,273 locations; region from `mh_candidates.parquet` (used only to split the data)

## Hypothesis (recorded before running)
Inside each region, a random 70/30 split gives clearly higher test R² than spatial CV, because nearby, similar fields fall
into both training and test. Training R² is much higher still. The inflation is expected to be largest where samples are
most densely packed.

## Setup
- For each of the 5 regions: `train_test_split(test_size=0.3, random_state=42)` on that region's locations only.
- Model and features identical to E09: `RandomForestRegressor(n_estimators=300, min_samples_leaf=3, max_features=0.33,
  random_state=42)` with a log1p/expm1 target transform, 42 no-location features (composite + pH/EC + terrain).
- Reported: training R², random 70/30 test R², and the spatial CV R² of the same region model (read from
  `results/09_region_models.csv`).
- **Inflation** = random 70/30 test R² − spatial CV R².

## Results (R²)

Spatial CV (from E09):

| Region | N | P | K | OC |
|---|---|---|---|---|
| Vidarbha | 0.177 | 0.054 | 0.275 | 0.150 |
| Marathwada | 0.236 | 0.252 | 0.062 | 0.052 |
| North MH | 0.082 | 0.104 | 0.117 | 0.213 |
| Western MH | 0.365 | 0.240 | −0.037 | 0.258 |
| Konkan | 0.204 | −0.001 | 0.025 | 0.134 |

Random 70/30, test:

| Region | N | P | K | OC |
|---|---|---|---|---|
| Vidarbha | 0.324 | 0.137 | 0.438 | 0.259 |
| Marathwada | 0.340 | 0.242 | 0.149 | 0.053 |
| North MH | 0.219 | 0.229 | 0.262 | 0.320 |
| Western MH | 0.454 | 0.279 | 0.054 | 0.458 |
| Konkan | 0.321 | 0.100 | 0.197 | 0.292 |

Random 70/30, training:

| Region | N | P | K | OC |
|---|---|---|---|---|
| Vidarbha | 0.765 | 0.606 | 0.791 | 0.769 |
| Marathwada | 0.809 | 0.641 | 0.732 | 0.743 |
| North MH | 0.742 | 0.635 | 0.720 | 0.760 |
| Western MH | 0.800 | 0.707 | 0.637 | 0.777 |
| Konkan | 0.805 | 0.535 | 0.671 | 0.792 |

Inflation (random test − spatial CV):

| Region | N | P | K | OC |
|---|---|---|---|---|
| Vidarbha | 0.147 | 0.083 | 0.163 | 0.109 |
| Marathwada | 0.105 | −0.010 | 0.087 | 0.001 |
| North MH | 0.137 | 0.124 | 0.145 | 0.107 |
| Western MH | 0.089 | 0.039 | 0.092 | 0.200 |
| Konkan | 0.117 | 0.102 | 0.173 | 0.158 |

## Interpretation
1. **The random split inflates scores inside regions too.** Inflation is positive in 18 of 20 cases, typically +0.09 to
   +0.20 R². The two exceptions are Marathwada P (−0.010) and OC (+0.001), where the two methods agree.
2. **Training R² (0.54–0.81) is far above both test scores**, so the models fit noise in the training data.
3. With a random split, region models would appear to reach N 0.45, OC 0.46 (Western MH) and K 0.44 (Vidarbha).
   These numbers are not honest estimates for new locations. The spatial CV values are the ones to report.
4. Same pattern as E08 (statewide): the evaluation design changes the result as much as the choice of model or features.
5. The density part of the hypothesis was **not tested**: sample density per region was not computed.

## Caveats
- The random split is a single 70/30 split (one test set per region), whereas spatial CV is 5-fold with pooled
  out-of-fold predictions. Part of the difference may be split-to-split variation, especially for Konkan (1,772 locations).
- Single seed (42), no tuning.

## Use in the paper
Together with E08: the inflation from random splitting is present both statewide and within every region,
so all reported results use spatial CV.
