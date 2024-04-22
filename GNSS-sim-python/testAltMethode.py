import math

# delays
u = 60
v = 60.1
w = 60.25

# steps
k=10

# delay at time t from the timeframe of the satalite
def getDelayFor(t):
    a = (u+w-2*v)/(2*k**2)
    b = (w-u)/(2*k)
    c = v

    x=t*10*k

    y=a*x*x+b*x+c

    return y

def getDelayAt(t):
    a = (u+w-2*v)/(2*k**2)
    b = (w-u)/(2*k)
    c = v

    x = (-b+math.sqrt(b**2-4*a*(c-t)))/(2*a)

    return x/10/k

print(getDelayFor(0.1))
print(getDelayAt(60.25))

#offsetAt(60.1) -> 0
# solve for y=0 (y=t)
