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

            "PD0": 0.08, # drag at 0 lift
            "PDa": 1.9, # quadratic with AoA from zero lift point
            # "PDa": 1.67, # golf discs have less drag per angle of attack;

            "PTy0": -0.02, # pitching moment from disc stability at 0 AoA
            "PTya": 0.13, # pitching moment from disc stability linear in AoA

            "PTxwx": -1.08e-3, # dampening factor for wobble
            "PTzwz": -3.4e-5, # spin down

            "PTxwz": 0, # rolling moment related to spin precession?
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

    stall: float = math.pi / 4
    neg_stall: float = -40 * math.pi / 180

    @staticmethod
    def normalizeAlpha(alpha: float) -> float:
        if alpha > math.pi or alpha < -math.pi:
            raise ValueError
        if alpha > math.pi / 2:
            return math.pi - alpha
        if alpha < -math.pi / 2:
            return -math.pi - alpha
        return alpha

    def C_lift(self, alpha: float) -> float:
        """
        Lift force scale factor. Linear in the angle of attack (`alpha`).

        Args:
            alpha (float): angle of attack in radians

        Returns:
            (float) lift force scale factor
        """
        alpha = Model.normalizeAlpha(alpha)

        PL0 = self.get_value("PL0")
        PLa = self.get_value("PLa")
        if alpha < 0:
            # a x^2 + b x + c
            b = PLa
            c = PL0
            a = -b / 2 / Model.neg_stall
            if alpha < Model.neg_stall:
                alpha_0 = self.get_value("alpha_0")
                scale = (alpha_0 - Model.neg_stall) / (Model.neg_stall + math.pi / 2)
                x = Model.neg_stall - (Model.neg_stall - alpha) * scale
                return a * x * x + b * x + c
            else:
                return a * alpha * alpha + b * alpha + c
        elif alpha < Model.stall:
            return PL0 + PLa * alpha
        else:
            # this is the case where the disc has stalled out at about 45 degrees
            prestall = PL0 + PLa * Model.stall
            return (math.pi / 2 - alpha) * prestall / 2

    def C_drag(self, alpha: float) -> float:
        """
        Drag force scale factor. Quadratic in the angle of attack (`alpha`).

        Args:
            alpha (float): angle of attack in radians

        Returns:
            (float) drag force scale factor
        """
        alpha = Model.normalizeAlpha(alpha)

        PD0 = self.get_value("PD0")
        PDa = self.get_value("PDa")
        alpha_0 = self.get_value("alpha_0")
        delta = alpha - alpha_0

        # negative AoA drag is based on glide
        # for ultrastar it is about 3/4 of the positive drag coefficient
        glide_coefficeint = 3 / 4
        neg_PDa = PDa * glide_coefficeint

        # .4 rad is about where this stops being quadratic
        quadratic_rise_rate = PDa * 0.4
        if alpha < Model.neg_stall:
            range = Model.neg_stall + math.pi / 2
            stall_alpha = alpha_0 - Model.neg_stall
            prestall = (PD0 + neg_PDa * stall_alpha ** 2) / (1.5 * glide_coefficeint)
            full_nose_down = self.C_drag(glide_coefficeint * 40 * math.pi / 180) - prestall
            return prestall - (alpha - Model.neg_stall) / range * full_nose_down
        elif delta < 0.0:
            return PD0 + neg_PDa * delta ** 2
        elif delta <= 0.4:
            return PD0 + PDa * delta ** 2
        elif alpha <= Model.stall:
            # handle drag dropping off after about .4 rad
            #return PD0 + quadratic_rise_rate * 0.4 + quadratic_rise_rate * (delta - 0.4)
            return PD0 + PDa * delta ** 2
        else:
            # handle stall case at about 45 degrees
            range = math.pi / 2 - Model.stall
            stall_alpha = Model.stall - alpha_0
            prestall = (PD0 + PDa * stall_alpha ** 2) / 1.5
            full_nose_up = self.C_drag(40 * math.pi / 180) - prestall
            return prestall + (alpha - Model.stall) / range * full_nose_up


    def C_x(self, aoa: float, v_norm: float, wz: float) -> float:
        """
        Rolling moment.  Normally zero except at high advance rates.
        Check out FrisbeeAerodynamics.pdf page 145

        Args:
            aoa: angle of attack
            v_norm: velocity relative to the wind
            wz:

        Returns: rolling moment
        """
        return 0

    def C_y(self, alpha: float) -> float:
        """
        pitching moment.  pitching causes turn and fade due to gyroscopic precession.

        'y'-torque scale factor. Linearly additive in the 'y' angular velocity
        (`w_y`) and the angle of attack (`alpha`).

        Args:
            alpha (float): angle of attack in radians
            wy (float): 'y' angular velocity in radians per second

        Returns:
            (float) 'y'-torque scale factor
        """

        alpha = Model.normalizeAlpha(alpha)

        # TODO: figure out why sideways motion happens with 0 pty0
        PTy0 = self.get_value("PTy0")
        # PTya = self.get_value("PTya")
        PTya = 0.008 * 180 / math.pi

        deg_30_in_rad = 30 * math.pi / 180
        if alpha < -deg_30_in_rad:
            percent = (alpha + math.pi / 2) / (math.pi/2 - deg_30_in_rad)
            return percent * (-self.C_y(deg_30_in_rad) + 2 * PTy0)
        elif alpha < 0:
            return -self.C_y(-alpha) + 2 * PTy0

        cavity_pitch_adjust = 0
        # speed0
        angle_of_cavity = 0.28
        cavity_scale = 1.0 * 2 * angle_of_cavity / math.pi

        #speed2
        angle_of_cavity = 0.28
        cavity_scale = 0.8 * 2 * angle_of_cavity / math.pi

        #speed5
        angle_of_cavity = 0.28
        cavity_scale = 0.48 * 2 * angle_of_cavity / math.pi

        #speed7
        angle_of_cavity = 0.28
        cavity_scale = 0.4 * 2 * angle_of_cavity / math.pi

        #speed9
        angle_of_cavity = 0.28
        cavity_scale = 0.35 * 2 * angle_of_cavity / math.pi

        #speed11
        angle_of_cavity = 0.28
        cavity_scale = 0.3 * 2 * angle_of_cavity / math.pi

        #speed14
        angle_of_cavity = 0.28
        cavity_scale = 0.2 * 2 * angle_of_cavity / math.pi

        # angle_of_cavity = 3 * self.coefficients["cavity_volume"] / self.coefficients["rim_depth"] / self.diameter
        if alpha <= angle_of_cavity:
            cavity_pitch_adjust = -math.sin(math.pi * alpha / angle_of_cavity / 2) * PTya * cavity_scale
        else:
            cavity_pitch_adjust = -PTya * cavity_scale
        pitch = PTy0 + PTya * alpha
        if alpha <= 0.3:
            return pitch + cavity_pitch_adjust
        elif alpha <= Model.stall:
            # pitch doubles after about .3 rad
            # return pitch + PTya * (alpha - 0.3)
            return pitch + cavity_pitch_adjust
        elif alpha <= 80 * math.pi / 180:
            # after stall the pitch drops
            return self.C_y(15 * math.pi / 180)
        else:
            # last 10 degrees of drop down to 0 at 90 deg
            before_drop = self.C_y(15 * math.pi / 180)
            return ((math.pi / 2 - alpha) * 180 / math.pi) * before_drop / 10

    def C_side(self, aoa, v_norm, wz):
        """
        Side force caused by magnus forces at high advance rates.
        https://en.wikipedia.org/wiki/Magnus_effect

        advance ratio (AdvR) = wz * r / v

        # Magnus force for a cylinder of length L is approximately:
        F/L = p * v * 2 * pi * r^2 * wz

        L in this context is approximately the rim height

        side force coefficient is multiplied by the force magnitude which is
        .5 * p * v^2 * disc Area = .5 * p * pi * r^2 * v^2

        F = f_mag * rim_height * 4 * wz / v

        Args:
            aoa: angle of attack
            v_norm: velocity.norm()
            wz: rate of rotation in rads for the z axis
            f_amp: force amplitude

        Returns:

        """
        if aoa < Model.neg_stall or aoa > Model.stall:
            return 0
        if v_norm < 0.1:
            return 0
        rim_depth = self.coefficients["rim_depth"]
        rim_width = self.coefficients["rim_width"]
        inner_diam = (self.diameter - rim_width)
        adjust = inner_diam / self.diameter * inner_diam / self.diameter
        #return 4 * rim_depth * wz * adjust / v_norm

        #advR = (self.diameter - rim_width) / 2 * wz / v_norm
        #return math.copysign(0.1, wz) * advR * advR

        return 0
