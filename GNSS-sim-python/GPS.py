import datetime
import math
import numpy as np
from scipy.integrate import odeint

import RINEX
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
        ["IODE", "Crs", "deltan", "M0"],
        ["Cuc", "e", "Cus", "sqrt_a"],
        ["toe", "Cic", "omega0", "Cis"],
        ["i0", "Crc", "omega", "omegaDot"],
        ["IDot", "codes_on_L2", "Continues WN", "L2_P_data_flag"],
        ["SV accuracy", "health", "T_GD", "IODC"],
        ["transmit time", "fit interval (BNK)", "spare1", "spare2"]
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
        sat["URA_index"] = N

        sat["a_f0"] = sat["clockbias"]
        sat["a_f1"] = sat["clockdrift"]
        sat["a_f2"] = sat["clockdriftrate"]

        sat["AODO"] = 0
        #sat["data id"] = 0b01
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
        
        sat["datetime"] = datetime.datetime(sat["year"], sat["month"], sat["day"], sat["hour"], sat["minute"], sat["second"])
        sat["t_oa"] = utcToConstelationTime(sat["datetime"])[1]
        sat["t_oc"] = utcToConstelationTime(sat["datetime"])[0]

        sat["A_1"] = header["A1"]
        sat["A_0"] = header["A0"]
        sat["t_ot"] = header["T"]
        sat["WN_t"] = header["W"]
        sat["WN_LSF"] = 1929%256 # week number, schedualed leep second: http://navigationservices.agi.com/GNSSWeb/
        sat["DN"] = 7            # day number
        sat["t_LSF"] = 18        # new leap second value

        sat["small delta_i"] = sat["i0"]-(0.3*math.pi)

        sat["health"] = 0 # force all sats to be healthy
        
        

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
    #t_oc = 0
    dt = syncTime[0] - sat["t_oc"]
    satClkCorr = (sat["clockdriftrate"] * dt + sat["clockdrift"]) * dt + sat["clockbias"]

    t_GD = sat["T_GD"]
    #print("T_GD:", t_GD)

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

