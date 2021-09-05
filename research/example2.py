import math
from pprint import pprint

import matplotlib.pyplot as plt
from scipy.optimize import minimize

from frispy import Disc
from frispy import Model
import numpy as np

# aviar, roc, buzzz, storm, quarter k, wraith
#speed = [2, 4, 5, 6, 9, 11]
#drag = [.077, .066, .058, .053, .059, .048]
#plt.plot(speed, drag)

#fade = [0, 1, 1, 2, 3, 5]
#dCm_da = [0.002, 0.003, .004, .005, .006, 0.008]
#plt.plot(fade, dCm_da)

turn = [-2, -1, -1, 0, 0, 1]
cm0 = [-0.033, -0.026, -0.020, -0.018, -0.015, -0.007]
plt.plot(turn, cm0)

plt.show()
