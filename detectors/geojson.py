import json
import numpy as np
import matplotlib.pyplot as plt

# function lla2ecef from https://github.com/kvenkman/ecef2lla/blob/master/lla2ecef.py
# The conversion from WGS-84 to Cartesian has an analytical solution
def lla2ecef(lon, lat, alt):
    a = 6378137
    a_sq = a**2
    e = 8.181919084261345e-2
    e_sq = e**2
    b_sq = a_sq*(1 - e_sq)

    #lat = np.array([lat]).reshape(np.array([lat]).shape[-1], 1)*np.pi/180
    #lon = np.array([lon]).reshape(np.array([lon]).shape[-1], 1)*np.pi/180
    #alt = np.array([alt]).reshape(np.array([alt]).shape[-1], 1)

    lat = lat*np.pi/180
    lon = lon*np.pi/180
    alt = alt

    N = a/np.sqrt(1 - e_sq*np.sin(lat)**2)
    x = (N+alt)*np.cos(lat)*np.cos(lon)
    y = (N+alt)*np.cos(lat)*np.sin(lon)
    z = ((b_sq/a_sq)*N+alt)*np.sin(lat)
    return x, y, z


#f = open('E:/Thesis/GNSS-SDR/myGPS/pvt.dat_240630_134529.geojson')
f = open('E:/Thesis/GNSS-SDR/myGPSlong/pvt.dat_240701_144243.geojson')
target = np.array([-2758918.635941, 4772301.120089, 3197889.437237])
target = np.array([lla2ecef(120.032669, 30.286502, 100)])
print("target:", target)

data = json.load(f)

llh_cords = data["geometry"]["coordinates"]
print(llh_cords[0])

ecef_cords = np.array(list(map(lambda llh: np.array([*lla2ecef(*llh)]), llh_cords)))

mean = np.mean(ecef_cords[-60:], axis=0)
print("mean:", mean)
#target = mean

offsets = ecef_cords-target
offsetx = offsets[:,0]
offsety = offsets[:,1]
offsetz = offsets[:,2]

plt.plot(offsetx, label="x Offset ECEF")
plt.plot(offsety, label="y Offset ECEF")
plt.plot(offsetz, label="z Offset ECEF")
plt.plot(np.linalg.norm(offsets, axis=1), label="Distance From Target")
plt.xlabel("Time (Seconds)")
plt.ylabel("Distance (Meters)")
plt.legend()
plt.grid()
plt.show()

stable = ecef_cords#[60:]
mean = np.mean(stable, axis=0)
dists = np.linalg.norm(stable-mean, axis=1)

plt.hist(dists, bins=100, range=[0.1, 0.3])#[0.1, 0.3], [1.55, 1.95]
plt.xlabel("Distance (Meters)")
plt.ylabel("Probability Density")
plt.show()
