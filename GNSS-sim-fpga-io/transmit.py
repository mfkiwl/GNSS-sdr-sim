import serial
import serial.tools.list_ports
import string
import struct
from datetime import datetime

radioFrequencyOut = 1602000000
outputRate = 15000000
modulationRate = 511000
subCycles = 100

chanel_assignemnt = {"R01":0, "R07":1, "R09":2, "R11":3, "R17":4, "R23":5, "R24":6, "R10":7, "R02":8}
#chanel_assignemnt = {"R01":0}

class Sat:
    ccode : str = ""
    id : str = ""
    arg : str =""
    radioFrequency : int = 0
    chanel : int = -1
    prn : int = 255

    def __init__(self, ccode: str, id: str, arg:str):
        self.ccode = ccode
        self.id = id
        self.arg = arg
        
        self.chanel = -1
        if ccode+id in chanel_assignemnt:
            self.chanel = chanel_assignemnt[ccode+id]
            self.prn = int(id)
            
        if ccode=="R":
            self.radioFrequency = 1602000000 + 562500 * int(arg)

def selectSerialPort():
    ports = serial.tools.list_ports.comports()

    if len(ports)==0:
        exit("No serial ports found!")

    if len(ports)==1:
        print("Only one serial port found, using it:", ports[0][0])
        return ports[0][0]

    print("Please select a serial port")
    ports.sort()
    for i in range(len(ports)):
        (port, desc, hwid) = ports[i]
        print("({}) {}: {} [{}]".format(i+1, port, desc, hwid))
    portId = int(input("(x): "))
    return ports[portId-1][0]

def parseFile(filePath):
    with open(filePath) as file:
        setup = {}
        line = next(file, None) # next -> getline
        while line != None:
            line = line.split()
            if line[0]=="setup":
                for cline in line[1:]:
                    (ccode, sats) = cline.split(":")
                    sats = sats[1:-1]
                    setup[ccode] = {}
                    for sat in sats.split(","):
                        o = sat.find("[")
                        id = sat[0:o]
                        arg = sat[o+1:-1]
                        setup[ccode+id]=Sat(ccode, id, arg)
                break
            line = next(file, None) # next -> getline
        yield setup

        line = next(file, None) # next -> getline
        while line != None:
            line = line.split()
            data = {}
            if line[0]=="data":
                for sat in line[1].split(","):
                    (name, info) = sat.split(":")
                    ccode = name.rstrip(string.digits)
                    id = name[len(ccode):]
                    vals = info.split("_")
                    data[name] = {"data": vals[0], "delay":float(vals[1]), "shift":float(vals[2]), "power":int(vals[3])}
            yield data
            line = next(file, None) # next -> getline

def to_DataFrame_bytes(id, data, setup):

    delay_samples = data["delay"] / 1000 * outputRate
    delay_n = (subCycles * modulationRate) * delay_samples

    PHASE_POWER = 30
    PHASE_RANGE = 2**PHASE_POWER

    scale = 100
    targetFrequency = setup.radioFrequency*scale + data["shift"]*scale
    shift = targetFrequency - radioFrequencyOut * scale
    normalPhaseSampleDelta = shift / outputRate
    unitStepPhase = normalPhaseSampleDelta / scale * (PHASE_RANGE)

    message = bytes()
    message += struct.pack(">B", setup.chanel%256) # -1 is for testing, find better way to address
    message += bytes.fromhex(data["data"].zfill(16))
    message += struct.pack(">q", int(delay_n))
    #print("delay n:", int(delay_n))
    #message += struct.pack(">q", 0)
    message += struct.pack(">l", int(unitStepPhase))
    #print("phase step:", int(unitStepPhase))
    #message += struct.pack(">l", 0)
    message += struct.pack(">B", int(data["power"]))


    print(message, message.hex())
    return message

