import const
import math
import numpy as np
from scipy.integrate import odeint


    #x = sat["x(t_b)"] + sat["x'(t_b)"]*t_k + 0.5*sat["x''(t_b)"]*t_k**2
    #y = sat["y(t_b)"] + sat["y'(t_b)"]*t_k + 0.5*sat["y''(t_b)"]*t_k**2
    #z = sat["z(t_b)"] + sat["z'(t_b)"]*t_k + 0.5*sat["z''(t_b)"]*t_k**2

    #return np.array([[x],[y],[z]])*1000

def getUserPosition():
    # moscouw
     return np.array([[2849.84002],[2196.13241],[5249.03460]])*1000
    # ankera
    #return np.array([[4114.64236],[2658.44850],[4072.25019]])*1000


def getTravelTime(userPos, satPos, eph):
    d = math.sqrt((userPos[0][0]-satPos[0][0])**2 + (userPos[1][0]-satPos[1][0])**2 + (userPos[2][0]-satPos[2][0])**2)
    # need to add ionosphere
    c = 299792458
    return d/c

def getDoplerShift(userPos, userVel, satPos, satVel, sat):
    f_k = sat["frequency"]
    #satPos = getSatPos(sat, tk)
    #vel = getSatPos(sat, tk+1)[0]-satPos
    vel = satVel
    #userPos = getUserPosition()

    c = 299792458
    #f_k = 1575420000 + sat["n"] * 562500 
    #v_reciever = 0 # todo: set corectly
    #a = vel
    #b = satPos-userPos
    #b = b/np.linalg.norm(b)
    #vel_k = (a[0][0]*b[0][0]+a[1][0]*b[1][0]+a[2][0]*b[2][0]) # satalite velocity toword target
    #f_shift = (c+v_reciever)/(c+vel_k)*f_k - f_k

    dPos = satPos-userPos
    dopp = np.sum(dPos*(satVel+userVel))
    dopp = dopp / np.linalg.norm(dPos)
    doppler = -dopp*f_k/c

    return doppler

def getVisability(userPos, satPos, sat):
    #satPos = getSatPos(sat, tk)
    #userPos = getUserPosition()
    # visability
    a = userPos #(-[[0],[0],[0]]) # vector from earh center through location
    a = a/np.linalg.norm(a)
    b = satPos - userPos # from location to satalite
    b = b/np.linalg.norm(b)
    dot_angle = a[0][0]*b[0][0]+a[1][0]*b[1][0]+a[2][0]*b[2][0] # dot product between the 2 needs to be >0

    return 100 if dot_angle > 0.0871557 else 0
    return (dot_angle)*100 if dot_angle > 0.0871557 else 0 # 5 degrees above horizon

def earthRotationCorrection(satPos, userPos):
    EARTH_WGS84_ROT = 7.2921151467E-5
    WGS84oe = EARTH_WGS84_ROT
    SPEED_OF_LIGHT = 299792458
    rhox = satPos[0][0]-userPos[0][0]
    rhoy = satPos[1][0]-userPos[1][0]
    return WGS84oe /SPEED_OF_LIGHT * (satPos[1][0]*rhox-satPos[0][0]*rhoy)/SPEED_OF_LIGHT

#def simulate(sats, shared, t):
#    time = t
#    userPos = getUserPosition()
#    results = {}
#    for satName in sats:
#        #print("Simulate sat:", satName)
#        sat = sats[satName]
#        transmitTime = t
#        satPos, satVel = getSatPos(sat, transmitTime)
#        travelTime = getTravelTime(userPos, satPos, sat, shared)
#        doplerShift = getDoplerShift(satPos, satVel, sat, transmitTime) 
#        power = getVisability(satPos, sat, transmitTime) # how visable was the currect location at the of transmition
#        arivelTime = transmitTime + travelTime
#        delay = arivelTime - time
#        results[sat["name"]] = {"delay":delay, "shift":doplerShift, "power":power, "satpos":satPos}
#
#    return results



def simulationResultsTranspose(results):
    trs = {}
    for satName in results[0].keys():
        delays = []
        shifts = []
        powers = []
        satpos = []
        for result in results:
            delays.append(result[satName]["delay"])
            shifts.append(result[satName]["shift"])
            powers.append(result[satName]["power"])
            satpos.append(result[satName]["satpos"])
        trs[satName] = {"delay":delays, "shift":shifts, "power":powers, "satpos":satpos}
    return trs

def addFrequency(trs, sats):
    for satName in trs:
        trs[satName]["frequency"] = 1602000000 + sats[satName]["n"]*562500