def fillBuffer(bitBuffer, dateTime:datetime.datetime, eph, ephs):
    if(dateTime.microsecond!=0 and dateTime.second%6!=0):
        print("not aligned")
        return [0]
    
    t = dateTime.minute*60+dateTime.second
    subframe = (t%5) +1

    if "frame" not in bitBuffer.store:
        bitBuffer.store["frame"] = 1
    frame = bitBuffer.store["frame"] # page
    bitBuffer.store["frame"] = (frame-1+1)%25+1

    (TOW, WN) = utcToConstelationTime(dateTime+datetime.timedelta(seconds=6))

    spareData={
        "TLM Message":0, 
        "Integrity Status Flag": 0,
        "reserved": 0,
        "Alert Flag":0,
        "Anti-Spoof Flag": 0,
        "subframe id": subframe,
        "TOW": TOW,
        "WN": WN,
        "t": -1 # should be used to make last bits of parity 0
    }

    bits = []

    start = addParity(NavMessage.dataStructureToBits(frameStart, eph, twosCompliment=True, spareData=spareData), bitBuffer)
    if 1 <= subframe and subframe <= 3:
        data = addParity(NavMessage.dataStructureToBits(frameLayouts123[subframe], eph, twosCompliment=True, spareData=spareData), bitBuffer)
        bits = start+data
    elif subframe==4:
        (data_id, sv_id) = page_ids_sf4[frame]
        spareData["data id"] = data_id
        spareData["sv (page) id"] = sv_id
        if data_id==1:
            # almonac
            sv = "G"+str(sv_id).zfill(2)
            if sv in ephs:
                data = addParity(NavMessage.dataStructureToBits(frame5_1to24, ephs[sv], twosCompliment=True, spareData=spareData), bitBuffer)
                bits = start+data
            else:
                data = addParity(NavMessage.dataStructureToBits([0, 8*24], eph, twosCompliment=True, spareData=spareData), bitBuffer)
                bits = start+data
        elif data_id==2:
            # other data
            if frame==18 or sv_id==56:
                # ionosphere and UTC
                data = addParity(NavMessage.dataStructureToBits(frame4_18, eph, twosCompliment=True, spareData=spareData), bitBuffer)
                bits = start+data
            elif frame==25 or sv_id==63:
                # flags and health
                data = addParity(NavMessage.dataStructureToBits(frame4_25, eph, twosCompliment=True, spareData=spareData), bitBuffer)
                bits = start+data
            else:
                # reserved
                data = addParity(NavMessage.dataStructureToBits(frame4_1_6_11_16_21, eph, twosCompliment=True, spareData=spareData), bitBuffer)
                bits = start+data
        else:
            data = addParity(NavMessage.dataStructureToBits([0, 8*24], eph, twosCompliment=True, spareData=spareData), bitBuffer)
            bits = start+data
            print("unexpected data id")

        #if frame in [1, 6, 11, 16, 21]: # reserved
        #    data = addParity(NavMessage.dataStructureToBits(frame4_1_6_11_16_21, eph, twosCompliment=True, spareData=spareData), bitBuffer)
        #    bits = start+data
        #elif frame in [12, 19, 20, 22, 23, 24]: # reserved
        #    data = addParity(NavMessage.dataStructureToBits(frame4_12_19_20_22_23_24, eph, twosCompliment=True, spareData=spareData), bitBuffer)
        #    bits = start+data
        #elif frame in [18]: # ionosphere and UTC
        #    data = addParity(NavMessage.dataStructureToBits(frame4_18, eph, twosCompliment=True, spareData=spareData), bitBuffer)
        #    bits = start+data
        #elif frame in [25]: # flags and health
        #    data = addParity(NavMessage.dataStructureToBits(frame4_25, eph, twosCompliment=True, spareData=spareData), bitBuffer)
        #    bits = start+data
        ## todo: more frame 4 cases
        #elif frame in [2, 3, 4, 5, 7, 8, 9, 10]:
        #    sv = [2, 3, 4, 5, 7, 8, 9, 10].index(frame)+25
        #    sv = "G"+str(sv).zfill(2)
        #    if sv in ephs:
        #        data = addParity(NavMessage.dataStructureToBits(frame5_1to24, ephs[sv], twosCompliment=True, spareData=spareData), bitBuffer)
        #        bits = start+data
        #    else:
        #        data = addParity(NavMessage.dataStructureToBits([0, 8*24], eph, twosCompliment=True, spareData=spareData), bitBuffer)
        #        bits = start+data
        #
        #else:
        #    data = addParity(NavMessage.dataStructureToBits([0, 8*24], eph, twosCompliment=True, spareData=spareData), bitBuffer)
        #    bits = start+data
    elif subframe==5:
        (data_id, sv_id) = page_ids_sf5[frame]
        spareData["data id"] = data_id
        spareData["sv (page) id"] = sv_id
        if data_id==1:
            # almonac
            sv = "G"+str(sv_id).zfill(2)
            if sv in ephs:
                data = addParity(NavMessage.dataStructureToBits(frame5_1to24, ephs[sv], twosCompliment=True, spareData=spareData), bitBuffer)
                bits = start+data
            else:
                data = addParity(NavMessage.dataStructureToBits([0, 8*24], eph, twosCompliment=True, spareData=spareData), bitBuffer)
                bits = start+data
        elif data_id==2:
            # other data
            if frame==25 or sv_id==51:
                data = addParity(NavMessage.dataStructureToBits(frame5_25, eph, twosCompliment=True, spareData=spareData), bitBuffer)
                bits = start+data

        #if frame==25:
        #    data = addParity(NavMessage.dataStructureToBits(frame5_25, eph, twosCompliment=True, spareData=spareData), bitBuffer)
        #    bits = start+data
        #else:
        #    sv = "G"+str(frame).zfill(2)
        #    if sv in ephs:
        #        data = addParity(NavMessage.dataStructureToBits(frame5_1to24, ephs[sv], twosCompliment=True, spareData=spareData), bitBuffer)
        #        bits = start+data
        #    else:
        #        data = addParity(NavMessage.dataStructureToBits([0, 8*24], eph, twosCompliment=True, spareData=spareData), bitBuffer)
        #        bits = start+data
    
        

    assert len(bits)%30 == 0

    return bits

