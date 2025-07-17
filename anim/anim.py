import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import pandas as pd

from utils import clean_hull, lon_lat_split


#First static plot of umbra 




print(f"[info] \033[34m/data/lonlat.dat\033[0m is being processed...")
lon_lat_split("../data/lonlat.dat", type = "umbra", delimiter=",", clean=True)
print("[info] Umbra data split completed.")
print(f"[info] \033[34m/data/lonlat_in.dat\033[0m is being processed...")
lon_lat_split("../data/lonlat_in.dat", type = "penumbra", delimiter=",", clean=True)
print("[info] Penumbra data split completed.")

data = np.loadtxt("../data/split/20241002lonlat_umbra.dat", delimiter=",")

#TODO Clean data such that outliers are properly removed. There are numerical artefacts in the plot (umbra_plot.png).
data = clean_hull(data[:,:2])
print(f"[debug] {data.shape}")
lon = data[:,0]
lat = data[:,1]
         

fig = plt.figure(figsize=(10, 5))
ax = plt.axes(projection=ccrs.Orthographic(-114,-20))
ax.set_global()
ax.coastlines()
ax.add_feature(cfeature.LAND, facecolor='lightgray')
ax.add_feature(cfeature.OCEAN, facecolor='lightblue')

ax.scatter(lon,lat,color='black', s=0.1, transform=ccrs.PlateCarree(), label='Points')
plt.savefig("./umbra_plot.png", dpi=600, bbox_inches='tight')


