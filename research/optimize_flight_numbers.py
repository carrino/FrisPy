import math
from pprint import pprint

from scipy.optimize import Bounds
import matplotlib.pyplot as plt
from scipy.optimize import minimize
import numpy as np


from frispy import Disc
from frispy import Discs

mph_to_mps = 0.44704
v = 60 * mph_to_mps # what is the optimal disc for 60mph
rot = -v / 0.211
a = 10
nose_up = -3
hyzer = 10

def distance(x):
    speed, glide, turn = x
    model = Discs.from_flight_numbers({"glide": glide, "speed": speed, "turn": turn})
    d = Disc(model, {"vx": math.cos(a * math.pi / 180) * v, "dgamma": rot, "vz": math.sin(a * math.pi / 180) * v,
                     "nose_up": nose_up, "hyzer": hyzer})
    r = d.compute_trajectory(20.0, **{"max_step": .2})
    rx = r.x[-1]
    array = r.y
    # find max of array
    min = np.amin([i for i in array if i <= 0])

    # return -rx - min
    return -rx

x0 = [13, 5, -1]
bounds = Bounds([1, 1, -4], [13, 5, 4])
# res = minimize(distance, x0, method='powell', bounds=bounds, options={'xtol': 1e-8, 'disp': True})
res = minimize(distance, x0, method='trust-constr', bounds=bounds, options={'xtol': 1e-5, 'disp': True})
pprint(res)
speed, glide, turn = res.x
model = Discs.from_flight_numbers({"glide": glide, "speed": speed, "turn": turn})
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
