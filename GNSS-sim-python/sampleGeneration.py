import NavMessage
import matplotlib.pyplot as plt

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

def callOrReturn(x, a):
    if callable(x):
        return x(a)
    else:
        return x

def generateDataSample(sats, data, bitsPerFrame, delay, doppler, power, plot=True):
    n = lenOr1(sats)
    sats    = ensureList(sats, n)
    data    = ensureList(data, n)
    bitsPerFrame = ensureList(bitsPerFrame, n)
    delay   = ensureList(delay, n)
    doppler = ensureList(doppler, n)
    power   = ensureList(power, n)

    frames = []

    points = [[] for i in range(n)]

    k = int(len(data[0])/bitsPerFrame[0])
    for t in range(k):
        frameData = []
        for j in range(n):
            i = t*bitsPerFrame[j]
            frame = data[j][i:i+bitsPerFrame[j]]
            delay_val = callOrReturn(delay[j], t)
            doppler_val = callOrReturn(doppler[j], t)
            power_val = callOrReturn(power[j], t)
            frameData.append("{}:{}_{:.9f}_{:.4f}_{}".format(sats[j], NavMessage.bitsToHex(frame), delay_val, doppler_val, power_val))
            points[j].append((delay_val, doppler_val, power_val, t))
        frames.append("data "+",".join(frameData))

    if plot:
        for data in points:
            ranges = list(zip(*data))
            plt.scatter(list(map(lambda x: x%1, ranges[0])), ranges[1], list(map(lambda x: x**2/50, ranges[2])), c=list(map(lambda x: x/k, ranges[3])))
        plt.show()

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

    sats = ["G04", "G1004"] # 
    setup = "G:("+",".join(map(lambda name: name[1:]+"[]", sats))+")"

    D1_subframe = (stringToBits("10001011")+[1,0,1,0]*((300-8)//4))
    D2_subframe = (stringToBits("10001011")+[1,1,0,0]*((300-8)//4))

    frameData = generateDataSample(sats, [D1_subframe*8, D1_subframe*8], [5, 5], 
                                   [lambda x: 60.5, lambda x : 60.5 if x<201 else 60.5+(x-201)/20000],
                                   #[lambda x: 60.512-x/20000, lambda x: 60.5+x/20000], 
                                   [lambda x: 20 if x<200 else 20-(x-200)/10, lambda x: 20 if x<200 else 20+(x-200)/10], 
                                   [lambda x: 60, lambda x: min(100, 0+x)])
    
    #frameData = generateDataSample([sats[0]], [D1_subframe*8], [5], 
    #                               [lambda x: 60.5], 
    #                               [lambda x: 20 if x<200 else 20-(x-200)/10], 
    #                               [lambda x: 60])
    
    #frameData = generateDataSample([sats[1]], [D2_subframe*8], [5], 
    #                               [lambda x : 60.5 if x<201 else 60.5+(x-201)/20000],
    #                               [lambda x: 20 if x<200 else 20+(x-200)/10], 
    #                               [lambda x: min(100, 0+x)])

    #frameData = generateDataSample(sats, [D1_subframe*7], [5], [60], [50], [100])
    
    store("data/gps.txt", setup, frameData)


    #sats = ["B10", "B01"] # smaller than B06 -> geostationary, no secondary code/[1,1]
    #setup = "B:("+",".join(map(lambda name: name[-2:]+"[]", sats))+")"

    #D1_subframe = (stringToBits("11100010010")+([1,0])*144+[1])
    #D2_subframe = (stringToBits("11100010010")+([1,0])*144+[1])

    #frameData = generateDataSample(sats, [D1_subframe*7, D2_subframe*70], [5, 50], 0, 0, 100)
    
    #store("data/beidou.txt", setup, frameData)



    #sats = ["I01"]
    #setup = "I:("+",".join(map(lambda name: name[-2:]+"[]", sats))+")"

    #subframe = stringToBits("1110101110010000")+([0,1]*int((600-16)/2))

    #frameData = generateDataSample(sats, [subframe*7], 5, 0, 0, 100)

    #store("data/irnss.txt", setup, frameData)

if __name__ == "__main__":
    main()