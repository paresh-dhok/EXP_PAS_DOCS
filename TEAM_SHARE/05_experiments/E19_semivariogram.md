# E19 — Semivariogram: how soil similarity changes with distance

**Date:** 2026-10-05
**Notebook:** cell run on 2026-10-05
**Results:** `results/19_semivariogram.csv`, figure `results/19_semivariogram.png`
**Data:** model table, 17,273 de-clustered locations; same-spot (nugget) value from E07 (`results/06_noise_ceiling.csv`)

## Question (recorded before running)
The guide asked about the variance between nearby and distant patches. How similar are fields as a function of the distance
between them? Over what distance does the similarity extend (the range), how large is the same-spot disagreement
(the nugget), and how does our 10 km block size compare with the range? This is needed to justify spatial
cross-validation to reviewers.

## Method
- Values: log1p of N, P, K, OC (the scale used by the models).
- Semivariance of a pair = ½ (difference)². Mean semivariance per distance class, divided by the total variance of the
  state, so that **1.0 = as different as two randomly chosen fields**.
- Distances from approximate metric coordinates (x = lon · 111,320 · cos(lat), y = lat · 110,574).
- Pairs: all pairs closer than 5 km (255,000 pairs in total); for longer distances all pairs among a random sample of
  4,000 locations (seed 42; about 8 million pairs).
- Distance classes: 30 m–100 m, 100–250 m, 250–500 m, 0.5–1, 1–2, 2–5, 5–10, 10–20, 20–50, 50–100, 100–200, 200–400 km.
  The de-clustered data has no pairs closer than 30 m.
- Same-spot value (< 30 m) = pooled variance within the 2–10-sample clusters of the clustered data (E07), relative to total variance.

## Results (relative semivariance; 1.0 = total variance)
| Distance | N | P | K | OC | Pairs |
|---|---|---|---|---|---|
| Same spot (< 30 m, E07) | 0.19 | 0.27 | 0.30 | 0.24 | — |
| 30–100 m | 0.16 | 0.21 | 0.29 | 0.18 | 5,813 |
| 100–250 m | 0.17 | 0.22 | 0.32 | 0.20 | 12,337 |
| 250–500 m | 0.18 | 0.23 | 0.33 | 0.20 | 21,842 |
| 0.5–1 km | 0.17 | 0.24 | 0.34 | 0.21 | 43,868 |
| 1–2 km | 0.18 | 0.27 | 0.36 | 0.24 | 65,543 |
| 2–5 km | 0.24 | 0.37 | 0.42 | 0.28 | 106,931 |
| 5–10 km | 0.27 | 0.42 | 0.49 | 0.32 | 12,119 |
| 10–20 km | 0.33 | 0.46 | 0.51 | 0.38 | 37,399 |
| 20–50 km | 0.45 | 0.63 | 0.61 | 0.55 | 195,061 |
| 50–100 km | 0.60 | 0.75 | 0.76 | 0.75 | 512,889 |
| 100–200 km | 0.94 | 1.02 | 1.00 | 0.99 | 1,444,620 |
| 200–400 km | 1.15 | 1.03 | 1.06 | 1.11 | 3,439,256 |

## Interpretation
1. **Nugget (noise): 16–30 % of the total variance.** Samples at the same spot already differ by 0.19 (N), 0.27 (P),
   0.30 (K) and 0.24 (OC) of the statewide variance. This is laboratory and sampling noise plus variation below 30 m.
2. **Flat from 30 m to about 1–2 km.** Fields up to 1–2 km apart are no more different than samples at the same spot.
   Within a village-sized area there is **no measurable spatial structure beyond the noise level**. Field-to-field
   prediction at this scale is therefore limited by noise, whatever the inputs.
3. **Steady rise from 2 km to 100–200 km.** Similarity extends over a very long distance. The total variance is reached
   only at about **100–200 km** (the range), the size of a district or region.
4. **At our 10 km block size the curve is only at 0.27–0.51.** Fields 10 km apart are still much more alike than random
   fields. So a 10 km spatial test still leaves similar fields in training and testing; it is stricter than a random
   split but **not fully independent**. This agrees with the lower scores under 50 km blocks (E02, E11) and the failure of
   transfer between regions (E09).
5. **Values above 1.0 beyond 200 km** (N 1.15, OC 1.11) indicate a regional trend: distant regions differ systematically
   (for example Konkan versus the Deccan plateau).
6. Together with E03 and E16, this explains why location, district averages, elevation and climate predict so much:
   the variation is organised at the 50–200 km scale.

## Consequences for the paper
- Justifies spatial cross-validation: with a random split, nearly every test field has training fields within 1–2 km,
  where the difference is at noise level.
- The 10 km block size must be reported as a **conservative lower bound on leakage, not full independence**; results with
  50 km blocks and leave-one-region-out should be shown beside it.
- The nugget supports the noise-ceiling result (E07).

## Caveats
- Isotropic (direction ignored); long distances use a sample of 4,000 locations; the 5–10 km class has fewer pairs (12,119).
- Coordinates are an equirectangular approximation (error of a few per cent over the state).
- Statewide variogram; within-region variograms were not computed.
