import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import pandas as pd


#First static plot of umbra 

data = np.loadtxt("./02102024lonlattest.dat", delimiter=",")
lon = data[:,0]
lat = data[:,1]


         

fig = plt.figure(figsize=(10, 5))
ax = plt.axes(projection=ccrs.Orthographic(-114,-20))
ax.set_global()
ax.coastlines()
ax.add_feature(cfeature.LAND, facecolor='lightgray')
ax.add_feature(cfeature.OCEAN, facecolor='lightblue')

ax.scatter(lon,lat,color='black', s=0.1, transform=ccrs.PlateCarree(), label='Points')
plt.savefig("./umbra_plot.png", dpi=300, bbox_inches='tight')
