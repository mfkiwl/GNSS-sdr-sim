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
        ["IODEC", "Crs", "deltan", "M0"],
        ["Cuc", "e", "Cus", "sqrt_a"],
        ["toe", "Cic", "omega0", "Cis"],
        ["i0", "Crc", "omega", "omegaDot"],
        ["IDot", "spare1", "WN", "spare2"],
        ["SV accuracy", "health", "T_GD1", "T_GD2"],
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
        
        acc = sat["SV accuracy"]
        URA_steps = [2.4, 3.4, 4.85, 6.85, 9.65, 13.65, 24, 48, 96, 192, 384, 768, 1536, 3072, 6144]
        N=0
        while N<len(URA_steps) and acc>URA_steps[N]:
            N+=1
        sat["URAI"] = N

        sat["SatH1"] = 0 # health

        sat["a_f0"] = sat["clockbias"]
        sat["a_f1"] = sat["clockdrift"]
        sat["a_f2"] = sat["clockdriftrate"]
        sat["t_oc"] = 0 # for clock corection?

        sat["AODC"] = sat["IODEC"]
        sat["AODE"] = sat["IODEC"]

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
        
        sat["A0GPS"] = -1
        sat["A1GPS"] = -1
        sat["A0Gal"] = -1
        sat["A1Gal"] = -1
        sat["A0GLO"] = -1
        sat["A1GLO"] = -1
        sat["A0UTC"] = -1
        sat["A1UTC"] = -1
        sat["delta t_LSF"] = -1
        sat["DN"] = -1
        sat["WN_LSF"] = -1

        sat["small delta_i"] = sat["i0"]-(0.3*math.pi)
        
        sat["datetime"] = datetime.datetime(sat["year"], sat["month"], sat["day"], sat["hour"], sat["minute"], sat["second"])
        (t_oa, WNa) = utcToConstelationTime(sat["datetime"])
        sat["t_oa"] = t_oa
        sat["WNa"] = WNa

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
    epochStart = datetime.datetime(year=2006, month=1, day=1)
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
        exit("D2 not suported yet ("+eph["name"]+")")
        return [0]
    else: # D1
        if "AmID" not in bitBuffer.store:
            bitBuffer.store["AmID"] = 0
        AmID = bitBuffer.store["AmID"] # page
        bitBuffer.store["MessageIndex"] = (AmID+1)%4
        subframe = (dateTime.second//6)%5 + 1
        page = ((dateTime.minute*60+dateTime.second)//30)%24 + 1
        # super frame (12 min / 36000 bits)
        # 24 frames (30 s / 1500 bits)
        #    5 subframes (6 s / 300 bits) : SYNC(11100010010) (first 15 bits not encoded, next 11 BCH(15, 11, 1): first 30 bit word with sync (26 info bit)) ( next 9 words, 2x BCH (22 info bits))
        #      10 words (0.6 s / 30 bits)

        data = [0] * (4 + 11*(1+9*2))

        (SOW, WN) = utcToConstelationTime(dateTime)

        spareData = {"FraID":subframe, "Pnum":page, "SOW":SOW, "WN":WN, "AmEpID":0b11, "AmID":AmID}
        if subframe==1:
            data = NavMessage.dataStructureToBits(subframe1_layout,          eph, twosCompliment=True, spareData=spareData)
        elif subframe==2:
            data = NavMessage.dataStructureToBits(subframe2_layout,          eph, twosCompliment=True, spareData=spareData)
        elif subframe==3:
            data = NavMessage.dataStructureToBits(subframe3_layout,          eph, twosCompliment=True, spareData=spareData)
        elif subframe==4 or subframe==5 and ( page <= 6 or (11 <= page and page <= 23)):
            satId = (subframe-4)*24+page
            satName = "C"+(str(satId).zfill(2))
            if satName in ephs:
                data = NavMessage.dataStructureToBits(subframe_almanac_layout,   eph, twosCompliment=True, spareData=spareData)
            else:
                data = NavMessage.dataStructureToBits(subframe_no_almanac_layout,   eph, twosCompliment=True, spareData=spareData)
        elif subframe==5 and (11 <= page and page <= 23):
            satId = 31 + page-11 + (AmID-1)*13
            satName = "C"+(str(satId).zfill(2))
            if satName in ephs:
                data = NavMessage.dataStructureToBits(subframe_almanac_layout,   eph, twosCompliment=True, spareData=spareData)
            else:
                data = NavMessage.dataStructureToBits(subframe_no_almanac_layout,   eph, twosCompliment=True, spareData=spareData)
        elif subframe==5 and page==7:
            addHealthInfo(spareData, ephs, range(1, 20), range(1, 20))
            data = NavMessage.dataStructureToBits(subframe_health1_layout,   eph, twosCompliment=True, spareData=spareData)
        elif subframe==5 and page==8:
            addHealthInfo(spareData, ephs, range(20, 31), range(20, 31))
            data = NavMessage.dataStructureToBits(subframe_health2_layout,   eph, twosCompliment=True, spareData=spareData)
        elif subframe==5 and page==9:
            data = NavMessage.dataStructureToBits(subframe_time_gnss_layout, eph, twosCompliment=True, spareData=spareData)
        elif subframe==5 and page==10:
            data = NavMessage.dataStructureToBits(subframe_time_utc_layout,  eph, twosCompliment=True, spareData=spareData)
        elif subframe==5 and page==24:
            match AmID:
                case 0b01:
                    addHealthInfo(spareData, ephs, range(31, 44), range(31, 44))
                case 0b10:
                    addHealthInfo(spareData, ephs, range(34, 57), range(31, 44))
                case 0b11:
                    addHealthInfo(spareData, ephs, range(57, 63), range(31, 38))
                    # reserved, just loop back around
                    addHealthInfo(spareData, ephs, range(1, 7), range(38, 44))
                case 0b00:
                    addHealthInfo(spareData, ephs, range(7, 20), range(31, 44))
            data = NavMessage.dataStructureToBits(subframe_health3_layout,   eph, twosCompliment=True, spareData=spareData)
        else:
            assert False, "case missing: "+str(subframe)+"/"+str(page)
        
        return encode_subframe(data)

    return [1]

def addHealthInfo(spareData, ephs, satRange, fieldRange):
    fieldRange = fieldRange.__iter__()
    for i in satRange:
        j = next(fieldRange)
        satName = "C"+(str(i).zfill(2))
        field = "hea"+str(j)
        if satName in ephs: # all sats not en eph -> behaving abnormal
            spareData[field] = 0b000000000
        else:
            spareData[field] = 0b111111111

SYNC = [1,1,1,0,0,0,1,0,0,1,0]

subframe1_layout = [[0, 4], ["FraID", 3], ["SOW", 20], ["SatH1", 1], ["AODC", 5], ["URAI", 4], ["WN", 13], ["t_oc", 17, 2**-3], ["T_GD1", 10, 10e9], ["T_GD2", 10, 10e9],
                    ["a_0", 8, 2**30], ["a_1", 8, 2**27], ["a_2", 8, 2**24], ["a_3", 8, 2**24], ["b_0", 8, 2**-11], ["b_1", 8, 2**-14], ["b_2", 8, 2**-16], ["b_3", 8, 2**-16],
                    ["a_f2", 11, 2**66], ["a_f0", 24, 2**33], ["a_f1", 22, 2**50], ["AODE", 5]]

subframe2_layout = [[0, 4], ["FraID", 3], ["SOW", 20], ["deltan", 16, 2**43/math.pi], ["Cuc", 18, 2**31], ["M0", 32, 2**31], ["e", 32, 2**33], ["Cus", 18, 2**31], ["Crc", 18, 2**6], ["Crs", 18, 2**6], ["sqrt_a", 32, 2**19], ["toe", 2, 2**-3]]

subframe3_layout = [[0, 4], ["FraID", 3], ["SOW", 20], ["toe", 15, 2**-3], ["i0", 32, 2**31], ["Cic", 18, 2**31], ["omegaDot", 24, 2**43], ["Cis", 18, 2**31], ["IDot", 14, 2**43], ["omega0", 32, 2**31], ["omega", 32, 2**31], [0, 1]]

# subframe 4 page 1 to 24(all), subframe 5 page 1 to 6
subframe_almanac_layout    = [[0, 4], ["FraID", 3], ["SOW", 20], [0, 1], ["Pnum", 7], ["sqrt_a", 24, 2**11], ["a_f1", 11, 2**38], ["a_f0", 11, 2**20], ["omega0", 24, 2**23], ["e", 17, 2**21], ["small delta_i", 16, 2**19], ["t_oa", 8, 2**-12], ["omegaDot", 17, 2**38], ["omega", 24, 2**23], ["M0", 24, 2**23], ["AmEpID", 2]] #AmEpID=0b11
subframe_no_almanac_layout = [[0, 4], ["FraID", 3], ["SOW", 20], [0, 1], ["Pnum", 7], [0, 176], ["AmEpID", 2]]

# subframe 5 page 7
subframe_health1_layout    = [[0, 4], ["FraID", 3], ["SOW", 20], [0, 1], ["Pnum", 7], ["hea1", 9], ["hea2", 9], ["hea3", 9], ["hea4", 9], ["hea5", 9], ["hea6", 9], ["hea7", 9], ["hea8", 9], ["hea9", 9], ["hea10", 9], ["hea11", 9], ["hea12", 9], ["hea13", 9], ["hea14", 9], ["hea15", 9], ["hea16", 9], ["hea17", 9], ["hea18", 9], ["hea19", 9], [0, 7]]

# subframe 5 page 8 -> health 0 for all ok
subframe_health2_layout    = [[0, 4], ["FraID", 3], ["SOW", 20], [0, 1], ["Pnum", 7], ["hea20", 9], ["hea21", 9], ["hea22", 9], ["hea23", 9], ["hea24", 9], ["hea25", 9], ["hea26", 9], ["hea27", 9], ["hea28", 9], ["hea29", 9], ["hea30", 9], ["WNa", 8], ["t_oa", 8], [0, 63]]

# subframe 5 page 9
subframe_time_gnss_layout  = [[0, 4], ["FraID", 3], ["SOW", 20], [0, 1], ["Pnum", 7], [0, 30], ["A0GPS", 14, 10e9], ["A1GPS", 16, 10e9], ["A0Gal", 14, 10e9], ["A1Gal", 16, 10e9], ["A0GLO", 14, 10e9], ["A1GLO", 16, 10e9], [0, 58]]

# subframe 5 page 10
subframe_time_utc_layout   = [[0, 4], ["FraID", 3], ["SOW", 20], [0, 1], ["Pnum", 7], ["t_LS", 8], ["delta t_LSF", 8], ["WN_LSF", 8], ["A0UTC", 32, 2**30], ["A1UTC", 24, 2**50], ["DN", 8], [0, 90]]

# subrame 5 page 11 to 23
subframe_almanac_layout2 = [[0, 4], ["FraID", 3], ["SOW", 20], [0, 1], ["Pnum", 7], ["sqrt_a", 24, 2**11], ["a_f1", 11, 2**38], ["a_f0", 11, 2**20], ["omega0", 24, 2**23], ["e", 17, 2**21], ["small delta_i", 16, 2**19], ["t_oa", 8, 2**-12], ["omegaDot", 17, 2**38], ["omega", 24, 2**23], ["M0", 24, 2**23], ["AmID", 2]]
subframe_no_almanac_layout2 = [[0, 4], ["FraID", 3], ["SOW", 20], [0, 1], ["Pnum", 7], [0, 176], ["AmID", 2]]

# subframe 5 page 24
subframe_health3_layout    = [[0, 4], ["FraID", 3], ["SOW", 20], [0, 1], ["Pnum", 7], ["hea31", 9], ["hea32", 9], ["hea33", 9], ["hea34", 9], ["hea35", 9], ["hea36", 9], ["hea37", 9], ["hea38", 9], ["hea39", 9], ["hea40", 9], ["hea41", 9], ["hea42", 9], ["hea43", 9], ["AmID", 2], [0, 59]]


def encode_subframe(data):
    assert len(data) == 4 + 11*(1+9*2), "Expected: "+str(4 + 11*(1+9*2))+", got: "+str(len(data))
    encoded = SYNC + data[0:4] + BCH(data[4:4+11])
    for i in range(9):
        a = BCH(data[4+11+11*2*i+ 0:4+11+11*2*i+11])
        b = BCH(data[4+11+11*2*i+11:4+11+11*2*i+22])
        encoded += [val for pair in zip(a, b) for val in pair]
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
    constelation.getSetupHeader = lambda sats: "C:("+",".join(map(lambda name: name[-2:]+"[]", sats))+")"

    return constelation