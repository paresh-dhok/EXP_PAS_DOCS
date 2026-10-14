# E47 — The group of samples at N ≈ 900 kg/ha (Raigad)

**Date:** 2026-10-14
**Notebook:** cell run on 2026-10-14 (data check only, no model)
**Results:** printed output only (no CSV)

## Why
The measured-vs-predicted figure (E40) shows a tight block of samples at N ≈ 900 kg/ha that is predicted well. Before
the paper claims that N is predicted well, check whether this group is real or a data artifact.

## Results
- **983 samples (2.9 %) have N > 850 kg/ha; 373 have N > 920.**
- **904 of the 983 come from one district: 491 = Raigad (Konkan).** Raigad has 1,781 samples; 50.8 % of them are
  above 850 and its **median N is 872 kg/ha** (statewide median about 195). Next: 492 Ratnagiri, 69 samples (11.4 %,
  median 301). All other districts: ≤ 4 samples above 850.
- The high values are **not one placeholder value**: 113 distinct values over 45 sampling dates. The most frequent are
  884.79 (101×), 878.51 (96×), 909.89, 934.99, 903.61 … They are spaced by **6.27 kg/ha**, the step of the alkaline
  KMnO₄ titration, i.e. they look like real laboratory readings.
- The same samples have higher OC (median 0.93 % vs 0.46 %) and lower pH (6.70 vs 7.65), consistent with Konkan
  lateritic/rice soils, but N is 2–3× higher than in the neighbouring district Ratnagiri.

## Interpretation
1. The values are probably genuine readings but reflect a **district-level (likely laboratory-level) offset** in
   Raigad: half the district above 850 kg/ha, while neighbouring Ratnagiri has a median of 301.
2. **Risk for the N headline:** these samples sit far from the mean (≈ 231) and are easy to predict from location and
   neighbour values, so they can carry a large share of the total N variance and inflate the statewide N R².
   E48 measures this by re-running the headline model without Raigad.

## Caveats
Whether the offset comes from the laboratory, the method or the soils cannot be decided from these data.
