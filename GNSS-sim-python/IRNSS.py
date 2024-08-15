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
import RINEX
import orbit

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
        ["IODEC", "Crs", "deltan", "M0"],
        ["Cuc", "e", "Cus", "sqrt_a"],
        ["toe", "Cic", "omega0", "Cis"],
        ["i0", "Crc", "omega", "omegaDot"],
        ["IDot", "blank1", "WN", "blank2"],
        ["SV accuracy", "health_L5_S", "T_GD", "blank3"],
        ["transmit time", "blank4", "spare5", "spare6"]
    ]

def postProcessRINAXData(data, header):
    for sat in data:
        sat["frequency"] = 1575420000
        if sat["year"] < 1000:
            sat["year"] += 2000
        
        acc = sat["SV accuracy"]
        URA_steps = [2.4, 3.4, 4.85, 6.85, 9.65, 13.65, 24, 48, 96, 192, 384, 768, 1536, 3072, 6144]
        N=0
        while N<len(URA_steps) and acc>URA_steps[N]:
            N+=1
        sat["URA"] = N

        sat["datetime"] = datetime.datetime(sat["year"], sat["month"], sat["day"], sat["hour"], sat["minute"], sat["second"])

        sat["a_f0"] = sat["clockbias"]
        sat["a_f1"] = sat["clockdrift"]
        sat["a_f2"] = sat["clockdriftrate"]
        sat["t_oc"] = utcToConstelationTime(sat["datetime"])[0] #0 # for clock corection?

        sat["sv id"] = int(sat["name"][-2:])

        sat["a_0"] = header["alpha1"]
        sat["a_1"] = header["alpha2"]
        sat["a_2"] = header["alpha3"]
        sat["a_3"] = header["alpha4"]
        
        sat["b_0"] = header["beta1"]
        sat["b_1"] = header["beta2"]
        sat["b_2"] = header["beta3"]
        sat["b_3"] = header["beta4"]

        sat["t_LS"] = header["t_LS"]
        

##############################
#                            #
#      ORBIT SIMULATION      #
#                            #
##############################

def getSatPosVel(eph, t):
    tk = t[0] - eph["toe"]
    #satPos_old = orbit.mulSatpos(eph, tk)
    #satPosN_old = orbit.mulSatpos(eph, tk+1)
    #satVel_old = satPosN_old-satPos_old
    (satPos, satVel) = mulSatpos.getSatPosVel(eph, tk)
    #return (satPos_old, satVel_old)
    return (np.array([satPos]).T, np.array([satVel]).T)

def travelTimeCorection(eph, satPos, userPos, t):
    return ionosphere.calcIonoCorrections(userPos, satPos, eph, t[0])/const.SPEED_OF_LIGHT

def utcToConstelationTime(dateTime : datetime.datetime):
    epochStart = datetime.datetime(year=1999, month=8, day=22)
    delta = dateTime-epochStart
    WN = delta.days//7
    weekStart = epochStart+datetime.timedelta(days=WN*7)
    delta = (dateTime-weekStart)
    TOW = delta.days*24*60*60 + delta.seconds + delta.microseconds/1000000
    return (TOW, WN)

def clockCorection(sat, syncTime):
    t_oc = 0
    dt = syncTime[0] - t_oc
    satClkCorr = (sat["clockdriftrate"] * dt + sat["clockdrift"]) * dt + sat["clockbias"]

    t_GD = sat["T_GD"]

    # relativistic corection, uses 0.1s old data, but should be beter than nothing
    if "E_k" in sat:
        F = -2*math.sqrt(const.EARTH_GRAVCONSTANT)/const.SPEED_OF_LIGHT**2
        relcorr = F * sat["e"] * sat["sqrt_a"] * math.sin(sat["E_k"])
        #print("relcorr:", relcorr)
        satClkCorr += relcorr

    return (syncTime[0]-satClkCorr + t_GD, syncTime[1]) # could be +, since i do inverse of reciever

def timeDifference(t1, t2):
    return t1[0]-t2[0]

####################################
#                                  #
#      NAV MESSAGE GENERATION      #
#                                  #
####################################

def stringToArray(dataString):
    dataBin = []
    for char in dataString:
        if char=='0':
            dataBin.append(0)
        if char=='1':
            dataBin.append(1)
    return dataBin

SYNC = stringToArray("1110101110010000")

