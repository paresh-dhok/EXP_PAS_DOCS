# E56 — Headline model repeated with five seeds

**Date:** 2026-10-14
**Notebook:** cell run on 2026-10-14 (after E55)
**Results:** `results/56_headline_seeds.csv` (seed × nutrient × test: R², RMSE)

## Why
Reviewer question: "single split, single seed". Each seed changes the random 70/30 split, the assignment of 10 km
blocks to spatial-CV folds, and the model seed.

## Setup
Final setup (32,096 samples, Raigad excluded; statewide LightGBM, E36 settings; 39 inputs + 4 neighbourhood features).
Seeds 42, 7, 13, 99, 2024. Run time 0.3 min. Check passed: seed 42 equals E49.

## Results — mean ± SD over 5 seeds (min–max)

| Test | N | P | K | OC |
|---|---|---|---|---|
| R², random 70/30 | **0.705 ± 0.006** (0.698–0.715) | **0.620 ± 0.006** (0.614–0.629) | **0.573 ± 0.010** (0.561–0.582) | **0.702 ± 0.010** (0.688–0.713) |
| R², spatial 10 km | **0.390 ± 0.031** (0.340–0.424) | **0.393 ± 0.008** (0.382–0.404) | **0.343 ± 0.015** (0.320–0.360) | **0.562 ± 0.015** (0.543–0.578) |
| RMSE, random 70/30 | 54.0 ± 0.8 | 15.17 ± 0.50 | 163.5 ± 2.3 | 0.213 ± 0.006 |
| RMSE, spatial 10 km | 76.8 ± 1.9 | 19.26 ± 0.13 | 201.8 ± 2.3 | 0.263 ± 0.004 |

## Interpretation
1. The headline is stable: SD ≤ 0.010 for the random split, 0.008–0.031 for spatial CV.
2. Spatial CV varies more than the random split (N SD 0.031): which blocks end up together in a fold matters.
3. The gap between random and spatial (N 0.32, P 0.23, K 0.23, OC 0.14 in the means) is 10–40 times the seed SD,
   so the validation effect is not a seed artefact.
4. For the paper, quote the 5-seed means ± SD as the headline.