PI = math.pi

# data id, sv id*
page_ids_sf4 = [(), 
                (2, 57), (1, 25), (1, 26), (1, 27), (1, 28), 
                (2, 57), (1, 29), (1, 30), (1, 31), (1, 32), 
                (2, 57), (2, 62), (2, 52), (2, 53), (2, 54), 
                (2, 57), (2, 55), (2, 56), (2, 58), (2, 59), 
                (2, 57), (2, 60), (2, 61), (2, 62), (2, 63)]

page_ids_sf5 = [(),
                (1,  1), (1,  2), (1,  3), (1,  4), (1,  5),
                (1,  6), (1,  7), (1,  8), (1,  9), (1, 10),
                (1, 11), (1, 12), (1, 13), (1, 14), (1, 15),
                (1, 16), (1, 17), (1, 18), (1, 19), (1, 20),
                (1, 21), (1, 22), (1, 23), (1, 24), (2, 51)]

frameStart = [
    [0b10001011, 8], ["TLM Message", 14], ["Integrity Status Flag", 1], ["reserved", 1],
    ["TOW", 17, 1/6], ["Alert Flag", 1], ["Anti-Spoof Flag", 1], ["subframe id", 3], ["t", 2]
]

frameLayouts123 = [
    [],
    [                                                                 # MSB
        ["WN", 10], ["codes_on_L2", 2], ["URA_index", 4], ["health", 6], ["IODC", 2, 1/(2**8)],
        ["L2_P_data_flag", 1], [0, 23],
        [0, 24],
        [0, 24],
        [0, 16], ["T_GD", 8, 2**31],
        # LSB
        ["IODC", 8], ["t_oc", 16, 2**-4],
        ["a_f2", 8, 2**55], ["a_f1", 16, 2**43],
        ["a_f0", 22, 2**31], ["t", 2]
    ],
    [
        ["IODE", 8], ["Crs", 16, 2**5],
        ["deltan", 16, 2**43 /PI], ["M0", 32, 2**31 /PI],
        ["Cuc", 16, 2**29], ["e", 32, 2**33],
        ["Cus", 16, 2**29], ["sqrt_a", 32, 2**19],
        ["toe", 16, 2**-4], ["fit interval (BNK)", 1], ["AODO", 5], ["t", 2]
    ],
    [
        ["Cic", 16, 2**29], ["omega0", 32, 2**31 /PI], ["Cis", 16, 2**29], ["i0", 32, 2**31 /PI], ["Crc", 16, 2**5], ["omega", 32, 2**31 /PI], ["omegaDot", 24, 2**43 /PI], ["IODE", 8], ["IDot", 14, 2**43 /PI], ["t", 2]
    ]
]

frame5_1to24 = [
    ["data id", 2], ["sv (page) id", 6], ["e", 16, 2**21],
    ["t_oa", 8, 2**-12], ["small delta_i", 16, 2**19],
    ["omegaDot", 16, 2**38], ["health", 8],
    ["sqrt_a", 24, 2**11],
    ["omega0", 24, 2**23],
    ["omega", 24, 2**23],
    ["M0", 24, 2**23],
    # MSB                                              LSB
    ["a_f0", 8, 2**20 * 2**-3], ["a_f1", 11, 2**38], ["a_f0", 3, 2**20], ["t", 2]
]

frame4_1_6_11_16_21 = [
    ["data id", 2], ["sv (page) id", 6], [0, 16],
    [0, 24], [0, 24], [0, 24], [0, 24], [0, 24], 
    [0, 8], [0, 16], 
    [0, 22], ["t", 2]
]
frame4_12_19_20_22_23_24 = frame4_1_6_11_16_21

