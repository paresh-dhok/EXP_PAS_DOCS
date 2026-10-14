# E37 — Position-only baselines (nearest samples, kriging), hybrids, and the contribution of each input group

**Date:** 2026-10-09
**Notebook:** cell run on 2026-10-09
**Results:** `results/37_baselines_and_input_groups.csv` (per region × nutrient × method: R² spatial, R² random 70/30)
**Data:** model table, 17,273 locations + climate; everything trained and tested inside each region

## Why
A reviewer of a mapping paper will ask (a) what each group of inputs contributes and (b) whether the model is better
than simply interpolating nearby soil samples. This experiment answers both.

No blind hypothesis: the cell was test-run before it was given (identical numbers). Expectation from E16, E33, E36:
interpolation from nearby samples would be at least as good as the models.

## Setup
- Tests: spatial (`GroupKFold(5, shuffle=True, random_state=42)` on 10 km blocks) and one random 70/30 split.
- Model for all input sets: LightGBM, fixed settings as in E36. Target log1p standardised; predictions clipped to the
  training range.
- **Input-group table:** inputs added step by step (satellite → + terrain → + pH, EC → + elevation + climate →
  + coordinates), and each group alone.
- **Position-only baselines** (use only the positions and values of the training samples):
  - Nearest 25 samples: inverse-distance-weighted mean of the 25 nearest training locations.
  - Ordinary kriging: exponential variogram (nugget, sill, range) fitted to the training data of each fold
    (up to 1,500 locations, lags to 60 km), prediction from the 32 nearest training locations.
- **Combinations:**
  - Regression kriging: LightGBM on the 48 inputs + kriging of its residuals (residuals from an inner 5-fold CV).
  - Hybrid: the kriged value is given to LightGBM as one more input (for training rows it is computed from the other
    inner folds), together with pH + EC, the 41 inputs, or the 48 inputs.
- Run time 1.2 min.

## Results — mean R² over the 5 regions

Table A, contribution of the input groups:

| Inputs | Spatial: N | P | K | OC | Random 70/30: N | P | K | OC |
|---|---|---|---|---|---|---|---|---|
| Satellite (33) | 0.036 | 0.013 | −0.024 | −0.045 | 0.068 | 0.033 | 0.051 | 0.028 |
| + terrain (39) | 0.068 | 0.033 | −0.020 | −0.021 | 0.139 | 0.068 | 0.073 | 0.066 |
| + pH, EC (41) | 0.142 | 0.112 | 0.021 | 0.066 | 0.251 | 0.162 | 0.135 | 0.174 |
| + elevation + climate (48) | 0.389 | 0.262 | 0.166 | 0.242 | 0.573 | 0.428 | 0.380 | 0.441 |
| + coordinates (50) | 0.448 | 0.301 | 0.221 | 0.309 | 0.607 | 0.470 | 0.413 | 0.471 |
| Alone: terrain (6) | −0.057 | −0.060 | −0.129 | −0.072 | 0.012 | −0.022 | −0.071 | −0.015 |
| Alone: pH, EC (2) | 0.130 | 0.098 | −0.012 | 0.077 | 0.208 | 0.118 | 0.068 | 0.147 |
| Alone: elevation + climate (7) | 0.373 | 0.286 | 0.183 | 0.254 | 0.626 | 0.536 | 0.417 | 0.479 |
| Alone: coordinates (2) | 0.464 | 0.314 | 0.221 | 0.321 | 0.655 | 0.538 | 0.436 | 0.496 |

Table B, models against position-only baselines:

| Method | Spatial: N | P | K | OC | Random 70/30: N | P | K | OC |
|---|---|---|---|---|---|---|---|---|
| **Ordinary kriging** | **0.507** | 0.369 | **0.271** | **0.349** | **0.677** | 0.571 | **0.468** | **0.517** |
| Nearest 25 samples | 0.493 | **0.373** | 0.263 | 0.340 | 0.667 | **0.587** | 0.463 | 0.511 |
| Coordinates only, LightGBM | 0.464 | 0.314 | 0.221 | 0.321 | 0.655 | 0.538 | 0.436 | 0.496 |
| 48 inputs | 0.389 | 0.262 | 0.166 | 0.242 | 0.573 | 0.428 | 0.380 | 0.441 |
| 50 inputs (48 + coordinates) | 0.448 | 0.301 | 0.221 | 0.309 | 0.607 | 0.470 | 0.413 | 0.471 |
| 48 inputs + kriging of residuals | 0.353 | 0.255 | 0.131 | 0.241 | 0.617 | 0.528 | 0.425 | 0.468 |
| Hybrid: kriged value + pH, EC | 0.460 | 0.315 | 0.201 | 0.289 | 0.656 | 0.543 | 0.446 | 0.496 |
| Hybrid: kriged value + 41 inputs | 0.459 | 0.315 | 0.204 | 0.299 | 0.638 | 0.498 | 0.431 | 0.494 |
| Hybrid: kriged value + 48 inputs | 0.476 | 0.332 | 0.222 | 0.310 | 0.642 | 0.525 | 0.447 | 0.497 |

Ordinary kriging per region:

| Region | Spatial: N | P | K | OC | Random 70/30: N | P | K | OC |
|---|---|---|---|---|---|---|---|---|
| Vidarbha | 0.377 | 0.299 | 0.504 | 0.405 | 0.746 | 0.669 | 0.722 | 0.537 |
| Marathwada | 0.576 | 0.550 | 0.263 | 0.131 | 0.602 | 0.719 | 0.334 | 0.139 |
| North MH | 0.417 | 0.445 | 0.348 | 0.390 | 0.576 | 0.615 | 0.622 | 0.534 |
| Western MH | 0.551 | 0.447 | 0.023 | 0.584 | 0.667 | 0.525 | 0.169 | 0.737 |
| Konkan | 0.610 | 0.105 | 0.218 | 0.238 | 0.797 | 0.327 | 0.491 | 0.637 |

## Additional check (script only, not a notebook cell): fewer training samples
To see whether the 48-input model overtakes kriging when samples are sparse, the training part of the random 70/30
split was thinned to 50 %, 20 %, 10 %, 5 % and 2 % (3 random draws each; mean of regions). N, kriging / 48-input model:
100 % 0.676 / 0.574; 50 % 0.649 / 0.515; 20 % 0.578 / 0.425; 10 % 0.522 / 0.327; 5 % 0.420 / 0.246; 2 % 0.246 / 0.118.
Kriging stays ahead at every density and for every nutrient (difference 0.03–0.26). Median distance from a test field
to its nearest training field: 0.19 km at 100 %, 1.6 km at 10 %, 10.8 km at 2 %.

## Interpretation
1. **Interpolation from nearby soil samples is the best method in both tests.** Ordinary kriging and the 25-nearest
   baseline, which use no satellite, terrain, climate or pH/EC data, exceed every LightGBM model: N 0.507 (kriging)
   vs 0.448 (50 inputs) in the spatial test, 0.677 vs 0.607 with the random split.
2. **No combination with our inputs improves on kriging.** Regression kriging and the hybrids are all below plain
   kriging (best hybrid N 0.476 spatial, 0.642 random). Thinning the samples does not change this.
3. **Contribution of the input groups (spatial, N):** satellite 0.04 → + terrain 0.07 → + pH, EC 0.14 →
   + elevation + climate 0.39 → + coordinates 0.45. The 33 Sentinel-2 features alone explain 0–4 % of the variation;
   pH and EC add about 0.07; the large steps come from elevation + climate and coordinates, i.e. from position.
4. **Elevation + climate alone (7 inputs) are as good as or better than all 48 inputs** (spatial N 0.373 vs 0.389;
   random 0.626 vs 0.573), and coordinates alone are better than the 50 inputs.
5. Consistent with E16, E33, E34 and E36: within a region the predictable part of N, P, K and OC is spatial, and the
   most direct way to use it is to interpolate measured samples.

## Decision (2026-10-09)
Paresh decided to keep the paper on machine-learning models and not to present kriging as a compared method.
The numbers stay documented here in case a reviewer asks for the baseline.

## Caveats
- One seed, one 70/30 split; kriging with a single exponential variogram per fold and 32 neighbours, not optimised.
- LightGBM at fixed settings; tuned models (E27, E29) are about 0.01–0.04 higher for the 48 inputs (Cubist N 0.425),
  still below kriging.
- Kriging needs measured samples near the target field; like the models, it has no skill far from the samples (E33).
