"""A01 - Audit of dataset provenance and validation leakage for the final experiments (E49-E56).

Read-only: reconstructs the exact data used in notebook cells 66 and 77 of Start/new.ipynb (same files, same code),
then measures counts, duplicates, train-test distances and the LRS self-exclusion logic. It does not change any
result file. Sensitivity runs at the end are DIAGNOSTICS, not replacements for E49-E56.
Run from anywhere:  python A01_provenance_leakage_audit.py   (writes A01_output.txt next to this file)
"""
import sys, time, warnings
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
from pathlib import Path
from scipy.spatial import cKDTree
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from sklearn.model_selection import GroupKFold, train_test_split, GroupShuffleSplit
from sklearn.metrics import r2_score

OUT_DIR = Path(r"D:\SEM 7\CAPSTONE\DATA\slusi\Start")
HERE = Path(__file__).parent
SEED = 42
BANDS   = ["B01","B02","B03","B04","B05","B06","B07","B08","B8A","B09","B11","B12"]
INDICES = ["NDVI","SAVI","NBR2","NDMI","NDWI","BSI","NDRE","CI","BI","RI",
           "R_B4B2","R_B11B12","R_B12B8","R_B11B8","R_B7B5","R_B6B5"]
CLIMATE = ["ppt_annual", "ppt_monsoon", "tmax_mean", "tmin_mean", "tmean", "def_annual"]
TARGETS = ["N", "P", "K", "OC"]
FEATS = BANDS + INDICES + ["pH", "EC"] + ["elev"] + CLIMATE + ["longitude", "latitude"]

def say(*a):
    print(*a); sys.stdout.flush()

# ---------------- 1. Provenance: rebuild exactly as cell 66 + cell 77 ----------------
say("=" * 30, "1. PROVENANCE", "=" * 30)
files = {f: pd.read_parquet(OUT_DIR / f) for f in ["mh_model_dataset.parquet", "mh_final_dataset.parquet",
                                                    "mh_composite.parquet", "mh_terrain.parquet", "mh_climate.parquet"]}
for f, d in files.items():
    say(f"{f:28s} rows {len(d):>7,}  cols {d.shape[1]:>3}  unique id {d['id'].nunique():>7,}")
reg  = pd.read_parquet(OUT_DIR / "mh_candidates.parquet", columns=["id", "region"])
clus = files["mh_model_dataset.parquet"].merge(reg, on="id", how="left")
dec  = files["mh_final_dataset.parquet"].merge(reg, on="id", how="left")
ctx  = files["mh_terrain.parquet"].merge(files["mh_climate.parquet"], on="id").merge(dec[["id", "longitude", "latitude"]], on="id")
say(f"clus (cell 66) rows {len(clus):,} | region missing {clus['region'].isna().sum()} | ctx rows {len(ctx):,}")

def xy(d):
    lat_r = np.deg2rad(d["latitude"].to_numpy())
    return np.c_[d["longitude"].to_numpy() * 111320 * np.cos(lat_r), d["latitude"].to_numpy() * 110574]
dist, nn = cKDTree(xy(ctx)).query(xy(clus))
for c in ["elev"] + CLIMATE:
    clus[c] = ctx[c].to_numpy()[nn]
clus["district"] = clus["id"].str.split("_").str[1]
mask = (clus["district"] != "491").to_numpy()
say(f"Raigad (491) rows {(~mask).sum():,} -> final rows {mask.sum():,}")
say("Final rows per region:", clus.loc[mask, "region"].value_counts().to_dict())
dm = dist[mask]
say("Distance from each final sample to the de-clustered location whose elevation/climate it borrowed (m): "
    f"median {np.median(dm):.0f}, 95% {np.percentile(dm,95):.0f}, 99% {np.percentile(dm,99):.0f}, max {dm.max():.0f}; "
    f"> 1 km {(dm > 1000).sum():,}, > 5 km {(dm > 5000).sum():,}")
ids_final = set(files["mh_final_dataset.parquet"]["id"]); ids_comp = set(files["mh_composite.parquet"]["id"])
say(f"Overlap: final-data ids that are also mh_final_dataset ids {clus.loc[mask,'id'].isin(ids_final).sum():,}; "
    f"mh_composite ids subset of mh_final ids: {ids_comp <= ids_final} ({len(ids_comp):,} of {len(ids_final):,})")
