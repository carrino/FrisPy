import math
from pprint import pprint

import matplotlib.pyplot as plt
from scipy.optimize import minimize

from frispy import Disc
from frispy import Discs

model = Discs.beefy_destroyer
mph_to_mps = 0.44704
v = 70 * mph_to_mps # what is the optimal flight for 70mph
rot = -v / model.diameter

def distance(x):
    a, nose_up, hyzer = x
    d = Disc(model, {"vx": math.cos(a * math.pi / 180) * v, "dgamma": rot, "vz": math.sin(a * math.pi / 180) * v,
                     "nose_up": nose_up, "hyzer": hyzer})
    r = d.compute_trajectory(20.0, **{"max_step": .2})
    rx = r.x[-1]
    return -rx

x0 = [4, -4, 0]
res = minimize(distance, x0, method='powell', options={'xtol': 1e-8, 'disp': True})
pprint(res)
a, nose_up, hyzer = res.x
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

plt.show()
