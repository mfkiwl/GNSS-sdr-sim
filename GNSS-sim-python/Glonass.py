import datetime
import math
import numpy as np
from scipy.integrate import odeint

import NavMessage
import Constelation

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
        [["name", str], ["year", int], ["month", int], ["day", int], ["hour", int], ["minute", int], ["second", int], "-tau(t_b)", "gamma(t_b)", ["message frame time", float_int]],
        ["x(t_b)", "x'(t_b)", "x''(t_b)", ["health", float_int]],
        ["y(t_b)", "y'(t_b)", "y''(t_b)", ["n", float_int]],
        ["z(t_b)", "z'(t_b)", "z''(t_b)", ["age of info", float_int]]
    ]

def postProcessRINAXData(data, header):
    for sat in data:
        sat["tau(t_b)"] = -sat["-tau(t_b)"]
        sat["l"] = sat["health"]!=0
        sat["B"] = sat["health"]
        sat["M"] = 0
        sat["t_b interval"] = 30
        sat["P"] = 0
        sat["P1"] = int(0b01)
        sat["P2"] = 0 # even?
        sat["N_T"] = 12 # day if 4 year periode staring from leap year (hard coded at day i write this)
        sat["F_T"] = 11 # i picked 64 meter accuracy
        sat["delta tau"] = 0 # time delay between L1 and L2, i only do L1 at the moment so just 0
        sat["frequency"] = 1602000000 + sat["n"]*562500
        
##############################
#                            #
#      ORBIT SIMULATION      #
#                            #
##############################

def getSatPos(eph, t):
    (t_b, _, _) = utcToConstelationTime(eph["datetime"])
    t_k = t[0]
    deltat = t_k - t_b#((eph["t_b interval"]/2)*60)
    posvel = np.array(calcOrbit(eph, deltat))
    return (np.array([[posvel[0]], [posvel[1]], [posvel[2]]]), np.array([[posvel[3]], [posvel[4]], [posvel[5]]]))

# from matlab reciver
# Constants
c20 = -0.00108262575 #const.C20; % 2nd zonal harmonic of ellipsoid

# These are slightly different values than in the ICD. 
# Max SV pos difference is anyhow just 2 cm
mu  = 398600500000000 #const.EARTH_GRAVCONSTANT; % Gravitational constant
ae  = 6378137 #const.EARTH_SEMIMAJORAXIS;	% Earth Semimajor axis
we  = 7.2921151467e-05 #const.EARTH_WGS84_ROT; % Earth rotation rate

def orbit_dif_func(y, t, acc, zero):
    r = math.sqrt( (y[0]**2) + (y[1]**2) + (y[2]**2) )
    dy=np.zeros(6)#zeros(6,1);
    dy[0]=y[3]
    dy[1]=y[4]
    dy[2]=y[5]
    dy[3]=(-mu/(r**3)*y[0] + 
        3/2*c20*mu*(ae**2)/(r**5)*y[0]*(1 - 5/(r**2)*(y[2]**2)) + 
        (we**2)*y[0] + 2*we*y[4] + acc[0])
    dy[4]=(-mu/(r**3)*y[1] + 
        3/2*c20*mu*(ae**2)/(r**5)*y[1]*(1 - 5/(r**2)*(y[2]**2)) + 
        (we**2)*y[1] - 2*we*y[3] + acc[1])
    dy[5]=(-mu/(r**3)*y[2] + 
        3/2*c20*mu*(ae**2)/(r**5)*y[2]*(3 - 5/(r**2)*(y[2]**2)) + acc[2])

    return dy

def calcOrbit(sat, deltat):
    tspan = np.linspace(0, deltat, 45)
    y0 = [sat["x(t_b)"]*1000, sat["y(t_b)"]*1000, sat["z(t_b)"]*1000, sat["x'(t_b)"]*1000, sat["y'(t_b)"]*1000, sat["z'(t_b)"]*1000]
    acc = [sat["x''(t_b)"]*1000, sat["y''(t_b)"]*1000, sat["z''(t_b)"]*1000]
    #print(y0, acc)
    sol = odeint(orbit_dif_func, y0, tspan, args=(acc, 0))[-1]
    return sol

