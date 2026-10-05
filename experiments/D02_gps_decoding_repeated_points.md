# D02 — GPS decoding and repeated GPS points

**Date:** 2026-09-28
**Notebook:** `new.ipynb` cells 5–6 (decision applied in cell 7)

## Objective
Decode the WKB geometry into longitude/latitude, check validity, and understand GPS points shared by several records.

## Method
- Vectorised decoding: `shapely.from_wkb` → `shapely.get_x` (longitude), `shapely.get_y` (latitude).
- Sanity check against a rough Maharashtra bounding box: lon 72.6–80.9, lat 15.6–22.1.
- Grouped records by exact (lon, lat) to count records per GPS point.
- Cell 6 inspected what the repeated points contain (districts, villages, dates, cycles, N/P/K combinations).

## Results
- 355,562 geometries decoded in 0.3 s. All are `Point`, with no NaN coordinates.
- Range: lon 72.55321–91.78704, lat 15.62376–26.12031.
  **10 points fall outside Maharashtra** (lon up to 91.8 = north-east India), so these are invalid coordinates.
- **Unique GPS points: 246,285** (69.27 % of records).
- **Points with more than 1 record: 31,490, holding 140,767 records.**

| Records at one point | Points |
|---|---|
| 1 | 214,795 |
| 2 | 15,563 |
| 3 | 4,728 |
| 4 | 2,887 |
| 5 | 1,950 |
| 6–10 | 4,022 |
| 11–15 | 1,217 |
| max | **112 records at one point** |

Records sharing a GPS point usually carry **different** N/P/K values (see the cell 6 output in the notebook),
so they are different samples filed under one coordinate.

## Interpretation
A coordinate shared by many different samples is very likely a placeholder (village centre or the sampler's position),
not the field. For any such record it is impossible to know which sample the satellite pixel represents.

## Decision
- **All records at repeated GPS points are excluded** (not "keep the first one"). Applied in cell 7 as `n_at_point == 1`.
- The 10 out-of-state points are excluded.
- Near-identical but not exactly equal coordinates are not caught here. That was found and handled later in **D08**.
