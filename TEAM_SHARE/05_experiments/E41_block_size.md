# E41 — Effect of the spatial block size (10, 25, 50, 100 km) on the base model

**Date:** 2026-10-14
**Notebook:** cell run on 2026-10-14 (after E39/E40, reuses their data and functions)
**Results:** `results/41_block_size.csv` (scope × nutrient × test: R², RMSE, MAE)

## Why
The paper shows how the reported accuracy depends on the validation design. A random 70/30 split tests a field whose
neighbours are in training; larger spatial blocks test fields progressively further from any training sample
(new village → new taluka → new district).

No blind hypothesis: the cell was test-run before it was given (identical numbers).

## Setup
- Data, inputs and model as E39/E40 (clustered 33,877; 39 inputs incl. longitude/latitude; LightGBM fixed settings).
- Tests: random 70/30, and 5-fold `GroupKFold(shuffle=True, random_state=42)` on square blocks of 10, 25, 50, 100 km.
- Scopes: statewide model, and one model per region (mean of 5 regions).
- Blocks statewide: 1,581 (10 km), 471 (25 km), 150 (50 km), 45 (100 km). Per region at 100 km: 10–17 blocks.

## Results — R²

| Test | Statewide: N | P | K | OC | Regions: N | P | K | OC |
|---|---|---|---|---|---|---|---|---|
| Random 70/30 | **0.774** | **0.499** | **0.465** | **0.686** | 0.614 | 0.535 | 0.448 | 0.523 |
| Spatial 10 km | 0.598 | 0.334 | 0.256 | 0.543 | 0.433 | 0.327 | 0.216 | 0.304 |
| Spatial 25 km | 0.549 | 0.287 | 0.198 | 0.477 | 0.376 | 0.262 | 0.172 | 0.274 |
| Spatial 50 km | 0.434 | 0.254 | 0.174 | 0.502 | 0.228 | 0.250 | 0.062 | 0.211 |
| Spatial 100 km | 0.442 | 0.212 | 0.114 | 0.417 | 0.241 | 0.191 | 0.056 | 0.155 |

RMSE, statewide (N / P / K / OC): random 74.8 / 17.39 / 190.7 / 0.234; 10 km 100.7 / 20.12 / 223.3 / 0.287;
25 km 106.6 / 20.82 / 231.9 / 0.308; 50 km 119.5 / 21.29 / 235.2 / 0.300; 100 km 118.7 / 21.88 / 243.6 / 0.325.

## Interpretation
1. **Accuracy falls steadily as test fields move further from training samples.** Statewide N: 0.77 (random) →
   0.60 (10 km) → 0.55 (25 km) → 0.43–0.44 (50–100 km). K loses three quarters of its R² (0.47 → 0.11).
2. The largest single step is random → 10 km (0.15–0.24): most of the random-split accuracy comes from neighbours
   within a few km.
3. Inside one region the fall is steeper (N 0.61 → 0.23 at 50 km; K 0.45 → 0.06): with large blocks a regional model
   has little left to learn from.
4. Statewide 50 km and 100 km are nearly equal (and OC is higher at 50 than at 25 km): with only 45–150 blocks the
   fold assignment adds noise of a few hundredths.


## Per region (one model per region), R²

Samples and blocks per region (10 / 25 / 50 / 100 km): Vidarbha 7,236 (430/145/51/17); Marathwada 9,293 (367/118/41/15); North MH 9,738 (373/102/38/16); Western MH 4,329 (251/82/32/13); Konkan 3,281 (175/58/24/10).

**N**

| Region | Random | 10 km | 25 km | 50 km | 100 km |
|---|---|---|---|---|---|
| Vidarbha | 0.664 | 0.375 | 0.312 | 0.156 | 0.061 |
| Marathwada | 0.643 | 0.512 | 0.501 | 0.417 | 0.424 |
| North MH | 0.475 | 0.360 | 0.289 | 0.118 | 0.097 |
| Western MH | 0.569 | 0.434 | 0.435 | 0.340 | 0.381 |
| Konkan | 0.720 | 0.484 | 0.345 | 0.110 | 0.244 |

**P**

| Region | Random | 10 km | 25 km | 50 km | 100 km |
|---|---|---|---|---|---|
| Vidarbha | 0.408 | 0.197 | 0.122 | 0.053 | 0.052 |
| Marathwada | 0.725 | 0.520 | 0.493 | 0.508 | 0.358 |
| North MH | 0.639 | 0.406 | 0.291 | 0.258 | 0.190 |
| Western MH | 0.550 | 0.407 | 0.349 | 0.301 | 0.343 |
| Konkan | 0.354 | 0.104 | 0.054 | 0.129 | 0.013 |

**K**

| Region | Random | 10 km | 25 km | 50 km | 100 km |
|---|---|---|---|---|---|
| Vidarbha | 0.691 | 0.474 | 0.479 | 0.463 | 0.379 |
| Marathwada | 0.392 | 0.242 | 0.197 | 0.120 | 0.069 |
| North MH | 0.596 | 0.395 | 0.317 | −0.030 | −0.022 |
| Western MH | 0.154 | −0.070 | −0.063 | −0.110 | −0.122 |
| Konkan | 0.409 | 0.041 | −0.068 | −0.136 | −0.022 |

**OC**

| Region | Random | 10 km | 25 km | 50 km | 100 km |
|---|---|---|---|---|---|
| Vidarbha | 0.423 | 0.201 | 0.134 | 0.033 | −0.058 |
| Marathwada | 0.367 | 0.172 | 0.174 | 0.118 | 0.068 |
| North MH | 0.524 | 0.335 | 0.241 | 0.161 | 0.155 |
| Western MH | 0.742 | 0.582 | 0.590 | 0.530 | 0.462 |
| Konkan | 0.557 | 0.232 | 0.230 | 0.216 | 0.146 |

### Per-region interpretation
1. **The fall with distance differs by region.** Vidarbha and North MH lose almost all N skill by 50 km
   (N 0.66 → 0.16 and 0.48 → 0.12); Marathwada and Western MH keep about 0.34–0.42 for N even at 50–100 km.
2. **K and OC behave regionally:** K keeps 0.38–0.46 at 50–100 km in Vidarbha but is ≤ 0 from 10 km (Western MH)
   or 25–50 km (Konkan, North MH); OC keeps 0.46–0.53 at 50–100 km in Western MH but falls to ≤ 0.03 in Vidarbha.
3. **P in Konkan and Vidarbha** is weak already at 10 km (0.10, 0.20) and near zero from 25 km.
4. With 10–17 blocks per region at 100 km, single values at 50–100 km can move by ±0.05 with another fold assignment;
   the non-monotonic cases (e.g. Konkan N 0.11 at 50 km vs 0.24 at 100 km) are within that noise.
5. These are the 39 inputs **without** neighbourhood features. A per-region block-size run with neighbourhood features
   has not been done.

## Caveats
One seed; with few large blocks, single values can move by ±0.03–0.05 with another fold assignment.
