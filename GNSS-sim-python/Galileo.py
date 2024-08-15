import Constelation
import NavMessage
import const
import mulSatpos
import RINEX

import datetime
import math
import numpy as np
import itertools

###########################
#                         #
#      RINEX PARSING      #
#                         #
###########################

def float_int(x):
    return int(float(x))

def byte_float_int(x):
    return int(float(x)).to_bytes(2)

def getRINEXDataRecordDesciption():
    return [
        [["name", str], ["year", int], ["month", int], ["day", int], ["hour", int], ["minute", int], ["second", int], "clockbias", "clockdrift", "clockdriftrate"],
        [["IODnav", float_int], "Crs", "deltan", "M0"],
        ["Cuc", "e", "Cus", "sqrt_a"],
        [["toe", float_int], "Cic", "omega0", "Cis"],
        ["i0", "Crc", "omega", "omegaDot"],
        ["IDot", ["dataSources", byte_float_int], "GALWeekNum", "spare1"],
        ["SISA", ["health", byte_float_int], "BGDE5aE1", "BGDE5bE1"],
        ["transmitionTime", "spare2", "spare3", "spare4"]
    ]

def postProcessRINAXData(data, header):
    for sat in data:
        sat["prn"] = int(sat["name"][1:])
        sat["frequency"] = 1575420000
        dataSources = sat["dataSources"]
        sat["INAV_E1B"]  = dataSources[1]&1<<0==1<<0
        sat["FNAV_E5aI"] = dataSources[1]&1<<1==1<<1
        sat["INAV_E5bI"] = dataSources[1]&1<<2==1<<2

        sat["affTocSISA_E5aE1"] = dataSources[0]&1<<0==1<<0
        sat["affTocSISA_E5bE1"] = dataSources[0]&1<<1==1<<1

        health = sat["health"]
        sat["E1B_DVS"] = health[1]&1<<0==1<<0
        sat["E1B_HS"]  = int(health[1]&0b11<<1)
        sat["E5a_DVS"] = health[1]&1<<3==1<<3
        sat["E5a_HS"]  = int(health[1]&0b11<<4)
        sat["E5b_DVS"] = health[1]&1<<6==1<<6
        sat["E5b_HS"]  = int((health[1]&1<<7)>>7 | (health[0]&1)<<1)

        sat["a0"] = 0 #header["a0"] # 0s make GST equal to UTC-leap seconds 
        sat["a1"] = 0 #header["a1"]
        sat["t_LS"] = header["t_LS"]
        sat["a_i0"] = header["a_i0"]
        sat["a_i1"] = header["a_i1"]
        sat["a_i2"] = header["a_i2"]

        sat["datetime"] = datetime.datetime(sat["year"], sat["month"], sat["day"], sat["hour"], sat["minute"], sat["second"])
        sat["t_oa"] = utcToConstelationTime(sat["datetime"])[1]
        sat["t_oc"] = utcToConstelationTime(sat["datetime"])[0]
    
    return [sat for sat in data if sat["INAV_E1B"]]

##############################
#                            #
#      ORBIT SIMULATION      #
#                            #
##############################

def R1(angle):
    return np.array([[1,  0,               0              ],
                     [0,  math.cos(angle), math.sin(angle)],
                     [0, -math.sin(angle), math.cos(angle)]])


def R2(angle):
    return np.array([[math.cos(angle), 0, -math.sin(angle)],
                     [0,               1,  0              ],
                     [math.sin(angle), 0,  math.cos(angle)]])


def R3(angle):
    return np.array([[ math.cos(angle), math.sin(angle), 0],
                     [-math.sin(angle), math.cos(angle), 0],
                     [ 0,               0,               1]])

