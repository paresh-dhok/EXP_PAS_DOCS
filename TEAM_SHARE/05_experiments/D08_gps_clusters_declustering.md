# D08 — GPS clusters (placeholder locations) and de-clustering

**Date:** 2026-09-30
**Notebook:** `new.ipynb` cells 22–23; the final removal of 10 close locations is in cell 24
**Output:** **`mh_final_dataset.parquet` (17,620 locations × 44 columns)**

## Objective
Samples within 30 m share the same 3×3 window (30 m × 30 m). Determine how common this is, whether these are real
neighbouring fields or placeholder coordinates, and how to obtain **independent** observations.

## Method
- Approximate metric coordinates: x = lon · 111,320 · cos(lat), y = lat · 110,574.
- `cKDTree.query_pairs(30 m)` gives close pairs. `connected_components` on the close-pair graph gives the clusters.
- For each cluster: size, spatial spread, number of dates and scenes, and the range of soil values.

## Results (on 33,877 samples)
| Finding | Value |
|---|---|
| Samples with another sample within 30 m | **20,170 (60 %)**, 118,798 close pairs |
| Isolated samples | 13,707 |
| Clusters with > 1 sample | 4,281; largest **179** |
| Nearest-neighbour distance | median 17.4 m; 25 % of samples have a neighbour within 4.8 m |

Samples by cluster size: 1: 13,707 | 2: 4,342 | 3–5: 4,815 | 6–10: 3,144 | 11–50: 6,344 | 51–200: 1,525.

Distance between close pairs: ≤ 0.1 m: 172 | 0.1–1 m: 2,741 | 1–2 m: 4,677 | 2–5 m: 17,517 | 5–10 m: 29,814 | 10–20 m: 39,691 | 20–30 m: 24,186.

Five largest clusters:

| Cluster | Samples | Spread | Dates | Scenes | District | N range | OC range |
|---|---|---|---|---|---|---|---|
| 10258 | 179 | 71 × 81 m | 6 | 4 | 485 Nanded | 27–266 | 0.42–0.63 |
| 10255 | 148 | 45 × 51 m | 4 | 2 | 485 Nanded | 185–266 | 0.42–0.63 |
| 10071 | 113 | 55 × 54 m | 7 | 5 | 485 Nanded | 182–268 | 0.36–0.68 |
| 10036 | 107 | 53 × 50 m | 6 | 4 | 485 Nanded | 194–274 | 0.42–0.83 |
| 3722 | 99 | 140 × 94 m | 3 | 3 | 478 Jalgaon | 97–212 | 0.12–0.73 |

Soil variability, median within-cluster std vs overall std: N 25.6 vs 158.8; P 2.95 vs 24.7; K 59.8 vs 258.9; OC 0.08 vs 0.43.

Other observations:
- `VILLAGE`, `TEHSIL` and `BLOCK` are **completely empty** for Maharashtra.
- Coordinate precision is mixed: about 11.3 k coordinates have 14 decimals and about 18 k have 7–8 decimals.
  This suggests two recording methods.

## Interpretation
179 different fields cannot fit inside 0.6 ha. The large clusters are samples from many fields around a village,
**geotagged at one spot**. The satellite pixel there does not represent those fields. Samples within 30 m also
share overlapping windows, so they are not independent observations and they cause leakage if split between training and test.

## Options evaluated
| Rule | Independent locations | Samples dropped |
|---|---|---|
| Keep only isolated samples | 13,707 | 20,170 |
| Drop clusters > 5, merge 2–5 | 17,220 | 11,013 |
| **Drop clusters > 10, merge 2–10** | **17,641** | **7,869** |
| Drop clusters > 20, merge 2–20 | 17,864 | 4,627 |
| Merge every cluster | 17,988 | 0 |

## Final procedure (cell 23, `MAX_CLUSTER = 10`, radius 30 m)
1. Tighter lower limits OC > 0.02 and EC > 0.005: 33,877 → **33,842**.
2. Clusters recomputed. **Dropped 347 clusters > 10 holding 7,861 samples → 25,981 samples**
   (13,703 isolated + 12,278 in clusters of 2–10).
3. Each cluster of 2–10 was merged into **one location**: median of coordinates, soil values, reflectances, AOT, WVP
   and date difference. Earliest sample_date, first scene id. All merged ids kept in `ids_merged` and the count in `n_merged`.
4. The 16 indices were **recomputed from the merged reflectances** (not medians of indices).
5. **17,630 locations.** Merged sizes: {1: 13,703, 2: 2,167, 3: 756, 4: 381, 5: 203, 6: 131, 7: 111, 8: 76, 9: 54, 10: 48}.
6. 10 locations were still < 30 m apart after merging (medians of neighbouring clusters moved closer). They were removed in cell 24 → **17,620**.

## Final targets (17,630 before the last 10 removed)
| | mean | std | min | 1 % | 50 % | 99 % | max |
|---|---|---|---|---|---|---|---|
| N | 227.7 | 157.7 | 22.09 | 47.04 | 189.41 | 918.40 | 1,408.77 |
| P | 23.79 | 25.74 | 1.012 | 2.711 | 16.41 | 136.87 | 298.33 |
| K | 421.9 | 256.8 | 21.65 | 63.46 | 361.54 | 1,421.75 | 2,505.85 |
| OC | 0.578 | 0.434 | 0.022 | 0.090 | 0.460 | 2.266 | 4.92 |
| pH | 7.48 | 0.69 | 4.17 | 5.35 | 7.66 | 8.60 | 10.00 |
| EC | 0.358 | 0.289 | 0.006 | 0.020 | 0.300 | 1.030 | 9.35 |

## Note on sample count
The guide's target of about 25 k was set before the clustering was known. There are **33,842 clean laboratory samples**,
but only **17,620 independent locations** as seen by a 30 m satellite window. The placeholder-GPS finding is itself
a data-quality contribution.
