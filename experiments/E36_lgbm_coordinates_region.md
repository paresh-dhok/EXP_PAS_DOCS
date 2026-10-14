# E36 — LightGBM with and without coordinates: spatial test and random 70/30 split, region-wise

**Date:** 2026-10-09
**Notebook:** cell run on 2026-10-09
**Results:** `results/36_lgbm_coordinates_region.csv` (per region × input set × nutrient: R² spatial, R² random 70/30)
**Data:** model table, 17,273 locations + climate; models trained and tested inside each region

## Question
What do longitude and latitude add to the input sets, and what do they reach on their own, under both the spatial test
and a random 70/30 split? This gives the coordinates-only baseline for the paper.

No blind hypothesis: the cell was test-run before it was given, and the numbers below are identical to that test run.
Expectation from E16 and E33: coordinates alone are at least as good as the 48 inputs.

## Setup
- Model: LightGBM, fixed settings (400 trees, learning rate 0.05, 15 leaves, min_child_samples 20, subsample 0.8,
  L2 5; colsample_bytree 0.5, or 1.0 for the two-input coordinate set). Target log1p standardised.
- Spatial test: `GroupKFold(5, shuffle=True, random_state=42)` on 10 km blocks, R² over all out-of-fold predictions.
- Random test: one 70/30 split inside each region (`train_test_split(test_size=0.30, random_state=42)`).
- Input sets: 41 inputs; 41 + lon/lat; 48 inputs (41 + elev + climate); 48 + lon/lat; lon/lat only. Run time 0.4 min.

## Results — mean R² over the 5 regions

| Inputs | Spatial: N | P | K | OC | Random 70/30: N | P | K | OC |
|---|---|---|---|---|---|---|---|---|
| 41 inputs | 0.139 | 0.115 | 0.019 | 0.068 | 0.247 | 0.159 | 0.142 | 0.178 |
| 41 + lon/lat | 0.431 | 0.291 | 0.206 | 0.296 | 0.570 | 0.421 | 0.361 | 0.440 |
| 48 inputs | 0.394 | 0.257 | 0.167 | 0.248 | 0.574 | 0.424 | 0.389 | 0.437 |
| 48 + lon/lat | 0.447 | 0.302 | 0.221 | 0.309 | 0.611 | 0.469 | 0.410 | 0.468 |
| **lon/lat only** | **0.464** | **0.314** | **0.221** | **0.321** | **0.655** | **0.538** | **0.436** | **0.496** |

Per region, 48 inputs:

| Region | Spatial: N | P | K | OC | Random 70/30: N | P | K | OC |
|---|---|---|---|---|---|---|---|---|
| Vidarbha | 0.311 | 0.157 | 0.437 | 0.246 | 0.626 | 0.321 | 0.648 | 0.400 |
| Marathwada | 0.460 | 0.521 | 0.169 | 0.086 | 0.553 | 0.671 | 0.303 | 0.088 |
| North MH | 0.336 | 0.241 | 0.236 | 0.286 | 0.480 | 0.480 | 0.500 | 0.484 |
| Western MH | 0.426 | 0.332 | −0.036 | 0.439 | 0.585 | 0.374 | 0.110 | 0.665 |
| Konkan | 0.436 | 0.035 | 0.029 | 0.181 | 0.626 | 0.271 | 0.386 | 0.548 |

Per region, 48 + lon/lat:

| Region | Spatial: N | P | K | OC | Random 70/30: N | P | K | OC |
|---|---|---|---|---|---|---|---|---|
| Vidarbha | 0.347 | 0.196 | 0.484 | 0.291 | 0.656 | 0.374 | 0.673 | 0.433 |
| Marathwada | 0.501 | 0.512 | 0.233 | 0.098 | 0.571 | 0.724 | 0.312 | 0.093 |
| North MH | 0.389 | 0.347 | 0.318 | 0.346 | 0.527 | 0.529 | 0.560 | 0.527 |
| Western MH | 0.488 | 0.411 | −0.019 | 0.568 | 0.608 | 0.441 | 0.109 | 0.701 |
| Konkan | 0.508 | 0.047 | 0.086 | 0.242 | 0.692 | 0.279 | 0.397 | 0.588 |

Per region, lon/lat only:

| Region | Spatial: N | P | K | OC | Random 70/30: N | P | K | OC |
|---|---|---|---|---|---|---|---|---|
| Vidarbha | 0.353 | 0.195 | 0.489 | 0.356 | 0.726 | 0.534 | 0.723 | 0.496 |
| Marathwada | 0.562 | 0.507 | 0.261 | 0.093 | 0.596 | 0.746 | 0.312 | 0.126 |
| North MH | 0.367 | 0.366 | 0.329 | 0.356 | 0.543 | 0.585 | 0.593 | 0.525 |
| Western MH | 0.509 | 0.419 | −0.019 | 0.548 | 0.634 | 0.505 | 0.125 | 0.708 |
| Konkan | 0.530 | 0.086 | 0.046 | 0.253 | 0.778 | 0.317 | 0.426 | 0.623 |

## Interpretation
1. **Longitude and latitude alone are the best input set in both tests and for every nutrient** (mean of regions):
   spatial 0.464 / 0.314 / 0.221 / 0.321, random 0.655 / 0.538 / 0.436 / 0.496.
2. **Adding the 48 inputs to the coordinates lowers the score** (spatial N 0.464 → 0.447; random N 0.655 → 0.611).
   The 48 inputs contain no information that improves on position within a region.
3. **The 48 inputs without coordinates reach about 80–90 % of the coordinates-only score** (spatial N 0.394 vs 0.464;
   random 0.574 vs 0.655), which is consistent with elevation + climate acting as position (E16, E34).
4. **41 inputs + lon/lat ≈ 48 inputs + lon/lat** (spatial N 0.431 vs 0.447): once coordinates are present, elevation and
   climate add little.
5. **Random 70/30 is 0.15–0.25 above the spatial test** for every set that carries position
   (48 inputs N 0.394 → 0.574; lon/lat only 0.464 → 0.655).
6. **Region values vary widely.** Highest with the 48 inputs and the random split: K 0.648 and N 0.626 in Vidarbha,
   P 0.671 in Marathwada, OC 0.665 in Western MH. Lowest: OC 0.088 in Marathwada, K 0.110 in Western MH.
   K in Western MH is at or below zero in the spatial test for every input set.
7. The coordinates-only values here are higher than in E33 (0.329 for N) because this LightGBM configuration uses all
   inputs per tree for the two-input set and larger trees; they agree with the Random Forest value of E16 (0.486).

## Caveats
- One 70/30 split and one seed; single-region random-split values can move by a few hundredths with another split.
- Fixed LightGBM settings, not tuned per input set.
- A coordinates-only model cannot be used outside the area covered by training samples (E33: no skill beyond 20–50 km).
