import math
from pprint import pprint

import matplotlib.pyplot as plt
from scipy.optimize import minimize

from frispy import Disc
from frispy import Model
from frispy import Discs

model = Discs.roc
v = 20
rot = -v / model.diameter
nose_up = 10

def distance(x):
    a, hyzer = x
    d = Disc(model, {"vx": math.cos(a * math.pi / 180) * v, "dgamma": rot, "vz": math.sin(a * math.pi / 180) * v, "nose_up": nose_up, "hyzer": hyzer})
    r = d.compute_trajectory(15.0, None, **{"max_step": .2})
    rx = r.x[-1]
    ry = r.y[-1]
    return -rx + ry / (rx + ry)

x0 = [10, 0]
res = minimize(distance, x0, method='powell', options={'xtol': 1e-8, 'disp': True})
pprint(res)
disc = Disc(model, {"vx": math.cos(res.x[0] * math.pi / 180) * v, "dgamma": rot, "vz": math.sin(res.x[0] * math.pi / 180) * v, "nose_up": nose_up, "hyzer": res.x[1]})

result = disc.compute_trajectory(15.0, None, **{"max_step": .2})
times = result.times
t, x, y, z = result.times, result.x, result.y, result.z

plt.plot(x, y)
plt.plot(x, z)

plt.show()
