import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.patches import Polygon
from matplotlib.animation import FuncAnimation
from datetime import datetime, timedelta

from utils import clean, get_eclipses, clean_hull2, orthodrome


config = {}
with open("../main.conf", "r") as configfile:
    for line in configfile:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        key, value = line.split("=", 1)
        config[key.strip()] = value.strip()
umbra_res    = int(config['umbra_res'])
penumbra_res = int(config['penumbra_res'])
init_year    = int(config['init_year'])
init_month   = int(config['init_month'])
init_day     = int(config['init_day'])
init_hour    = int(config['init_hour'])
init_min     = int(config['init_min'])
init_second  = int(config['init_second'])
init_dt = datetime(init_year, init_month, init_day, init_hour, init_min, init_second)

eclipses = get_eclipses("../data/split")
eclipse = 0




#print(f"[info] \033[34m/data/lonlat.dat\033[0m is being processed...")
#lon_lat_split("../data/lonlat.dat", type = "umbra", delimiter=",", clean=False)
#print("[info] Umbra data split completed.")
#print(f"[info] \033[34m/data/lonlat_in.dat\033[0m is being processed...")
#lon_lat_split("../data/lonlat_in.dat", type = "penumbra", delimiter=",", clean=False)
#print("[info] Penumbra data split completed.")

data_umbra = np.loadtxt("../data/split/" + eclipses[eclipse] + "lonlat_umbra.dat", delimiter=",")
data_umbra = data_umbra.reshape(int(data_umbra.shape[0]/umbra_res),umbra_res,3)
data_penumbra = np.loadtxt("../data/split/" + eclipses[eclipse] + "lonlat_penumbra.dat", delimiter=",")
data_penumbra = data_penumbra.reshape(int(data_penumbra.shape[0]/penumbra_res),penumbra_res,3)

#video parameters
total_frames = data_umbra.shape[0]
if total_frames != data_penumbra.shape[0]:
    print(f"\033[38;5;208m[warning]\033[0m Total frames in umbra ({total_frames}) and penumbra ({data_penumbra.shape[0]}) do not match.")
animlength = int(config['animlength'])
skip = total_frames//(int(config["animlength"])*int(config['animfps']))
center_lonlat = data_umbra[int(data_umbra.shape[0]/2),0,:2]

data_umbra = data_umbra[::skip,:,:]
data_umbra_clean = clean(data_umbra[0,:,:2])
data_umbra_clean_hull = clean_hull2(data_umbra_clean)
lon = data_umbra_clean[:, 0]
lat = data_umbra_clean[:, 1]




data_penumbra = data_penumbra[::skip,:,:]
data_penumbra_clean = clean(data_penumbra[0,:,:2])
data_penumbra_clean_hull = clean_hull2(data_penumbra_clean)
lon_pen = data_penumbra_clean_hull[:,0]
lat_pen = data_penumbra_clean_hull[:,1]
#print(f"[debug] Data shape penumbra_clean: {data_penumbra_clean.shape}\n[debug] Data shape umbra_clean: {data_umbra_clean.shape}")
#print(f"[debug] Data shape penumbra_clean_hull: {data_penumbra_clean_hull.shape}\n[debug] Data shape umbra_clean_hull: {data_umbra_clean_hull.shape}")

#Plot Setup
fig = plt.figure(figsize=(10, 5))
fig.patch.set_facecolor('black')
ax = plt.axes(projection=ccrs.Orthographic(center_lonlat[0],center_lonlat[1]))
ax.set_facecolor('black')
ax.set_global()
ax.coastlines()
ax.add_feature(cfeature.LAND, facecolor='green')
ax.add_feature(cfeature.OCEAN, facecolor='lightblue')
ax.set_title("Path of Totality for the 2024/10/02 Solar Eclipse", color = "white")
ax.gridlines(draw_labels=False, linewidth=0.5, color='black', alpha=0.5, linestyle='--', xlocs=np.arange(-180, 180, 15), ylocs=np.arange(-90, 90, 15))


polygon = Polygon(np.column_stack((lon, lat)), closed=True, facecolor='black', alpha=0.8, transform=ccrs.PlateCarree())
polygon_penumbra = Polygon(np.column_stack((lon_pen, lat_pen)), closed=True, facecolor='black', alpha=0.2, transform=ccrs.PlateCarree())
ax.add_patch(polygon)
ax.add_patch(polygon_penumbra)

#Animation
def update(frame):
    seconds = int(data_umbra[frame,0,2])
    # umbra frames
    new_data_umbra_clean = clean(data_umbra[frame,:,:2])
    new_data_umbra_clean_hull = clean_hull2(new_data_umbra_clean)
    new_lon = new_data_umbra_clean_hull[:, 0]
    new_lat = new_data_umbra_clean_hull[:, 1]
    #penumbra frames
    new_data_penumbra_clean = clean(data_penumbra[frame,:,:2])
    new_data_penumbra_clean_hull = clean_hull2(new_data_penumbra_clean, tol=2)
    new_lon_pen = new_data_penumbra_clean_hull[:, 0]
    new_lat_pen = new_data_penumbra_clean_hull[:, 1]

    dt = init_dt + timedelta(seconds=seconds)
    ax.set_title(f"Path of Totality: {dt} UTC", color = "white")

    polygon_penumbra.set_xy(np.column_stack((new_lon_pen, new_lat_pen)))
    polygon.set_xy(np.column_stack((new_lon, new_lat)))
    return polygon,polygon_penumbra,

print("[info] Rendering animation as MP4...")
ani = FuncAnimation(fig, update, frames=data_umbra.shape[0], blit=True, repeat=False)
#ani.save(f"{eclipses[eclipse]}_anim.mp4", writer="ffmpeg", dpi=100, fps=int(config['animfps']))
print(f"[info] Animation saved as \033[34m{eclipses[eclipse]}_anim.mp4\033[0m")
plt.close(fig)

#Plotting setup for "Großkreis"
orthodromedata = orthodrome([-30,+20],[-90,-60], res = 40)
print(orthodromedata)
testframe = -10
fig2 = plt.figure(figsize=(8, 6))
ax2 = fig2.add_subplot(1, 1, 1)
fig2.patch.set_facecolor('black')
#ax2 = plt.axes(projection=ccrs.Orthographic(-80,-20))
ax2 = plt.axes()
#ax2.set_facecolor('black')

#ax2.set_global()
#ax2.coastlines()
#ax2.add_feature(cfeature.LAND, facecolor='green')
#ax2.add_feature(cfeature.OCEAN, facecolor='lightblue')
ax2.set_title("[debug]", color = "white")
#ax2.scatter(orthodromedata[:,0],orthodromedata[:,1], color='black', alpha=0.2, transform=ccrs.PlateCarree())
ax2.scatter(orthodromedata[:,0],orthodromedata[:,1], color='black', alpha=0.2)
#polygon_penumbra = Polygon(np.column_stack((orthodromedata[:,0],orthodromedata[:,1])), closed=True, facecolor='black', alpha=0.2, transform=ccrs.PlateCarree())
#ax2.add_patch(polygon_penumbra)
plt.show()





