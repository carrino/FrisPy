#  Copyright (c) 2021 John Carrino

import math
from pprint import pprint

import matplotlib.pyplot as plt
from scipy.optimize import minimize

from frispy import Disc
from frispy import Discs

model = Discs.destroyer
mph_to_mps = 0.44704
v = 70 * mph_to_mps
rot = -v / model.diameter * 1.2

def distance(x):
    a, nose_up, hyzer = x
    d = Disc(model, {"vx": math.cos(a * math.pi / 180) * v, "dgamma": rot, "vz": math.sin(a * math.pi / 180) * v,
                     "nose_up": nose_up, "hyzer": hyzer})
    r = d.compute_trajectory(20.0, **{"max_step": .2})
    rx = r.x[-1]
    return -rx

x0 = [6, -3, 25]
a, nose_up, hyzer = x0
disc = Disc(model, {"vx": math.cos(a * math.pi / 180) * v, "dgamma": rot, "vz": math.sin(a * math.pi / 180) * v,
                 "nose_up": nose_up, "hyzer": hyzer})

result = disc.compute_trajectory(20.0, **{"max_step": .2})
times = result.times
t, x, y, z = result.times, result.x, result.y, result.z

plt.plot(x, y)
plt.plot(x, z)

#plt.plot(t, x)
#plt.plot(t, y)
#plt.plot(t, z)

pprint(x[-1] * 3.28084) # feet
pprint(Discs.destroyer.get_value("PD0"))

plt.show()
