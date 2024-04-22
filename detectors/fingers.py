import settings
import matplotlib.pyplot as plt
import numpy as np

tracking_chanels = settings.openTracking()
#print(tracking_chanels)

for chanel in tracking_chanels:
    if len(chanel["abs_P"].shape)==2:
        print(chanel.keys())
        E = np.array(chanel["abs_E"][:])
        print(E)
        P = np.array(chanel["abs_P"][:])
        L = np.array(chanel["abs_L"][:])
        E_n = E/P
        P_n = P/P
        L_n = L/P

        last_loc = 0
        loc = np.zeros(P.shape)
        for i in range(loc.shape[0]):
            loc[i][0]=last_loc
            last_loc += L_n[i][0]-E_n[i][0]

        #plt.plot(E_n)
        #plt.plot(P_n)
        #plt.plot(L_n)

        plt.plot(loc)

        #plt.plot(chanel["Prompt_I"][:])
        #plt.plot(chanel["Prompt_Q"][:])
        #plt.show()
plt.show()