import datetime
import math
import numpy as np

import Satallite
import orbit
import NavMessage

import Glonass
import Galileo
import GPS
import BeiDou
import IRNSS

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
            travelTimeDx = orbit.getTravelTime(userPos+np.array([[1],[0],[0]]), satPos, eph)-travelTime
            travelTimeDy = orbit.getTravelTime(userPos+np.array([[0],[1],[0]]), satPos, eph)-travelTime
            travelTimeDz = orbit.getTravelTime(userPos+np.array([[0],[0],[1]]), satPos, eph)-travelTime
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
            #delay = 0
            #doplerShift = 0
            #doplerShift = 0
            #delay=0
            #power=100

            data = sat.bitBuffer.getBits(sat.constelation.bitsPerFrame, dateTime, eph, ephs)
            #frameData.append("{}:{}_{:.9f}_{:.4f}_{}".format(name, NavMessage.bitsToHex(data), delay*1000, doplerShift, power))
            frameData.append("{}:{}_{:.9f}_{:.4f}_{}_{:.4f}_{:.4f}_{:.4f}".format(name, NavMessage.bitsToHex(data), delay*1000, doplerShift, power, travelTimeDx*1000000000, travelTimeDy*1000000000, travelTimeDz*1000000000))
            results[name] = {"data":data, "delay":delay*1000, "shift":doplerShift, "power":power, "eph":eph, "constelation":sat.constelation, "satPos":satPos, "D":[travelTimeDx, travelTimeDy, travelTimeDz]}
        i+=1
    return ("data "+",".join(frameData)+"\n", results)

def printResults(time, results, userPos, userVel):
    #userPos = np.array([[4687282.796],[1840346.018],[4055083.320]])
    ps = ""
    for name in results:
        #print("\033[F", end="")
        ps = ps+"\033[F"
    ps = ps+"\033[F\033[F\033[J" + (" "*150) + "\n"
    #print("\033[F", end="")
    #print("\033[F", " "*50)

    #print("time:", time.strftime('%F %T.%f')[:-3], "@", userPos.T[0], "v:", userVel.T[0], " "*10)
    ps = ps + "time:" + time.strftime('%F %T.%f')[:-3] + "@" + str(userPos.T[0]) + "v:" + str(userVel.T[0]) + (" "*15)
    for name in results:
        result = results[name]
        elevation, azimuth, alivation = orbit.calcAzimElevDist(userPos, result["satPos"]-userPos)
        ps = ps + ("\n{} : {:3.0f} @ {} {:10.6f} {:10.4f}, {} ([{:11.1f} {:11.1f} {:11.1f}], [{:9.6f} {:9.6f} {:5.1f}])   ".format(name, result["power"], result["constelation"].getIdString(result["eph"]), result["delay"], result["shift"], "".join(map(str,result["data"])), result["satPos"][0][0], result["satPos"][1][0], result["satPos"][2][0], elevation, azimuth, alivation))
        #print("{} : {:3.0f} @ {} {:10.6f} {:10.4f}, {} ([{:11.1f} {:11.1f} {:11.1f}], [{:9.6f} {:9.6f} {:5.1f}])".format(name, result["power"], result["constelation"].getIdString(result["eph"]), result["delay"], result["shift"], "".join(map(str,result["data"])), result["satPos"][0][0], result["satPos"][1][0], result["satPos"][2][0], elevation, azimuth, alivation))
        #print(name, ":", result["power"], "@", result["constelation"].getIdString(result["eph"]), result["delay"], result["shift"], result["data"], " "*10)
    print(ps, end="")

def selectSats(sats, names):
    newSats = {}
    for satName in names:
        newSats[satName] = sats[satName]
    return newSats

