import itertools
import re
from pprint import pprint

def split(y):
    expr = r"((-?\d*)(\.\d*([EeDd][+-]?\d*)?)?|[^\s]*)"
    return [m[0] for m in re.findall(expr, y) if m[0]!=""]

def parse_float(x):
    return float(x.replace("D", "E"))

def matchHeader(line, header, headerData):
    # check if header matches
    if len(line)==len(header):
        for i in range(len(header)):
            if isinstance(header[i], str):
                if header[i]!=line[i]:
                    return
    else:
        return
    
    #header matches, store results
    for i in range(len(header)):
        if isinstance(header[i], list):
            headerData[header[i][0]] = header[i][1](line[i])

def parseRINEX(fileName, dataDescription, headerDescription, constelationPrefix="R"):
    file = open(fileName, 'r')
    lines = file.readlines()
    
    headerData = {}
    
    header = itertools.takewhile(lambda line: line.strip().upper()!="END OF HEADER", lines)
    for line in header:
        fields = split(line.strip())

        # for galileo
        #if fields[0].upper() == "GAL":
        #    headerData["a_i0"] = float(fields[1])
        #    headerData["a_i1"] = float(fields[2])
        #    headerData["a_i2"] = float(fields[3])
        #if fields[0].upper() == "GAUT": # GAL-UTC(a0, a1)
        #    headerData["a0"]   = float(fields[1])
        #    headerData["a1"]   = float(fields[2])
        #    headerData["TOW"]  = int(  fields[3])
        #    headerData["WN"]   = int(  fields[4])
        
        # for glonass
        #if fields[0].upper() == "GLUT": # TIME SYSTEM CORR
        #    headerData["h1"] = float(fields[1])
        #    headerData["h2"] = float(fields[2])
        #    headerData["h3"] = int(  fields[3])
        #    headerData["h4"] = int(  fields[4])

        # for GPS / Rinex V2
        if fields[-1].upper() == "ALPHA" and fields[-2].upper() == "ION":
            headerData["alpha1"] = parse_float(fields[0])
            headerData["alpha2"] = parse_float(fields[1])
            headerData["alpha3"] = parse_float(fields[2])
            headerData["alpha4"] = parse_float(fields[3])
            #print("ION Alpha")
        if fields[-1].upper() == "BETA" and fields[-2].upper() == "ION":
            headerData["beta1"] = parse_float(fields[0])
            headerData["beta2"] = parse_float(fields[1])
            headerData["beta3"] = parse_float(fields[2])
            headerData["beta4"] = parse_float(fields[3])
            #print("ION Beta")
        if fields[-1].upper() == "A0,A1,T,W" and fields[-2].upper() == "DELTA-UTC:":
            headerData["A0"] = parse_float(fields[0])
            headerData["A1"] = parse_float(fields[1])
            headerData["T"] = parse_float(fields[2])
            headerData["W"] = parse_float(fields[3])
            #print("Delta UTC")

        # for beidou
        #if fields[0].upper() == "BDSA":
        #    headerData["alpha1"] = parse_float(fields[1])
        #    headerData["alpha2"] = parse_float(fields[2])
        #    headerData["alpha3"] = parse_float(fields[3])
        #    headerData["alpha4"] = parse_float(fields[4])
        #if fields[0].upper() == "BDSB":
        #    headerData["beta1"] = parse_float(fields[1])
        #    headerData["beta2"] = parse_float(fields[2])
        #    headerData["beta3"] = parse_float(fields[3])
        #    headerData["beta4"] = parse_float(fields[4])
        #if fields[0].upper() == "BDUT": # GAL-UTC(a0, a1)
        #    headerData["a0"]   = float(fields[1])
        #    headerData["a1"]   = float(fields[2])
        #    headerData["TOW"]  = int(  fields[3])
        #    headerData["WN"]   = int(  fields[4])

        # for irnss
        #if fields[0].upper() == "IRNA":
        #    headerData["alpha1"] = parse_float(fields[1])
        #    headerData["alpha2"] = parse_float(fields[2])
        #    headerData["alpha3"] = parse_float(fields[3])
        #    headerData["alpha4"] = parse_float(fields[4])
        #if fields[0].upper() == "IRNB":
        #    headerData["beta1"] = parse_float(fields[1])
        #    headerData["beta2"] = parse_float(fields[2])
        #    headerData["beta3"] = parse_float(fields[3])
        #    headerData["beta4"] = parse_float(fields[4])
        #if fields[0].upper() == "IRUT": # GAL-UTC(a0, a1)
        #    headerData["a0"]   = parse_float(fields[1])
        #    headerData["a1"]   = parse_float(fields[2])
        #    headerData["TOW"]  = int(  fields[3])
        #    headerData["WN"]   = int(  fields[4])


        # all
        if fields[-1].upper() == "SECONDS" and fields[-2].upper() == "LEAP":
            headerData["t_LS"] = int(fields[0])
            #print("Leap Seconds")
        
        for header in (headerDescription+[[["t_LS", int], ["dt_LS", int], ["WN_LSF", int], ["DN", int], "LEAP", "SECONDS"]]):
            matchHeader(fields, header, headerData)
    
    lines = itertools.dropwhile(lambda line: line.strip().upper()!="END OF HEADER", lines)
    lines = itertools.islice(lines, 1, None)

    def batch(lines):
        next = []
        for line in lines:
            if line[0] not in [" ", "\t"] and len(next)>0:
                yield next
                next = []
            next.append(line)
        yield next

    #batchedLines = itertools.batched(lines, 8) #CHECK: is 8 standered?
    batchedLines = batch(lines)
    #batchedLines = map(lambda x: list(map(lambda y: y.strip().split(), list(x))), batchedLines)
    expr = r"((-?\d*)(\.\d*([EeDd][+-]?\d*)?)?|[^\s]*)"
    batchedLines = map(lambda x: list(map(lambda y: [m[0] for m in re.findall(expr, y) if m[0]!=""], list(x))), batchedLines)
    
    satsList = []
    satsMap = {}

    for entry in list(batchedLines):
        valid = False
        sat = {}
        if entry[0][0].strip().isnumeric():
            valid = True
            entry[0][0] = constelationPrefix+(entry[0][0].strip().zfill(2))
        if entry[0][0][0]==constelationPrefix:
            valid = True
            for row in range(len(dataDescription)):
                rowDataDescription = dataDescription[row]
                if len(entry[row])-1 == len(dataDescription[row]) and len(entry[row][0])==1 and entry[row][1].strip().isnumeric():
                    entry[row] = [entry[row][0]+"0"+entry[row][1]]+entry[row][2:]
                if len(entry[row]) < len(rowDataDescription):
                    rowDataDescription = [x for x in rowDataDescription if not isinstance(x, str) or (x.find("spare")==-1 and x.find("blank")==-1)]
                    if len(entry[row]) < len(rowDataDescription):
                        rowDataDescription2 = [x for x in rowDataDescription if not isinstance(x, str) or x.find("BNK")==-1] # Blank Not Known -> need to find previus value
                        assert len(entry[row]) == len(rowDataDescription2), "Data desciption and rinex data don't match even after removing spares"
                        for i in range(len(rowDataDescription)-len(entry[row])):
                            #entry[row].append("0")
                            if entry[0][0] in satsMap.keys():
                                oldv = satsMap[entry[0][0]][row][len(entry[row])+i]
                                entry[row].append(oldv)
                                print("BNK: Blank Not Known found setting to previusly read value: "+str(oldv))
                            elif len(satsMap.keys()) > 0:
                                oldv = satsMap[list(satsMap.keys())[0]][row][len(entry[row])+i]
                                entry[row].append(oldv)
                                print("BNK: Blank Not Known found, and no previus value for this satalite, using value from "+list(satsMap.keys())[0]+": "+oldv)
                            else:
                                print("BNK: Blank Not Known found, no previus values, setting to 0")
                                entry[row].append("0")
                else:
                    assert len(entry[row]) == len(rowDataDescription), "Data desciption and rinex data don't match"
                for column in range(len(rowDataDescription)):
                    if isinstance(rowDataDescription[column], list):
                        f = rowDataDescription[column][1]
                        sat[rowDataDescription[column][0]] = f(entry[row][column])
                    else:
                        sat[rowDataDescription[column]] = float(entry[row][column].replace("D", "E"))
        if valid:
            satsList.append(sat)
            satsMap[entry[0][0]] = entry
    
    return satsList, headerData

def float_int(x):
    return int(float(x))

    

#["record_id", "year", "month", "day", "hour", "min", "sec", "Epoch flag", "num sat in epoch", "(reserved)", "reciver clock offset"],
#        ["m", ],
#        [],
#        []



def main():
    print("RINEX")
    #pprint(firstSats)

if __name__ == "__main__":
    main()