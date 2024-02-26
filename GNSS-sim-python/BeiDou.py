import datetime
import math
import numpy as np
from scipy.integrate import odeint

import NavMessage
import Constelation
import Galileo
import const
import mulSatpos
import ionosphere

###########################
#                         #
#      RINEX PARSING      #
#                         #
###########################

def float_int(x):
    return int(float(x))

def getRINEXDataRecordDesciption():
    #"-tau(t_b)" : negative clock corection, "gamma(t_b)" : requency corection
    #"message frame time" second in week
    #"n" : transmition index
    return [
        [["name", str], ["year", int], ["month", int], ["day", int], ["hour", int], ["minute", int], ["second", float_int], "clockbias", "clockdrift", "clockdriftrate"],
        ["AODE", "Crs", "deltan", "M0"],
        ["Cuc", "e", "Cus", "sqrt_a"],
        ["toe", "Cic", "omega0", "Cis"],
        ["i0", "Crc", "omega", "omegaDot"],
        ["IDot", "spare1", "WN", "spare2"],
        ["SV accuracy", "health", "TGD1", "TGD2"],
        ["transmit time"]
        #["transmit time", "AODC", "spare3", "spare4"]
    ]

def indexOrDefault(data, index, default):
    return data[index] if index in data else default

def postProcessRINAXData(data, header):
    for sat in data:
        sat["frequency"] = 1575420000
        if sat["year"] < 1000:
            sat["year"] += 2000
        
        sat["a_f0"] = sat["clockbias"]
        sat["a_f1"] = sat["clockdrift"]
        sat["a_f2"] = sat["clockdriftrate"]
        sat["t_oc"] = 0 # for clock corection?

        sat["sv id"] = int(sat["name"][-2:])

        sat["a_0"] = indexOrDefault(header, "alpha1", 0)
        sat["a_1"] = indexOrDefault(header, "alpha2", 0)
        sat["a_2"] = indexOrDefault(header, "alpha3", 0)
        sat["a_3"] = indexOrDefault(header, "alpha4", 0)
        
        sat["b_0"] = indexOrDefault(header, "beta1", 0)
        sat["b_1"] = indexOrDefault(header, "beta2", 0)
        sat["b_2"] = indexOrDefault(header, "beta3", 0)
        sat["b_3"] = indexOrDefault(header, "beta4", 0)

        sat["t_LS"] = indexOrDefault(header, "t_LS", 0)
        
        sat["datetime"] = datetime.datetime(sat["year"], sat["month"], sat["day"], sat["hour"], sat["minute"], sat["second"])
        
##############################
#                            #
#      ORBIT SIMULATION      #
#                            #
##############################

def getSatPosVel(eph, t):
    tk = t[0] - eph["toe"]
    satPos_old = Galileo.getSatPos(eph, tk)
    satPosN_old = Galileo.getSatPos(eph, tk+1)
    satVel_old = satPosN_old-satPos_old
    (satPos, satVel) = mulSatpos.getSatPosVel(eph, tk)
    #return (satPos_old, satVel_old)
    return (np.array([satPos]).T, np.array([satVel]).T)

def travelTimeCorection(eph, satPos, userPos, t):
    return ionosphere.calcIonoCorrections(userPos, satPos, eph, t[0])/const.SPEED_OF_LIGHT

def utcToConstelationTime(dateTime : datetime.datetime):
    epochStart = datetime.datetime(year=1980, month=1, day=6)
    delta = dateTime-epochStart
    WN = delta.days//7 # was /
    weekStart = epochStart+datetime.timedelta(days=WN*7)
    delta = (dateTime-weekStart)
    TOW = delta.days*24*60*60 + delta.seconds + delta.microseconds/1000000
    return (TOW, WN)

def clockCorection(sat, syncTime):
    t_oc = 0
    dt = syncTime[0] - t_oc
    satClkCorr = (sat["clockdriftrate"] * dt + sat["clockdrift"]) * dt + sat["clockbias"]

    t_GD = 0#sat["T_GD"]

    # relativistic corection, uses 0.1s old data, but should be beter than nothing
    #if "E_k" in sat:
    #    F = -2*math.sqrt(const.EARTH_GRAVCONSTANT)/const.SPEED_OF_LIGHT**2
    #    relcorr = F * sat["e"] * sat["sqrt_a"] * math.sin(sat["E_k"])
    #    #print("relcorr:", relcorr)
    #    satClkCorr += relcorr

    return (syncTime[0]-satClkCorr + t_GD, syncTime[1]) # could be +, since i do inverse of reciever

def timeDifference(t1, t2):
    return t1[0]-t2[0]

####################################
#                                  #
#      NAV MESSAGE GENERATION      #
#                                  #
####################################

def fillBuffer(bitBuffer, dateTime:datetime.datetime, eph, ephs):
    if(dateTime.microsecond!=0 and dateTime.second%6!=0):
        print("not aligned")
        return [0]

    if eph["sv id"]<6: # D2
        return [0]
    else: # D1
        subframe = (dateTime.second/6)%5
        frame = ((dateTime.minute+dateTime.second)/30)%24
        # super frame (12 min / 36000 bits)
        # 24 frames (30 s / 1500 bits)
        #    5 subframes (6 s / 300 bits) : SYNC(11100010010) (first 15 bits not encoded, next 11 BCH(15, 11, 1): first 30 bit word with sync (26 info bit)) ( next 9 words, 2x BCH (22 info bits))
        #      10 words (0.6 s / 30 bits)
        return [0]

    return [1]

SYNC = [1,1,1,0,0,0,1,0,0,1,0]

def encode_subframe(data):
    assert len(data) == 4 + 11*(1+9*2)
    encoded = SYNC + data[0:4] + BCH(data[4:4+11])
    for i in range(9):
        a = BCH(data[4+11+11*2*i+ 0:4+11+11*2*i+11])
        b = BCH(data[4+11+11*2*i+11:4+11+11*2*i+22])
        encoded.append([val for pair in zip(a, b) for val in pair])
    return encoded

def BCH(data):
    D0 = 0
    D1 = 0
    D2 = 0
    D3 = 0

    for b in data:
        G1 = D3^b
        D3 = D2
        D2 = D1
        D1 = G1^D0
        D0 = G1

    return data + [D3, D2, D1, D0]

#############################
#                           #
#      PACKAGE FOR USE      #
#                           #
#############################

def getConstelation():
    constelation = Constelation.Constelation()
    constelation.prefix="C"
    constelation.bitsPerFrame = lambda eph: 50 if eph["sv id"]<6 else 5
    constelation.RINEXDataRecordDesciption = getRINEXDataRecordDesciption()
    constelation.postProcessRINAXData = postProcessRINAXData
    constelation.utcToConstelationTime = utcToConstelationTime
    constelation.clockCorection = clockCorection
    constelation.timeDifference = timeDifference
    constelation.getSatPosVel = getSatPosVel
    constelation.travelTimeCorection = travelTimeCorection
    constelation.fillBuffer = fillBuffer
    constelation.getSetupHeader = lambda sats: "B1c:("+",".join(map(lambda name: name[-2:]+"[]", sats))+")"

    return constelation