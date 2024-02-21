import serial
import serial.tools.list_ports

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

def parseFile(file):
    yield "setup"
    for line in [file, "data", "test"]:
        yield line

def main():

    source = parseFile("file")
    print("setup:", next(source))
    for line in source:
        print("line:", line)

    exit("message")
    port = selectSerialPort()

    with serial.Serial(port) as ser:
        while True:
            iq = ser.read(2)
            i = int.from_bytes(iq[0:1], signed=True)
            q = int.from_bytes(iq[1:2], signed=True)
            print(i, q)

if __name__ == "__main__":
    main()