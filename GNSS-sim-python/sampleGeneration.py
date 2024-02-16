import NavMessage

def ensureList(input, size):
    if isinstance(input, list):
        if len(input) >= size:
            return input
        else:
            return input + ([input[-1]]*(size-len(input)))
    else:
        return [input]*size

def lenOr1(input):
    if isinstance(input, list):
        return len(input)
    else: return 1

def generateDataSample(sats, data, bitsPerFrame, delay, doppler, power):
    n = lenOr1(sats)
    sats    = ensureList(sats, n)
    data    = ensureList(data, n)
    bitsPerFrame = ensureList(bitsPerFrame, n)
    delay   = ensureList(delay, n)
    doppler = ensureList(doppler, n)
    power   = ensureList(power, n)

    frames = []
    for t in range(int(len(data[0])/bitsPerFrame[0])):
        frameData = []
        for j in range(n):
            i = t*bitsPerFrame[j]
            frame = data[j][i:i+bitsPerFrame[j]]
            frameData.append("{}:{}_{:.9f}_{:.4f}_{}".format(sats[j], NavMessage.bitsToHex(frame), delay[j], doppler[j], power[j]))
        frames.append("data "+",".join(frameData))
    return "\n".join(frames)

def stringToBits(s):
    return list(map(int, s))

def store(resultFile, setup, frameData):
    outputFile = open(resultFile, "w")
    outputFile.write("setup "+setup+"\n")
    outputFile.write(frameData)
    outputFile.close()

def main():
    print("sample generation")

    sats = ["B10", "B01"] # smaller than B06 -> geostationary, no secondary code/[1,1]
    setup = "B:("+",".join(map(lambda name: name[-2:]+"[]", sats))+")"

    D1_subframe = (stringToBits("11100010010")+([1,0])*144+[1])
    D2_subframe = (stringToBits("11100010010")+([1,0])*144+[1])

    frameData = generateDataSample(sats, [D1_subframe*7, D2_subframe*70], [5, 50], 0, 0, 100)
    
    store("data/beidou.txt", setup, frameData)



    sats = ["I01"]
    setup = "I:("+",".join(map(lambda name: name[-2:]+"[]", sats))+")"

    subframe = stringToBits("1110101110010000")+([0,1]*int((600-16)/2))

    frameData = generateDataSample(sats, [subframe*7], 5, 0, 0, 100)

    store("data/irnss.txt", setup, frameData)

if __name__ == "__main__":
    main()