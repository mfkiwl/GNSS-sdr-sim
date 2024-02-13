import datetime
import Constelation
import NavMessage

class TimedEfemris:
    ephs = []
    lastIndex = 0

    def __init__(self, ephs):
        self.ephs = sorted(ephs, key=lambda obj: obj["datetime"])

    def get(self, datetime):
        if self.ephs[self.lastIndex]["datetime"]<=datetime and (len(self.ephs)<=self.lastIndex+1 or datetime<self.ephs[self.lastIndex+1]["datetime"]):
            return self.ephs[self.lastIndex]
        if self.ephs[0]["datetime"]>datetime:
            return self.ephs[0]
        if self.ephs[-1]["datetime"]<datetime:
            return self.ephs[-1]
        for i in range(len(self.ephs)-1):
            if self.ephs[i]["datetime"]<=datetime and datetime<self.ephs[i+1]["datetime"]:
                self.lastIndex = i
                return self.ephs[i]
    
    def getEarliest(self):
        return self.ephs[0]
    
    def getLatest(self):
        return self.ephs[-1]

class Satallite:
    name : str = ""
    constelation : Constelation.Constelation = None
    eph : TimedEfemris = None
    bitBuffer : NavMessage.BitBuffer = None

    def __init__(self, name: str, constelation: Constelation.Constelation, ephs):
        self.name = name
        self.constelation = constelation
        self.eph = TimedEfemris(ephs)
        self.bitBuffer = NavMessage.BitBuffer()
        self.bitBuffer.fillBuffer = constelation.fillBuffer

def getGoodRange(sats: dict[str, Satallite]):
    earliest = []
    latest = []
    for name in sats:
        sat: Satallite = sats[name]
        earliest.append(sat.eph.getEarliest()["datetime"])
        latest.append(sat.eph.getLatest()["datetime"])
    earliest.sort()
    latest.sort()
    return (earliest[0], earliest[-1], latest[0], latest[-1])