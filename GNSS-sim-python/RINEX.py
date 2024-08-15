import itertools
import re
from pprint import pprint

def split(y):
    """Split a line of the a RINEX file into string values.
    Takes special care of floats that don't have spaces inbetween them.
    """
    expr = r"((-?\d*)(\.\d*([EeDd][+-]?\d*)?)?|[^\s]*)"
    return [m[0] for m in re.findall(expr, y) if m[0]!=""]

def parse_float(x):
    """Parse a string as they can occur in a RINEX file into a float 
    """
    return float(x.replace("D", "E"))

def matchHeader(line, header, headerData):
    """check if 'line' matches one of the entries in 'header'
    If it matches add the results to headerData
    """
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
    """Parse a RINEX file.
    Using the 'headerDescription' to know what to parse from the header
    Using the 'dataDescription' to parse a satellite entry if the 'constelationPrefix' matches
    If the RINEX(v2) file has no prefix for the satellite 'constelationPrefix' is added
    """
    file = open(fileName, 'r')
    lines = file.readlines()
    
    headerData = {}
    
    header = itertools.takewhile(lambda line: line.strip().upper()!="END OF HEADER", lines)
    # parse lines in header
    for line in header:
        fields = split(line.strip())

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

        # all
        if fields[-1].upper() == "SECONDS" and fields[-2].upper() == "LEAP":
            headerData["t_LS"] = int(fields[0])
            #print("Leap Seconds")
        
        for header in (headerDescription+[[["t_LS", int], ["dt_LS", int], ["WN_LSF", int], ["DN", int], "LEAP", "SECONDS"]]):
            matchHeader(fields, header, headerData)


    def batch(lines):
        """Group lines into blocks for one satellite.
        """
        next = []
        for line in lines:
            if line[0] not in [" ", "\t"] and len(next)>0:
                yield next
                next = []
            next.append(line)
        yield next

    # split satellite entries into groups of lines
    lines = itertools.dropwhile(lambda line: line.strip().upper()!="END OF HEADER", lines)
    lines = itertools.islice(lines, 1, None)
    batchedLines = batch(lines)
    expr = r"((-?\d*)(\.\d*([EeDd][+-]?\d*)?)?|[^\s]*)"
    batchedLines = map(lambda x: list(map(lambda y: [m[0] for m in re.findall(expr, y) if m[0]!=""], list(x))), batchedLines)
    
    satsList = []
    satsMap = {}

    # parse satellite entries
    for entry in list(batchedLines):
        valid = False
        sat = {}
        if entry[0][0].strip().isnumeric():
            # is a RINEX v2 entry -> add prefix so it can be parsed by v3 logic
            valid = True
            entry[0][0] = constelationPrefix+(entry[0][0].strip().zfill(2))
        if entry[0][0][0]==constelationPrefix:
            # this entry is for the satellite constelation we are parsing for
            valid = True
            for row in range(len(dataDescription)):
                rowDataDescription = dataDescription[row]
                if len(entry[row])-1 == len(dataDescription[row]) and len(entry[row][0])==1 and entry[row][1].strip().isnumeric():
                    entry[row] = [entry[row][0]+"0"+entry[row][1]]+entry[row][2:] #add zero padding to id number of only 1 digit
                if len(entry[row]) < len(rowDataDescription): # handel a miss match
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
                    # parse values according to data description
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
    """parse a string as a float and convert it to an int
    """
    return int(float(x))



def main():
    print("RINEX")
    #pprint(firstSats)

if __name__ == "__main__":
    main()