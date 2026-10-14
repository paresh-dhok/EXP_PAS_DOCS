# E35 — Repeat runs with five seeds (error bars)

**Date:** 2026-10-09
**Notebook:** cell run on 2026-10-09 (part 4 of the four-part cell)
**Results:** `results/35_seed_repeats.csv` (R² per seed × region × input set × nutrient)
**Data:** model table, 17,273 locations + climate; region-wise protocol (10 km spatial CV, 5 folds, inside each region)

## Why
All earlier experiments used seed 42 only. This run measures how much the results change when the assignment of blocks
to folds and the model's random seed change.

## Hypothesis
Across seeds the mean R² over regions changes by about 0.01. **Not a blind hypothesis:** seen in a preview run.

## Setup
- Seeds 42, 7, 13, 99, 2024. The seed sets both `GroupKFold(5, shuffle=True, random_state=seed)` and the model seed.
- Model: LightGBM, fixed settings (200 trees, learning rate 0.05, 7 leaves, min_child_samples 40, subsample 0.8,
  colsample 0.5, L2 5); target log1p standardised.
- Input sets: 41 inputs and 41 + elev + climate. 200 jobs.

## Results — mean R² over the 5 regions, across 5 seeds

| Input set | Nutrient | Mean | SD | Min | Max |
|---|---|---|---|---|---|
| 41 inputs | N | 0.140 | 0.006 | 0.133 | 0.146 |
| | P | 0.113 | 0.003 | 0.110 | 0.116 |
| | K | 0.041 | 0.003 | 0.036 | 0.044 |
| | OC | 0.076 | 0.011 | 0.056 | 0.084 |
| 41 + elev + climate | N | 0.383 | 0.003 | 0.380 | 0.387 |
| | P | 0.249 | 0.011 | 0.235 | 0.264 |
| | K | 0.172 | 0.005 | 0.168 | 0.179 |
| | OC | 0.250 | 0.012 | 0.239 | 0.265 |

Average SD of a single region × nutrient cell across seeds: 0.013 (41 inputs), 0.015 (41 + elev + climate).

## Interpretation
1. **Hypothesis confirmed.** The mean over regions is stable: SD 0.003–0.012. The main conclusions (R² of about
   0.04–0.14 with the 41 inputs, about 0.17–0.38 with elevation + climate) do not depend on the seed.
2. **Differences between the best models are within this noise.** In E29 the top seven models differ by ≤ 0.027 for N
   and the four boosting models by ≤ 0.005; with an SD of about 0.006 for the mean and 0.013 for a single cell, these
   models cannot be ranked. Only the large gaps are real (ensembles and boosting vs linear models; with vs without
   elevation + climate).
3. Single region × nutrient cells should be quoted with about ±0.03 (two SD).

## Caveats
- One model type with fixed settings; the seed-to-seed variation of other models (especially the neural network) may be
  larger.
- Five seeds give a rough SD, not a confidence interval. The variation between regions is much larger than the
  variation between seeds and is not described by these numbers.
