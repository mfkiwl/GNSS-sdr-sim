import datetime
import Constelation
import NavMessage
from typing import Self

class TimedEfemris:
    """ Store list of ephemeris
    Allows for easy indexing by time
    """
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
    
    def add(self, other: Self):
        self.ephs = self.ephs+other.ephs
        self.ephs = sorted(self.ephs, key=lambda obj: obj["datetime"])

    def getEarliest(self):
        return self.ephs[0]
    
    def getLatest(self):
        return self.ephs[-1]

class Satallite:
    """ Store data for a satellite: ephemeris, constelation, and name
    """
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

    def add(self, other: Self):
        """ Add ephemeris entries from another satellite object
        """
        if self.name!=other.name:
            print("merge rejected diffrent satalite")
        else:
            self.eph.add(other.eph)

def getGoodRange(sats: dict[str, Satallite]):
    """Check for what time range ephemeris data is available
    """
    earliest = []
    latest = []
    for name in sats:
        sat: Satallite = sats[name]
        earliest.append(sat.eph.getEarliest()["datetime"])
        latest.append(sat.eph.getLatest()["datetime"])
    earliest.sort()
    latest.sort()
    return (earliest[0], earliest[-1], latest[0], latest[-1])