# D06 — Full 3×3 extraction (rounds 1–5)

**Date:** 2026-09-28
**Notebook:** `new.ipynb` cells 15–18
**Output:** `mh_s2_3x3.parquet` (raw DN statistics, 61,617 rows)

## Objective
Extract the exact 3×3 window statistics (D04) for enough pairs to obtain ≥ 25 k usable samples, quickly and resumably.

## Ordering strategy
- Each sample's pairs are ranked by |date difference|, then scene cloud cover, then scene id (`rank` 0, 1, 2 …).
- **Round 1:** rank-0 pair (closest scene) of every Jan–May sample.
- **Rounds 2+:** the next-ranked scene, only for samples without a usable result yet.
- June samples were held back and were never needed.

## Speed and robustness tests
| Test | Result |
|---|---|
| 4 workers, first retry configuration (timeout 120 s, 6 attempts, backoff 5·2ⁿ s) | 200 pairs took 362 s. **One stuck pair held the batch**, and the kernel had to be restarted |
| Fixed retry configuration: timeout (10 s connect, 30 s read), 3 attempts, backoff 2/4/8 s | used from then on |
| 8 workers | 6.3 pairs/s, no HTTP 429 |
| **16 workers** | **8.5 pairs/s, no HTTP 429** (chosen) |

Results are saved every 2,000 pairs, and rerunning skips pairs that are already saved.

## Results
| Stage | Pairs | Outcome |
|---|---|---|
| Benchmarks | 600 | 597 OK |
| **Round 1** | 52,802 | ~19.1 pairs/s, ~46 min; 202 failed |
| Retry of failed pairs | 202 | all failed again (HTTP 500) |
| Round 2 | 7,445 | +3,138 usable samples |
| Round 3 | 698 | — |
| Round 4 | 72 | — |
| Round 5 | 12 | +2 usable |
| **Total** | **61,617 rows** | 61,332 OK, **285 failed** |

**Usable samples (SCL majority = 5): 40,988. Of these, all 9 pixels SCL = 5: 36,022.**

## Quality audit (after round 1, separate script)
- Duplicate (id, scene) rows: 0. Zero or missing band values among usable rows: 0.
- **Failures are scene-specific, not random:** the 202 round-1 failures came from 7 scenes, one of them with 106
  (`S2A_MSIL2A_20240517T050651_R019_T44QLJ_…`). These scenes consistently return HTTP 500 from the server.
  The affected samples were covered by their next-closest scene in round 2.
- Window pixel counts: B04 = 9 for 53,171 of 53,200 OK rows. ~30 incomplete windows (scene edge) were removed later.
- Usable (round 1) by region: North MH 10,795, Marathwada 10,090, Vidarbha 8,028, Western MH 5,009, Konkan 3,773.
- By month: Jan 2,590, Feb 4,125, Mar 6,835, Apr 9,312, May 14,833. All 2024.
- Date difference of usable round-1 pairs: −2 … +2 days (a closer scene always existed).
- Soil values of usable samples contain impossible entries (e.g. N max 213,225; K max 552,016; pH min −26.9, max 6,982).
  These were handled in D07.

## Decision
The satellite extraction is complete. Use **only samples where all 9 window pixels are bare soil** (user decision, 2026-09-30).
