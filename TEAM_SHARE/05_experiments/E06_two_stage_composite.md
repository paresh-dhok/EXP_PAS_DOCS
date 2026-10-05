# E06 — Two-stage model with the multi-date bare-soil composite

**Date:** 2026-10-01
**Notebook:** cell run on 2026-10-01 (not yet saved to disk when this file was written)
**Results:** `results/07_two_stage_composite.csv` (file number 07; experiment ID E06, see the README note)
**Data:** 17,273 locations = final dataset + terrain + composite (≥ 3 bare dates); 1,554 spatial blocks (10 km)

## Hypothesis (before running)
The 12-date bare-soil composite (D10) removes one-day noise. If field-level soil signal exists in the spectra, it should
appear with the composite, especially for OC (the target with the strongest support in the composite literature).

## Setup
Same two-stage procedure as E04/E05 (district mean from training folds + RF 200 trees, min_samples_leaf 5,
max_features 1.0, seed 42; 10 km spatial blocks, 5 folds). The district-only baseline was recomputed on these 17,273 locations.

| Stage 2 set | Features | Count |
|---|---|---|
| C_single_fusion | single-date 12 bands + 16 indices + pH, EC (reference on the same rows) | 30 |
| S_comp_satellite_only | composite 12 bands + 16 indices + 5 temporal std | 33 |
| CC_comp_fusion | S + pH, EC | 35 |
| CCT_comp_fusion_terrain | CC + 7 terrain | 42 |
| CCTG_comp_all_GPS | CCT + longitude, latitude | 44 |

## Results
District-only baseline (17,273 rows): N 0.611, P 0.383, K 0.368, OC 0.610.

| Set | Two-stage N | P | K | OC |
|---|---|---|---|---|
| C_single_fusion | 0.610 | 0.392 | 0.358 | 0.605 |
| S_comp_satellite_only | 0.605 | 0.382 | 0.364 | 0.604 |
| CC_comp_fusion | 0.609 | 0.391 | 0.365 | 0.607 |
| CCT_comp_fusion_terrain | 0.632 | 0.380 | 0.377 | **0.617** |
| CCTG_comp_all_GPS | **0.665** | 0.390 | **0.390** | 0.611 |

| Set | **Within-district** N | P | K | OC |
|---|---|---|---|---|
| C_single_fusion | −0.002 | −0.006 | −0.014 | −0.014 |
| S_comp_satellite_only | −0.021 | −0.012 | −0.008 | −0.017 |
| CC_comp_fusion | −0.016 | −0.001 | −0.006 | −0.007 |
| CCT_comp_fusion_terrain | 0.021 | 0.005 | 0.006 | 0.017 |
| CCTG_comp_all_GPS | **0.125** | 0.037 | 0.031 | 0.011 |

## Interpretation
- **The composite did not add field-level skill, not even for OC** (within-district ≈ 0).
- Since the cleaner, more stable soil signal also fails, single-image noise was **not** the limiting factor.
- Terrain combinations give ≤ 0.02. Only GPS adds noticeably (N 0.125).
- Chain of evidence: single date → 12-date composite (185,946 observations) → + terrain → + GPS. No bare-soil remote data
  explains field-level variation in SHC values beyond the district average.

## Status
Uses location (district stage). Diagnostic. The field-only (no-location) composite model **has not been run yet**.