def getSatPos(sat, t_k):
    if t_k > 302400:
        t_k -= 604800
    if t_k < -302400:
        t_k += 604800
    
    #mu = 3.986004418e14 # gravitational parameter
    mu = const.EARTH_GRAVCONSTANT

    # mean anomoly
    M_k = sat["M0"] + (math.sqrt(mu)/(sat["sqrt_a"]**3) + sat["deltan"])*t_k
    #M_k=M_k%(2*math.pi)

    # eccentricity anomaly
    E_k = M_k
    for i in range(20):
        y = E_k - sat["e"] * math.sin(E_k) - M_k
        a = 1 - sat["e"] * math.cos(E_k)
        E_k -= y/a
    sat["E_k"] = E_k

    #E_k=E_k%(2*math.pi)

    # true anomoly
    v_k = math.atan2((math.sqrt(1-sat["e"]**2)*math.sin(E_k)),(math.cos(E_k)-sat["e"]))
    
    #argument of ladetude // cus, cuc: check unit half circles or radians
    u_k = sat["omega"] + v_k + sat["Cuc"]*(math.cos(sat["omega"] + v_k)**2) + sat["Cus"]*(math.sin(sat["omega"] + v_k)**2) 
    #radial distance
    r_k = sat["sqrt_a"]**2 * (1-sat["e"]*math.cos(E_k)) + sat["Crc"]*(math.cos(sat["omega"] + v_k)**2) + sat["Crs"]*(math.sin(sat["omega"] + v_k)**2)
    #inclanation
    i_k = sat["i0"] + sat["IDot"]*t_k + sat["Cic"]*(math.cos(sat["omega"] + v_k)**2) + sat["Cis"]*(math.sin(sat["omega"] + v_k)**2)
    # lngdetude of asending node
    #omegae = 7.2921151467E-5 # rotational velocity earth
    omegae = const.EARTH_WGS84_ROT
    lambda_k = sat["omega0"]+(sat["omegaDot"]-omegae)*t_k - omegae*sat["toe"]
    
    XYZ_k = np.dot(np.dot(np.dot(R3(-lambda_k), R1(-i_k)), R3(-u_k)), np.array([[r_k],[0],[0]]))
    return XYZ_k

def getSatPosVel(eph, t):
    tk = t[0]-eph["toe"]
    satPos_old = getSatPos(eph, tk)
    satPosN_old = getSatPos(eph, tk+1)
    satVel_old = satPosN_old-satPos_old
    (satPos, satVel) = mulSatpos.getSatPosVel(eph, tk)
    return (np.array([satPos]).T, np.array([satVel]).T)

def utcToConstelationTime(dateTime : datetime.datetime):
    epochstart = datetime.datetime(year=1999, month=8, day=22)
    wn = (dateTime-epochstart).days//7
    weekStart = epochstart+datetime.timedelta(days=wn*7)
    tow_td : datetime.timedelta = (dateTime-weekStart)
    tow = tow_td.days*24*60*60 + tow_td.seconds + tow_td.microseconds/1000000
    return (tow, wn)

def clockCorection(sat, syncTime):
    t_oc = 0 #sat["t_oc"]
    dt = syncTime[0] - t_oc
    satClkCorr = (sat["clockdriftrate"] * dt + sat["clockdrift"]) * dt + sat["clockbias"]

    t_GD = sat["BGDE5bE1"]

    return (syncTime[0]-satClkCorr + t_GD, syncTime[1]) # could be +, since i do inverse of reciever

def timeDifference(t1, t2):
    return t1[0]-t2[0]

####################################
#                                  #
#      NAV MESSAGE GENERATION      #
#                                  #
####################################

