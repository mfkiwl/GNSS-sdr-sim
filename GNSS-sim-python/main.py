import datetime
import math
import numpy as np

import Satallite
import orbit
import NavMessage

import Glonass
import Galileo
import GPS

SPEED_OF_LIGHT = 299792458

def generateFrame(userPos, userVel, sats: dict[str, Satallite.Satallite], dateTime: datetime.datetime):
    
    frameData = []
    
    ephs = {}
    for name in sats:
        ephs[name] = sats[name].eph.get(dateTime)

    

    results = {}
    i = 0
    delay_0 = None
    
    #print()
    #print(dateTime)
    for name in sats:
        sat = sats[name]
        eph = ephs[name]
        eph = sat.constelation.checkEphemeris(eph, dateTime)
        if eph is None:
            frameData.append("{}:{}_{:.1f}_{:.1f}_{}".format(name, "0", 0, 0, 0))
        else:
            syncTime = sat.constelation.utcToConstelationTime(dateTime)
            transmitTime = sat.constelation.clockCorection(eph, syncTime)
            satPos, satVel = sat.constelation.getSatPosVel(eph, transmitTime)
            travelTime = orbit.getTravelTime(userPos, satPos, eph)
            doplerShift = orbit.getDoplerShift(userPos, userVel, satPos, satVel, eph)  # add user pos and vel
            power = orbit.getVisability(userPos, satPos, eph) # how visable was the currect location at the of transmition
            #arivelTime = transmitTime + travelTime
            #delay = arivelTime - transmitTime
            delay = travelTime + sat.constelation.timeDifference(transmitTime, syncTime)
            travelTimeCorrection = sat.constelation.travelTimeCorection(eph, satPos, userPos, syncTime)
            delay += travelTimeCorrection
            earthRotationCorection = orbit.earthRotationCorrection(satPos, userPos)
            delay += earthRotationCorection
            #print(earthRotationCorection)


            #delay = i/50/20/5 + i/50/20

            #if delay_0==None:
            #    delay_0=delay
            #print(name, (delay-delay_0)*1000)

            #print(name, delay*SPEED_OF_LIGHT-21807950.99675922+25386264.284501)

            data = sat.bitBuffer.getBits(sat.constelation.bitsPerFrame, dateTime, eph, ephs)
            frameData.append("{}:{}_{:.9f}_{:.4f}_{}".format(name, NavMessage.bitsToHex(data), delay*1000, doplerShift, power))
            results[name] = {"data":data, "delay":delay*1000, "shift":doplerShift, "power":power, "eph":eph, "constelation":sat.constelation, "satPos":satPos}
        i+=1
    return ("data "+",".join(frameData)+"\n", results)

def printResults(time, results, userPos):
    userPos = np.array([[4687282.796],[1840346.018],[4055083.320]])
    for name in results:
        print("\033[F", end="")
    print("\033[F", end="")
    print("\033[F", " "*50)

    print("time:", time, " "*10)
    for name in results:
        result = results[name]
        elevation, azimuth, alivation = orbit.calcAzimElevDist(userPos, result["satPos"]-userPos)
        print("{} : {:3.0f} @ {} {:10.6f} {:10.4f}, {} ([{:11.1f} {:11.1f} {:11.1f}], [{:9.6f} {:9.6f} {:5.1f}])".format(name, result["power"], result["constelation"].getIdString(result["eph"]), result["delay"], result["shift"], result["data"], result["satPos"][0][0], result["satPos"][1][0], result["satPos"][2][0], elevation, azimuth, alivation))
        #print(name, ":", result["power"], "@", result["constelation"].getIdString(result["eph"]), result["delay"], result["shift"], result["data"], " "*10)
    

def main():
    print("main")

    constelation = Glonass.getConstelation()
    rinexFile = "data/Glonass/ANK200TUR_S_20240110000_01D_RN.rnx"
    resultFile = "data/glonass.txt"
    
    #constelation = Galileo.getConstelation()
    #rinexFile = "data/Galileo/IZMI00TUR_S_20233320000_01D_EN.rnx"
    #resultFile = "data/galileo.txt"

    #constelation = GPS.getConstelation()
    #rinexFile = "data/GPS/brdc3260.23n"
    #resultFile = "data/gps.txt"


    startTime = datetime.datetime(2024,1,11, 2, 0) # glonass
    #startTime = datetime.datetime(2023,11,22, 4, 0) # gps
    duration = datetime.timedelta(seconds=210)



    sats, headerData = constelation.loadSatsFromRinax(rinexFile)
    #sats = {"G01":sats["G01"]}
    #sats = {"G02":sats["G02"], "G03":sats["G03"], "G08":sats["G08"], "G10":sats["G10"], "G14":sats["G14"], "G21":sats["G21"], "G22":sats["G22"], "G27":sats["G27"], "G32":sats["G32"]}
    #sats = {"G01":sats["G01"]}
    #sats = {"G02":sats["G02"], "G03":sats["G03"], "G08":sats["G08"], "G10":sats["G10"], "G14":sats["G14"]}
    #sats = {"E07":sats["E07"], "E08":sats["E08"], "E12":sats["E12"], "E13":sats["E13"], "E19":sats["E19"]}
    #sats = {"E07":sats["E07"]}
    #sats = {"E04":sats["E04"], "E05":sats["E05"], "E09":sats["E09"], "E10":sats["E10"], "E11":sats["E11"], "E12":sats["E12"], "E18":sats["E18"], "E34":sats["E34"], "E36":sats["E36"]}
    #sats = {"R01":sats["R01"], "R09":sats["R09"], "R17":sats["R17"], "R23":sats["R23"], "R24":sats["R24"]}
    setup = constelation.getSetupHeader(sats)

    print("min(min), max(min), min(max), max(max)")
    for time in Satallite.getGoodRange(sats):
        print(time)
    print("\n"*10)

    timestep = datetime.timedelta(milliseconds=100) # hardcoded 0.1s
    endTime = startTime+duration

    userPos = np.array([[4541995.72232094],[833907.206476633],[4384738.7981905]])
    userVel = np.array([[0],[0],[0]])

    outputFile = open(resultFile, "w")
    outputFile.write("setup "+setup+"\n")

    time = startTime

    while time <= endTime:
        #print("time:", time, end="\r")
        t = time.second+time.microsecond/1000000
        #print(t)
        #posOscillation = np.array([[math.sin(2*t/math.pi)],[math.sin(2*t/math.pi)],[math.sin(2*t/math.pi)]]) * 25
        #print(posOscillation)
        (dataString, result) = generateFrame(userPos, userVel, sats, time)
        printResults(time, result, userPos)
        outputFile.write(dataString)
        time += timestep

    outputFile.close()

    #print(generateFrame(userPos, userVel, sats, time)[0])

    print("Done")

if __name__ == "__main__":
    main()