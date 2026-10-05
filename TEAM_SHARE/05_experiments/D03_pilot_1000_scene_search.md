# D03 — 1,000-sample pilot, scene search, region and season decision

**Date:** 2026-09-28
**Notebook:** `new.ipynb` cells 7–11
**Outputs:** `pilot_1000.parquet`, `pilot_1000_scenes.parquet`, `pilot_1000_matches.parquet`, `pilot_1000_s2_raw.parquet`

## Objective
Prove a fast, rate-limit-safe Sentinel-2 acquisition on 1,000 samples before scaling, and measure the real usable-sample rate.

## Eligibility rules (cell 7)
A record is **eligible** if:
1. It is the only record at its GPS point (`n_at_point == 1`, see D02).
2. It has a date that parses (`format="%m/%d/%y, %I:%M %p"`): 250,672 of 250,672 non-null dates parse.
3. It lies inside the Maharashtra bounding box.
4. N, P and K are numeric.

**Eligible records: 119,814.**

## Pilot sample
`eligible.sample(n=1000, random_state=42)`. It covers 34 districts, 51 MGRS tiles, 194 dates and 695 tile–date groups,
with dates from 2023-09-18 to 2024-07-31.

## Scene search (cell 8)
- Planetary Computer STAC `sentinel-2-l2a`. **One search per MGRS tile** (bbox of the tile's points; dates = min/max ± 3 days),
  with a server-side filter `eo:cloud_cover < 10`. Only scenes whose own MGRS tile matches are kept.
- 51 tiles, 51 requests, 71.9 s, **1,031 scenes**.
- Local matching at ±3 days: **667 pairs, 406 samples (of 1,000), 364 scenes.**
  Scenes per sample: {1: 231, 2: 104, 3: 57, 4: 13, 5: 1}.

## Pixel extraction (cells 9–10)
- Extraction method benchmark: see D04.
- **Footprint filter:** a point can lie in the tile but outside the scene's valid-data area (orbit edge), which
  returns all zeros. Keeping only pairs whose point is inside `item.geometry` leaves **500 of 667 pairs**.
- Data-API point extraction, 4 workers: 500 pairs in 100 s, all OK.

| SCL class at the point | Pairs |
|---|---|
| 5 bare soil | **411** |
| 4 vegetation | 68 |
| 8 cloud medium | 5 |
| 7 unclassified | 5 |
| 3 cloud shadow | 4 |
| 0 no data | 3 |
| 10 thin cirrus | 2 |
| 9 cloud high | 2 |

**Samples with at least one SCL = 5 observation: 316 of 1,000 (31.6 %).**

## Region and season analysis (cell 11)
Eligible records by month (all regions):

| Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 4,348 | 6,370 | 8,957 | 12,095 | 22,855 | 37,193 | 24,587 | 285 | 238 | 674 | 1,023 | 1,189 |

Pilot usable rate (with the cloud < 10 % filter still on):
- By month: Jan 0.44, Feb 0.61, Mar 0.61, **Apr 0.68**, May 0.53, **Jun 0.06, Jul 0.00**.
- By region: North MH 0.44, Marathwada 0.41, Konkan 0.35, Vidarbha 0.27, Western MH 0.16.

Eligible pool by region: Vidarbha 36,515, Western MH 25,025, North MH 24,538, Marathwada 24,164, Konkan 9,572.

## Interpretation
- Most samples are taken in May–July. June and July coincide with the monsoon (clouds) and sowing (vegetation), so they are rarely usable.
- Feb–May (pre-kharif fallow, after the rabi harvest) gives 53–68 % usable.
- Vidarbha alone would give roughly 8–10 k usable samples. That is too few for the guide's 25 k target.

## Decisions
1. **Study area: all of Maharashtra**, with Vidarbha reported as a focus region.
2. **Season: pre-kharif (Jan–Jun)**. July onwards is dropped.
3. **The scene-level cloud filter is dropped.** The local SCL at the pixel is the real criterion, because a cloudy scene can still be clear over the field.
4. **Usable observation = SCL 5 (bare soil) and within ±3 days of sampling.** Both are required: ±3 days ensures the same surface state as at sampling, and SCL 5 ensures the pixel is bare.