def fillBuffer(bitBuffer, dateTime:datetime.datetime, eph, ephs):
    if(dateTime.microsecond!=0 and dateTime.second%12!=0):
        print("not aligned")
        return [0]
    
    subframe = ((dateTime.minute*60+dateTime.second)//12)%4

    data = [1]*232

    if subframe+1==1:
        data = NavMessage.dataStructureToBits(data1, eph, twosCompliment=True, spareData={})
    if subframe+1==2:
        data = NavMessage.dataStructureToBits(data2, eph, twosCompliment=True, spareData={})
    if subframe+1==3 or subframe+1==4:
        if "MessageIndex" not in bitBuffer.store:
            bitBuffer.store["MessageIndex"] = 0
        messageIndex = bitBuffer.store["MessageIndex"] # page
        bitBuffer.store["MessageIndex"] = (messageIndex+1)%len(message_sequence)
        data = getMessage(message_sequence[messageIndex], eph, ephs)

    return SYNC + encode_subframe(packageSubFrame(subframe, data, eph, dateTime))

# 7 is almonac, second is sat, 14 is differential correction, 26 is time, ...
message_sequence = [[7, "I01"], [7, "I02"], [7, "I03"], [7, "I04"], [7, "I05"], [7, "I06"], [7, "I07"], [7, "I08"], [7, "I09"], [7, "I10"]]
almanac = [["WN", 10], ["e", 16, 2**21], ["toa", 16, 2**-4], ["i0", 24, 2**23/math.pi], ["omegaDot", 16, 2**38/math.pi], ["sqrt_a", 24, 2**11], ["omega0", 24, 2**23/math.pi], ["omega", 24, 2**23/math.pi], ["M0", 24, 2**23/math.pi], ["a_f0", 11, 2**20], ["a_f1", 11, 2**38], ["sv id", 6], ["T_GD", 8, 2**31], [0, 6]]

data1 = [["WN", 10], ["a_f0", 22, 2**31], ["a_f1", 16, 2**43], ["a_f2", 8, 2**55], ["URA", 4], ["t_oc", 16, 1/16], ["T_GD", 8, 2**31],
         ["deltan", 22, 2**41/math.pi], ["IODEC", 8], [0, 10], ["health_L5_S", 2], 
         ["Cuc", 15, 2**28], ["Cus", 15, 2**28], ["Cic", 15, 2**28], ["Cis", 15, 2**28], ["Crc", 15, 2**4], ["Crs", 15, 2**4],
         ["IDot", 14, 2**43/math.pi], [0, 2]
         ]

data2 = [["M0", 32, 2**31/math.pi], ["toe", 16, 1/16], ["e", 32, 2**33], ["sqrt_a", 32, 2**19], ["omega0", 32, 2**31/math.pi], ["omega", 32, 2**31/math.pi], ["omegaDot", 22, 2**41/math.pi], ["i0", 32, 2**31/math.pi], [0, 2]]

def getMessage(id, eph, ephs):
    message = None
    if id[0] == 7:
        if id[1] in eph:
            message = NavMessage.dataStructureToBits(almanac, ephs[id[1]])
        else:
            message = [0]*220
    else:
        print("message not implemented, using 0")
        message = [0]*220
    
    return NavMessage.numToBits(id[0], 6) + message + NavMessage.numToBits(eph["sv id"], 6)

def indexOrZero(data, index):
    if index<0 or index>=len(data):
        return 0
    else:
        return data[index]

def encode_subframe(bits):
    tbits = [0]*6+bits
    G1 = lambda i : tbits[i+6 -0] ^ tbits[i+6 -1] ^ tbits[i+6 -2] ^ tbits[i+6 -3] ^ tbits[i+6 -6]
    G2 = lambda i : tbits[i+6 -0] ^ tbits[i+6 -2] ^ tbits[i+6 -3] ^ tbits[i+6 -5] ^ tbits[i+6 -6]

    FEC = [0]*584
    for i in range(292):
        FEC[2*i+0] = G1(i)
        FEC[2*i+1] = G2(i)

    assert len(bits)==292
    return NavMessage.interleave(FEC, 8, 73)


def packageSubFrame(subframe, data, eph, dateTime:datetime.datetime):
    assert len(data)==232
    #TLM(8) : reserved for later use
    #TOWC(17) : time of week (12 secconds), start of sub frame
    #alert flag : use sat at own risk
    #AutoNav : sat is using AutoNav data
    #subframe id
    #spare bit
    #(message id)
    #(this sat prn)
    #data
    #CRC
    #tail
    (TOWC, WN) = utcToConstelationTime(dateTime)#+datetime.timedelta(seconds=12))

    start = NavMessage.dataStructureToBits([
            ["TLM", 8], ["TOWC", 17, 1/12], ["ALERT", 1], ["AUTONAV", 1], ["subframe", 2], [0, 1]
            ], eph, twosCompliment=True, spareData={"TLM":0, "TOWC":TOWC, "ALERT":0, "AUTONAV":0, "subframe":subframe})

    main = start+data

    CRC = NavMessage.crc_remainder(main, stringToArray("1101111100110010011000011"), 0)

    return main+CRC+[0]*6
    
#############################
#                           #
#      PACKAGE FOR USE      #
#                           #
#############################

def getConstelation():
    constelation = Constelation.Constelation()
    constelation.prefix="I"
    constelation.bitsPerFrame = 5
    constelation.RINEXDataRecordDesciption = getRINEXDataRecordDesciption()
    constelation.RINEXheaderDescription = [
        ["IRNA", ["alpha1", RINEX.parse_float], ["alpha2", RINEX.parse_float], ["alpha3", RINEX.parse_float], ["alpha4", RINEX.parse_float], "IONOSPHERIC", "CORR"],
        ["IRNB", ["beta1",  RINEX.parse_float], ["beta2",  RINEX.parse_float], ["beta3",  RINEX.parse_float], ["beta4",  RINEX.parse_float], "IONOSPHERIC", "CORR"],
        ["IRUT", ["a0", RINEX.parse_float], ["a1", RINEX.parse_float], ["TOW", int], ["WN", int], "TIME", "SYSTEM", "CORR"],
    ]
    constelation.postProcessRINAXData = postProcessRINAXData
    constelation.utcToConstelationTime = utcToConstelationTime
    constelation.clockCorection = clockCorection
    constelation.timeDifference = timeDifference
    constelation.getSatPosVel = getSatPosVel
    constelation.travelTimeCorection = travelTimeCorection
    constelation.fillBuffer = fillBuffer
    constelation.getSetupHeader = lambda sats: "I:("+",".join(map(lambda name: name[-2:]+"[]", sats))+")"

    return constelation