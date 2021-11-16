import json
import math
from pprint import pprint

import matplotlib.pyplot as plt
from scipy.optimize import minimize

from frispy import Disc
from frispy import Model
from frispy import Discs

model = Discs.destroyer
v = 25
rot = -126
nose_up = 0
hyzer = 0
uphill = 10
rotation_factor = 1 / 5
#dtheta = -rot * rotation_factor
dtheta = 21.5
dphi = 0
hyzer = math.atan(rotation_factor) / 2 * 180 / math.pi

# gamma is spin LHBH/RHFH (spin around Z axis)
# phi is anhyzer (roll around X axis)
# theta is nose down (pitch around Y axis)

x0 = [10, 0]
disc = Disc(model, {"vx": math.cos(uphill * math.pi / 180) * v, "dgamma": rot, "vz": math.sin(uphill * math.pi / 180) * v,
                    "nose_up": nose_up, "hyzer": hyzer, "dphi": dphi, "dtheta": dtheta})
                    #"nose_up": nose_up, "hyzer": hyzer})

#result = disc.compute_trajectory(20)
result = disc.compute_trajectory(20, **{"max_step": .5, "rtol": 5e-4, "atol": 1e-6})
times = result.times
t, x, y, z = result.times, result.x, result.y, result.z

#plt.plot(x, y)
#plt.plot(x, z)

plt.plot(t, result.dphi)
plt.plot(t, result.dtheta)
#plt.plot(t, result.dgamma)

#plt.plot(t, y)
#plt.plot(t, x)

#plt.plot(t, result.phi)
#plt.plot(t, [i * 180 / math.pi for i in result.phi])
#plt.plot(t, [i * 180 / math.pi for i in result.theta])
#plt.plot(t, [math.sin(i) for i in result.gamma])

pprint(x[-1])
pprint(len(x))
#res = {
#    'p': result.pos,
#    't': [i.tolist() for i in result.times],
#    'v': [i.tolist() for i in result.v],
#    'phi': result.phi, # anhyzer
#    'theta': result.theta, # nose down
#    'qx': result.qx.tolist(),
#    'qy': result.qy.tolist(),
#    'qz': result.qz.tolist(),
#    'qw': result.qw.tolist(),
#}
#
#dump = json.dumps(res)
#pprint(dump)

plt.show()
