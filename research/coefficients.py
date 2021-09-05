import math

import matplotlib.pyplot as plt

from frispy import Discs

model = Discs.ultrastar

# plot coefficients from -180 to 180
deg = range(-180, 180)
lift = map(lambda x: model.C_lift(x * math.pi / 180), deg)
plt.plot(deg, lift)

plt.show()
