import matplotlib.pyplot as plt

from frispy import Disc
from frispy import Model
import numpy as np

# estimate drag from speed
# estimate PL0 from glide
# estimate PTy0 from turn
# estimate PTya from turn and fade

nuke = Model(**{
    "PL0": 0.138,  # lift factor at 0 AoA
    "PLa": 2.29,  # lift factor linear with AoA
    "PD0": 0.055,  # drag at 0 lift
    "PDa": 0.69,  # quadratic with AoA from zero lift point
    "PTxwz": 0,  # rolling moment related to spin precession?
    "PTy0": -0.08,  # pitching moment from disc stability at 0 AoA
    "PTya": 0.3,  # pitching moment from disc stability linear in AoA
    "PTywy": -1.3e-2,  # dampening factor for pitch
    "PTxwx": -1.3e-2,  # dampening factor for roll
    "PTzwz": -3.4e-5,  # spin down
    "I_xx": 6.183E-04,
    "I_zz": 1.231E-03,
    "mass": 0.175,
    "diameter": 0.212,
    "rim_depth": 0.012,
    "rim_width": 0.025,
})

#disc = Disc(nuke)
#disc = Disc(None, {"vx": 35, "dgamma": 120, "vz": 3, "theta": 0.2, "phi": -0.05})
disc = Disc(None, {"vx": 25, "dgamma": -100, "dtheta": 0, "vz": 4, "theta": 0.0, "phi": -1.5})
#phi is anhyzer (roll)
#theta is nose down (pitch)
#result = disc.compute_trajectory(3.0, None, **{"max_step": .0001, "rtol": 1e-6, "atol": 1e-9})
result = disc.compute_trajectory(5)
times = result.times
t, x, y, z, phi, dtheta, theta = result.times, result.x, result.y, result.z, result.phi, result.dtheta, result.theta

#plt.plot(x, y)
#plt.plot(x, z)
#plt.plot(t, theta)

#plt.plot(t, result.dtheta)
#plt.plot(t, result.dphi)

plt.plot(t, theta)
plt.plot(t, phi)

plt.show()
