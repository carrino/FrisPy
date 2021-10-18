import math
from pprint import pprint

import matplotlib.pyplot as plt
from scipy.optimize import minimize

from frispy import Disc
from frispy import Model
from frispy import Discs

model = Discs.wraith
v = 25
rot = -v / model.diameter
nose_up = 0
a = 10

def distance(x):
    hyzer = x[0]
    d = Disc(model, {"vx": math.cos(a * math.pi / 180) * v, "dgamma": rot, "vz": math.sin(a * math.pi / 180) * v, "nose_up": nose_up, "hyzer": hyzer})
    r = d.compute_trajectory(15.0, None, **{"max_step": .2})
    rx = r.x[-1]
    ry = abs(r.y[-1])
    return -rx + ry / (rx + ry)

x0 = [0]
res = minimize(distance, x0, method='powell', options={'xtol': 1e-8, 'disp': True})
pprint(res)
hyzer = res.x[0]
disc = Disc(model, {"vx": math.cos(a * math.pi / 180) * v, "dgamma": rot, "vz": math.sin(a * math.pi / 180) * v,
                 "nose_up": nose_up, "hyzer": hyzer})

result = disc.compute_trajectory(15.0, None, **{"max_step": .2})
times = result.times
t, x, y, z = result.times, result.x, result.y, result.z

plt.plot(x, y)
plt.plot(x, z)

plt.show()