# check unit might need to multiply or devide by pi for 1-3 (/semi-circle)
frame4_18 = [
    ["data id", 2], ["sv (page) id", 6], ["a_0", 8, 2**30], ["a_1", 8, 2**27],
    ["a_2", 8, 2**24], ["a_3", 8, 2**24], ["b_0", 8, 2**-11], 
    ["b_1", 8, 2**-14], ["b_2", 8, 2**-16], ["b_3", 8, 2**-16],
    ["A_1", 24, 2**50],
    ["A_0", 32, 2**30], ["t_ot", 8, 2**-12], ["WN_t", 8],
    ["t_LS", 8], ["WN_LSF", 8], ["DN", 8],
    ["t_LSF", 8], [0, 14], ["t", 2]
]

frame4_25 = [["data id", 2], ["sv (page) id", 6], [0, 8*23]]
frame5_25 = [["data id", 2], ["sv (page) id", 6], [0, 8*23]]



def addParity(data, bitbuffer):
    assert len(data)%24==0
    if "lastParityBits" not in bitbuffer.store:
        bitbuffer.store["lastParityBits"] = [0, 0]
        #print("first starting with: [0, 0]")
    lastParityBits = bitbuffer.store["lastParityBits"]
    # last bits are t and need to be solved for to make the total last bits 00
    encoded = []
    N = len(data)//24
    for j in range(N):
        d = data[24*j:24*(j+1)]
        
        
        #hammingCode = 0
        #for i in range(len(e)):
        #    if e[i]==1:
        #        hammingCode = hammingCode^i
        #hammingBits = [0]*6
        #for i in range(len(hammingBits)):
        #    if (hammingCode>>i)&1==1:
        #        hammingBits[i]=1

        e = lastParityBits + d
        def nDataBits(x):
            return e[x-1]
            return e[x-1] if e[1]!=1 else 1-e[x-1]

        if j==N-1:
            D29 = (nDataBits(2)  ^ nDataBits(3)  ^ nDataBits(5)  ^ nDataBits(7)  ^ nDataBits(8)  ^ 
                   nDataBits(9)  ^ nDataBits(11) ^ nDataBits(12) ^ nDataBits(16) ^ nDataBits(17) ^ 
                   nDataBits(18) ^ nDataBits(19) ^ nDataBits(20) ^ nDataBits(23) ^ nDataBits(24) ^ 
                   nDataBits(26))
            D30 = (nDataBits(1)  ^ nDataBits(5)  ^ nDataBits(7)  ^ nDataBits(8)  ^ nDataBits(10) ^ 
                   nDataBits(11) ^ nDataBits(12) ^ nDataBits(13) ^ nDataBits(15) ^ nDataBits(17) ^ 
                   nDataBits(21) ^ nDataBits(24) ^ nDataBits(25) ^ nDataBits(26))
            if [D29, D30]==[1,1]:
                d[-1] = 1-d[-1]
            if [D29, D30]==[1,0]:
                d[-1] = 1-d[-1]
                d[-2] = 1-d[-2]
            if [D29, D30]==[0,1]:
                d[-2] = 1-d[-2]
            
        e = lastParityBits + d
        def nDataBits(x):
            return e[x-1]
            return e[x-1] if e[1]!=1 else 1-e[x-1]
        
        hammingBits =[
                nDataBits(1)  ^ nDataBits(3)  ^ nDataBits(4)  ^ nDataBits(5)  ^ nDataBits(7)  ^
                nDataBits(8)  ^ nDataBits(12) ^ nDataBits(13) ^ nDataBits(14) ^ nDataBits(15) ^
                nDataBits(16) ^ nDataBits(19) ^ nDataBits(20) ^ nDataBits(22) ^ nDataBits(25),

                nDataBits(2)  ^ nDataBits(4)  ^ nDataBits(5)  ^ nDataBits(6)  ^ nDataBits(8)  ^
                nDataBits(9)  ^ nDataBits(13) ^ nDataBits(14) ^ nDataBits(15) ^ nDataBits(16) ^
                nDataBits(17) ^ nDataBits(20) ^ nDataBits(21) ^ nDataBits(23) ^ nDataBits(26),

                nDataBits(1)  ^ nDataBits(3)  ^ nDataBits(5)  ^ nDataBits(6)  ^ nDataBits(7)  ^
                nDataBits(9)  ^ nDataBits(10) ^ nDataBits(14) ^ nDataBits(15) ^ nDataBits(16) ^
                nDataBits(17) ^ nDataBits(18) ^ nDataBits(21) ^ nDataBits(22) ^ nDataBits(24),

                nDataBits(2)  ^ nDataBits(4)  ^ nDataBits(6)  ^ nDataBits(7)  ^ nDataBits(8)  ^
                nDataBits(10) ^ nDataBits(11) ^ nDataBits(15) ^ nDataBits(16) ^ nDataBits(17) ^
                nDataBits(18) ^ nDataBits(19) ^ nDataBits(22) ^ nDataBits(23) ^ nDataBits(25),

                nDataBits(2)  ^ nDataBits(3)  ^ nDataBits(5)  ^ nDataBits(7)  ^ nDataBits(8)  ^ 
                nDataBits(9)  ^ nDataBits(11) ^ nDataBits(12) ^ nDataBits(16) ^ nDataBits(17) ^ 
                nDataBits(18) ^ nDataBits(19) ^ nDataBits(20) ^ nDataBits(23) ^ nDataBits(24) ^ 
                nDataBits(26),

                nDataBits(1)  ^ nDataBits(5)  ^ nDataBits(7)  ^ nDataBits(8)  ^ nDataBits(10) ^ 
                nDataBits(11) ^ nDataBits(12) ^ nDataBits(13) ^ nDataBits(15) ^ nDataBits(17) ^ 
                nDataBits(21) ^ nDataBits(24) ^ nDataBits(25) ^ nDataBits(26)
        ]
        lastParityBits = hammingBits[-2:]
        #print("".join(map(str,d)), "".join(map(str,hammingBits)))
        if nDataBits(2)==1:
            d = list(map(lambda x: 1-x, d))
        encoded += d+hammingBits
    
    assert lastParityBits == [0,0]
    bitbuffer.store["lastParityBits"] = lastParityBits
    #print()
    #print("".join(map(str,encoded)))
    return encoded

