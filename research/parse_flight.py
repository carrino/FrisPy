#  Copyright (c) 2021 John Carrino
import math
from pprint import pprint
import matplotlib.pyplot as plt
import numpy as np

from frispy import ThrowData

#flight: ThrowData = ThrowData.readFile("condor.throw")
#flight: ThrowData = ThrowData.readFile("great.throw")
flight: ThrowData = ThrowData.readFile("busted_accel_6.throw")
RADIUS_ACCEL = 0.01778 # 0.700 inches in m

time = [0] * ThrowData.NUM_POINTS
for i in range(ThrowData.NUM_POINTS):
    time[i] = time[i-1] + flight.durationMicros[i]

# plt.plot(time, [i[0] for i in flight.gyros])
# plt.plot(time, [i[1] for i in flight.gyros])
# plt.plot(time, [i[2] for i in flight.gyros])

rot = flight.getStartingRotation()
pprint(rot.as_quat())

euler = rot.as_euler('zyx')
phi = euler[2]
theta = euler[1]
pprint(euler)

# plt.plot(time, [i[0] for i in flight.accel0])
#plt.plot(time, [i[1] for i in flight.accel0])
#plt.plot(time, [i[2] for i in flight.accel0])

#plt.plot(time, [-i[0] for i in flight.accel1])
#plt.plot(time, [i[1] for i in flight.accel1])
#plt.plot(time, [i[2] for i in flight.accel1])

#plt.plot(time, [i[0] for i in flight.accel2])
#plt.plot(time, [i[1] for i in flight.accel2])
#plt.plot(time, [i[2] for i in flight.accel2])

def linearAcc(acc1, acc2):
    x = (acc1[0] - acc2[0]) / 2
    y = (acc1[1] - acc2[1]) / 2
    return math.sqrt(x*x + y*y)

#plt.plot(time, [i[2] for i in flight.gyros])
#plt.plot(time, [(j[0] + i[0]) / 2 for i,j in zip(flight.accel1, flight.accel2)])
#plt.plot(time, [math.sqrt(max(0, (j[1] + i[1]) / 2 / RADIUS_ACCEL)) for i,j in zip(flight.accel1, flight.accel2)])
#plt.plot(time, [linearAcc(i, j) for i,j in zip(flight.accel1, flight.accel2)])

#plt.plot(time, [i[0] for i in flight.gyros])
#plt.plot(time, [i[1] for i in flight.gyros])
#plt.plot(time, [i[2] for i in flight.gyros])

#plt.plot(time, [i[1] for i in flight.accel0])
plt.plot(time, [i[0] for i in flight.accel1])
#plt.plot(time, [i[0] for i in flight.accel2])
#plt.plot(time, [(i[2] + j[2])/2 for i,j in zip(flight.accel1, flight.accel2)])

plt.show()
