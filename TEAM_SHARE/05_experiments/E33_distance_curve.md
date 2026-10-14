# E33 — Distance curve: R² against the distance between the test block and the training fields

**Date:** 2026-10-09
**Notebook:** cell run on 2026-10-09 (part 2 of the four-part cell)
**Results:** `results/33_distance_curve.csv`, figure `results/33_distance_curve.png`
**Data:** model table, 17,273 locations + climate; inside each region

## Why
Ploton et al. (2020, Nature Communications) separated test and training data by up to 150 km, because their target was
spatially correlated up to about 120 km, and showed R² falling from 0.50 to about zero with distance. Our protocol uses
10 km blocks while our nutrients are correlated up to 100–200 km (E19). This experiment measures how our R² depends on
that distance.

## Hypothesis
R² falls as the training fields are moved further from the test block, for all three input sets, and reaches zero or
below by about 50 km. **Not a blind hypothesis:** a preview with 10 test blocks per region was seen before the full run.

## Setup
- Test units: 10 km blocks with at least 5 locations; 100 chosen at random per region (483 in total; one region has
  fewer than 100 such blocks).
- For each test block, a model is trained on the other locations of the same region after removing every training
  location within r km of any test location, r ∈ {0, 2, 5, 10, 20, 50, 100}; r = 0 means only the block itself is left
  out. A radius is skipped for a block if fewer than 300 training locations remain.
- Radii 0–50 km are evaluated on the same blocks (those that still have training data at 50 km); 100 km on the blocks
  available at 100 km.
- Model: LightGBM, fixed settings (200 trees, learning rate 0.05, 7 leaves, min_child_samples 40, subsample 0.8,
  colsample 0.5, L2 5); target log1p standardised.
- R² per region is computed over all test locations of that region's blocks, then averaged over the 5 regions.
- "Random split": ordinary 5-fold random split inside each region, all locations.
- Input sets: 41 inputs; 41 + elev + climate; longitude + latitude only. Run time 5.5 min.

## Results — mean R² over 5 regions

41 inputs:

| Training fields excluded within | N | P | K | OC |
|---|---|---|---|---|
| random split | 0.239 | 0.178 | 0.107 | 0.173 |
| block left out | 0.144 | 0.104 | 0.037 | 0.072 |
| 2 km | 0.131 | 0.094 | 0.029 | 0.063 |
| 5 km | 0.118 | 0.085 | 0.021 | 0.050 |
| 10 km | 0.078 | 0.068 | 0.005 | 0.023 |
| 20 km | −0.018 | 0.030 | −0.028 | −0.033 |
| 50 km | −0.195 | −0.048 | −0.141 | −0.132 |
| 100 km | −0.489 | −0.214 | −0.312 | −0.362 |

41 + elev + climate:

| Training fields excluded within | N | P | K | OC |
|---|---|---|---|---|
| random split | 0.561 | 0.414 | 0.324 | 0.425 |
| block left out | 0.374 | 0.226 | 0.162 | 0.263 |
| 2 km | 0.350 | 0.192 | 0.125 | 0.213 |
| 5 km | 0.326 | 0.185 | 0.107 | 0.189 |
| 10 km | 0.251 | 0.172 | 0.067 | 0.127 |
| 20 km | 0.142 | 0.080 | 0.000 | 0.012 |
| 50 km | −0.015 | −0.045 | −0.186 | −0.142 |
| 100 km | −0.438 | −0.273 | −0.446 | −0.466 |

Longitude + latitude only:

| Training fields excluded within | N | P | K | OC |
|---|---|---|---|---|
| random split | 0.530 | 0.418 | 0.301 | 0.402 |
| block left out | 0.329 | 0.180 | 0.142 | 0.260 |
| 2 km | 0.292 | 0.169 | 0.113 | 0.227 |
| 5 km | 0.258 | 0.163 | 0.096 | 0.193 |
| 10 km | 0.198 | 0.151 | 0.065 | 0.160 |
| 20 km | 0.069 | 0.124 | 0.013 | 0.053 |
| 50 km | −0.129 | 0.053 | −0.088 | −0.079 |
| 100 km | −0.518 | −0.286 | −0.361 | −0.343 |

## Interpretation
1. **Hypothesis confirmed.** R² decreases steadily with distance for every input set and nutrient and is at or below
   zero by 20–50 km.
2. **"Block left out" reproduces our protocol:** 0.144 / 0.104 / 0.037 / 0.072 with the 41 inputs, equal to the
   LightGBM region-wise values of E29/E35. So the 10 km block protocol measures prediction for fields whose nearest
   training fields are just outside a 10 km cell.
3. **Even the 41 field-level inputs depend on nearby training data.** Their R² for N falls from 0.144 to 0.078 at 10 km
   and to zero at 20 km. Part of what was treated as field-level signal is therefore local spatial structure carried by
   pH, EC and the satellite features (see E34: these inputs locate a field better than chance).
4. **The model with elevation + climate follows the longitude + latitude model** at every distance (difference mostly
   ≤ 0.06). This is the result of Ploton et al. (full model ≈ coordinates-only model): the added variables act as
   position.
5. **Practical statement:** with these inputs, a model has predictive value only for fields within roughly 10–20 km of
   its training samples. Beyond about 20 km (41 inputs) to 50 km (with elevation + climate) it is no better than the
   mean of the test area, and at 100 km it is clearly worse.
6. **Each step of separation removes accuracy:** for N with elevation + climate, 0.561 (random) → 0.374 (block left
   out) → 0.251 (10 km) → 0.142 (20 km) → −0.015 (50 km).

## Caveats
- R² is measured against the mean of the test locations. A model trained far away can have a wrong overall level
  (offset) and still rank fields correctly; negative values mainly show this offset. The curve therefore describes
  prediction of actual values, not ranking.
- Removing training fields also reduces their number, which lowers R² by itself, especially in the smaller regions
  (Konkan, Western MH) and at 50–100 km. `median_n_train` is stored in the CSV for each radius.
- One model (LightGBM, fixed settings), one random choice of test blocks, one seed; blocks with fewer than 5 locations
  are not used as test blocks.
- Regions are 150–500 km across, so the 100 km values rest on training data from one part of the region.