def to_DataFrame_bytes_raw(id, data, setup, chanel_info):

    delay_samples = data["delay"] / 1000 * outputRate
    delay_n = (subCycles * modulationRate) * delay_samples

    PHASE_POWER = 30
    PHASE_RANGE = 2**PHASE_POWER

    scale = 100
    targetFrequency = setup.radioFrequency*scale + data["shift"]*scale
    shift = targetFrequency - radioFrequencyOut * scale
    normalPhaseSampleDelta = shift / outputRate
    unitStepPhase = normalPhaseSampleDelta / scale * (PHASE_RANGE)


    added_delay = delay_n-chanel_info["last_delay"]
    itterNStep = subCycles * modulationRate # inputRate
    bufferNStep = subCycles * outputRate
    delayNStep = int(added_delay*itterNStep/(bufferNStep*modulationRate+added_delay)) # f(delay_n)
    chanel_info["last_delay"] = delay_n # todo: account for rounding errors
    
    #unitStepPhase = 100000
    power = 255//len(chanel_assignemnt) # data["power"]

    message = bytes()
    message += struct.pack(">B", setup.chanel%256) # -1 is for testing, find better way to address
    message += struct.pack(">B", setup.prn)
    message += bytes.fromhex(data["data"].zfill(16))
    message += struct.pack(">q", int(delayNStep))[1:8]
    #print("delay n:", int(delay_n))
    #message += struct.pack(">q", 0)
    message += struct.pack(">l", int(unitStepPhase))
    #print("phase step:", int(unitStepPhase))
    #message += struct.pack(">l", 0)
    message += struct.pack(">B", int(power))


    print(message, message.hex())
    return message

def uploadFrame(ser, data):
    ser.write(b'\xaa\xaa')
    ser.write(data)

def main():

    source = parseFile("data/glonass.txt")
    setup = next(source)
    print("setup:", setup)
    n = 0
    #for step in source:
    #    #print("line:", line)
    #    for ccode in step:
    #        for sat in step[ccode]:
    #            print(to_DataFrame_bytes(sat, step[ccode][sat]))
    #            break
    #        break
    #    break
    #    n+=1
    #print("n:", n)

    #exit("message")

    chanel_info={}
    frames = []
    # load initalization frames
    for i in range(2):
        step = next(source)
        for sat in step:
            #if setup[sat].chanel >= chanel_count or setup[sat].chanel<0:
            #    continue
            if setup[sat].chanel not in chanel_info:
                chanel_info[setup[sat].chanel] = {"last_delay":0}

            frames.append(to_DataFrame_bytes_raw(sat, step[sat], setup[sat], chanel_info[setup[sat].chanel]))

    port = selectSerialPort()
    with serial.Serial(port) as ser, open("data/OutputIQ.sigmf-data", "wb") as binFile:
        frames_to_skip = 2
        frames_saved = 0

        for step in source:
            for sat in step:
                #if setup[sat].chanel >= chanel_count or setup[sat].chanel<0:
                #    continue
                frames.append(to_DataFrame_bytes_raw(sat, step[sat], setup[sat], chanel_info[setup[sat].chanel]))
            
            k=0
            while k<outputRate/10:
                
                
                #if k>200:
                #    exit()


                if(outputRate/10-k >= 16):
                    k+=16
                    if frames:
                        uploadFrame(ser, frames.pop(0))
                        print(datetime.now(), "upload")
                    iqs = ser.read(32)
                    #for i in range(16):
                    #    print(ser.readline().decode('utf-8'), end="")
                    #for l in range(16):
                    #    i = int.from_bytes(iqs[0+2*l:1+2*l], signed=True)
                    #    q = int.from_bytes(iqs[1+2*l:2+2*l], signed=True)
                    #    print(i, q)
                    if frames_to_skip<=0:
                        binFile.write(iqs)
                else:
                    k+=1
                    iq = ser.read(2)
                    #print(ser.readline().decode('utf-8'), end="")
                    #i = int.from_bytes(iq[0:1], signed=True)
                    #q = int.from_bytes(iq[1:2], signed=True)
                    #print(i, q)
                    if frames_to_skip<=0:
                        binFile.write(iq)
                    
                #if ser.in_waiting > 10:
                #    print(ser.readline().decode('utf-8'), end="")

                if(k%int(outputRate/10/100)<16):
                    print(int(k/int(outputRate/10/100)), "% (of 0.1s) ("+str(frames_saved*0.1)+" s)", end="\r")
            
            if frames_to_skip>1 :
                frames_to_skip -= 1
            elif frames_to_skip==1:
                frames_to_skip -= 1
                print("start saving")
            else:
                frames_saved += 1
                

if __name__ == "__main__":
    main()