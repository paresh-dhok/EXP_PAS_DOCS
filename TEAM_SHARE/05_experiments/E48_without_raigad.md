# E48 — Headline model without Raigad

**Date:** 2026-10-14
**Notebook:** cell run on 2026-10-14 (after E47, reuses E42–E43 functions)
**Results:** `results/48_without_raigad.csv` (nutrient × test: R², RMSE)

## Why
E47 found that Raigad (district 491, Konkan) has a median N of 872 kg/ha, with half its samples above 850 — most likely
a district- or laboratory-level offset. This measures how much of the headline N accuracy depends on it.

The cell was **not** test-run before it was given (user's request).

## Setup
Headline setup (statewide LightGBM, 39 inputs + 4 neighbourhood features, E36 settings), all Raigad samples removed:
32,096 samples. Random 70/30 and 10 km spatial CV. Run time 0.1 min.

## Results
**Raigad: 1,781 samples (5.3 %) carry 60.9 % of the total N variance.**

| Data | Test | R² N | R² P | R² K | R² OC | RMSE N | RMSE P | RMSE K | RMSE OC |
|---|---|---|---|---|---|---|---|---|---|
| With Raigad (E42) | Random 70/30 | 0.812 | 0.606 | 0.551 | 0.712 | 68.3 | 15.41 | 174.7 | 0.224 |
| With Raigad (E42) | Spatial 10 km | 0.661 | 0.375 | 0.308 | 0.537 | 92.5 | 19.49 | 215.4 | 0.289 |
| **Without Raigad** | **Random 70/30** | **0.706** | **0.614** | **0.564** | **0.701** | 55.0 | 15.08 | 164.6 | 0.215 |
| **Without Raigad** | **Spatial 10 km** | **0.393** | **0.396** | **0.352** | **0.578** | 76.7 | 19.22 | 200.4 | 0.258 |

## Interpretation
1. **The N headline depends heavily on Raigad.** Without it, N R² falls from 0.812 to 0.706 (random) and from 0.661 to
   0.393 (spatial 10 km). A model that only learns "Raigad is high" earns a large part of the statewide N R²,
   because 5 % of the samples carry 61 % of the N variance.
2. **P, K and OC are not inflated by Raigad;** they are equal or better without it (spatial: P 0.375 → 0.396,
   K 0.308 → 0.352, OC 0.537 → 0.578).
3. **Without Raigad the validation effect is larger for N:** random → spatial costs 0.31 (vs 0.15 with Raigad).
4. RMSE for N drops from 68 to 55 kg/ha (random) because the hardest-to-fit extreme values are gone; R² falls because
   the remaining N variance is much smaller.
5. Consequence for the paper: an N R² of 0.81 must not be reported without saying that it rests on one district.

## Caveats
One seed, one split. Removing a whole district is a strong intervention; the alternative is reporting both versions.
