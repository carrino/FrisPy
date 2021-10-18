"""
The ``Trajectory`` is the interface to the differential equation solver
for the disc trajectory.
"""

from numbers import Number
from typing import Dict, Union
from scipy.spatial.transform import Rotation

import numpy as np


class Trajectory:
    """
    Class for computing the disc flight trajectory. Takes initial values
    and interfaces with an ODE solver.

    Units are meters [m] for length, kilograms [kg] for mass, seconds [s]
    for time, and radians [rad] for angles.

    Args:
        x (float): horizontal position; default is 0 m
        y (float): horizontal position; default is 0 m
        z (float): vertical position; default is 1 m
        vx (float): x-velocity; default is 10 m/s
        vy (float): y-velocity; default is 0 m/s
        vz (float): z-velocity; default is 0 m/s
        phi (float): 1st Euler angle (pitch); default is 0 rad
        theta (float): 2nd Euler angle (roll); default is 0 rad
        gamma (float): 3rd Euler angle (spin); default is 0 rad
        phidot (float): phi angular velocity; default is 0 rad/s
        thetadot (float): theta angular velocity; default is 0 rad/s
        gammadot (float): gamma angular velocity; default is 50 rad/s

    """

    def __init__(self, **kwargs):
        # A default flight configuration
        self._initial_conditions: Dict[str, float] = {
            "x": 0,
            "y": 0,
            "z": 1,
            "vx": 10,
            "vy": 0,
            "vz": 0,
            "phi": 0,
            "theta": 0,
            "gamma": 0,
            "phidot": 0,
            "thetadot": 0,
            "gammadot": 50,
        }
        self._coord_order = [
            "x",
            "y",
            "z",
            "vx",
            "vy",
            "vz",
            "phi",
            "theta",
            "gamma",
            "phidot",
            "thetadot",
            "gammadot",
        ]

        # set arguments to initial conditions
        for k, v in kwargs.items():
            assert (
                k in self._initial_coordinates
            ), f"invalid initial condition name {k}"
            assert isinstance(v, Number), f"invalid type for {v}, {type(v)}"
            self._initial_conditions[k] = v

        # Coordinate array
        self._current_coordinates = self.initial_conditions_array.copy()
        self._all_coordinates = self.initial_conditions_array.reshape(1, -1)

    @property
    def initial_conditions(self) -> Dict[str, float]:
        return self._initial_conditions

    @property
    def initial_conditions_array(self) -> np.ndarray:
        return np.array([self.initial_conditions[k] for k in self._coord_order])

    @property
    def velocity(self) -> np.ndarray:
        """
        Velocity vector [m/s].
        """
        return self._current_coordinates[3:6]

    @staticmethod
    def calculate_intermediate_quantities(
        rotation: Rotation,
        velocity: np.ndarray,
        ang_velocity: np.ndarray,
    ) -> Dict[str, Union[float, np.ndarray, Dict[str, np.ndarray]]]:
        """
        Compute intermediate quantities on the way to computing the time
        derivatives of the kinematic variables.

        Args:
        TODO
        """
        # Rotation matrix
        R = rotation.as_matrix()
        # Unit vectors
        zhat = R @ np.array([0, 0, 1])
        v_dot_zhat = velocity @ zhat
        v_in_plane = velocity - zhat * v_dot_zhat
        xhat = v_in_plane / np.linalg.norm(v_in_plane)
        yhat = np.cross(zhat, xhat)

        # Angle of attack
        angle_of_attack = -np.arctan(v_dot_zhat / np.linalg.norm(v_in_plane))

        # wobble is only the in x and y axis relative to zhat
        w = R @ np.array([ang_velocity[0], ang_velocity[1], 0])
        return {
            "unit_vectors": {"xhat": xhat, "yhat": yhat, "zhat": zhat},
            "angle_of_attack": angle_of_attack,
            "w": w,
        }
