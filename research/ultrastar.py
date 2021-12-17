#  Copyright (c) 2021 John Carrino
import math
from pprint import pprint

import matplotlib.pyplot as plt
from scipy.optimize import minimize

from frispy import Disc
from frispy import Discs

model = Discs.ultrastar
mph_to_mps = 0.44704
v = 50 * mph_to_mps
rot = -v / model.diameter
ceiling = 2.5

def distance(x):
    a, nose_up, hyzer = x
    d = Disc(model, {"vx": math.cos(a * math.pi / 180) * v, "dgamma": rot, "vz": math.sin(a * math.pi / 180) * v,
                     "nose_up": nose_up, "hyzer": hyzer})
    r = d.compute_trajectory(15.0, **{"max_step": .2})
    rx = r.x[-1]
    ry = abs(r.y[-1])

    overCelingIndex = next(filter(lambda i: r.z[i] > ceiling, range(len(r.z))), None)
    if overCelingIndex is not None:
        return -r.x[overCelingIndex]

    return -rx + ry / (rx + ry)

bnds = [(-90, 90)] * 3
x0 = [8, -3, 25]
res = minimize(distance, x0, method='powell', bounds=bnds, options={'xtol': 1e-8, 'disp': True})
pprint(res)
a, nose_up, hyzer = res.x
disc = Disc(model, {"vx": math.cos(a * math.pi / 180) * v, "dgamma": rot, "vz": math.sin(a * math.pi / 180) * v,
                 "nose_up": nose_up, "hyzer": hyzer})

result = disc.compute_trajectory(15.0, **{"max_step": .2})
times = result.times
t, x, y, z = result.times, result.x, result.y, result.z

pprint(x[-1] * 3.28084) # feet

plt.plot(x, y)
plt.plot(x, z)

# plt.plot(t, x)
# plt.plot(t, [v[0] for v in result.v])

plt.show()
