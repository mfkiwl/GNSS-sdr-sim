import main
import orbit

import datetime
import numpy as np
import socket
import time

import Constelation
import Glonass
import Galileo
import GPS
import BeiDou
import IRNSS

def startClient():
    print("Starting")

    (startTime, duration, posVelFunc, sats, setup, config) = init()

    sim = run(startTime, duration, posVelFunc, sats)

    with socket.socket() as sock:
        print("connecting")
        sock.connect(("localhost", 21978))
        print("connected")
        sockFile = sock.makefile(mode = 'rw')
        while True:
            line = sockFile.readline().strip()
            #print("line:", line)
            if line=="config":
                sockFile.write(config+"\n")
                sockFile.flush()
            elif line=="setup":
                sockFile.write(setup+"\n")
                sockFile.flush()
            elif line=="next":
                dataString = next(sim, None)
                if dataString is not None:
                    sockFile.write(dataString+"\n")
                    sockFile.flush()
                else:
                    #sockFile.close()
                    break
            else:
                print("Unexpected request:", line)
                #sockFile.close()
    print("Done")

def init():
    sats, setup = Constelation.loadSats([
        (GPS.getConstelation(), "data/GPS/brdc3260.23n"),
        #(GPS.getConstelation(), "data/GPS/Brdc3250.23n"),

        
        #(GPS.getConstelation(), "D:/data/brdc/BRDM00DLR_S_20241970000_01D_MN.rnx"),
        #(Glonass.getConstelation(), "D:/data/brdc/BRDM00DLR_S_20241970000_01D_MN.rnx"),
        #(Galileo.getConstelation(), "D:/data/brdc/BRDM00DLR_S_20241970000_01D_MN.rnx"),
        #(BeiDou.getConstelation(), "D:/data/brdc/BRDM00DLR_S_20241970000_01D_MN.rnx"),
        #(IRNSS.getConstelation(), "D:/data/brdc/BRDM00DLR_S_20241970000_01D_MN.rnx"),
    ])

    centerFrequency = 1575420000 # L1  gps / galileo
    #centerFrequency = 1602000000 # L1  glonass
    #centerFrequency = 1561098000 # B1i beidou
    #centerFrequency = 1176450000 # L5  irnss
    #sampleRate = 2600000
    sampleRate = 15000000
    #IQFile = "../../data/OutputIQ.sigmf-data"
    IQFile = "D:/data/iq/gps_oldbrdc15.bin"

    config = "config "+str(centerFrequency)+" "+str(sampleRate)+" "+IQFile

    #startTime = datetime.datetime(2023,11,22, 0, 0) # brdc3260.23n
    startTime = datetime.datetime(2024,7,16, 0, 0) # BRDM00DLR_S_20241970000_01D_MN.rnx
    duration = datetime.timedelta(seconds=60*5+1)

    #userPos = np.array([[-2758918.635941], [4772301.120089], [3197889.437237]]) # gps-sdr-sim
    #userPos = np.array([[1240086], [5460847], [3043454]]) # University of Delhi, New Delhi, India : 28.685194, 77.205865, 240
    userPos = orbit.wgslla2xyz(28.685194, 77.205865, 240)
    posVelFunc = main.simplePathInterpolation([(startTime, userPos)])

    return (startTime, duration, posVelFunc, sats, setup, config)

def run(startTime, duration, posVelFunc, sats):
    timestep = datetime.timedelta(milliseconds=100) # hardcoded 0.1s
    endTime = startTime+duration
    time = startTime

    while time <= endTime:
        t = time.second+time.microsecond/1000000
        (pos, vel) = posVelFunc(time)
        (dataString, result) = main.generateFrame(pos, vel, sats, time)
        main.printResults(time, result, pos, vel)
        yield dataString
        time += timestep

if __name__ == "__main__":
    startClient()