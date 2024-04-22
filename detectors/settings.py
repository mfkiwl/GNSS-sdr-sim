GNSS_SDR_dump_folder = "//wsl.localhost/Debian/home/mike/GNSS-SDR/dump_/"
IQ_file = "//wsl.localhost/Debian/home/mike/GNSS-SDR/OutputIQ.sigmf-data"

observables = "observables.mat"
tracking = ".*tracking_ch.*\\.mat"
acquisition = "acq_"

import h5py
import os
import re

def to_signed(v):
    if v>127 :
        v-=256
    return v

def openIQ(file=IQ_file):
    with open(file, "rb") as f:
        while bytes := f.read(2):
            yield (to_signed(bytes[0]), to_signed(bytes[0]))

def openMat(file):
    os.environ["HDF5_USE_FILE_LOCKING"] = "FALSE"
    f = h5py.File(file, 'r')
    return f

def openObservables():
    return openMat("GNSS_SDR_dump_folder"+observables)

def openTracking():
    chanels = []
    regex = re.compile(tracking)
    for root, dirs, files in os.walk(GNSS_SDR_dump_folder):
        for file in files:
            if regex.match(str(file)):
                #print(GNSS_SDR_dump_folder+file)
                chanels.append(openMat(GNSS_SDR_dump_folder+file))
    
    return chanels
