"""Train-test distances for the exact E49/E50 splits (seed 42) on the original 32,096-sample dataset.
Read-only: rebuilds clus, mask and block ids exactly as notebook cells 66, 69 and 77, recreates the same
train_test_split / GroupKFold splits, and measures the distance from each test sample to its nearest training sample.
No model is fitted. Output: results/57_train_test_distances_E49_E50.csv
"""
import numpy as np, pandas as pd
from pathlib import Path
from scipy.spatial import cKDTree
from sklearn.model_selection import GroupKFold, train_test_split

OUT_DIR = Path(r"D:\SEM 7\CAPSTONE\DATA\slusi\Start")
reg = pd.read_parquet(OUT_DIR / "mh_candidates.parquet", columns=["id", "region"])
clus = pd.read_parquet(OUT_DIR / "mh_model_dataset.parquet").merge(reg, on="id", how="left")      # cell 66
def xy(d):
    lat_r = np.deg2rad(d["latitude"].to_numpy())
    return np.c_[d["longitude"].to_numpy() * 111320 * np.cos(lat_r), d["latitude"].to_numpy() * 110574]
def blocks_km(d, km):                                                                              # cell 69
    p = xy(d); s = km * 1000
    return pd.Series([f"{a}_{b}" for a, b in zip((p[:, 0] // s).astype(int), (p[:, 1] // s).astype(int))]).factorize()[0]
G = {km: blocks_km(clus, km) for km in [10, 25, 50, 100]}
clus["district"] = clus["id"].str.split("_").str[1]
mask = (clus["district"] != "491").to_numpy()                                                     # cell 77
P = xy(clus)[mask]
n = mask.sum()
rows = []
def add(name, dd):
    q = np.percentile(dd, [5, 25, 50, 75, 95])
    rows.append({"design": name, "test_samples": len(dd), "p5_m": q[0], "p25_m": q[1], "median_m": q[2], "p75_m": q[3], "p95_m": q[4],
                 "share_le_30m": np.mean(dd <= 30), "share_le_100m": np.mean(dd <= 100), "share_le_1km": np.mean(dd <= 1000), "share_le_5km": np.mean(dd <= 5000)})
tr, te = train_test_split(np.arange(n), test_size=0.30, random_state=42)                         # E49 / E50 random
add("random 70/30", cKDTree(P[tr]).query(P[te])[0])
for km in [10, 25, 50, 100]:                                                                       # E49 (10 km) / E50
    g = G[km][mask]; dd = np.zeros(0)
    for a, b in GroupKFold(n_splits=5, shuffle=True, random_state=42).split(np.zeros(n), None, g):
        dd = np.r_[dd, cKDTree(P[a]).query(P[b])[0]]
    add(f"spatial {km} km", dd)
res = pd.DataFrame(rows)
res.to_csv(OUT_DIR / "results" / "57_train_test_distances_E49_E50.csv", index=False)
print(res.round(3).to_string(index=False))