def store(trs, save_count):
    
    dataFile = open("GlonassC/GlonassC/data.h", "w")
    dataFile.write("#pragma once\n")
    dataFile.write("#include <stdint.h>\n\n")

    for satName in trs:
        datastream = trs[satName]["datastream"][0:save_count] # 3 subframes of 15 pages of 500 symbols
        delay = trs[satName]["delay"][0:int(save_count/25)]
        dopler = trs[satName]["shift"][0:int(save_count/25)]
        power = trs[satName]["power"][0:int(save_count/25)]

        dataFile.write("uint8_t sat"+satName+"_data_example[] = { ")
        dataFile.write(','.join(map(str, datastream)))
        dataFile.write(" };\n")
        
        dataFile.write("size_t sat"+satName+"_data_length = ")
        dataFile.write(str(len(datastream)))
        dataFile.write(";\n")
        
        dataFile.write("double sat"+satName+"_delay_ms[] = {")
        dataFile.write(','.join(map(lambda x: str(x*1000), delay)))
        dataFile.write("};\n")
        
        dataFile.write("float sat"+satName+"_doppler[] = {")
        dataFile.write(','.join(map(lambda x: str(x)+"f", dopler)))
        dataFile.write("};\n")

        dataFile.write("int sat"+satName+"_power[] = {")
        dataFile.write(','.join(map(lambda x: str(int(x)), power)))
        dataFile.write("};\n")

        dataFile.write("long sat"+satName+"_frequency = ")
        dataFile.write(str(trs[satName]["frequency"]))
        dataFile.write(";\n\n")

    dataFile.close()

    return None

#ported from FGI-GSRx
def wgsxyz2lla(pos):
    A = const.EARTH_SEMIMAJORAXIS
    F = const.EARTH_FLATTENING # note: the const parameter is the inverse flattening
    E2 = (2-F)*F

    ## Input sanity check
    #if isvector( xyz )
    #    if length( xyz ) ~= 3
    #        error( 'Input is a vector of length %d, 3 expected', length( xyz ) );
    #    elseif iscolumn( xyz ) %size( xyz, 1 ) == 3
    #        xyz = xyz';       
    #    end                
    #elseif size( xyz, 2 ) ~= 3
    #    error( 'Input must be of size nx3, %d×%d encountered', ...
    #        size( xyz, 1 ), size( xyz, 2 ) );
    #end

    # The actual conversion
    lat = 0
    lon = math.atan2( pos[1][0], pos[0][0] )*180/math.pi
    alt = 0

    # The iteration of latitude and altitude is started at zero latitude
    p = math.sqrt(pos[0][0]*pos[0][0] + pos[1][0]*pos[1][0])
    for iteration in range(10):
        N = A / math.sqrt( 1 - E2 * math.sin( lat )**2 )
        alt = p / math.cos( lat ) - N
        lat = math.atan( pos[2][0] / p / (1 - E2 * (N / (N + alt ) ) ) )*180/math.pi

    return (lat, lon, alt)

#ported from FGI-GSRx
def calcAzimElevDist(ref_xyz, los_xyz):

    ## Input sanity check
    #if isvector( los_xyz )
    #    if length( los_xyz ) ~= 3
    #        error( 'xyz is a vector of length %d, 3 expected', length( los_xyz ) );
    #    elseif size( los_xyz, 1 ) == 3
    #        los_xyz = los_xyz';
    #    end                
    #elseif size( los_xyz, 2 ) ~= 3
    #    error( 'xyz must be of size n×3, %d×%d encountered', ...
    #           size( los_xyz, 1 ), size( los_xyz, 2 ) );
    #end

    #if ~isvector( ref_xyz ) || length( ref_xyz ) ~= 3
    #    error( 'ref_xyz must be a vector of length 3, %d×%d encountered', ...
    #        size( ref_xyz, 1 ), size( ref_xyz, 2 ) );
    #elseif norm( ref_xyz ) < 1e6
    #    warning( 'calcAzimElevDist:possibleLLAorigin', ...
    #            'Origin coordinates [%d %d %d] input as XYZ; sure they are not lat-lon-alt?', ...
    #            ref_xyz(1), ref_xyz(2), ref_xyz(3)  );
    #end

    # Construct the rotation matrix from XYZ to local level
    (reflat, reflon, _) = wgsxyz2lla(ref_xyz )
    reflat = reflat/180*math.pi
    reflon = reflon/180*math.pi

    R = np.array([[-math.sin( reflon ),                  math.cos( reflon ),                  0],
        [-math.sin( reflat ) * math.cos( reflon ),   -math.sin( reflat ) * math.sin( reflon ),    math.cos( reflat )],
        [math.cos( reflat ) * math.cos( reflon ),    math.cos( reflat ) * math.sin( reflon ),    math.sin( reflat )]])

    ## Compute azimuth, elevation, and distance
    # Transform xyz to local level coordinates
    enu = np.dot(R, los_xyz)

    dist = np.linalg.norm(enu)
    az = math.atan2( enu[0][0], enu[1][0] )*180/math.pi
    el = math.atan( enu[2][0] / math.sqrt( enu[0][0]*enu[0][0] + enu[1][0]*enu[1][0] ))*180/math.pi
    return (el, az, dist)

def main():
    print("orbit")
    #tspan = np.linspace(0, -778.2986593, 15)
    #y0 = [20638417.4804688, -19003576.171875, 6140998.53515625, -7242.57946014404, 394.978523254395, 3449.37324523926]
    #acc = [4.65661287307739e-06, -1.21071934700012e-05, 2.79396772384644e-06]
    #sol = odeint(orbit_dif_func, y0, tspan, args=(acc, 0))[-1]
    #print(sol)


if __name__ == "__main__":
    main()