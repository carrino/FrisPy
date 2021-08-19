"""
The ``Environment`` object.
"""

from typing import Optional

import numpy as np


class Environment:
    """
    The environment in which the disc is flying in. This object contains
    information on the magnitude and direction of gravity, properties of the
    wind, and also intrinsic properties of the disc such as its area and
    mass.

    Args:
        air_density (float): default is 1.225 kg/m^3
        area (float): default is 0.057 m^2
        g (float): default is 9.81 m/s^2; gravitational acceleration on Earth
        grav_vector (Optional[numpy.ndarray]): default is [0,0,-1] if left as
            ``None``; is a unit vector.
        I_zz (float): default is 0.001219 kg*m^2; z-axis moment of inertia
        I_xx (float): default is 0.175 kg*m^2; x and y-axis moments of inertia
            (i.e. is the same as I_yy and the cross components I_xy)
        mass (float): defualt is 0.175 kg
    """

    def __init__(
        self,
        air_density: float = 1.225,
        g: float = 9.81,
        grav_vector: Optional[np.ndarray] = None,
    ):
        self._air_density = air_density
        self._g = g
        self._grav_vector = grav_vector or np.array([0.0, 0.0, -1.0])

    @property
    def air_density(self) -> float:
        return self._air_density

    @property
    def g(self) -> float:
        return self._g

    @property
    def grav_vector(self) -> np.ndarray:
        return self._grav_vector

