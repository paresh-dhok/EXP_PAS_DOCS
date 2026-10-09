# E28 — Low / medium / high class prediction, region-wise

**Date:** 2026-10-09
**Notebook:** cell run on 2026-10-09
**Results:** `results/28_class_prediction_region.csv` (per region × input set × model × nutrient: class shares and counts,
accuracy, balanced accuracy, macro F1, recall of each class; plus the columns `k50`, `ba50`, `skill50` added afterwards,
see "Rare classes")
**Data:** model table, 17,273 locations + climate; region-wise protocol (10 km spatial CV, 5 folds, inside each region)

## Why
E12 tested class prediction for the whole state (SVC balanced accuracy N 0.623, P 0.493, K 0.515, OC 0.524). Part of
that came from differences between regions. This experiment repeats the test under the final region-wise protocol.

## Hypothesis (recorded before running)
1. Balanced accuracy is above chance in most region × nutrient cells, but lower than the statewide E12 values.
2. Plain accuracy stays close to the majority baseline.
3. Elevation + climate raises balanced accuracy.

## Setup
- Classes from the Soil Health Card limits (below first limit = low, between = medium, at or above second = high):
  N 280 / 560 kg/ha, P 10 / 25 kg/ha, K 110 / 280 kg/ha, OC 0.5 / 0.75 %.
- Models (fixed settings, no tuning):
  - Majority: most common class of the training fold
  - Logistic regression: C 1, class_weight balanced, standardised inputs
  - KNN: 25 neighbours, distance-weighted, standardised inputs
  - SVC: RBF, C 1, class_weight balanced, standardised inputs
  - Random Forest: 300 trees, min_samples_leaf 5, max_features sqrt, class_weight balanced_subsample
- Outer folds identical to E18–E27. Input sets: **41 inputs** and **41 + elev + climate**. 200 jobs, run time 2.2 min.

## Class counts per region (low / medium / high)

| Region | N | P | K | OC |
|---|---|---|---|---|
| Vidarbha (3,561) | 3007 / 537 / **17** | 632 / 1895 / 1034 | **26** / 1087 / 2448 | 2164 / 919 / 478 |
| Marathwada (3,838) | 3394 / 444 / **0** | 1142 / 2231 / 465 | **9** / 427 / 3402 | 3170 / 635 / **33** |
| North MH (5,373) | 4638 / 734 / **1** | 196 / 4261 / 916 | 185 / 1979 / 3209 | 2744 / 1744 / 885 |
| Western MH (2,729) | 2249 / 443 / **37** | 348 / 1241 / 1140 | 114 / 752 / 1863 | 1784 / 490 / 455 |
| Konkan (1,772) | 633 / 460 / 679 | 529 / 738 / 505 | 152 / 353 / 1267 | 75 / 291 / 1406 |

N is "low" for 82–88 % of locations in four regions; K is "high" for 60–89 % in all regions.

## Results — mean over the 5 regions, as printed by the cell (all classes present counted)

Balanced accuracy:

| Model | 41 inputs: N | P | K | OC | + elev + climate: N | P | K | OC |
|---|---|---|---|---|---|---|---|---|
| Majority (chance) | 0.356 | 0.327 | 0.333 | 0.333 | 0.356 | 0.327 | 0.333 | 0.333 |
| Logistic regression | **0.511** | 0.494 | 0.467 | 0.421 | 0.579 | 0.547 | **0.527** | **0.472** |
| KNN | 0.415 | 0.407 | 0.382 | 0.357 | 0.450 | 0.467 | 0.399 | 0.380 |
| SVC | 0.506 | **0.496** | **0.469** | **0.422** | **0.595** | **0.572** | 0.511 | 0.470 |
| Random Forest | 0.465 | 0.480 | 0.420 | 0.401 | 0.560 | 0.560 | 0.464 | 0.460 |

Accuracy:

| Model | 41 inputs: N | P | K | OC | + elev + climate: N | P | K | OC |
|---|---|---|---|---|---|---|---|---|
| Majority | 0.746 | 0.546 | 0.714 | 0.678 | 0.746 | 0.546 | 0.714 | 0.678 |
| Logistic regression | 0.633 | 0.485 | 0.524 | 0.456 | 0.714 | 0.551 | 0.589 | 0.508 |
| KNN | 0.790 | 0.596 | 0.734 | 0.678 | 0.806 | 0.632 | 0.746 | 0.682 |
| SVC | 0.702 | 0.513 | 0.610 | 0.516 | 0.767 | 0.608 | 0.654 | 0.562 |
| Random Forest | **0.801** | **0.613** | 0.731 | **0.681** | **0.839** | **0.675** | **0.764** | **0.702** |

Macro F1 (41 inputs): Majority 0.323 / 0.242 / 0.277 / 0.267; SVC 0.471 / 0.460 / 0.422 / 0.398;
Random Forest 0.472 / 0.481 / 0.418 / 0.391.

SVC, 41 inputs, share of each true class found (mean over regions): N low 0.766, medium 0.513, high 0.139;
P 0.423 / 0.471 / 0.594; K 0.278 / 0.477 / 0.653; OC 0.497 / 0.379 / 0.389.

