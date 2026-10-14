# E43 — Neighbourhood context inside each region

**Date:** 2026-10-14
**Notebook:** cell run on 2026-10-14 (after E42, reuses its functions)
**Results:** `results/43_neighbourhood_region.csv` (region × nutrient × inputs × test: R², RMSE)

## Why
E42 tested neighbourhood context with one statewide model. This repeats it with one model per region, as a
robustness check of the headline.

No blind hypothesis: the cell was test-run before it was given (identical numbers). The first test run had a bug
(the inputs label did not switch the neighbourhood features on); it was fixed before the cell was given.

## Setup
As E42 (clustered 33,877; 39 inputs; 4 neighbourhood features from the 10 nearest training samples; LightGBM fixed
settings), but trained and tested inside each of the 5 regions. Tests: random 70/30 and 10 km spatial CV.

## Results — mean of 5 regions

| Inputs | Test | R² N | R² P | R² K | R² OC | RMSE N | RMSE P | RMSE K | RMSE OC |
|---|---|---|---|---|---|---|---|---|---|
| 39 inputs | Random 70/30 | 0.614 | 0.535 | 0.448 | 0.523 | 79.4 | 17.14 | 186.1 | 0.228 |
| 39 inputs | Spatial 10 km | 0.433 | 0.327 | 0.216 | 0.304 | 99.2 | 20.28 | 225.1 | 0.290 |
| 39 + neighbourhood | Random 70/30 | **0.636** | **0.585** | **0.484** | **0.531** | 76.9 | 16.37 | 179.5 | 0.226 |
| 39 + neighbourhood | Spatial 10 km | 0.456 | 0.341 | 0.245 | 0.305 | 96.5 | 20.09 | 219.8 | 0.295 |

Per region, 39 + neighbourhood:

| Region | Random: N | P | K | OC | Spatial 10 km: N | P | K | OC |
|---|---|---|---|---|---|---|---|---|
| Vidarbha | 0.709 | 0.530 | 0.693 | 0.434 | 0.420 | 0.235 | 0.482 | 0.275 |
| Marathwada | 0.650 | 0.739 | 0.407 | 0.369 | 0.552 | 0.501 | 0.307 | 0.188 |
| North MH | 0.492 | 0.727 | 0.610 | 0.539 | 0.376 | 0.440 | 0.350 | 0.358 |
| Western MH | 0.590 | 0.544 | 0.217 | 0.751 | 0.400 | 0.408 | −0.065 | 0.577 |
| Konkan | 0.739 | 0.387 | 0.493 | 0.562 | 0.533 | 0.121 | 0.153 | 0.127 |

## Interpretation
1. Neighbourhood context helps inside regions too, but less than statewide (random: +0.01 to +0.05, vs +0.03 to +0.11
   in E42).
2. Region-wise models stay below the statewide model (random N 0.636 vs 0.812; OC 0.531 vs 0.712): the statewide model
   also learns the differences between regions. The statewide model remains the headline.
3. Random 70/30 → spatial 10 km costs 0.18–0.23 for N, P (except Marathwada), K and OC, the same pattern as statewide.
4. Best single cells (random): OC 0.751 in Western MH, P 0.739 in Marathwada, N 0.739 in Konkan, K 0.693 in Vidarbha.
   K in Western MH stays below zero under spatial CV, as in every earlier experiment.

## Caveats
One seed, one split; k = 10 neighbours chosen by us.
