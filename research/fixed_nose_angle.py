import math
from pprint import pprint

import matplotlib.pyplot as plt
from scipy.optimize import minimize

from frispy import Disc
from frispy import Model
from frispy import Discs

model = Discs.wraith
v = 20
rot = v / -.211
hz = rot / (2 * math.pi)
nose_up = 15

def distance(x):
    a, hyzer = x
    d = Disc(model, {"vx": math.cos(a * math.pi / 180) * v, "dgamma": rot, "vz": math.sin(a * math.pi / 180) * v, "nose_up": nose_up, "hyzer": hyzer})
    r = d.compute_trajectory(10.0, None, **{"max_step": .1})
    rx = r.x[-1]
    ry = r.y[-1]
    return -rx + ry / (rx + ry)

x0 = [10, 0]
res = minimize(distance, x0, method='powell', options={'xtol': 1e-8, 'disp': True})
pprint(res)
disc = Disc(model, {"vx": math.cos(res.x[0] * math.pi / 180) * v, "dgamma": rot, "vz": math.sin(res.x[0] * math.pi / 180) * v, "nose_up": nose_up, "hyzer": res.x[1]})

#result = disc.compute_trajectory(8.0, None, **{"max_step": .1, "rtol": 1e-6, "atol": 1e-9})
result = disc.compute_trajectory(8.0, None, **{"max_step": .1})
#result = disc.compute_trajectory(8)
times = result.times
t, x, y, z = result.times, result.x, result.y, result.z

plt.plot(x, y)
plt.plot(x, z)

plt.show()