## Rare classes
Several classes have very few samples in a region (bold in the count table): high N has 0–37 samples in four regions,
low K has 9 and 26 samples in Marathwada and Vidarbha, high OC has 33 in Marathwada. The share of such a class that is
found cannot be estimated reliably, and it pulls the balanced accuracy of that cell down.

Balanced accuracy was therefore recomputed from the saved per-class recalls using **only classes with at least 50
samples** (`ba50`; `k50` = number of such classes, so chance = 1 / `k50`: 0.5 where two classes remain, 0.333 where three).

SVC, 41 inputs, `ba50` (chance in brackets):

| Region | N | P | K | OC |
|---|---|---|---|---|
| Vidarbha | 0.729 (0.5) | 0.514 (0.333) | 0.737 (0.5) | 0.444 (0.333) |
| Marathwada | 0.637 (0.5) | 0.609 (0.333) | 0.603 (0.5) | 0.522 (0.5) |
| North MH | 0.625 (0.5) | 0.420 (0.333) | 0.529 (0.333) | 0.453 (0.333) |
| Western MH | 0.672 (0.5) | 0.515 (0.333) | 0.410 (0.333) | 0.506 (0.333) |
| Konkan | 0.534 (0.333) | 0.422 (0.333) | 0.502 (0.333) | 0.347 (0.333) |

SVC, 41 + elev + climate, `ba50`:

| Region | N | P | K | OC |
|---|---|---|---|---|
| Vidarbha | 0.786 | 0.597 | 0.792 | 0.496 |
| Marathwada | 0.853 | 0.706 | 0.628 | 0.614 |
| North MH | 0.683 | 0.470 | 0.631 | 0.496 |
| Western MH | 0.684 | 0.565 | 0.385 | 0.580 |
| Konkan | 0.599 | 0.520 | 0.541 | 0.370 |

Random Forest accuracy minus Majority accuracy, 41 inputs (percentage points / 100):

| Region | N | P | K | OC |
|---|---|---|---|---|
| Vidarbha | +0.010 | +0.036 | +0.083 | −0.004 |
| Marathwada | −0.009 | +0.065 | −0.001 | −0.003 |
| North MH | −0.003 | +0.017 | +0.028 | +0.021 |
| Western MH | +0.007 | +0.207* | −0.023 | +0.006 |
| Konkan | +0.269* | +0.008 | −0.002 | −0.006 |

\* In these two cells the classes are nearly equal in size, so the majority class changes from fold to fold and the
Majority baseline scores below the largest class share (Konkan N 0.314 vs 0.38; Western MH P 0.408 vs 0.45). The true
gain over "always predict the largest class" is about +0.20 (Konkan N) and +0.16 (Western MH P).

Random Forest accuracy is above Majority in 12 of 20 cells with the 41 inputs (mean +0.035) and in 16 of 20 with
elevation + climate (mean +0.074).

## Interpretation
1. **Hypothesis 1 confirmed.** With the 41 inputs, class-balanced models (SVC, logistic regression) reach a mean
   balanced accuracy of about 0.51 (N), 0.50 (P), 0.47 (K), 0.42 (OC) against a chance level of about 0.33. Compared
   with the statewide E12 values, N, K and OC are lower (0.623 → 0.506, 0.515 → 0.469, 0.524 → 0.422); P is unchanged
   (0.493 → 0.496).
2. **Hypothesis 2 confirmed.** Random Forest accuracy exceeds the majority baseline by 0 to 7 points on average
   (N +5.5, P +6.7, K +1.7, OC +0.3), and most of the N and P gain comes from two cells (Konkan N, Western MH P).
   In the four regions where 82–88 % of locations are low in N, the model adds at most 1 point for N.
3. **Hypothesis 3 confirmed.** Elevation + climate raises SVC balanced accuracy to 0.595 / 0.572 / 0.511 / 0.470.
4. **Accuracy and balanced accuracy pull in opposite directions.** Random Forest and KNN have the highest accuracy
   because they mostly predict the common class. SVC and logistic regression find more of the less common classes
   (higher balanced accuracy) but their accuracy falls below the majority baseline (SVC N 0.702 vs 0.746).
5. **A linear classifier equals the SVC** in balanced accuracy (differences ≤ 0.005 with the 41 inputs). As in the
   regression experiments, the algorithm matters little.
6. **Weak cells:** OC in Konkan (0.347, at chance) and K in Western MH (0.410). **Strongest cells:** P in Marathwada
   (0.609 of 0.333 chance), N and K in Vidarbha as two-class problems (0.73–0.74 of 0.5 chance).

## Caveats
- No tuning; single seed.
- `ba50` and the cell's own balanced accuracy have different chance levels across cells, so their means over regions
  should be read next to the chance level, not alone.
- Class limits are the fixed SHC limits. Samples close to a limit can change class from the short-range variability
  alone (E07, E19), which caps the achievable class accuracy; that cap has not been estimated here.
- pH and EC are laboratory values, a best case for a field sensor.