#############################
#                           #
#      PACKAGE FOR USE      #
#                           #
#############################

def getConstelation():
    constelation = Constelation.Constelation()
    constelation.prefix="G"
    constelation.bitsPerFrame = 5
    constelation.RINEXDataRecordDesciption = getRINEXDataRecordDesciption()
    constelation.RINEXheaderDescription = [
        ["GPSA", ["alpha1", RINEX.parse_float], ["alpha2", RINEX.parse_float], ["alpha3", RINEX.parse_float], ["alpha4", RINEX.parse_float], "IONOSPHERIC", "CORR"],
        ["GPSB", ["beta1",  RINEX.parse_float], ["beta2",  RINEX.parse_float], ["beta3",  RINEX.parse_float], ["beta4",  RINEX.parse_float], "IONOSPHERIC", "CORR"],
        ["GPUT", ["A0", RINEX.parse_float], ["A1", RINEX.parse_float], ["T", int], ["W", int], "TIME", "SYSTEM", "CORR"], #UTC
    ]
    constelation.postProcessRINAXData = postProcessRINAXData
    constelation.utcToConstelationTime = utcToConstelationTime
    constelation.clockCorection = clockCorection
    constelation.timeDifference = timeDifference
    constelation.getSatPosVel = getSatPosVel
    constelation.travelTimeCorection = travelTimeCorection
    constelation.fillBuffer = fillBuffer
    constelation.getSetupHeader = lambda sats: "G:("+",".join(map(lambda name: name[1:]+"[]", sats))+")"

    return constelation