def main():
    print("main")

    #constelation = Glonass.getConstelation()
    #rinexFile = "data/Glonass/ANK200TUR_S_20240110000_01D_RN.rnx"
    #resultFile = "data/glonass.txt"
    
    #constelation = Galileo.getConstelation()
    #rinexFile = "data/Galileo/IZMI00TUR_S_20233320000_01D_EN.rnx"
    #rinexFile = "\\\\wsl.localhost\\Ubuntu\\home\\mike\\galileo-sdr-sim\\rinex_files\\week171.rnx"
    #resultFile = "data/galileo.txt"

    constelation = GPS.getConstelation()
    rinexFile = "data/GPS/brdc3240.23n"
    resultFile = "data/gps.txt"

    #constelation = BeiDou.getConstelation()
    #rinexFile = "data/BeiDou/Brdc0530.24f"
    #resultFile = "data/beidou.txt"

    #constelation = IRNSS.getConstelation()
    #rinexFile = "data/IRNSS/KRGG00ATF_R_20240530000_01D_IN.rnx"
    #resultFile = "data/irnss.txt"


    #startTime = datetime.datetime(2024,2,21, 23,00) # IRNSS
    #startTime = datetime.datetime(2024,2,22, 1,0) # BeiDou
    #startTime = datetime.datetime(2024,1,11, 2, 0) # glonass
    startTime = datetime.datetime(2023,11,20, 0, 0) # gps
    #startTime = datetime.datetime(2023,11,21, 23, 59, 54) # gps
    #startTime = datetime.datetime(2023,11,27, 23, 45) # galileo?
    #startTime = datetime.datetime(2021,6,20, 0, 0) # galileo week 171?
    
    
    duration = datetime.timedelta(seconds=181)



    sats, headerData = constelation.loadSatsFromRinax(rinexFile)
    #sats = { "G02":sats["G02"], "G1002":sats["G03"]} #
    #sats = selectSats(sats, ["G01", "G02", "G03", "G04", "G08", "G14", "G17", "G19", "G21", "G22", "G28", "G31", "G32"])
    #sats = selectSats(sats, ["G01", "G02", "G03", "G04", "G08", "G14", "G17", "G19"])
    #sats = selectSats(sats, ["G01", "G02", "G03", "G04", "G08", "G14"])
    #sats = selectSats(sats, ["G01"])
    #sats = {"G01":sats["G01"]}
    #sats = {"G02":sats["G02"], "G03":sats["G03"], "G08":sats["G08"], "G10":sats["G10"], "G14":sats["G14"]}
    #sats = {"E07":sats["E07"], "E08":sats["E08"], "E12":sats["E12"], "E13":sats["E13"], "E19":sats["E19"]}
    #sats = {"E02":sats["E02"]}
    #sats = {"E04":sats["E04"], "E05":sats["E05"], "E09":sats["E09"], "E10":sats["E10"], "E11":sats["E11"], "E12":sats["E12"], "E18":sats["E18"], "E34":sats["E34"], "E36":sats["E36"]}
    #sats = selectSats(sats, ["E04", "E05", "E09", "E10", "E11", "E12", "E34", "E36"])
    #sats = {"R01":sats["R01"]}
    #sats = {"R01":sats["R01"], "R09":sats["R09"], "R17":sats["R17"], "R23":sats["R23"], "R24":sats["R24"]}
    #sats = selectSats(sats, ["R01", "R02", "R07", "R09", "R10", "R11", "R17", "R23", "R24"])
    #sats = {"I02":sats["I02"]}
    #del sats["C01"], sats["C02"], sats["C03"], sats["C04"], sats["C05"]
    #sats = {"C06":sats["C06"]}
    #sats = {"C06":sats["C06"], "C09":sats["C09"], "C12":sats["C12"], "C16":sats["C16"], "C19":sats["C19"], "C20":sats["C20"], "C22":sats["C22"]}
    #del sats["E33"]
    setup = constelation.getSetupHeader(sats)

    print("min(min), max(min), min(max), max(max)")
    for time in Satallite.getGoodRange(sats):
        print(time)
    print("\n"*10)

    timestep = datetime.timedelta(milliseconds=100) # hardcoded 0.1s
    endTime = startTime+duration

    #userPos = np.array([[3992112.0],[4929847.0],[-662268.0]])
    #userPos = np.array([[4541995.72232094],[833907.206476633],[4384738.7981905]]) # piza
    #userPos = np.array([[1239522], [5463155], [3039514]]) # new deli
    userPos = np.array([[-2758918.635941], [4772301.120089], [3197889.437237]]) # gps-sdr-sim
    userVel = np.array([[0],[0],[0]])

    perpPos = np.array([userPos[0], -userPos[2], userPos[1]])
    perpPos /= math.sqrt(perpPos[0][0]**2 + perpPos[1][0]**2 + perpPos[2][0]**2)
    syncErrorPos = np.array([[0.1], [0.05], [0.15]])

    # fixed position
    posVelFunc = simplePathInterpolation([(startTime, userPos)])

    # slow move away
    #posVelFunc = simplePathInterpolation([
    #    #(startTime+datetime.timedelta(seconds=0),  userPos+1000*perpPos), 
    #    (startTime+datetime.timedelta(seconds=37), userPos             +syncErrorPos),  
    #    (startTime+datetime.timedelta(seconds=38), userPos-1*perpPos   +syncErrorPos),
    #    (startTime+datetime.timedelta(seconds=39), userPos-3*perpPos   +syncErrorPos),
    #    (startTime+datetime.timedelta(seconds=40), userPos-6*perpPos   +syncErrorPos),
    #    (startTime+datetime.timedelta(seconds=41), userPos-10*perpPos  +syncErrorPos),
    #    (startTime+datetime.timedelta(seconds=60), userPos-105*perpPos +syncErrorPos)
    #    #(startTime+datetime.timedelta(seconds=45), userPos), 
    #    #(startTime+datetime.timedelta(seconds=60), userPos-300*perpPos)
    #])

    # sweep past
    #posVelFunc = simplePathInterpolation([
    #    (startTime+datetime.timedelta(seconds=10), userPos-200*perpPos  +syncErrorPos),
    #    (startTime+datetime.timedelta(seconds=30), userPos-90*perpPos  +syncErrorPos),
    #    (startTime+datetime.timedelta(seconds=60), userPos+90*perpPos  +syncErrorPos)
    #    #(startTime+datetime.timedelta(seconds=45), userPos), 
    #    #(startTime+datetime.timedelta(seconds=60), userPos-300*perpPos)
    #])

    

    outputFile = open(resultFile, "w")
    outputFile.write("setup "+setup+"\n")

    time = startTime

    while time <= endTime:
        #print("time:", time, end="\r")
        t = time.second+time.microsecond/1000000
        #print(t)
        #posOscillation = np.array([[math.sin(2*t/math.pi)],[math.sin(2*t/math.pi)],[math.sin(2*t/math.pi)]]) * 25
        #print(posOscillation)
        (pos, vel) = posVelFunc(time)
        (dataString, result) = generateFrame(pos, vel, sats, time)
        printResults(time, result, pos, vel)
        outputFile.write(dataString)
        time += timestep

    outputFile.close()

    #print(generateFrame(userPos, userVel, sats, time)[0])

    print("Done")

def simplePathInterpolation(timePosPairs: tuple[datetime.datetime, np.ndarray]):
    timePosPairs = sorted(timePosPairs)
    def getPosVelAtTime(time):
        index = 0
        for timePos in timePosPairs:
            if timePos[0]>time:
                break
            index+=1
        start = timePosPairs[index-1] if index>0 else (time, timePosPairs[0][1])
        end   = timePosPairs[index] if index<len(timePosPairs) else (start[0]+datetime.timedelta(seconds=1), start[1])
        span = (end[0]-start[0])
        span_s = span.microseconds/1000000 + span.seconds + span.days*24*60*60

        current = (time-start[0])
        current_s = current.microseconds/1000000 + current.seconds + current.days*24*60*60

        posNow = start[1] + current_s/span_s * (end[1]-start[1])
        velNow = (end[1]-start[1])/span_s

        return (posNow, velNow)
    return getPosVelAtTime

if __name__ == "__main__":
    main()