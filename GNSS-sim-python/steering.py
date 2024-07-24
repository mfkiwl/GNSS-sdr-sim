import keyboard
import numpy as np
import math

import orbit
import const

def normalize(v):
    norm = np.linalg.norm(v)
    if norm == 0: 
       return v
    return v / norm

class Steering:
    def __init__(self, pos):
        self.pos = pos

    def __call__(self, time):
        move = np.array([[0],[0],[0]])

        (lat, lon, alt) = orbit.wgsxyz2lla(self.pos)

        if keyboard.is_pressed("left arrow"):
            #print("l")
            move = move+normalize(self.pos - orbit.wgslla2xyz(lat+0.00001, lon, alt))
        if keyboard.is_pressed("right arrow"):
            #print("r")
            move = move+normalize(self.pos - orbit.wgslla2xyz(lat-0.00001, lon, alt))
        
        if keyboard.is_pressed("up arrow"):
            #print("u")
            move = move+normalize(self.pos - orbit.wgslla2xyz(lat, lon+0.00001, alt))
        if keyboard.is_pressed("down arrow"):
            #print("d")
            move = move+normalize(self.pos - orbit.wgslla2xyz(lat, lon-0.00001, alt))

        
        if keyboard.is_pressed("left shift"):
            #print("s")
            move = move+normalize(self.pos - orbit.wgslla2xyz(lat, lon, alt+1))
        if keyboard.is_pressed("left ctrl"):
            #print("c")
            move = move+normalize(self.pos - orbit.wgslla2xyz(lat, lon, alt-1))

        dt = 0.1

        self.pos = self.pos+move*dt
        return (self.pos, move)
    
def xyz2lla(pos):
    return (0,0,0)

if __name__ == "__main__":
    posvelfunc = Steering(orbit.wgslla2xyz(28.685194, 77.205865, 240))
    while not keyboard.is_pressed("q"):
        (pos, vel) = posvelfunc(None)
        print("[{:11.1f} {:11.1f} {:11.1f}], [{:2.2f} {:2.2f} {:2.2f}])".format(pos[0][0], pos[1][0], pos[2][0], vel[0][0], vel[1][0], vel[2][0]), end="\r")
        