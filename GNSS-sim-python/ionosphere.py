import const
import orbit
import math

########################
#                      #
#    Genneral Model    #
#                      #
#################################################################
#                                                               #
#   ###    ####   #   #   #   #   ####   ###     ###    #       #
#  #       #      ##  #   ##  #   #      #  #   #   #   #       #
#  #  ##   ###    # # #   # # #   ###    ###    #####   #       #
#  #   #   #      #  ##   #  ##   #      # #    #   #   #       #
#   ###    ####   #   #   #   #   ####   #  #   #   #   ####    #
#                                                               #
#################################################################

# ported from FGI-GSRx
def calcIonoCorrections(userPos, satPos, eph, refTime):

    iAlpha0 = eph["a_0"]
    iAlpha1 = eph["a_1"]
    iAlpha2 = eph["a_2"]
    iAlpha3 = eph["a_3"]

    iBeta0 = eph["b_0"]
    iBeta1 = eph["b_1"]
    iBeta2 = eph["b_2"]
    iBeta3 = eph["b_3"]

    pi = math.pi

    (elev, azim, height) = orbit.calcAzimElevDist(userPos, satPos-userPos)

    # Calculate helping coordinates
    (dLat,dLon,dAlt) = orbit.wgsxyz2lla(userPos)
    dEle = elev/180*pi #satSingle.elev/180*pi
    dAzi = azim/180*pi #satSingle.azim/180*pi
    dwTowMs = refTime * 1000

    # Constants
    INV_PI = 1/const.PI
    SPEED_OF_LIGHT = const.SPEED_OF_LIGHT
    SECONDS_IN_DAY = const.SECONDS_IN_DAY

    # SV elevation in semicircles.
    es  = dEle * INV_PI

    # Receiver latitude in semicircles.
    phu = dLat/180

    # Receiver longitude in semicircles.
    lmu = dLon/180             

    dIono = None
    # Don't compute ionospheric correction for SV's below the horizon.
    if (es < 0.0):
        dIono=0.0
    else:
        # Compute slant factor f.
        temp = 0.53 - es
        f = 1.0 + 16.0*temp*temp*temp

        # Use nocturnal value when ionospheric correction is unavailable
        dIono = f * 5.0e-9 * SPEED_OF_LIGHT + 0.5

        # Compute Earth angle psi (semicircles).
        psi = 0.0137 / (es + 0.11) - 0.022

        # Compute subionospheric latitude phi (semicircles).
        # Here dAzi is in radians.
        phi = phu + psi * math.cos(dAzi)

        # Limit phi to between +75 degrees and - 75 degrees.
        if (phi > 0.416):
            phi = 0.416
        elif (phi < -0.416):
            phi = -0.416
        

        # Compute subionospheric longitude lmi (semicircles).
        lmi = lmu + psi * math.sin(dAzi) / math.cos(phi*pi)

        # Compute local time in seconds
        # = GMT + 43200 seconds per semicircle of longitude 
        sec = dwTowMs * 0.001
        tlocal = sec + SECONDS_IN_DAY * 0.5 * lmi

        if (tlocal >= SECONDS_IN_DAY):
            lMultiples = math.floor(tlocal / SECONDS_IN_DAY)
            tlocal = tlocal - SECONDS_IN_DAY * (lMultiples)
        elif (tlocal < 0.0):
            lMultiples = math.floor((abs(tlocal)) / SECONDS_IN_DAY) + 1
            tlocal = tlocal + SECONDS_IN_DAY * (lMultiples)
        

        # Compute subionospheric geomagnetic latitude phm (semicircles).
        phm = phi + 0.064 * math.cos((lmi - 1.617) * pi)
        phm2 = phm * phm
        phm3 = phm2 * phm

        # Diurnal maximum time delay: suma. Diurnal period: sumb.    
        suma = iAlpha0 + iAlpha1*phm + iAlpha2*phm2 + iAlpha3*phm3 
        sumb = iBeta0 + iBeta1*phm + iBeta2*phm2 + iBeta3*phm3
            
        if (suma < 0.0):
            suma = 0.0
        

        if (sumb < 72000.0):
            sumb = 72000.0
        

        if (sumb != 0.0):
            xtemp = 2.0 * pi * (tlocal - 50400.0) / sumb
        else:
            xtemp = 0.0
        

        if (abs(xtemp) < 1.57):
            x2 = xtemp * xtemp
            x4 = x2 * x2
            temp = 1.0 - x2 * 0.5 + x4 * (1.0 / 24.0)
            dIono = f * (5.0e-9 + suma * temp) * SPEED_OF_LIGHT + 0.5
        else:
            dIono = f * 5.0e-9 * SPEED_OF_LIGHT

    return dIono
        
        
#####################
#                   #
#   NeQuick Model   #
#                   #
#######################################################
#                                                     #
#   #   #    ##     ###            #          #  #    #
#   ##  #   #  #   #   #   #   #        ###   # #     #
#   # # #   ###    #  ##   #   #   #   #      ###     #
#   #  ##   #      #  ##   #   #   #   #      #  #    #
#   #   #    ###    #####   ###    #    ###   #   #   #
#                                                     #
#######################################################

# todo

def main():
    print("ionosphere")

if __name__ == "__main__":
    main()