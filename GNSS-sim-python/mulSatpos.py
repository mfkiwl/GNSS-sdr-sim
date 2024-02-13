import const
import math

# ported from FGI-GSRx

def getSatPosVel(eph, tk):
    gpsPi = const.PI
    c = const.SPEED_OF_LIGHT # Speed of light
    WGS84oe = const.EARTH_WGS84_ROT # WGS-84 value for the earths rotation velocity 
    GravConstant = const.EARTH_GRAVCONSTANT # WGS-84 value for the earths universal gravitation constant
    F = -2*math.sqrt(GravConstant)/c**2

    dCrs     =eph["Crs"] 		#sine correction to radius
    dCuc     =eph["Cuc"] 		#cosine correction to lattitude
    dCus     =eph["Cus"] 		#sine correction to lattitude
    dCic     =eph["Cic"] 		#cosine correction to inclination
    dCrc     =eph["Crc"] 		#cosine correction to radius
    dCis     =eph["Cis"] 		#sine correction to inclination
    dToe     =eph["toe"]
    dn       =eph["deltan"] 	#mean motion difference from computed value
    M0       =eph["M0"] 		#mean anomaly at reference time
    ecc      =eph["e"] 			#eccentricity
    sqrta    =eph["sqrt_a"]		#square root of semimajor axis
    dOmega   =eph["omega"] 		#argument of perigee
    dOmega0  =eph["omega0"] 	#right ascencion at reference time
    dOmegaDot=eph["omegaDot"]	#rate of right ascencion
    dI0      =eph["i0"] 		#orbital inclination
    dIdot    =eph["IDot"]       #rate of inclination angle
    geoSV    =False# eph["geo"]       # Geostationary satellite

    dA = sqrta * sqrta
    dN0 = math.sqrt(GravConstant /(dA * dA * dA))
    Mdot = dN0
    Mdot = Mdot + dn
                   
    # Mean anomaly
    M = M0 + Mdot*tk
    # Reduce mean anomaly to between 0 and 360 deg
    M   = (M + 2*gpsPi)%(2*gpsPi)

    # Initial guess of eccentric anomaly
    E = M

    # Iteratively compute eccentric anomaly 
    for k in range(20):

        sE = math.sin(E)
        cE = math.cos(E)
        dEdM = 1.0 / (1.0 - ecc * cE)
        dTemp  = (M - E + ecc * sE) * dEdM

        if(abs(dTemp) < 1.0e-14):
            break
            
        E = E + dTemp
    

    # Reduce eccentric anomaly to between 0 and 360 deg
    E   = (E + 2*gpsPi)%(2*gpsPi)

    # Compute relativistic correction term
    relcorr = F * ecc * sqrta * sE

    #dDeltaFreq    = eph(prn).a_f1 + 2.0*tk*eph(prn).a_f2;  
    # TBA: dDeltaTime = eph(prn).a_f0 + tk*(eph(prn).a_f1 + tk*eph(prn).a_f2) + relcorr;
                        
    Edot = dEdM * Mdot

    # Calculate the true anomaly and angle phi
    sqrt1mee=math.sqrt(1-ecc**2)
    P=math.atan2(sqrt1mee*sE,cE-ecc) + dOmega;

    # Reduce phi to between 0 and 360 deg
    P = P%(2*gpsPi)

    Pdot = sqrt1mee*dEdM*Edot
    Pdot2 = 2 * Pdot

    dtemp = 2 * P
    s2P = math.sin(dtemp)
    c2P = math.cos(dtemp)

    # Correct radius
    R    = dA * (1.0 - ecc * cE)
    Rdot = dA * ecc * sE * Edot
    R     = R + dCrs * s2P + dCrc * c2P
    Rdot  = Rdot + Pdot2 * (dCrs * c2P - dCrc * s2P)

    # Correct inclination
    I    = dI0
    I     = I + dIdot * tk + dCis * s2P + dCic * c2P
    Idot  = dIdot + Pdot2 * (dCis * c2P - dCic * s2P)

    # Correct argument of latitude
    U = P + dCus * s2P + dCuc * c2P
    Udot = Pdot + Pdot2 * (dCus * c2P - dCuc * s2P)

    sU = math.sin(U)
    cU = math.cos(U)

    Xp    = R * cU
    Yp    = R * sU
    Xpdot = Rdot * cU - Yp * Udot
    Ypdot = Rdot * sU + Xp * Udot

    # Compute the angle between the ascending node and the Greenwich meridian
    if(geoSV):
        L  = dOmega0 + tk * dOmegaDot
        L = L - WGS84oe * dToe
        Ldot = dOmegaDot - WGS84oe; # Does not know if this is correct
    else:
        L  = dOmega0 + tk * (dOmegaDot - WGS84oe)
        L = L - WGS84oe * dToe
        Ldot = dOmegaDot - WGS84oe

    # Reduce to between 0 and 360 deg
    L = (L + 2*gpsPi)%(2*gpsPi)

    sL = math.sin(L)
    cL = math.cos(L)

    sI = math.sin(I)
    cI = math.cos(I)

    dtemp = Yp * cI

    # Compute satellite coordinates
    satPositions = [0]*3 
    satPositions[0] = Xp * cL - dtemp * sL  
    satPositions[1] = Xp * sL + dtemp * cL
    satPositions[2] = Yp * sI

    if(geoSV):
        # For GEO satellite position computation:
        minus5degreeInRadian = ((gpsPi*(-5))/180)
        R_x = [[1,                0,                       0],
               [0,   math.cos(minus5degreeInRadian), math.sin(minus5degreeInRadian)],
               [0,  -math.sin(minus5degreeInRadian), math.cos(minus5degreeInRadian)]]

        R_z = [[math.cos(WGS84oe*tk),  math.sin(WGS84oe*tk),     0],
               [-math.sin(WGS84oe*tk), math.cos(WGS84oe*tk),     0],
               [0,                   0,                1]]

        satPositions = (R_z*R_x)*satPositions

    # Include relativistic correction in clock correction 
    #satClkCorr = satClkCorr + relcorr;

    dX = Xp * cL - dtemp * sL
    dY = Xp * sL + dtemp * cL
    dZ = Yp * sI

    dtemp2 = dZ*Idot
    dtemp3 = Ypdot*cI

    satVelocity = [0]*3
    satVelocity[0] = -Ldot*(dY) + Xpdot*cL - (dtemp3 + dtemp2)*sL
    satVelocity[1] = Ldot*(dX) + Xpdot*sL + (dtemp3 - dtemp2)*cL
    satVelocity[2] = dtemp*Idot + Ypdot*sI
    #satVelocity(4) = dDeltaFreq;

    return satPositions, satVelocity

