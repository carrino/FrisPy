import math
from pprint import pprint

import matplotlib.pyplot as plt
from scipy.optimize import minimize

from frispy import Disc
from frispy import Discs
from frispy import Model

coefficents = Discs.wraith.coefficients.copy()
mass = 0.160
mass_multiple = Discs.wraith.mass / mass
coefficents['mass'] = mass
coefficents['I_xx'] = coefficents['I_xx'] / mass_multiple
coefficents['I_zz'] = coefficents['I_zz'] / mass_multiple
model = Model(**coefficents)
v = 20 * math.sqrt(mass_multiple)
rot = -v / model.diameter
z = 20

def distance(x):
    a, nose_up, hyzer = x
    d = Disc(model, {"z": z, "vx": math.cos(a * math.pi / 180) * v, "dgamma": rot, "vz": math.sin(a * math.pi / 180) * v,
                     "nose_up": nose_up, "hyzer": hyzer})
    r = d.compute_trajectory(15.0, None, **{"max_step": .2})
    rx = r.x[-1]
    ry = r.y[-1]
    return -rx + ry / (rx + ry)

# 175g wraith 20m/s [ 2.03652849, -5.29455721, 20.57560961] -> 120.8m
# 160g wraith 21m/s [ 0.13502528, -0.85695224, 26.88916461] -> 126.9m

# 175g wraith 25m/s [ 3.2128121 , -0.04261368, 34.65603539] -> 152.9m
# 160g wraith 26m/s [ 5.67660944,  0.44777144, 42.195757 ] -> 158.1m
x0 = [3, 0, 34]
res = minimize(distance, x0, method='powell', options={'xtol': 1e-8, 'disp': True})
pprint(res)
a, nose_up, hyzer = res.x
disc = Disc(model, {"z": z, "vx": math.cos(a * math.pi / 180) * v, "dgamma": rot, "vz": math.sin(a * math.pi / 180) * v,
                 "nose_up": nose_up, "hyzer": hyzer})

result = disc.compute_trajectory(15.0, None, **{"max_step": .2})
times = result.times
t, x, y, z = result.times, result.x, result.y, result.z

plt.plot(x, y)
plt.plot(x, z)

plt.show()
