import math
from pprint import pprint

import matplotlib.pyplot as plt
from scipy.optimize import minimize

from frispy import Disc
from frispy import Discs
from frispy import Model


model = Discs.wraith
v = 20
rot = v / -.211
hz = rot / (2 * math.pi)

def distance(x):
    a, nose_up, hyzer = x
    d = Disc(model, {"vx": math.cos(a * math.pi / 180) * v, "dgamma": rot, "vz": math.sin(a * math.pi / 180) * v, "nose_up": nose_up, "hyzer": hyzer})
    r = d.compute_trajectory(10.0, None, **{"max_step": .1})
    rx = r.x[-1]
    ry = r.y[-1]
    return -rx + ry / (rx + ry)

#disc = Disc()
#disc = Disc(wraith, {"vx": 30, "dgamma": -100, "vz": 10, "nose_up": -5, "hyzer": 52})
#disc = Disc(wraith, {"vx": 30, "dgamma": -100, "vz": 10, "nose_up": 0, "hyzer": 40.5})

# 8.9 m/s left at 3s      65m
#disc = Disc(wraith, {"vx": math.cos(angle) * v, "dgamma": rot, "vz": math.sin(angle) * v, "nose_up": 5, "hyzer": 5})

#10.47 m/s left at 3s   76m
#disc = Disc(wraith, {"vx": math.cos(angle) * v, "dgamma": rot, "vz": math.sin(angle) * v, "nose_up": 0, "hyzer": 10})
#disc = Disc(roc, {"vx": math.cos(angle) * v, "dgamma": rot, "vz": math.sin(angle) * v, "nose_up": 0, "hyzer": 0})


#12.1 m/s left at 3s   85m
#disc = Disc(wraith, {"vx": math.cos(angle) * v, "dgamma": rot, "vz": math.sin(angle) * v, "nose_up": -5, "hyzer": 15})

#12.7   89m total
#disc = Disc(wraith, {"vx": math.cos(angle) * v, "dgamma": rot, "vz": math.sin(angle) * v, "nose_up": -8, "hyzer": 20})

# 89 m total
#disc = Disc(wraith, {"vx": math.cos(angle) * v, "dgamma": rot, "vz": math.sin(angle) * v, "nose_up": -10, "hyzer": 25})

#88m
#disc = Disc(wraith, {"vx": math.cos(angle) * v, "dgamma": rot, "vz": math.sin(angle) * v, "nose_up": -12, "hyzer": 32})

# gamma is spin LHBH/RHFH
# phi is anhyzer (roll)
# theta is nose down (pitch)


#disc = Disc(wraith, {"vx": math.cos(angle) * v, "dgamma": rot, "vz": math.sin(angle) * v, "nose_up": 0, "hyzer": 7})
#disc = Disc(wraith, {"vx": math.cos(angle) * v, "dgamma": rot, "vz": math.sin(angle) * v, "nose_up": 0, "hyzer": 7, "dphi": rot/100})

x0 = [14, -4, 0]
#res = minimize(distance, x0, method='nelder-mead', options={'xatol': 1e-8, 'disp': True})
res = minimize(distance, x0, method='powell', options={'xtol': 1e-8, 'disp': True})
pprint(res)
disc = Disc(model, {"vx": math.cos(res.x[0] * math.pi / 180) * v, "dgamma": rot, "vz": math.sin(res.x[0] * math.pi / 180) * v, "nose_up": res.x[1], "hyzer": res.x[2]})

#result = disc.compute_trajectory(8.0, None, **{"max_step": .1, "rtol": 1e-6, "atol": 1e-9})
result = disc.compute_trajectory(8.0, None, **{"max_step": .1})
#result = disc.compute_trajectory(8)
times = result.times
t, x, y, z = result.times, result.x, result.y, result.z

plt.plot(x, y)
plt.plot(x, z)
#plt.plot(x, result.vy)

#plt.plot(t, result.dtheta)
#plt.plot(t, result.dphi)
#plt.plot(t, result.dgamma)

#plt.plot(t, x)
#plt.plot(t, y)
#plt.plot(t, z)
#plt.plot(t, result.vx)
#plt.plot(t, result.vz)
#plt.plot(t, result.dphi)
#plt.plot(t, result.dtheta)

plt.show()
