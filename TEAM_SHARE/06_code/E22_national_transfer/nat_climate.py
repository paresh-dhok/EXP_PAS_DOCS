# TerraClimate (PC zarr), 2011-2020 means, Paresh's D11 definitions, nearest 4 km cell, all-India
import sys,os,time; sys.path.insert(0,os.path.dirname(__file__)); from natcommon import *
import xarray as xr
t0=time.time(); P=points()
col=pystac_client.Client.open("https://planetarycomputer.microsoft.com/api/stac/v1",modifier=pc.sign_inplace).get_collection("terraclimate"); a=col.assets["zarr-abfs"]
ds=xr.open_zarr(a.href,storage_options=a.extra_fields["xarray:open_kwargs"]["storage_options"],consolidated=True)
ds=ds[["ppt","tmax","tmin","def"]].sel(time=slice("2011-01-01","2020-12-31"),lat=slice(BBOX[3],BBOX[1]),lon=slice(BBOX[0],BBOX[2]))
print(ds,flush=True)
m=ds.time.dt.month
clim={"ppt_annual":ds.ppt.mean("time")*12,"ppt_monsoon":ds.ppt.where(m.isin([6,7,8,9])).mean("time")*4,
      "tmax_mean":ds.tmax.mean("time"),"tmin_mean":ds.tmin.mean("time"),"def_annual":ds["def"].mean("time")*12}
out=pd.DataFrame({"id":P.id}); lo=xr.DataArray(P.lon.to_numpy(),dims="p"); la=xr.DataArray(P.lat.to_numpy(),dims="p")
for k,v in clim.items():
    v=v.compute(); out[k]=v.sel(lon=lo,lat=la,method="nearest").to_numpy(); print(k,f"{time.time()-t0:.0f}s",flush=True)
out["tmean"]=(out.tmax_mean+out.tmin_mean)/2
save(out,"climate")
