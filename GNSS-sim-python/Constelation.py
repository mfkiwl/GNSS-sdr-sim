import datetime
import numpy as np
import RINEX
import Satallite

class Constelation:
    """Data structure to hold all the various functions and values that are required to define a GNSS signal.
    """

    prefix = "" #G for GPS, R for GLONASS, E for galileo, ...
    RINEXDataRecordDesciption = [] # array of arrays of possible array: array of lines, each line an array of values on that line, each value a string label or array of string label and parsing function (float is default parsing function)
    RINEXheaderDescription = []    # array of arrays of possible array: array of lines, each line an array of values on that line, each value a string that must match or array of string label and parsing function, for values that need to be stored
    postProcessRINAXData = lambda data, header: None # function called after parsing, handel any needed post processing here
    getSatPosVel = lambda eph, t : (np.zeros(1,3), np.zeros(1,3)) # return a satellite's position and velocity
    # usually ony the following two lines are needed:
    #   mulSatpos.getSatPosVel(eph, t[0]-eph["toe"])
    #   return (np.array([satPos]).T, np.array([satVel]).T)

    bitsPerFrame = -1 # how many bits to send for encoding every 0.1 seconds: bitrate/10

    utcToConstelationTime = lambda t : t # format the time as needed by the other functions, usually split in Time Of Week and Week Number. I have not used it for time corections
    checkEphemeris = lambda self, eph, t : eph # check if data needs to be/can send for this satellite
    clockCorection = lambda self, eph, syncTime: syncTime # correct drift of the clock onboard the satellite, calculated before the satellites position is calculated
    timeDifference = lambda self, t1, t2: 0 # time difference is seconds, t1 and t2 are in the format returned by utcToConstelationTime
    travelTimeCorection = lambda self, eph, satPos, userPos, t: 0 # correct for effect of ionosphere, calculated after the satellites position is found

    fillBuffer = lambda self, t, sat, sats : [0, 1] # generate a navigation message

    getIdString = lambda self, eph : eph["name"] # get the prefix+number of a satellite

    getSetupHeader = lambda sats : "" # header that gets send to encoding to set it up corectly: prefix:(sv_id[arg],sv_id[arg],...)

    def addTimeStamp(self, ephList): 
        """Turn values in ephemeris into a datetime object
        """
        for eph in ephList:
            eph["datetime"] = datetime.datetime(eph["year"], eph["month"], eph["day"], eph["hour"], eph["minute"], eph["second"])

    def ephsToSats(self, ephList):
        """group ephemeri by sv_id turn those groups into satellite object for easy indexing.
        """
        ephPerSat = {}
        for eph in ephList:
            if eph["name"] not in ephPerSat:
                ephPerSat[eph["name"]] = []
            ephPerSat[eph["name"]].append(eph)
        sats = {}
        for name in ephPerSat:
            sats[name] = Satallite.Satallite(name, self, ephPerSat[name])
        return sats

    def loadSatsFromRinax(self, filename):
        """Parse the RINEX file 'filename' using the functions that have been set for this Constelation object
        Return a map of satellites and the header data
        """
        ephList, headerData = RINEX.parseRINEX(filename, self.RINEXDataRecordDesciption, self.RINEXheaderDescription, self.prefix)
        newList = self.postProcessRINAXData(ephList, headerData)
        ephList = newList if newList is not None else ephList
        self.addTimeStamp(ephList)
        sats = self.ephsToSats(ephList)
        return sats, headerData

def loadSats(files: list[tuple[Constelation, str]]):
    """Load satellites using multiple constelation and file path combinations
    Return a map of satellites and the setup header for the encoding setup
    """
    sats = {}
    constSats = {}
    consts : list[Constelation] = []
    for file in files:
        newSats, _ = file[0].loadSatsFromRinax(file[1])
        for sat in newSats:
            if sat in sats:
                sats[sat].add(newSats[sat])
            else:
                sats[sat] = newSats[sat]
            if file[0].prefix not in constSats:
                constSats[file[0].prefix] = {}
                consts.append(file[0])
            constSats[file[0].prefix][sat] = sats[sat]

    setup = "setup"
    for const in consts:
        setup = setup+" "+const.getSetupHeader(constSats[file[0].prefix])

    return sats, setup
