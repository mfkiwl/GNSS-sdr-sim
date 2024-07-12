import main

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
        (GPS.getConstelation(), "data/GPS/Brdc3250.23n"),
    ])

    centerFrequency = 1575420000
    sampleRate = 2600000
    IQFile = "../../data/OutputIQ_c.sigmf-data"
    config = "config "+str(centerFrequency)+" "+str(sampleRate)+" "+IQFile

    startTime = datetime.datetime(2023,11,22, 0, 0)
    duration = datetime.timedelta(seconds=40)

    userPos = np.array([[-2758918.635941], [4772301.120089], [3197889.437237]]) # gps-sdr-sim
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