import math
from pprint import pprint

import matplotlib.pyplot as plt

from frispy import Discs

model = Discs.ultrastar

# plot coefficients from -180 to 180
deg = range(-90, 90)
#lift = [model.C_lift(x * math.pi / 180) for x in deg]
#plt.plot(deg, lift)

#drag = [model.C_y(x * math.pi / 180) for x in deg]
#plt.plot(deg, drag)

pitch = [model.C_y(x * math.pi / 180) for x in deg]
plt.plot(deg, pitch)

plt.show()
