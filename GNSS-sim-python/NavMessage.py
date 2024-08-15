import itertools


class BitBuffer:
    """Data structure and functions to communicate between the generation of the navigation message and the 0.1 second frames that are send for encoding
    """

    buffer = []
    store = {}

    fillBuffer = lambda self, t, sat, sats : [0, 1]

    debugBuffer = []

    def __init__(self):
        self.buffer = []

    def getBits(self, n, datetime, sat, sats):
        if not isinstance(n, int):
            n = n(sat)
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
    """Convert a number to a array of bits.
    'bits' indicates how many bits to use to encode 'val'.
    """
    if val is None:
        return [0]*bits
    val = int(round(val))
    res = [0]*bits
    for i in range(bits):
        res[bits-i-1] = 1 if val&1<<i==1<<i else 0
    return res

def dataStructureToBits(structure, data, twosCompliment=False, spareData = {}):
    """Use the given 'structure' to create a bit array.
    To fill the structure values are first taken from 'data'.
    If a value is not present in data look in 'spareData'.
    'twosCompliment' indicates how to encode data
    """
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
    """Convert array of bits to a string
    """
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

# modified from CRC Wikipedia
def crc_remainder(input_bitstring, polynomial_bitstring, initial_filler):
    """Calculate the CRC remainder of a string of bits using a chosen polynomial.
    initial_filler should be '1' or '0'.
    """
    polynomial_bitstring = list(itertools.dropwhile(lambda x : x == 0, polynomial_bitstring))
    len_input = len(input_bitstring)
    initial_padding = [initial_filler]*(len(polynomial_bitstring) - 1)
    input_padded_array = list(input_bitstring + initial_padding)
    while 1 in input_padded_array[:len_input]:
        cur_shift = input_padded_array.index(1)
        for i in range(len(polynomial_bitstring)):
            input_padded_array[cur_shift + i] \
            = int(int(polynomial_bitstring[i] != input_padded_array[cur_shift + i]))
    return input_padded_array[len_input:]

def interleave(data, c=8, r=30):
    """Interleave a array
    """
    assert len(data)==c*r
    datai = [0]*len(data)
    for i in range(c):
        for j in range(r):
            datai[i*r+j] = data[j*c+i]
    return datai



def main():
    print("NavMessage")

if __name__ == "__main__":
    main()