def fillBuffer(bitBuffer, dateTime:datetime.datetime, eph, ephs):
    if(dateTime.microsecond!=0):
        print("not aligned")
        return [0]
    t = (dateTime.minute*60+dateTime.second)%(720)
    page = t%15
    subFrame = (t//15)%24

    # get page data
    # encode page

    # +datetime.timedelta(seconds=1)
    (TOW, WN) = utcToConstelationTime(dateTime) #+datetime.timedelta(seconds=1)

    word = getWord(subFrame, page, eph, ephs, {"TOW":TOW, "WN":WN})
    #assert(len(word), 128)

    p_even, p_odd = make_nominal_pages(word, (t+1)%3+1)

    if dateTime.second%2==1 :
        page = (SYNC + NavMessage.interleave(encode_page(p_even))
            + SYNC + NavMessage.interleave(encode_page(p_odd)))
        #assert(len(page), 128)
        return page
    else:
        page = SYNC + NavMessage.interleave(encode_page(p_odd))
        #assert(len(page), 64)
        return page

def getWord(subFrame, page, eph, ephs, time):
    word_order = [2, 4, 6, [7, 9], [8, 10], 0, 0, 16, 0, 0, 1, 3, 5, 0, 16]
    word_num = word_order[page]
    if isinstance(word_num, list):
        word_num = word_num[subFrame%2]

        satIndex = subFrame//2
        sv1k = "E"+str((satIndex+19+0)%36)
        sv2k = "E"+str((satIndex+19+1)%36)
        sv3k = "E"+str((satIndex+19+2)%36)
        sv1 = ephs[sv1k] if sv1k in ephs else None
        sv2 = ephs[sv2k] if sv2k in ephs else None
        sv3 = ephs[sv3k] if sv3k in ephs else None

        
        if word_num==7:
            start = NavMessage.dataStructureToBits([
                [7, 6],
                [-1, 4], # IOD_a
                [-1, 2], # WN_a
                [-1, 10] # t_0a
            ], eph, twosCompliment=True)
            almonacSV1 = [0]*133 if sv1 is None else NavMessage.dataStructureToBits(almonacForSatDataStructure, sv1, twosCompliment=True)
            return start + almonacSV1[0:(6+13+11+16+11+16+11+16)] + [0]*6
        elif word_num==8:
            start = NavMessage.dataStructureToBits([
                [8, 6],
                [-1, 4], # IOD_a
            ], eph, twosCompliment=True)
            almonacSV1 = [0]*133 if sv1 is None else NavMessage.dataStructureToBits(almonacForSatDataStructure, sv1, twosCompliment=True)
            almonacSV2 = [0]*133 if sv2 is None else NavMessage.dataStructureToBits(almonacForSatDataStructure, sv2, twosCompliment=True)
            return start + almonacSV1[(6+13+11+16+11+16+11+16):] + almonacSV2[0:(6+13+11+16+11+16+11)] + [0]*1
        elif word_num==9:
            start = NavMessage.dataStructureToBits([
                [9, 6],
                [-1, 4], # IOD_a
                [-1, 2], # WN_a
                [-1, 10] # t_0a
            ], eph, twosCompliment=True)
            almonacSV2 = [0]*133 if sv2 is None else NavMessage.dataStructureToBits(almonacForSatDataStructure, sv2, twosCompliment=True)
            almonacSV3 = [0]*133 if sv3 is None else NavMessage.dataStructureToBits(almonacForSatDataStructure, sv3, twosCompliment=True)
            return start + almonacSV2[(6+13+11+16+11+16+11):] + almonacSV3[0:(6+13+11+16+11)]
        elif word_num==10:
            start = NavMessage.dataStructureToBits([
                [10, 6],
                [-1, 4], # IOD_a
            ], eph, twosCompliment=True)
            almonacSV3 = [0]*133 if sv3 is None else NavMessage.dataStructureToBits(almonacForSatDataStructure, sv3, twosCompliment=True)
            end = NavMessage.dataStructureToBits([
                [-1, 16], # A_0G
                [-1, 12], # A_1G
                [-1, 8],  # t_0G
                [-1, 6]   # WN_0G
            ], eph, twosCompliment=True)
            return start + almonacSV3[(6+13+11+16+11):] + end
        print("unexpected word number")
        return [0]*128

    else:
        if word_num<=6:
            return NavMessage.dataStructureToBits(
                words0to6dataStructure[word_num], eph, twosCompliment=True, spareData=time
            )
        elif word_num==16:
            A_nominal = 29600000
            i_nominal = 56
            e_nominal = 0

            dA_red = (eph["sqrt_a"]**2-A_nominal)
            e_xred = eph["e"]*math.cos(eph["omega"])
            e_yred = eph["e"]*math.sin(eph["omega"])
            lambda_0red = eph["M0"]+eph["omega"]
            di_0red = eph["i0"]-i_nominal/180
            return NavMessage.dataStructureToBits([
                [16, 6],
                [dA_red,       5,  2**-8],
                [e_xred,       13, 2**22],
                [e_yred,       13, 2**22],
                [di_0red,      17, 2**22],
                ["omega0",     23, 2**22],
                [lambda_0red,  23, 2**22],
                ["clockbias",  22, 2**26],
                ["clockdrift", 6,  2**35]
            ], eph, twosCompliment=True)
        return [0]*128

words0to6dataStructure = [
    [[0, 6], [int(0b10), 2], [0, 88], ["WN", 12], ["TOW", 20]],
    [[1, 6], ["IODnav", 10], ["toe", 14, 1/60], ["M0", 32, 2**31/math.pi], ["e", 32, 2**33], ["sqrt_a", 32, 2**19], [0, 2]],
    [[2, 6], ["IODnav", 10], ["omega0", 32, 2**31/math.pi], ["i0", 32, 2**31/math.pi], ["omega", 32, 2**31/math.pi], ["IDot", 14, 2**43/math.pi], [0, 2]],
    [[3, 6], ["IODnav", 10], ["omegaDot", 24, 2**43/math.pi], ["deltan", 16, 2**43/math.pi], ["Cuc", 16, 2**29], ["Cus", 16, 2**29], ["Crc", 16, 2**5], ["Crs", 16, 2**5], [0, 8]],
    [[4, 6], ["IODnav", 10], ["prn", 6], ["Cic", 16, 2**29], ["Cis", 16, 2**29], [-1, 14, 1/60], ["clockbias", 31, 2**34], ["clockdrift", 21, 2**46], ["clockdriftrate", 6, 2**59], [0, 2]], # check(-1),  t0c -> calculate, when corection param starts
    [[5, 6], ["a_i0", 11, 10**9 * 2**2], ["a_i1", 11, 10**9 * 2**8], ["a_i2", 14, 10**9 * 2**15], [0, 5], ["BGDE5aE1", 10, 2**32], ["BGDE5bE1", 10, 2**32], ["E5b_HS", 2], ["E1B_HS", 2], ["E5b_DVS", 1], ["E1B_DVS", 1], ["WN", 12], ["TOW", 20], [0, 23]],
    [[6, 6], ["a0", 32, 10**9 * 2**30], ["a1", 24, 10**15 * 2**50], ["t_LS", 8], [0*3600, 8], [-1, 8], [-1, 8], [-1, 3], [-1, 8], ["TOW", 20], [0, 3]]
]

almonacForSatDataStructure = [
    ["prn",        6],
    [-1,           13, 2**9], # delta(a^1/2)
    ["e",          11, 2**16],
    ["omega",      16, 2**14/math.pi],
    [-1,           11, 2**15/math.pi], # small delta_i
    ["omega0",     16, 2**33/math.pi],
    ["omegaDot",   11, 2**15/math.pi],
    ["M0",         16, 2**15/math.pi],
    ["clockbias",  16, 2**19],
    ["clockdrift", 13, 2**38],
    ["E5b_HS",     2],
    ["E1B_HS",     2]
]

##################################
#                                #
#      NAV MESSAGE ENCODING      #
#                                #
##################################

def indexOrZero(data, index):
    if index<0 or index>=len(data):
        return 0
    else:
        return data[index]

def stringToArray(dataString):
    dataBin = []
    for char in dataString:
        if char=='0':
            dataBin.append(0)
        if char=='1':
            dataBin.append(1)
    return dataBin

SSP_values = [-1, stringToArray("00000100"), stringToArray("00101011"), stringToArray("00101111")]
SYNC = stringToArray("0101100000")

crc_primitive = "100000100011101110101001"
crc_generator = "1100001100100110011111011"

#data: 128 bit array
def make_nominal_pages(data, SSP_i):
    tail = [0]*6

    # even = 0
    # page type = 0
    # data k : 112
    # tail = 000000
    
    crc_protected_1 = [0, 0] + data[0:112]
    
    # odd = 1
    # page type = 0
    # data j : 16
    # resrved : 40
    # SAR : 22 = 1 000000...
    # Spare : 2
    
    crc_protected_2 = [1, 0] + data[112:128] + [0]*40 + [1]+[0]*21 + [0,0]
    
    # CRCj : 24 : even/odd, page type, data k, data j, spare, sar, reserved
    #                 2         2         112    16      2     22     40    =  194
    
    #print(len(crc_protected_1+crc_protected_2))
    #print(''.join(map(lambda x: str(x), crc_protected_1+crc_protected_2)))
    crc = NavMessage.crc_remainder(crc_protected_1+crc_protected_2, stringToArray("1100001100100110011111011"), 0)
    #print(len(crc))
    crc = [0]*(24-len(crc)) + crc
    
    # SSP : 8
    # tail = 000000
    
    return (crc_protected_1 + tail, crc_protected_2 + crc + SSP_values[SSP_i] + tail)

def encode_page(plain):
    
    def encode1(d, i):
        G1 = (indexOrZero(d, i-0) + indexOrZero(d, i-1) + indexOrZero(d, i-2) + indexOrZero(d, i-3) + indexOrZero(d, i-6))%2
        G2 = (indexOrZero(d, i-0) + indexOrZero(d, i-2) + indexOrZero(d, i-3) + indexOrZero(d, i-5) + indexOrZero(d, i-6) + 1)%2
        
        
        #G1 = (indexOrZero(d, i-0) + indexOrZero(d, i-3) + indexOrZero(d, i-4) + indexOrZero(d, i-5) + indexOrZero(d, i-6))%2
        #G2 = (indexOrZero(d, i-0) + indexOrZero(d, i-1) + indexOrZero(d, i-3) + indexOrZero(d, i-4) + indexOrZero(d, i-6))%2
        return (G1, G2)
    
    sG1 = [0]*len(plain)
    sG2 = [0]*len(plain)
    sG = [0]*(2*len(plain))
    for i in range(len(plain)):
        G1, G2 = encode1(plain, i)
        sG1[i] = G1
        sG2[i] = G2
        sG[2*i] = G1
        sG[2*i+1] = G2
    
    return sG

#############################
#                           #
#      PACKAGE FOR USE      #
#                           #
#############################

def getConstelation():
    constelation = Constelation.Constelation()
    constelation.prefix = "E"
    constelation.bitsPerFrame = 25
    constelation.RINEXDataRecordDesciption = getRINEXDataRecordDesciption()
    constelation.RINEXheaderDescription = [
        ["GAL", ["a_i0", RINEX.parse_float], ["a_i1", RINEX.parse_float], ["a_i2", RINEX.parse_float], "IONOSPHERIC", "CORR"],
        ["GAL", ["a_i0", RINEX.parse_float], ["a_i1", RINEX.parse_float], ["a_i2", RINEX.parse_float], ["a_i3", RINEX.parse_float], "IONOSPHERIC", "CORR"],
        ["GAUT", ["a0", RINEX.parse_float], ["a1", RINEX.parse_float], ["TOW", int], ["WN", int], "TIME", "SYSTEM", "CORR"], #UTC
    ]
    constelation.postProcessRINAXData = postProcessRINAXData
    constelation.utcToConstelationTime = utcToConstelationTime
    constelation.clockCorection = clockCorection
    constelation.timeDifference = timeDifference
    constelation.getSatPosVel = getSatPosVel
    constelation.fillBuffer = fillBuffer
    constelation.getSetupHeader = lambda sats: "E:("+",".join(map(lambda name: name[-2:]+"[]", sats))+")"

    return constelation
