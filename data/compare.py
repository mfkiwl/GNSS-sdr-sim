import matplotlib.pyplot as plt
import os

file_name_a = "data/OutputIQ_c.sigmf-data"
file_name_b = "data/OutputIQ_vhdl.sigmf-data"

def to_signed(v):
    if v>127 :
        v-=256
    return v

I_a = []
Q_a = []

I_b = []
Q_b = []

with open(file_name_a, "rb") as fa, open(file_name_b, "rb") as fb:
    while ((bytes_a := fa.read(2)) and (bytes_b := fb.read(2))):
        I_a.append(to_signed(bytes_a[0])*61/28)
        Q_a.append(to_signed(bytes_a[1])*61/28)
        I_b.append(to_signed(bytes_b[0]))
        Q_b.append(to_signed(bytes_b[1]))

n = len(I_a)

i = 0
delta = 10
while  i<n and abs(I_a[i]-I_b[i])<=delta and abs(Q_a[i]-Q_b[i])<=delta:
    i+=1
print("diffrence after:", i)
print("out of:         ", n)

if i!=n:
    Q_z = list(zip(list(zip(I_a, Q_a)), list(zip(I_b, Q_b))))
    print(Q_z[i], Q_z[i-5 if i > 5 else 0:i+20])