

class BitBuffer:

    buffer = []
    store = {}

    fillBuffer = lambda self, t, sat, sats : [0, 1]

    debugBuffer = []

    def __init__(self):
        self.buffer = []

    def getBits(self, n, datetime, sat, sats):
        if len(self.buffer) >= n:
            data = self.buffer[0:n]
            self.buffer = self.buffer[n:]
            return data
        else:
            bits = self.fillBuffer(self, datetime, sat, sats)
            self.buffer += bits
            self.debugBuffer += bits
            # how to deal with not aligned
            return self.getBits(n, datetime, sat, sats)
            




def numToBits(val, bits):
    if val is None:
        return [0]*bits
    val = int(round(val))
    res = [0]*bits
    for i in range(bits):
        res[bits-i-1] = 1 if val&1<<i==1<<i else 0
    return res

def dataStructureToBits(structure, data, twosCompliment=False, spareData = {}):
    result = []
    for entry in structure:
        if isinstance(entry, list):
            result += dataStructureToBits(entry, data, twosCompliment, spareData)
        else:
            v = None
            if isinstance(structure[0], str):
                if structure[0] in data:
                    v = data[structure[0]]
                elif structure[0] in spareData:
                    v = spareData[structure[0]]
                else:
                    raise Exception("key: '"+str(structure[0])+"' not found in data or spare data")
            else:
                v = structure[0]
            if len(structure)>=3:
                v *= structure[2]
            if((not twosCompliment) and v<0):
                tmp = [1] + numToBits(v*-1, structure[1]-1)
                return tmp
            else:
                tmp = numToBits(v, structure[1])
                return tmp
    return result

def bitsToHex(bits):
    hex = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "A", "B", "C", "D", "E", "F"]
    charbits = bits[0:4]
    v=0
    for i in range(len(charbits)):
        v+=bits[i]*1<<i
    char = hex[v]
    if(len(bits)>4):
        return bitsToHex(bits[4:])+char
    else:
        return char

def main():
    print("NavMessage")

if __name__ == "__main__":
    main()
