# D01 — Maharashtra filter

**Date:** 2026-09-28
**Notebook:** `new.ipynb` cells 0–4
**Output:** `Start\maharashtra_raw.parquet`

## Objective
Extract all Maharashtra records from the SLUSI Soil Health data without changing any column, using the most
reliable state/district identifier.

## Input
`SLUSI_Soil_Health_data.16-5037---7-8388--125-3251--41-5041.parquet`
- 0.22 GB, **5,182,371 rows**, 46 columns, 5 row groups (first group 1,048,576 rows)
- All columns are `string` except `geometry` (`binary`, WKB point)
- The text columns `STATE` and `DISTRICT` are empty for most rows (≈4.48 M missing), so they were not used.

## Method
1. Inspected the schema and the first 10 rows (cell 0–1). The official codes appear in three places:
   the `id` prefix (`27_490_shc_...`), `sid` (state) and `did` (district).
2. Cross-checked the three sources with pyarrow compute (cell 2).
3. Filtered `sid == "27"` and wrote the result with zstd compression (cell 3). Verified by reading it back.
4. Counted records per district against the official list of 36 Maharashtra district codes (cell 4).

## Results
| Check | Count |
|---|---|
| Null `id` / `sid` / `did` | 0 / 0 / 0 |
| Rows with `sid == 27` | 355,562 |
| Rows with `id` prefix 27 | 355,562 |
| Both agree | 355,562 (0 disagreements either way) |
| `did` == district in `id` | 355,562 |
| `did` in the 36 official codes | 355,562 |

Output: `maharashtra_raw.parquet` is 16.0 MB with **355,562 rows × 46 columns**. Its schema is identical to the master.

**Districts present: 34 of 36.** Missing: 482 Mumbai and 483 Mumbai Suburban (fully urban, no SHC farm samples).
Largest: Nashik 22,788, Satara 21,982, Ahilyanagar 15,829, Pune 14,752, Chandrapur 14,178.
Smallest: Palghar 4,918, Sindhudurg 4,762, Thane 3,763.

## Issues
The first summary attempt failed (`TypeError: Series.rename() got an unexpected keyword argument 'columns'`)
because `pc.value_counts` returns a struct array. This affected only the printout; the file had already been
written and verified. It was fixed in cell 4.

## Decision
State code from `sid` (it agrees 100 % with the `id` prefix). The master file was not modified.
