# Soil N, P, K and OC prediction from Sentinel-2 and Soil Health Card data (Maharashtra)

Capstone work: estimating soil nitrogen, phosphorus, potassium and organic carbon from satellite data, terrain and a
low-cost pH/EC reading, using Soil Health Card laboratory results as ground truth.

## Where to start

| You want to… | Read |
|---|---|
| Understand the project from the basics | [`TEAM_SHARE/PROJECT_GUIDE.md`](TEAM_SHARE/PROJECT_GUIDE.md) |
| Know what each data file contains | [`DATASETS.md`](DATASETS.md) |
| Run a new experiment the agreed way | [`TEAM_SHARE/REGION_WISE_PROTOCOL.md`](TEAM_SHARE/REGION_WISE_PROTOCOL.md) |
| See what has been done and found | [`experiments/README.md`](experiments/README.md) (D00–D11 data steps, E01–E18 experiments) |
| Get the numbers | [`results/`](results) (one or two CSV files per experiment) |

## Contents

| Path | Content |
|---|---|
| `*.parquet`, `composite_parts/` | Data files, described in [`DATASETS.md`](DATASETS.md) |
| `experiments/` | One documentation file per data step and experiment |
| `results/` | Result tables (CSV) and figures |
| `new.ipynb` | Working notebook with all cells that were run |
| `s2_composite.py` | Download script for the multi-date satellite composite |
| `TEAM_SHARE/` | The package shared with the team: guides plus copies of the data, results, experiments and code |

## Key facts

- **Final dataset:** 17,620 independent bare-soil locations in Maharashtra, sampled January–May 2024
  (17,273 with a multi-date satellite composite).
- **Model inputs (41):** `pH`, `EC` + 33 satellite composite features + 6 terrain features. No location inputs.
- **Testing:** region-wise (train and test inside one of 5 regions) with 10 km spatial blocks; never a random split.
- **Targets:** N, P, K (kg/ha) and OC (%).
