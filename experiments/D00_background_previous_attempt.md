# D00 — Background: previous acquisition attempt (abandoned)

**Date:** before 2026-09-28 (earlier work, `Acquisition\` folder, `Acquisition\data_search.ipynb`)
**Status:** Abandoned. Replaced by the pipeline in D03–D06.

## What was done earlier
- A 5,000-point pilot (`Acquisition\trail_5000.parquet`): unique GPS points with valid dates, sampled with `random_state=42`.
- MGRS tile per point (`mgrs` 1.5.4). The 5,000 points fall in 55 tiles.
- **Point-by-point STAC search** (one search per sample) hit the Planetary Computer **rate limit**
  (`APIError: You have exceeded a rate limit`). A partial result was saved as `Acquisition\partial_scene_search_5000.parquet`
  (≈597 pairs, 278 samples, 457 scenes).
- **Tile-based STAC search** (one search per MGRS tile, date range = min/max sample date ± 3 days) worked:
  55 searches, 2,858 scenes, 164.4 s, no rate-limit errors. Local matching (±3 days) gave 11,475 sample–scene
  pairs, 4,918 samples and 1,739 scenes.

## Why it was abandoned
The extraction opened each of 15 remote COG assets per scene with rasterio. A benchmark on one scene
(S2B_MSIL2A_20240724T051659_R062_T43QGB, 13 points) gave:

| Asset | Time (s) | Asset | Time (s) |
|---|---|---|---|
| B01 | 38.00 | B09 | 38.53 |
| B02 | 32.10 | B11 | 43.51 |
| B03 | 32.22 | B12 | 43.01 |
| B04 | 31.18 | SCL | 3.96 |
| B05 | 49.06 | AOT | 6.00 |
| B06 | 50.16 | WVP | 3.49 |
| B07 | 46.82 | | |
| B08 | 31.86 | **Total** | **501.71 s (8.36 min/scene)** |

1,739 scenes × 8.36 min ≈ **10 days**. Not viable.

## Lessons carried forward
1. Never do one STAC search per sample. Search once per MGRS tile and match locally.
2. The bottleneck is downloading COG blocks (≈1–2 MB per band per point). The solution must avoid downloading
   blocks to the local machine (see D03/D04: Planetary Computer data API).
3. Benchmark before scaling.
