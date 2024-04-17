#  Copyright (c) 2021 John Carrino

import math
from pprint import pprint
import matplotlib.pyplot as plt
from frispy import Disc, Discs, Environment
from frispy.wind import ConstantWind
import numpy as np

model = Discs.destroyer
model = Discs.from_flight_numbers({"glide": 5, "speed": 12, "turn": -3})
mph_to_mps = 0.44704
v = 60 * mph_to_mps
rot = -v / model.diameter
wind = ConstantWind(np.array([v/2, 0, 0]))

x0 = [12, 0, 0]
a, nose_up, hyzer = x0
disc = Disc(model, {"vx": math.cos(a * math.pi / 180) * v, "dgamma": rot, "vz": math.sin(a * math.pi / 180) * v,
                 "nose_up": nose_up, "hyzer": hyzer},
                 Environment(wind=wind))

alt_max_step = 0.1 * (model.diameter * math.pi) / v
result = disc.compute_trajectory(20.0, **{"max_step": alt_max_step})
times = result.times
t, x, y, z = result.times, result.x, result.y, result.z

#plt.plot(x, result.theta)
plt.plot(x, y)
plt.plot(x, z)

#plt.plot(t, x)
#plt.plot(t, y)
#plt.plot(t, z)

pprint(x[-1] * 3.28084) # feet

plt.show()