def utcToConstelationTime(dateTime : datetime.datetime):
    midnight = dateTime.replace(hour=0, minute=0, second=0, microsecond=0)
    leapyear = dateTime.replace(year=int(dateTime.year/4)*4, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    tk = (dateTime - midnight)
    t_k = tk.seconds + tk.microseconds/1000000
    N_T = (dateTime - leapyear).days
    N_4 = int((leapyear.year - 1996)/4)
    return (t_k, N_T, N_4)

def clockCorection(sat, syncTime):

    (t_b, _, _) = utcToConstelationTime(sat["datetime"])
    t_k = syncTime[0]
    deltat = t_k - t_b#((eph["t_b interval"]/2)*60)


    satClkCorr = -sat["tau(t_b)"] + sat["gamma(t_b)"] * deltat

    #satClkCorr = (sat["clockdriftrate"] * dt + sat["clockdrift"]) * dt + sat["clockbias"]


    return (syncTime[0]-satClkCorr, syncTime[1]) # could be +, since i do inverse of reciever

def timeDifference(t1, t2):
    return t1[0]-t2[0]

####################################
#                                  #
#      NAV MESSAGE GENERATION      #
#                                  #
####################################

def fillBuffer(bitBuffer, dateTime:datetime.datetime, eph, ephs):
    if(dateTime.microsecond!=0 and dateTime.second%2!=0):
        print("not aligned")
        return [0]
    t = (dateTime.minute*60+dateTime.second)%(150)
    frame = int(t/30)
    string = int((t-30*frame)/2)

    frame+=1
    string+=1

    #print("f, s:",frame,string)

    update = False
    if "eph" not in bitBuffer.store or bitBuffer.store["eph"]!=eph:
        update = True
        bitBuffer.store["eph"]=eph

    (t_k, N_T, N_4) = utcToConstelationTime(dateTime)
    (t_b, _, _) = utcToConstelationTime(eph["datetime"])
    #t_b += (eph["t_b interval"]*60)/2
    data = []

    if string<=4:
        data = generateImmediateData(eph, string, frame, t_k, t_b, update)
    elif string==5:
        data = generateNonImmediateData(eph, string, frame)
    elif string>=14 and frame==5:
        data = generateSat25SpotData(eph, string, frame)
    else:
        aSatNum = int((string-6)/2)+(frame-1)*5 + 1
        aSatName = "R"+(str(aSatNum).zfill(2))
        if aSatName in ephs:
            data = generateAlmonac(ephs[aSatName], string, frame)
        else:
            data = NavMessage.dataStructureToBits([[string, 4], [0, 72]], {})
    
    return dataToString(data)

    
def getTkDataStructure(t_k):
    return [[int(t_k/60/60)%24, 5, 1], [int(t_k/60)%60, 6, 1], [int(t_k/30), 1, 1]]

def generateImmediateData(sat, stringnumber, framenumber, t_k, t_b, hasNewData=False):

    P3 = 0 if framenumber == 5 else 1
    P4 = 1 if hasNewData else 0
    E = t_k # time elapsed since upload
    # p4 -> 1 indicates update
    # M -> modification/version: 00
    # ln -> health 0=ok
    #print("efemris")
    datastructure = [
        [[1, 4], [0, 2], ["P1", 2], getTkDataStructure(t_k),                             ["x'(t_b)", 24, 2**20], ["x''(t_b)", 5, 2**30], ["x(t_b)", 27, 2**11]],
        [[2, 4], ["B", 3], ["P2", 1], [t_b, 7, 1/60/15], [0, 5],                         ["y'(t_b)", 24, 2**20], ["y''(t_b)", 5, 2**30], ["y(t_b)", 27, 2**11]],
        [[3, 4], [P3, 1], ["gamma(t_b)", 11, 2**40], [0, 2], ["P", 1], ["l", 1],         ["z'(t_b)", 24, 2**20], ["z''(t_b)", 5, 2**30], ["z(t_b)", 27, 2**11]],
        [[4, 4], ["tau(t_b)", 22, 2**30], ["delta tau", 5, 2**30], [E, 5], [0, 14], [P4, 1], ["F_T", 4], [0, 3], ["N_T", 11], ["n", 5], ["M", 2]]
    ]

    return NavMessage.dataStructureToBits(datastructure[stringnumber-1], sat)

def generateNonImmediateData(sat, stringnumber, framenumber):
    datastructure = [
        [[5, 4], ["N^A", 11], ["tau_c", 32, 2**27], [0, 1], ["N_4", 5], ["tau_GPS", 22, 2**30], ["l", 1]]
    ]
    return NavMessage.dataStructureToBits(datastructure[0], {"tau_c":0, "N_4":int((2024-1996)/4), "tau_GPS":0, "N^A":12, "l":sat["l"]})

def generateAlmonac(sat, stringnumber, framenumber):
    #print("almonac")
    # l : C_n
    tau = sat["tau(t_b)"]
    lambda_longitude_ascending_node = 0
    delta_i_mean_inclination = 0
    epsilon_eccentricity = 0
    omega_argument_perigee = 0
    tau_lambda_time_ascending_node = 0
    delta_T_period_corection = 0
    delta_T_period_corection_change = 0
    H_carrier_frequency_number = 0

    datastructure = [
        [[stringnumber, 4], ["l", 1], ["M", 2], ["n", 5], [tau, 10], [lambda_longitude_ascending_node, 21], [delta_i_mean_inclination, 18], [epsilon_eccentricity, 15]],
        [[stringnumber, 4], [omega_argument_perigee, 16], [tau_lambda_time_ascending_node, 21], [delta_T_period_corection, 22], [delta_T_period_corection_change, 7], [H_carrier_frequency_number, 5], ["l", 1]],
    ]
    return NavMessage.dataStructureToBits(datastructure[stringnumber%2], sat)

def generateSat25SpotData(sat, stringnumber, framenumber):
    #print("alast frame of superframe only has 4 sats, fill 5th with this")
    datastructure = [
       [[14, 4], ["B1", 11], ["B2", 10], ["KP", 2], [0, 76-4-11-10-2]],
       [[15, 4], [0, 76-1-4], ["l", 1]]
    ]
    return NavMessage.dataStructureToBits(datastructure[stringnumber%2], {"B1":0, "B2":0, "KP":0, "l":sat["l"]})

def dataToString(data):
    # data : 40 bits

    # bit position 85 is 0
    # encode data: bit 85 to 9 (77 bits)
    # hamming code: bit 9 to 1 (8 bits)
    # time mark: 15 bits 30 symbols: "111110001101110101000010010110"

    assert len(data) == 76

    # todo: check ordering
    hammingCode = 0
    for i in range(len(data)):
        if data[i]==1:
            hammingCode = hammingCode^i
    hammingBits = [0]*8
    for i in range(len(hammingBits)):
        if (hammingCode>>i)&1==1:
            hammingBits[i]=1


    relativeCode = [0]
    for v in data+hammingBits:
        relativeCode.append((v+relativeCode[-1])%2)
    
    #print("relative code", relativeCode)

    bibinaryCode = [0]*(len(relativeCode)*2)
    for i in range(len(relativeCode)):
        bibinaryCode[2*i+0] = relativeCode[i]
        bibinaryCode[2*i+1] = (relativeCode[i]+1)%2

    return bibinaryCode+[1,1,1,1,1,0,0,0,1,1,0,1,1,1,0,1,0,1,0,0,0,0,1,0,0,1,0,1,1,0]

#############################
#                           #
#      PACKAGE FOR USE      #
#                           #
#############################

def checkEphemeris(eph, t):
    interval = datetime.timedelta(minutes=eph["t_b interval"]);
    ephTime = eph["datetime"]
    if ephTime-interval<=t and t<ephTime+interval+interval:
        #print("use :", eph["name"])
        return eph
    else:
        #print("skip:", eph["name"])
        return None

def getConstelation():
    constelation = Constelation.Constelation()
    constelation.prefix="R"
    constelation.bitsPerFrame = 10
    constelation.RINEXDataRecordDesciption = getRINEXDataRecordDesciption()
    constelation.postProcessRINAXData = postProcessRINAXData
    constelation.utcToConstelationTime = utcToConstelationTime
    constelation.clockCorection = clockCorection
    constelation.timeDifference = timeDifference
    constelation.getSatPosVel = getSatPos
    constelation.fillBuffer = fillBuffer
    constelation.checkEphemeris = checkEphemeris
    constelation.getIdString = lambda eph: eph["name"]+" ["+str(eph["n"])+"]"
    constelation.getSetupHeader = lambda sats: "R:("+",".join(map(lambda name: name[-2:]+"["+str(sats[name].eph.getEarliest()["n"])+"]", sats))+")"

    return constelation