# E50 — Final setup: accuracy against spatial block size (10–100 km), statewide and per region

**Date:** 2026-10-14
**Notebook:** cell run on 2026-10-14 (after E49)
**Results:** `results/50_block_size_final.csv` (scope × nutrient × test: R², RMSE)
**Replaces E41 for the paper** (E41: with Raigad, without neighbourhood features).

## Setup
- Final setup as E49: 32,096 samples (Raigad excluded), 39 inputs + 4 neighbourhood features, LightGBM (E36 settings).
- Tests: random 70/30 and 5-fold `GroupKFold(shuffle=True, random_state=42)` on square blocks of 10, 25, 50, 100 km.
- Scopes: statewide model; one model per region. Samples: Vidarbha 7,236, Marathwada 9,293, North MH 9,738,
  Western MH 4,329, Konkan 1,500 (Raigad removed). Run time 0.5 min.
- The cell was **not** test-run before it was given; check passed (statewide random row = E49).

## Results — statewide, R² (RMSE)

| Test | N | P | K | OC |
|---|---|---|---|---|
| Random 70/30 | **0.706** (55.0) | **0.614** (15.08) | **0.564** (164.6) | **0.701** (0.215) |
| Spatial 10 km | 0.393 (76.7) | 0.396 (19.22) | 0.352 (200.4) | 0.578 (0.258) |
| Spatial 25 km | 0.309 (81.8) | 0.368 (19.66) | 0.269 (212.9) | 0.497 (0.282) |
| Spatial 50 km | 0.231 (86.3) | 0.335 (20.16) | 0.211 (221.1) | 0.476 (0.288) |
| Spatial 100 km | 0.224 (86.7) | 0.290 (20.83) | 0.166 (227.4) | 0.326 (0.326) |

Mean of 5 regional models, R²:

| Test | N | P | K | OC |
|---|---|---|---|---|
| Random 70/30 | 0.645 | 0.589 | 0.475 | 0.500 |
| Spatial 10 km | 0.375 | 0.334 | 0.226 | 0.318 |
| Spatial 25 km | 0.294 | 0.305 | 0.173 | 0.276 |
| Spatial 50 km | 0.222 | 0.281 | 0.120 | 0.209 |
| Spatial 100 km | 0.173 | 0.237 | 0.060 | 0.170 |

## Per region, R²

| Region | Nutrient | Random | 10 km | 25 km | 50 km | 100 km |
|---|---|---|---|---|---|---|
| Vidarbha | N | 0.709 | 0.420 | 0.306 | 0.125 | 0.113 |
| Marathwada | N | 0.650 | 0.552 | 0.534 | 0.462 | 0.377 |
| North MH | N | 0.492 | 0.376 | 0.239 | 0.158 | 0.068 |
| Western MH | N | 0.590 | 0.400 | 0.439 | 0.303 | 0.357 |
| Konkan | N | 0.783 | 0.129 | −0.046 | 0.060 | −0.048 |
| Vidarbha | P | 0.530 | 0.235 | 0.132 | 0.032 | 0.043 |
| Marathwada | P | 0.739 | 0.501 | 0.528 | 0.526 | 0.463 |
| North MH | P | 0.727 | 0.440 | 0.326 | 0.314 | 0.298 |
| Western MH | P | 0.544 | 0.408 | 0.423 | 0.388 | 0.368 |
| Konkan | P | 0.404 | 0.086 | 0.117 | 0.147 | 0.015 |
| Vidarbha | K | 0.693 | 0.482 | 0.461 | 0.455 | 0.341 |
| Marathwada | K | 0.407 | 0.307 | 0.233 | 0.203 | 0.111 |
| North MH | K | 0.610 | 0.350 | 0.243 | −0.066 | −0.123 |
| Western MH | K | 0.217 | −0.065 | −0.087 | −0.172 | −0.168 |
| Konkan | K | 0.450 | 0.059 | 0.017 | 0.180 | 0.137 |
| Vidarbha | OC | 0.434 | 0.275 | 0.217 | 0.061 | −0.091 |
| Marathwada | OC | 0.369 | 0.188 | 0.180 | 0.105 | 0.086 |
| North MH | OC | 0.539 | 0.358 | 0.280 | 0.194 | 0.207 |
| Western MH | OC | 0.751 | 0.577 | 0.562 | 0.486 | 0.437 |
| Konkan | OC | 0.404 | 0.194 | 0.144 | 0.200 | 0.211 |

## Interpretation
1. **Statewide, accuracy falls steadily with distance:** N 0.71 → 0.39 (10 km) → 0.23 (50 km); K 0.56 → 0.17 at
   100 km; OC holds best (0.70 → 0.48 at 50 km).
2. **The biggest single step is random → 10 km** (N −0.31, P −0.22, K −0.21, OC −0.12).
3. **Regions differ strongly.** Marathwada and Western MH keep useful accuracy at 50–100 km for N and P (0.30–0.53);
   Vidarbha and North MH lose most skill by 50 km; Konkan (1,500 samples without Raigad) has high random-split R²
   (N 0.78) but almost none under spatial CV — its random-split score comes entirely from nearby samples.
4. K in Western MH is below zero under every spatial test (as in all earlier experiments).

## Caveats
One seed; at 50–100 km a region has only 10–50 blocks, so single regional values can move by about ±0.05
(non-monotonic cases such as Western MH N 0.40 → 0.44 at 25 km are within that noise).
