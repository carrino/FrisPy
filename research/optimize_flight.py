import math
from pprint import pprint

import matplotlib.pyplot as plt
from scipy.optimize import minimize, Bounds

from frispy import Disc, Discs, Environment
from frispy.wind import ConstantWind
import numpy as np

model = Discs.beefy_destroyer
model = Discs.from_flight_numbers({"glide": 5, "speed": 13, "turn": 0, "weight": 0.135})
mph_to_mps = 0.44704
v = 60 * mph_to_mps
rot = -v / model.diameter

wind = ConstantWind(np.array([20*mph_to_mps, 0, 0]))

def distance(x):
    a, nose_up, hyzer = x
    d = Disc(model, {"vx": math.cos(a * math.pi / 180) * v, "dgamma": rot, "vz": math.sin(a * math.pi / 180) * v,
                     "nose_up": nose_up, "hyzer": hyzer},
                     Environment(wind=wind))
    r = d.compute_trajectory(20.0, **{"max_step": .2})
    rx = r.x[-1]
    return -rx

x0 = [40, -10, 10]
bounds = Bounds([-90, -90, -90], [50, 90, 90])
res = minimize(distance, x0, method='powell', bounds=bounds, options={'xtol': 1e-8, 'disp': True})
pprint(res)
a, nose_up, hyzer = res.x
disc = Disc(model, {"vx": math.cos(a * math.pi / 180) * v, "dgamma": rot, "vz": math.sin(a * math.pi / 180) * v,
                 "nose_up": nose_up, "hyzer": hyzer},
                 Environment(wind=wind))

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
