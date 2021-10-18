import math
from pprint import pprint

import matplotlib.pyplot as plt
from scipy.optimize import minimize

from frispy import Disc
from frispy import Model
import numpy as np

def drag_from_speed(speed: float) -> float:
    return .089 - 0.012 * math.sqrt(speed)

# ultrastar, aviar, roc, buzzz, storm, quarter k, wraith, flick
speed = [0.1, 2, 4, 5, 6, 9, 11, 12]
drag = [.085, .072, .066, .058, .053, .059, .048, .058]
#plt.plot([math.sqrt(s) for s in speed], drag)  # decently linear
#plt.plot([math.sqrt(s) for s in speed], [drag_from_speed(x) for x in speed])  # decently linear

#fade = [0, 1, 1, 2, 3, 5]
#dCm_da = [0.002, 0.003, .004, .005, .006, 0.008]
#plt.plot(fade, dCm_da)

def cm0_from_turn(t: float) -> float:
    return t * 0.009 - 0.016

turn = [-2, -1, -1, 0, 0, 1]
cm0 = [-0.033, -0.026, -0.020, -0.018, -0.015, -0.007]
#plt.plot(turn, cm0)
#plt.plot(turn, [cm0_from_turn(x) for x in turn])

def maxGlideRangeForSpeed(speed: float) -> float:
    if speed < 3:
        return 3
    elif speed > 5:
        return 5
    else:
        return speed

def cl0FromGlide(glide: float, speed: float) -> float:
    percent = glide / maxGlideRangeForSpeed(speed)
    return 0.152 * percent

# ultrastar, aviar, roc, buzzz, storm, quarter k, wraith, flick
glide = [2.7,   3,  1.4,  3.3,  3.,  4.5,  4.8, 3.3]
cl0 = [.135, .152, .053, .099, .107, .138, .143, .1, ]
#plt.plot(glide, cl0)
#plt.plot(speed, cl0)
plt.plot([g/maxGlideRangeForSpeed(s) for s,g in zip(speed, glide)], cl0)
plt.plot([g/maxGlideRangeForSpeed(s) for s,g in zip(speed, glide)], [cl0FromGlide(g, s) for s,g in zip(speed, glide)])

def dcl_da_from_speed(speed: float) -> float:
    return .052 - 0.004 * math.sqrt(speed)

# ultrastar, aviar, roc, buzzz, storm, quarter k, wraith, flick
dcl_da = [.051, .044, .043, .041, .045, .039, .04, 0.038]
#plt.plot([math.sqrt(s) for s in speed], dcl_da)
#plt.plot([math.sqrt(s) for s in speed], [dcl_da_from_speed(i) for i in speed])

plt.show()
