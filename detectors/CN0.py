import settings
import matplotlib.pyplot as plt

tracking_chanels = settings.openTracking()
#print(tracking_chanels)

for chanel in tracking_chanels:
    CN0 = chanel["CN0_SNV_dB_Hz"]
    if len(CN0.shape)==2:
        plt.plot(CN0[:])
        #plt.plot(chanel["PRN"][:])

plt.show()