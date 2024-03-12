#        tmp_n := n + itterNStep - delay_step; -- i am stearing on delay step, no feedback, will this work? need good external controle.
#        if tmp_n >= bufferNStep then -- tmp_n -> n?
#          n <= tmp_n - bufferNStep;
#          enable_modulation <= ENABLED;
#        else
#          n <= tmp_n;
#          enable_modulation <= DISABLED;
#        end if;

outputRate = 1023000
modulationRate = 1023000
subCycles = 100

itterNStep = subCycles * modulationRate # inputRate
bufferNStep = subCycles * outputRate

def step(n, delay_step):
    tmp_n = n + itterNStep - delay_step
    if tmp_n >= bufferNStep:
        n = tmp_n - bufferNStep
        return True, n
    else:
        n = tmp_n
        return False, n

def main():
    steps = [40976666, 231, 11, 11, 11, 12, 11, 11, 11, 11, 22, 11]
    targets = [6992977489662, 6992978616564, 6992979743676, 6992980871206, 6992981999050, 6992983127209, 6992984255681, 6992985384362, 6992986513463, 6992987642877, 6992989902647, 6992991032898]

    print("start")

    n = 0
    i = 0
    delay = 0
    k = 0
    while k < len(steps):
        do_next, n = step(n, steps[k])
        delay += steps[k]
        if do_next:
            i+=1
            if i==(modulationRate//10):
                print(delay, targets[k], delay-targets[k])
                k+=1
                i=0


if __name__ == "__main__":
    main()
