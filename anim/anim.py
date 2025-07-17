import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import pandas as pd


#First static plot of umbra 

lon = [10]
lat = [20]

with open("./02102024lonlattest.dat", "r") as file:
    lines = file.readlines()
    for line in lines:
        print(line.strip().split(sep=','))
         

fig = plt.figure(figsize=(10, 5))
ax = plt.axes(projection=ccrs.Orthographic())
ax.set_global()
ax.coastlines()
ax.add_feature(cfeature.LAND, facecolor='lightgray')
ax.add_feature(cfeature.OCEAN, facecolor='lightblue')

ax.scatter(lon,lat,color='red', s = 50, transform=ccrs.PlateCarree(), label='Points')
plt.show()
