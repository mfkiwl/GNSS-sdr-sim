import settings
import matplotlib.pyplot as plt
import itertools

i = 0

#i_max = list(itertools.islice(map(max, itertools.batched(map( lambda x: x[0], settings.openIQ()), n=10000)), 1000))
#q_max = list(itertools.islice(map(max, itertools.batched(map( lambda x: x[1], settings.openIQ()), n=10000)), 1000))
iq_max = map( #itertools.islice(
    #map(
        lambda x: map(max, x), 
        map(
            lambda x: list(zip(*x)), 
            itertools.batched(settings.openIQ(), n=10000)
        )
    )
    #, 1000)

R = 1#50 # ohm
energy = list(map(lambda iq: (next(iq)/255)**2+(next(iq)/255)**2 / (2*R), iq_max))

#z_iq_max = list(zip(*iq_max))
#i_max = z_iq_max[0]
#q_max = z_iq_max[1]

plt.plot(energy)
plt.show()

energy = []
for iq in settings.openIQ():
    R = 1#50 # ohm
    e = (iq[0]/255)**2+(iq[1]/255)**2 / (2*R)
    energy.append(e)
    i+=1
    if i==10000:
        break

plt.plot(energy)
plt.show()