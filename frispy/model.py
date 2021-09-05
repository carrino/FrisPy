"""
Physical model for the forces and torques on a disc.
"""
import math
from pprint import pprint
from typing import Dict

import numpy as np


class Model:
    """
    Coefficient model for a disc. Holds all of the aerodynamic
    parameters coupling the kinematic variables (spins and angles)
    to the force magnitudes.
    """

    def __init__(self, **kwargs):
        self._coefficients: Dict[str, float] = {
            "PL0": 0.13, # lift factor at 0 AoA
            "PLa": 2.7, # lift factor linear with AoA
            "PD0": 0.18, # drag at 0 lift
            "PDa": 0.69, # quadratic with AoA from zero lift point
            "PTxwx": -1.3e-2, # dampening factor for roll
            "PTxwz": 0, # rolling moment related to spin precession?
            "PTy0": -8.2e-2, # pitching moment from disc stability at 0 AoA
            "PTya": 0.43, # pitching moment from disc stability linear in AoA
            "PTywy": -1.3e-2, # dampening factor for pitch
            "PTzwz": -3.4e-5, # spin down
            "I_zz": 0.002352,
            "I_xx": 0.001219,
            "mass": 0.175,
            "diameter": 0.27,
            "rim_depth": 0.02,
            "rim_width": 0.007,
            "height": 0.032,
        }
        for k, v in kwargs.items():
            self.coefficients[k] = v
            if k == "CD0":
                # handle the case where we only know the drag at AoA 0 and not lift = 0
                continue
            assert k in self.coefficients, f"invalid coefficient name {k}"
        self.coefficients["area"] = np.pi * (self.coefficients["diameter"] / 2) ** 2
        self.coefficients["cavity_volume"] = (self.coefficients["rim_depth"]
                * np.pi * (self.coefficients["diameter"] / 2 - self.coefficients["rim_width"]) ** 2
        )
        alpha_0 = -self.coefficients["PL0"] / self.coefficients["PLa"]
        self.coefficients["alpha_0"] = alpha_0
        if "CD0" in self.coefficients:
            self.coefficients["PD0"] = self.coefficients["CD0"] - self.coefficients["PDa"] * alpha_0 * alpha_0

        #pprint(self.coefficients["cavity_volume"] / self.coefficients["rim_depth"] / self.coefficients["diameter"] * 180 / math.pi)

    def set_value(self, name: str, value: float) -> None:
        """
        Set the value of a coefficient.

        Args:
            name (str): name of the coefficient
            value (float): value of the coefficient
        """
        assert name in self.coefficients, f"invalid coefficient name {name}"
        self._coefficients[name] = value

    def set_values(self, coefs: Dict[str, float]) -> None:
        """
        Set the values of the coefficients.

        Args:
            coefs (Dict[str, float]): key-value pairs of coeffient names
                ane their values
        """
        for k, v in coefs.items():
            self.set_value(k, v)

    def get_value(self, name: str) -> float:
        """
        Obtain the value of the coefficient.

        Args:
            name (str): name of the coefficient

        Returns:
            value of the coefficient with the name `name`
        """
        assert name in self.coefficients, f"invalid coefficient name {name}"
        return self.coefficients[name]

    @property
    def coefficients(self) -> Dict[str, float]:
        return self._coefficients

    @property
    def mass(self) -> float:
        return self.get_value("mass")

    @property
    def area(self) -> float:
        return self.get_value("area")

    @property
    def diameter(self) -> float:
        return self.get_value("diameter")

    @property
    def I_zz(self) -> float:
        return self.get_value("I_zz")

    @property
    def I_xx(self) -> float:
        return self.get_value("I_xx")

    @property
    def dampening_factor(self) -> float:
        return self.get_value("PTxwx")

    @property
    def dampening_z(self) -> float:
        return self.get_value("PTzwz")

    #####################################################################
    # Below are functions connecting physical variables to force/torque #
    # scaling factors (the `C`s)                                        #
    #####################################################################

    def C_lift(self, alpha: float) -> float:
        """
        Lift force scale factor. Linear in the angle of attack (`alpha`).

        Args:
            alpha (float): angle of attack in radians

        Returns:
            (float) lift force scale factor
        """
        PL0 = self.get_value("PL0")
        PLa = self.get_value("PLa")
        if alpha < math.pi / 2:
            return PL0 + PLa * alpha
        else:
            # this is the case where the disc has stalled out
            prestall = PL0 + PLa * (math.pi / 2)
            return (math.pi - alpha) * prestall / 2

    def C_drag(self, alpha: float) -> float:
        """
        Drag force scale factor. Quadratic in the angle of attack (`alpha`).

        Args:
            alpha (float): angle of attack in radians

        Returns:
            (float) drag force scale factor
        """
        PD0 = self.get_value("PD0")
        PDa = self.get_value("PDa")
        alpha_0 = self.get_value("alpha_0")
        delta = (alpha - alpha_0)

        # .4 rad is about where this stops being quadratic
        quadratic_rise_rate = PDa * 0.4
        if delta <= 0.4:
            return PD0 + PDa * delta ** 2
        elif alpha < math.pi / 2:
            # handle drag dropping off after about .4 rad
            return PD0 + quadratic_rise_rate * 0.4 + quadratic_rise_rate * (delta - 0.4)
        else:
            # handle stall case
            prestall = PD0 + quadratic_rise_rate * 0.4 + quadratic_rise_rate * (math.pi / 2 - 0.4)
            poststall_rate = quadratic_rise_rate / 3
            return prestall / 1.4 + poststall_rate * (alpha - math.pi / 2)

    def C_x(self, wz: float) -> float:
        """
        'x'-torque scale factor. Linearly additive in the 'z' angular velocity
        (`w_z`) and the 'x' angular velocity (`w_x`).

        Args:
            wx (float): 'x' angular velocity in radians per second
            wz (float): 'z' angular velocity in radians per second

        Returns:
            (float) 'x'-torque scale factor
        """
        PTxwz = self.get_value("PTxwz")
        return PTxwz * wz

    def C_y(self, alpha: float) -> float:
        """
        'y'-torque scale factor. Linearly additive in the 'y' angular velocity
        (`w_y`) and the angle of attack (`alpha`).

        Args:
            alpha (float): angle of attack in radians
            wy (float): 'y' angular velocity in radians per second

        Returns:
            (float) 'y'-torque scale factor
        """

        PTy0 = self.get_value("PTy0")
        PTya = self.get_value("PTya")
        cavity_pitch_adjust = 0
        angle_of_cavity = self.coefficients["cavity_volume"] / self.coefficients["rim_depth"] / self.coefficients["diameter"]
        if angle_of_cavity > alpha > -angle_of_cavity:
            cavity_pitch_adjust = -math.sin(math.pi * alpha / angle_of_cavity) * (PTya * angle_of_cavity / 4)
        pitch = PTy0 + PTya * alpha
        if alpha <= 0.3:
            return pitch + cavity_pitch_adjust
        elif alpha <= math.pi / 2:
            # pitch doubles after about .3 rad
            return pitch + PTya * (alpha - 0.3)
        elif alpha <= 80 * math.pi / 180:
            # after stall the pitch drops
            return self.C_y(15 * math.pi / 180)
        else:
            # last 10 degrees of drop down to 0 at 90 deg
            before_drop = self.C_y(15 * math.pi / 180)
            return ((math.pi - alpha) * 180 / math.pi) * before_drop / 10
