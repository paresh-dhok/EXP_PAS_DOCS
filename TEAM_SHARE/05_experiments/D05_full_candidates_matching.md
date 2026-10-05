# D05 — Full candidate set and sample–scene matching

**Date:** 2026-09-28
**Notebook:** `new.ipynb` cell 14
**Outputs:** `mh_candidates.parquet`, `mh_scenes.parquet`, `mh_pairs.parquet`

## Objective
Apply the pilot-proven search and matching to all eligible pre-kharif samples, without the cloud filter.

## Method
1. **Candidates:** eligible records (D03 rules) with sampling month ≤ 6, plus region (5 Maharashtra divisions) and MGRS tile.
2. **STAC search:** one search per MGRS tile, with no cloud filter, `limit=1000`, and retry with backoff.
   For each scene, only id, tile, datetime, `eo:cloud_cover` and the footprint (WKB) are stored.
3. **Matching (local, per tile):** keep pairs with `|scene date − sample date| ≤ 3 days` **and** the point inside the scene footprint.

## Results
| Item | Value |
|---|---|
| Candidates (Jan–Jun) | **91,818** in 56 tiles |
| By region | Vidarbha 27,486, North MH 20,900, Marathwada 19,271, Western MH 16,460, Konkan 7,701 |
| STAC searches | 56 (142 s, no rate-limit errors) |
| Scenes | 2,666 |
| **Pairs (±3 d, in footprint)** | **151,831** |
| Samples with ≥ 1 pair | 89,973 |
| Scenes per sample | {1: 43,128, 2: 33,710, 3: 11,478, 4: 1,516, 5: 101, 7: 40} |
| Samples with ≥ 1 pair, by region | Vidarbha 27,085, North MH 20,900, Marathwada 19,256, Western MH 15,565, Konkan 7,167 |
| Estimated extraction time (all pairs, 0.26 s/pair) | 11.0 h |

## Decision
11 h for all pairs was considered too long. The extraction was restructured (D06):
- closest-date scene first, with further scenes only for samples that are not yet usable
- Jan–May first and June held back (6 % pilot yield)
- benchmark the number of parallel workers
