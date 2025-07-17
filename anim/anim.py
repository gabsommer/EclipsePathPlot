import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import pandas as pd
from matplotlib.patches import Polygon

from utils import clean_hull, lon_lat_split, clean


#import values from config file
config = {}

with open("../main.conf", "r") as configfile:
    for line in configfile:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        key, value = line.split("=", 1)
        config[key.strip()] = value.strip()

umbra_res = config['umbra_res']
penumbra_res = config['penumbra_res']





print(f"[info] \033[34m/data/lonlat.dat\033[0m is being processed...")
lon_lat_split("../data/lonlat.dat", type = "umbra", delimiter=",", clean=False)
print("[info] Umbra data split completed.")
print(f"[info] \033[34m/data/lonlat_in.dat\033[0m is being processed...")
lon_lat_split("../data/lonlat_in.dat", type = "penumbra", delimiter=",", clean=False)
print("[info] Penumbra data split completed.")

data = np.loadtxt("../data/split/20241002lonlat_umbra.dat", delimiter=",")
data = data.reshape(int(int(data.shape[0])/int(umbra_res)),int(umbra_res),3)
#TODO Clean data such that outliers are properly removed. There are numerical artefacts in the plot (umbra_plot.png).

#pick test plot at 100
data = clean(data[100,:,:])
lon = data[:, 0]
lat = data[:, 1]

fig = plt.figure(figsize=(10, 5))
ax = plt.axes(projection=ccrs.Orthographic(-114,-20))
ax.set_global()
ax.coastlines()
ax.add_feature(cfeature.LAND, facecolor='lightgray')
ax.add_feature(cfeature.OCEAN, facecolor='lightblue')

#ax.scatter(lon,lat,color='black', s=0.1, transform=ccrs.PlateCarree(), label='Points')
polygon = Polygon(np.column_stack((lon, lat)), closed=True, facecolor='black', alpha=0.5, transform=ccrs.PlateCarree())
ax.add_patch(polygon)
plt.savefig("./umbra_plot.png", dpi=600, bbox_inches='tight')
print("[info] File saved as \033[34mumbra_plot.png\033[0m")




