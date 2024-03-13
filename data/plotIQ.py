import matplotlib.pyplot as plt
import os

file_name = "data/OutputIQ_c.sigmf-data"

file_stats = os.stat(file_name)
IQ_samples = file_stats.st_size/2
print("samples", IQ_samples)

I = []
Q = []

n = 0

with open(file_name, "rb") as f:
    while (bytes := f.read(2)):
        i = int(bytes[0])
        if i>127 :
            i-=256
        q = int(bytes[1])
        if q>127 :
            q-=256
        I.append(i)
        Q.append(q)
        n += 1
        if n== 200000:
            break
        #print(i, q)
        #exit()

plt.plot(I, label="I")
plt.plot(Q, label="Q")
plt.legend()
plt.show()
