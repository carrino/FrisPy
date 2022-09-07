import math
from pprint import pprint

import matplotlib.pyplot as plt
from scipy.optimize import minimize

from frispy import Disc
from frispy import Discs

# model = Discs.wraith
model = Discs.beefy_destroyer
model = Discs.from_flight_numbers({"speed": 12, "glide": 5, "turn": 1})
mph_to_mps = 0.44704
v = 60 * mph_to_mps
# rot = -v / model.diameter
rot = -1200 / 60 * 2 * math.pi
nose_up = 0

def distance(x):
    # 4.53107967, 14.92600242
    a, hyzer = x
    d = Disc(model, {"vx": math.cos(a * math.pi / 180) * v, "dgamma": rot, "vz": math.sin(a * math.pi / 180) * v, "nose_up": nose_up, "hyzer": hyzer})
    r = d.compute_trajectory(15.0, **{"max_step": .2})
    rx = r.x[-1]
    ry = abs(r.y[-1])
    return -rx + ry / (rx + ry)

# pprint(distance([ 1.95602303e+01, -4.23592524e-04]))

x0 = [10, 0]
res = minimize(distance, x0, method='powell', options={'xtol': 1e-8, 'disp': True})
pprint(res)
disc = Disc(model, {"vx": math.cos(res.x[0] * math.pi / 180) * v, "dgamma": rot, "vz": math.sin(res.x[0] * math.pi / 180) * v, "nose_up": nose_up, "hyzer": res.x[1]})

result = disc.compute_trajectory(15.0, **{"max_step": .2})
times = result.times
t, x, y, z = result.times, result.x, result.y, result.z

plt.plot(x, y)
plt.plot(x, z)

pprint(x[-1] * 3.28084) # feet
plt.show()

