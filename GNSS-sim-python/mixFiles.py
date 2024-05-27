import string
import re

class Sat:
    ccode : str = ""
    id : str = ""
    arg : str =""
    prn : int = 255

    def __init__(self, ccode: str, id: str, arg:str):
        self.ccode = ccode
        self.id = id
        self.arg = arg

def addToPRN(id, v):
    parts = re.split("(\d+)$", id)
    code = parts[0]
    prn = int(parts[1])+v
    return code+(str(prn).zfill(2))

def parseFile(filePath, PRN_shift = 0, power_factor = lambda x: 1):
    with open(filePath) as file:
        setup = {}
        line = next(file, None) # next -> getline
        while line != None:
            line = line.split()
            if line[0]=="setup":
                for cline in line[1:]:
                    (ccode, sats) = cline.split(":")
                    sats = sats[1:-1]
                    for sat in sats.split(","):
                        o = sat.find("[")
                        id = str(int( sat[0:o] )+PRN_shift).zfill(2)
                        arg = sat[o+1:-1]
                        setup[ccode+id]=Sat(ccode, id, arg)
                break
            line = next(file, None) # next -> getline
        yield setup

        line = next(file, None) # next -> getline
        i=0
        while line != None:
            line = line.split()
            data = {}
            if line[0]=="data":
                for sat in line[1].split(","):
                    (name, info) = sat.split(":")
                    ccode = name.rstrip(string.digits)
                    id = str(int( name[len(ccode):] )+PRN_shift).zfill(2)
                    vals = info.split("_")
                    data[ccode+id] = {"data": vals[0], "delay":float(vals[1]), "shift":float(vals[2]), "power":int(float(vals[3])*power_factor(i))}
                i+=1
            yield data
            line = next(file, None) # next -> getline

def merge(dicts):
    res = {}
    for d in dicts:
        res.update(d)
    return res

def formatSatData(name, hex, delay, shift, power):
    return "{}:{}_{:.9f}_{:.4f}_{}".format(name, hex, delay, shift, power)

def main():
    fileA = "data/gps.txt"
    fileB = "data/gps_spoof.txt"
    fileOut = "data/mix.txt"

    streamA = parseFile(fileA, PRN_shift=0,    power_factor=lambda t:0.6)
    streamB = parseFile(fileB, PRN_shift=1000, power_factor=lambda t:max(min(1, (t-360)/30), 0))

    streams = zip(streamA, streamB)

    setup = merge(next(streams))
    print("setup:", setup)

    groups = {}
    for k in setup:
        if setup[k].ccode not in groups:
            groups[setup[k].ccode] = {}
        groups[setup[k].ccode][k] = setup[k]

    setupline = "setup "+" ".join(map(lambda c: c+":("+",".join(map(lambda s: groups[c][s].id+"["+groups[c][s].arg+"]", groups[c]))+")",groups))+"\n"

    outputFile = open(fileOut, "w")
    outputFile.write(setupline)

    for datas in streams:
        data = merge(datas)
        mixed_frame = "data "+",".join(map(lambda k: formatSatData(k, data[k]["data"], data[k]["delay"], data[k]["shift"], data[k]["power"]), data))+"\n"
        outputFile.write(mixed_frame)

    outputFile.close()

if __name__ == "__main__":
    main()
