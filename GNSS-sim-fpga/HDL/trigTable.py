import math
import matplotlib.pyplot as plt
import numpy as np

n = 256

sinTable = [0]*n
cosTable = [0]*n

for i in range(n):
  sinTable[i] = int(math.sin(i *(2*math.pi / 4 / n))*255)
  cosTable[i] = int(math.cos(i *(2*math.pi / 4 / n))*255)

def tableSin(x):
    x = int(x/(2*math.pi)*4*n)
    while x<0:
        x += 4*n
    while x>=4*n:
        x -= 4*n
    if x >= 0 and x < n:
        return sinTable[x]/255
    elif x>=n and x<2*n:
        return sinTable[n-(x-n)-1]/255
    elif x>=2*n and x<3*n:
        return -sinTable[x-2*n]/255
    elif x>=3*n and x<4*n:
        return -sinTable[n-(x-3*n)-1]/255

for i in range(16):
    for j in range(16):
        print("X\""+hex(sinTable[16*i+j])[2:].zfill(2)+"\"", end=", ")
    print()

xs = np.linspace(-2*math.pi, 4*math.pi, 10000)
plt.plot([tableSin(x)/100 for x in xs], label="table")
plt.plot([math.sin(x)/100 for x in xs], label="math")
plt.plot([math.cos(x)/100 for x in xs], label="cos")
plt.plot([math.sin(x)-tableSin(x) for x in xs], label="error")
plt.legend();
plt.show()