This project is still a work in progress

This GNSS simulator can be used to generate IQ files.
It supports GPS C/A, Galileo E1, GLONASS L1, IRNSS L5, and BeiDou L1i.

GPS, Galileo GLONASS and IRNSS have an accuracy between 0 and 10 meter against FGI-GSRx.
The BeiDou implementation has an error of around 5km, most likely due to a bug I have not been able to find yet.

The simulator does not have a nice interface, so running it takes a couple steps.
1. Find the RINEX file(s) only for the constelations and times you want to simulate.
2. Edit GNSS-sim-python/main.py to use the right file, and set the right time and duration.
3. Run main.py to generate the data and delay text file.
4. Edit GNSS-sim-C/GNSS-sim-C/GNSS-sim-C.cpp to use the just created file, and set the sampling rate and center frequency.
5. Run the project in Visual Studio (2019)
6. IQ file is located at data/OutputIQ.sigmf-data