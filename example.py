import math

import matplotlib.pyplot as plt

from frispy import Disc
from frispy import Model
import numpy as np

# estimate drag from speed
# estimate PL0 from glide
# estimate PTy0 from turn
# estimate PTya from turn and fade

wraith = Model(**{
    "PL0": 0.143,  # lift factor at 0 AoA (depends on glide)
    "PLa": 2.29,  # lift factor linear with AoA (0.04 deg -> 2.29 rad) (constant)
    "PD0": 0.055,  # drag at 0 lift  (based on disc speed)
    # (.055 at speed 11, .061 speed 5, .067 speed 4, .083 speed 2)
    "PDa": 1.67,  # quadratic with AoA from zero lift point (constant)
    "PTxwz": 0,  # rolling moment related to spin precession?
    "PTy0": -0.02,  # pitching moment from disc stability at 0 AoA (based on turn of disc, also based on cavity of disc)
    # -0.02 turn -1, -0.007 turn 1, -0.033 turn -2, -0.015 turn 0  (per degree not per rad)
    "PTya": 0.343,  # pitching moment from disc stability linear in AoA (0.006 / deg -> 0.343) (based on fade of disc)
    # fade 0 0.002, fade 1 0.004, fade 3  0.006, fade 5 0.008  (per degree not per rad)
    "PTywy": -1.3e-2,  # dampening factor for pitch (constant)
    "PTxwx": -1.3e-2,  # dampening factor for roll (constant)
    "PTzwz": -3.4e-5,  # spin down (constant)
    "I_xx": 6.183E-04,
    "I_zz": 1.231E-03,
    "mass": 0.175,
    "diameter": 0.211,
    "rim_depth": 0.012,
    "rim_width": 0.021,
    "height": 0.014,
})

angle = 15 * math.pi / 180
v = 25
rot = v / -.211
hz = rot / (2 * math.pi)
#disc = Disc()
#disc = Disc(wraith, {"vx": 30, "dgamma": -100, "vz": 10, "nose_up": -5, "hyzer": 52})
#disc = Disc(wraith, {"vx": 30, "dgamma": -100, "vz": 10, "nose_up": 0, "hyzer": 40.5})

# 8.9 m/s left at 3s      65m
disc = Disc(wraith, {"vx": math.cos(angle) * v, "dgamma": rot, "vz": math.sin(angle) * v, "nose_up": 5, "hyzer": 0})

#10.47 m/s left at 3s   76m
#disc = Disc(wraith, {"vx": math.cos(angle) * v, "dgamma": rot, "vz": math.sin(angle) * v, "nose_up": 0, "hyzer": 7})

#12.1 m/s left at 3s   85m
#disc = Disc(wraith, {"vx": math.cos(angle) * v, "dgamma": rot, "vz": math.sin(angle) * v, "nose_up": -5, "hyzer": 15})

#12.7   89m total
#disc = Disc(wraith, {"vx": math.cos(angle) * v, "dgamma": rot, "vz": math.sin(angle) * v, "nose_up": -8, "hyzer": 20})

# 89 m total
#disc = Disc(wraith, {"vx": math.cos(angle) * v, "dgamma": rot, "vz": math.sin(angle) * v, "nose_up": -10, "hyzer": 25})

#88m
#disc = Disc(wraith, {"vx": math.cos(angle) * v, "dgamma": rot, "vz": math.sin(angle) * v, "nose_up": -12, "hyzer": 28})

# gamma is spin LHBH/RHFH
# phi is anhyzer (roll)
# theta is nose down (pitch)

#
disc = Disc(wraith, {"vx": math.cos(angle) * v, "dgamma": rot, "vz": math.sin(angle) * v, "nose_up": 0, "hyzer": 7, "dphi": -1})

#result = disc.compute_trajectory(3.0, None, **{"max_step": .0001, "rtol": 1e-6, "atol": 1e-9})
result = disc.compute_trajectory(8)
times = result.times
t, x, y, z = result.times, result.x, result.y, result.z

plt.plot(x, y)
plt.plot(x, z)

#plt.plot(t, result.dtheta)
#plt.plot(t, result.dphi)
#plt.plot(t, result.dgamma)

#plt.plot(t, x)
#plt.plot(t, y)
#plt.plot(t, z)
#plt.plot(t, result.vx)

plt.show()
