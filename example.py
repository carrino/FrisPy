import matplotlib.pyplot as plt

from frispy import Disc

disc = Disc()
disc = Disc(None, {"vx": 13.42, "dgamma": 54.25})
result = disc.compute_trajectory()
times = result.times
t, x, y, z = result.times, result.x, result.y, result.z

plt.plot(t, x)
plt.plot(t, y)
plt.plot(t, z)
plt.show()
