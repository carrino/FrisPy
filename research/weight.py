import math
from pprint import pprint

import matplotlib.pyplot as plt
from scipy.optimize import minimize

from frispy import Disc
from frispy import Discs
from frispy import Model

model = Discs.stable_wraith
#v = 25 # 25 m/s is 56 mph
v = 30 # 30 m/s is 67 mph
rot = -v / model.diameter
weight_factor = 0.175 / 0.175
model.set_value("I_xx", 6.183E-04 * weight_factor)
model.set_value("I_zz", 1.231E-03 * weight_factor)
model.set_value("mass", 0.175 * weight_factor)
#v = v * math.sqrt(1/weight_factor)
#pprint(v)


def distance(x):
    a, nose_up, hyzer = x
    d = Disc(model, {"vx": math.cos(a * math.pi / 180) * v, "dgamma": rot, "vz": math.sin(a * math.pi / 180) * v,
                     "nose_up": nose_up, "hyzer": hyzer})
    r = d.compute_trajectory(15.0, **{"max_step": .2})
    rx = r.x[-1]
    ry = abs(r.y[-1])
    return -rx + ry / (rx + ry)

bnds = [(-90, 90)] * 3
x0 = [8, -3, 20]
res = minimize(distance, x0, method='powell', bounds=bnds, options={'xtol': 1e-8, 'disp': True})
pprint(res)
a, nose_up, hyzer = res.x
disc = Disc(model, {"vx": math.cos(a * math.pi / 180) * v, "dgamma": rot, "vz": math.sin(a * math.pi / 180) * v,
                 "nose_up": nose_up, "hyzer": hyzer})

result = disc.compute_trajectory(15.0, **{"max_step": .2})
times = result.times
t, x, y, z = result.times, result.x, result.y, result.z

#plt.plot(x, y)
#plt.plot(x, z)

#plt.plot(t, x)
plt.plot(t, y)
plt.plot(t, z)

plt.show()
