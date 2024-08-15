import os
import json
import math
import numpy as np
import matplotlib.pyplot as plt

def findGeoJson(folder):
    results = {}
    for f in os.scandir(folder):
        if f.is_dir():
            for f2 in os.scandir(f.path):
                if f2.is_file() and os.path.splitext(f2.path)[1]==".geojson":
                    #print(f2.path)
                    file = open(f2.path)
                    myJson = json.load(file)
                    results[f.name] = myJson
                    file.close()
    return results

EARTH_SEMIMAJORAXIS = 6378137
EARTH_FLATTENING = 1/298.257223563 

#ported from FGI-GSRx
def wgslla2xyz(wlat, wlon, walt):
    A_EARTH = EARTH_SEMIMAJORAXIS
    flattening = EARTH_FLATTENING

    NAV_E2 = (2-flattening)*flattening # also e^2
    deg2rad = math.pi/180

    slat = math.sin(wlat*deg2rad)
    clat = math.cos(wlat*deg2rad)
    r_n = A_EARTH/math.sqrt(1 - NAV_E2*slat*slat)
    return (
        (r_n + walt)*clat*math.cos(wlon*deg2rad),
        (r_n + walt)*clat*math.sin(wlon*deg2rad),
        (r_n*(1 - NAV_E2) + walt)*slat
    )

def geoJsonToECEF(geoJson):
    return map(lambda lla: wgslla2xyz(lla[1], lla[0], lla[2]), geoJson["geometry"]["coordinates"])

titleMap = {
    "myGPS_26":"GNSS-SDR: GPS position fixes @ 2.6MHz sample rate",
    "myGPS_15":"GNSS-SDR: GPS position fixes @ 15MHz sample rate",
    "myBeidou_26":"GNSS-SDR: Beidou position fixes @ 2.6MHz sample rate",
    "myBeidou_15":"GNSS-SDR: Beidou position fixes @ 15MHz sample rate",
    "myGalileo_26":"GNSS-SDR: Galileo position fixes @ 2.6MHz sample rate (SinBOC)",
    "myGalileo_15_sinBOC":"GNSS-SDR: Galileo position fixes @ 15MHz sample rate (SinBOC)",
    "myGalileo_15":"GNSS-SDR: Galileo position fixes @ 15MHz sample rate (CBOC)",
    "GPS_sdr_sim":"GNSS-SDR: GPS position fixes @ 2.6MHz sample rate (gps-sdr-sim)",
    "Galileo_sdr_sim":"GNSS-SDR: Galileo position fixes @ 2.6MHz sample rate (SinBOC) (galileo-sdr-sim)",
}

def main():
    print("run [min] [max] [mean] [std] [mean-target]")
    target = np.array([3908805, 319054, 5013110])
    geoJson = findGeoJson(".")
    for key in geoJson:
        ECEFs = np.fromiter(geoJsonToECEF(geoJson[key]), dtype=np.dtype((float, 3)))
        mean = np.mean(ECEFs, axis=0)
        std = np.std(ECEFs, axis=0)
        min = np.min(ECEFs, axis=0)
        max = np.max(ECEFs, axis=0)
        print(key, min, max, mean, std, mean-target)

        fig = plt.figure(figsize=(12,5))

        plt.subplot(1, 2, 1)
        plt.plot(ECEFs-target)
        plt.xlabel("Index of Position Fix over time")
        plt.ylabel("Distance (meter)")
        plt.title("Error over time")
        #plt.show()
        plt.subplot(1, 2, 2)
        plt.hist(ECEFs[:,0]-target[0], bins=48, alpha=0.7)
        plt.hist(ECEFs[:,1]-target[1], bins=48, alpha=0.7)
        plt.hist(ECEFs[:,2]-target[2], bins=48, alpha=0.7)
        plt.xlabel("Distance (meter)")
        plt.ylabel("Count")
        plt.title("Error Histogram")

        if key in titleMap:
            fig.suptitle(titleMap[key])
        else:
            fig.suptitle(key)
        plt.savefig("E:/Thesis/images/GNSS-SDR-Eval/"+key+".pdf")
        plt.show()
        

if __name__ == "__main__":
    main()