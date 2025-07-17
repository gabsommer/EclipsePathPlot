import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import matplotlib.animation as animation
import pandas as pd
from datetime import datetime, timedelta
import math

from utils import clean_hull, clean, data_pd


# Read configuration from main.conf
config = {}
with open("main.conf", "r") as file:
    for line in file:
        line = line.strip()
        if not line or line.startswith("#"):  # Ignore empty lines and comments
            continue
        key, value = line.split("=", 1)
        config[key.strip()] = float(value.strip())

plotpoints = int(config["umbra_res"])
plotpoints_in = int(config["penumbra_res"])
init_year = int(config["init_year"])
init_month = int(config["init_month"])
init_day = int(config["init_day"])
init_hour = int(config["init_hour"])
init_minute = int(config["init_min"])
init_second = int(config["init_second"])


init_date = datetime(
    init_year, init_month, init_day, init_hour, init_minute, init_second
)

print("Loading data ...")
data_anim = data_pd("./data/latlong.dat", plotpoints)
data_anim_in = data_pd("./data/latlong_in.dat", plotpoints_in)
data_new = data_anim[0, :, :]
data_new_in = data_anim_in[0, :, :]
data_new = np.expand_dims(data_new, axis=0)
data_new_in = np.expand_dims(data_new_in, axis=0)
timenow = data_new[0, 0, 2]

for i in range(data_anim.shape[0] - 1):
    if data_anim[i, 0, 2] - timenow >= 180:
        timenow = data_anim[i, 0, 2]
        add2d = data_anim[i, :, :]
        data_new = np.append(data_new, add2d[np.newaxis, :, :], axis=0)
timenow = data_new[0, 0, 2]
for i in range(data_anim_in.shape[0] - 1):
    if data_anim_in[i, 0, 2] - timenow >= 180:
        timenow = data_anim_in[i, 0, 2]
        add2d_in = data_anim_in[i, :, :]
        data_new_in = np.append(data_new_in, add2d_in[np.newaxis, :, :], axis=0)
print("Loading data finished.")
print("Data array shape is: ", data_new.shape)
print("Data array_in shape is: ", data_new_in.shape)

print("Animating ...")

umbra_number = 0

matplotlib.use("Agg")
fig = plt.figure()
fig.patch.set_facecolor("black")
fig.patch.set_alpha(1)
ax = fig.add_subplot(111)
ax.set_title("Solar Eclipse 2nd October 2024", color="white")


m = Basemap(projection="ortho", lon_0=-115, lat_0=-20, resolution="l")
m.drawcoastlines(linewidth=0.1)
m.fillcontinents(color="darkgreen", lake_color="aqua")
m.drawparallels(np.arange(-90.0, 120.0, 15.0), linewidth=0.5)
m.drawmeridians(np.arange(0.0, 420.0, 30.0), linewidth=0.5)
m.drawmapboundary(fill_color="aqua", linewidth=0.1)

x, y = m(data_new[umbra_number, :, 0], data_new[umbra_number, :, 1])


x_in, y_in = m(data_new_in[umbra_number, :, 0], data_new_in[umbra_number, :, 1])


(line,) = ax.fill([], [], color="black", alpha=0.6, lw=0)
(line_in,) = ax.fill([], [], color="black", alpha=0.3, lw=0)


def init_in():
    line_in.set_xy(list(zip(x_in, y_in)))


def init():
    line.set_xy(list(zip(x, y)))
    return (line,)


def animate_in(i):
    cleandata = clean(data_new_in[i, :, :])
    x_in, y_in = m(cleandata[:, 0], cleandata[:, 1])

    #################
    # x_in,y_in = m(data_new_in[i,:,0],data_new_in[i,:,1])
    xy_in = zip(x_in, y_in)
    listxy_in = list(xy_in)
    line_in.set_xy(listxy_in)

    date_now = init_date + timedelta(seconds=data_new[i, 0, 2])
    ax.set_title(
        "Solar Eclipse {}".format(date_now.strftime("%d. %B %Y %H:%MUTC")),
        color="white",
    )

    return (line_in,)


def animate(i):
    cleandata = clean(data_new[i, :, :])
    x, y = m(cleandata[:, 0], cleandata[:, 1])
    # x,y = m(data_new[i,:,0],data_new[i,:,1])
    xy = zip(x, y)
    listxy = list(xy)
    line.set_xy(listxy)

    date_now = init_date + timedelta(seconds=data_new[i, 0, 2])
    ax.set_title(
        "Solar Eclipse {}".format(date_now.strftime("%d. %B %Y %H:%MUTC")),
        color="white",
    )
    return (line,)


ani = animation.FuncAnimation(
    fig, animate, np.arange(data_new.shape[0]), init_func=init, interval=2, blit=False
)  # arange(600) for test data
print("Animation finished!")

print("Rendering video file (this may take a while) ...")
writervideo = animation.FFMpegWriter(
    fps=15
)  # 600 Frames, 10 frames pro sekunde ergibt eine Minute Videolänge!
ani.save("umbra_animation.mp4", writer=writervideo, dpi=200)
# plt.savefig("./pictures/umbra.png", dpi = 100)

print("Rendering finished!")


"""
fig, ax = plt.subplots()
fig.patch.set_facecolor('black')
fig.patch.set_alpha(0.7)


m = Basemap(projection='ortho',lon_0=-115,lat_0=-20,resolution='l')
m.drawcoastlines(linewidth=0.1)
m.fillcontinents(color='darkgreen',lake_color='aqua')
m.drawparallels(np.arange(-90.,120.,15.),linewidth=0.5)
m.drawmeridians(np.arange(0.,420.,30.),linewidth=0.5)
m.drawmapboundary(fill_color='deepskyblue',linewidth=0.1)

data = np.array([
    -122.96,-10.035,7192986,
-122.63,-10.238,7192986,
-122.39,-10.521,7192986,
-122.27,-10.858,7192986,
-122.28,-11.216,7192986,
-122.42,-11.56,7192986,
-122.68,-11.857,7192986,
-123.02,-12.077,7192986,
-123.43,-12.199,7192986,
-123.85,-12.21,7192986,
-124.25,-12.109,7192986,
-124.58,-11.906,7192986,
-124.82,-11.62,7192986,
-124.94,-11.281,7192986,
-124.92,-10.921,7192986,
-124.78,-10.576,7192986,
-124.52,-10.28,7192986,
-124.17,-10.062,7192986,
-123.77,-9.9429,7192986,
-123.35,-9.9335,7192986
])
data = data.reshape((20,3))
dataappend = data[0,:]
data = np.append(data, dataappend[np.newaxis,:], axis = 0)
x, y = m(data[:,0], data[:,1])


#m.plot(data[:,0],data[:,1],latlon=True,color="black",linestyle="-",linewidth=0.3)
#ax.plot(x,y)
ax.fill(x,y,"black", alpha = 0.6)
plt.savefig("./sandbox/basemaptest.png", dpi = 300)
"""