say("Columns of mh_model_dataset used as inputs present:", all(c in clus.columns for c in BANDS + INDICES + ['pH', 'EC']))
say(f"Value ranges in final data: N {clus.loc[mask,'N'].min():.1f}-{clus.loc[mask,'N'].max():.1f}, "
    f"OC min {clus.loc[mask,'OC'].min():.3f}, EC min {clus.loc[mask,'EC'].min():.3f}")

d = clus[mask].reset_index(drop=True)
P = xy(d)
X = d[FEATS].to_numpy(float)

# ---------------- 2a. Duplicates and GPS clusters inside the final data ----------------
say("\n" + "=" * 30, "2a. DUPLICATES / CLUSTERS IN FINAL DATA", "=" * 30)
say(f"ids unique: {d['id'].is_unique}")
key = d["longitude"].round(6).astype(str) + "_" + d["latitude"].round(6).astype(str)
grp = key.value_counts()
say(f"Exact-coordinate groups: {len(grp):,} for {len(d):,} samples; samples sharing exact coordinates with another: "
    f"{int(grp[grp > 1].sum()):,} ({grp[grp > 1].sum() / len(d):.1%}); largest group {grp.max()}")
rec = d[["longitude", "latitude"] + TARGETS + ["pH", "EC"]].round(6).astype(str).agg("|".join, axis=1)
rc = rec.value_counts()
say(f"Fully identical records (coords + N,P,K,OC,pH,EC): {int(rc[rc > 1].sum()):,} rows in {int((rc > 1).sum()):,} groups")
pairs = cKDTree(P).query_pairs(30.0, output_type="ndarray")
A = coo_matrix((np.ones(len(pairs)), (pairs[:, 0], pairs[:, 1])), shape=(len(d), len(d)))
ncomp, lab = connected_components(A, directed=False)
size = np.bincount(lab)[lab]
say(f"30 m clusters (D08 rule): isolated {(size == 1).sum():,}; in clusters 2-10 {((size >= 2) & (size <= 10)).sum():,}; "
    f"in clusters > 10 (dropped as placeholder GPS in D08) {(size > 10).sum():,}; largest {size.max()}")

