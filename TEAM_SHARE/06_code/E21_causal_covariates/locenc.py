import sys,glob,os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
import common
common.D=os.environ["REPO_TS"]; common.FEATDIR=os.environ["FEATDIR"]
from common import *
from sklearn.ensemble import RandomForestRegressor
data,groups=load(); GROUPS={"base_41":FEATS}
for f in sorted(glob.glob(common.FEATDIR+"f_*.parquet")):
    g=os.path.basename(f)[2:-8]; x=pd.read_parquet(f); cols=[c for c in x.columns if c!="id" and x[c].notna().mean()>0.5 and x[c].nunique()>1]
    data=data.merge(x[["id"]+cols],on="id",how="left"); GROUPS[g]=cols
cv=GroupKFold(n_splits=5,shuffle=True,random_state=42); loc=[]
for g,cs in GROUPS.items():
    for reg in REGIONS:
        idx=np.where(data.region==reg)[0]; sub=data.iloc[idx]; gg=groups[idx]
        for tgt in ["longitude","latitude"]:
            y=sub[tgt].to_numpy(); oof=np.zeros(len(sub))
            for a,b in cv.split(sub,y,gg):
                oof[b]=RandomForestRegressor(n_estimators=200,min_samples_leaf=3,max_features=0.33,n_jobs=-1,random_state=42).fit(sub[cs].iloc[a],y[a]).predict(sub[cs].iloc[b])
            loc.append(dict(group=g,region=reg,coord=tgt,R2=r2_score(y,oof)))
L=pd.DataFrame(loc); L.to_csv(common.FEATDIR+"location_encoding.csv",index=False)
print(L.groupby("group").R2.mean().sort_values(ascending=False).round(3).to_string())