# ---------------- 2b. Train-test distances under each validation design ----------------
say("\n" + "=" * 30, "2b. DISTANCE FROM EACH TEST SAMPLE TO ITS NEAREST TRAINING SAMPLE", "=" * 30)
def blocks_km(Pxy, km):
    s = km * 1000
    return pd.Series([f"{a}_{b}" for a, b in zip((Pxy[:, 0] // s).astype(int), (Pxy[:, 1] // s).astype(int))]).factorize()[0]
def summarise(name, dd, extra=""):
    q = np.percentile(dd, [5, 25, 50, 75])
    say(f"{name:22s} 5% {q[0]:>8.0f} | 25% {q[1]:>8.0f} | median {q[2]:>8.0f} | 75% {q[3]:>8.0f} m | "
        f"=0 m {np.mean(dd == 0):5.1%} | <=30 m {np.mean(dd <= 30):5.1%} | <=1 km {np.mean(dd <= 1000):5.1%} | "
        f"<=5 km {np.mean(dd <= 5000):5.1%} {extra}")
tr, te = train_test_split(np.arange(len(d)), test_size=0.30, random_state=SEED)
dd = cKDTree(P[tr]).query(P[te])[0]
rec_tr = set(rec.iloc[tr])
summarise("random 70/30 (seed 42)", dd, f"| test rows with an identical record in train {rec.iloc[te].isin(rec_tr).mean():.1%}")
G = {km: blocks_km(P, km) for km in [10, 25, 50, 100]}
cross30 = {}
for km in [10, 25, 50, 100]:
    out = np.zeros(len(d)); fold = np.zeros(len(d), int)
    for f, (a, b) in enumerate(GroupKFold(n_splits=5, shuffle=True, random_state=SEED).split(X, None, G[km])):
        out[b] = cKDTree(P[a]).query(P[b])[0]; fold[b] = f
    cross30[km] = np.mean(fold[pairs[:, 0]] != fold[pairs[:, 1]])
    exact_cross = (pd.Series(fold).groupby(key.values).nunique() > 1).sum()
    summarise(f"spatial {km} km blocks", out, f"| exact-coord groups split across folds {exact_cross}")
say("Share of <=30 m sample pairs that end up in different folds: " + ", ".join(f"{k} km {v:.1%}" for k, v in cross30.items()))

# ---------------- 2c. LRS self-exclusion check (cell 70 logic) ----------------
say("\n" + "=" * 30, "2c. LRS SELF-EXCLUSION (cell 70: query k=11 on training points, drop column 0)", "=" * 30)
dist11, idx11 = cKDTree(P[tr]).query(P[tr], k=11)
own = np.arange(len(tr))
first_not_self = idx11[:, 0] != own
self_kept = (idx11[:, 1:] == own[:, None]).any(1)
self_missing = ~(idx11 == own[:, None]).any(1)
say(f"Training rows (random split): {len(tr):,}")
say(f"  column 0 is NOT the row itself (tie at distance 0): {first_not_self.sum():,} ({first_not_self.mean():.1%})")
say(f"  the row's OWN label is among its 10 LRS neighbours: {self_kept.sum():,} ({self_kept.mean():.1%})")
say(f"  the row itself is not in its 11 nearest at all (>=11 ties at 0 m): {self_missing.sum():,}")
say("Test rows: LRS uses cKDTree(P[tr]) and y[tr] only (cell 70, fit_predict_nb), so no test label can enter by construction.")

# ---------------- 2d. Sensitivity diagnostics (NOT replacements of E49-E56) ----------------
say("\n" + "=" * 30, "2d. DIAGNOSTIC SENSITIVITY RUNS (seed 42, statewide LightGBM, 39 inputs + LRS)", "=" * 30)
from lightgbm import LGBMRegressor
def lgbm():
    return LGBMRegressor(n_estimators=400, learning_rate=0.05, num_leaves=15, min_child_samples=20, subsample=0.8,
                         subsample_freq=1, colsample_bytree=0.5, reg_lambda=5.0, n_jobs=-1, random_state=SEED, verbose=-1)
def nb(P_tr, y_tr, P_q, self_query, exact_self=False):
    if not self_query:
        dq, iq = cKDTree(P_tr).query(P_q, k=10)
    elif not exact_self:                                     # cell 70 logic
        dq, iq = cKDTree(P_tr).query(P_q, k=11); dq, iq = dq[:, 1:], iq[:, 1:]
    else:                                                    # drop the row itself by index, whatever its rank
        dq, iq = cKDTree(P_tr).query(P_q, k=12)
        own_ = np.arange(len(P_q))[:, None]
        keep = iq != own_
        dq = np.array([r[k][:10] for r, k in zip(dq, keep)]); iq = np.array([r[k][:10] for r, k in zip(iq, keep)])
    w = 1 / np.maximum(dq, 1.0); v = np.log1p(y_tr)[iq]
    return np.c_[(w * v).sum(1) / w.sum(1), v[:, 0], np.log1p(dq[:, 0]), v.std(1)]
def run(y, tr_, te_, exact_self=False, use_nb=True):
    Xtr, Xte = X[tr_], X[te_]
    if use_nb:
        Xtr = np.c_[Xtr, nb(P[tr_], y[tr_], P[tr_], True, exact_self)]
        Xte = np.c_[Xte, nb(P[tr_], y[tr_], P[te_], False)]
    z = np.log1p(y[tr_]); mu, sd = z.mean(), z.std()
    return r2_score(y[te_], np.expm1(lgbm().fit(Xtr, (z - mu) / sd).predict(Xte) * sd + mu))
gs_exact = next(GroupShuffleSplit(n_splits=1, test_size=0.30, random_state=SEED).split(X, None, key.values))
gs_30m = next(GroupShuffleSplit(n_splits=1, test_size=0.30, random_state=SEED).split(X, None, lab))
rows = []
t0 = time.time()
for t in TARGETS:
    y = d[t].to_numpy(float)
    rows.append({"target": t,
                 "A random, cell-70 LRS (= E49)": run(y, tr, te),
                 "B random, exact self-exclusion": run(y, tr, te, exact_self=True),
                 "C split by exact location": run(y, *gs_exact),
                 "D split by 30 m cluster": run(y, *gs_30m),
                 "E split by 30 m cluster, no LRS": run(y, *gs_30m, use_nb=False)})
res = pd.DataFrame(rows).set_index("target").T.round(3)
say(res.to_string())
say(f"(diagnostic runs took {time.time() - t0:.0f} s)")
