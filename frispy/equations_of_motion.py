from typing import Dict, Union

import numpy as np
import math

from frispy.environment import Environment
from frispy.model import Model
from scipy.spatial.transform import Rotation


class EOM:
    """
    ``EOM`` is short for "equations of motion" is used to run the ODE solver
    from `scipy`. It takes in a model for the disc, the trajectory object,
    the environment, and implements the functions for calculating forces
    and torques.
    """

    def __init__(
            self,
            environment: Environment = Environment(),
            model: Model = Model(),
    ):
        self._environment = environment
        self._model = model

    @property
    def environment(self) -> Environment:
        return self._environment

    @property
    def model(self) -> Model:
        return self._model

    def compute_forces(
            self,
            position: np.ndarray,
            rotation: Rotation,
            velocity: np.ndarray,
            ang_velocity: np.ndarray,
    ) -> Dict[str, Union[float, np.ndarray, Dict[str, np.ndarray]]]:
        """
        Compute the lift, drag, and gravitational forces on the disc.
        """
        res = EOM.calculate_intermediate_quantities(rotation, velocity, ang_velocity)
        aoa = res["angle_of_attack"]
        v_norm = np.linalg.norm(velocity)
        vhat = np.array([1, 0, 0])
        if v_norm > math.ulp(1):
            vhat = velocity / v_norm
        force_amplitude = (
                0.5
                * self.environment.air_density
                * (velocity @ velocity)
                * self.model.area
        )
        # Compute the lift and drag forces
        res["F_lift"] = (
                self.model.C_lift(aoa)
                * force_amplitude
                * np.cross(vhat, res["unit_vectors"]["yhat"])
        )
        res["F_side"] = (
                self.model.C_side(aoa, v_norm, ang_velocity[2])
                * force_amplitude
                * res["unit_vectors"]["yhat"]
        )
        res["F_drag"] = self.model.C_drag(aoa) * force_amplitude * (-vhat)
        # Compute gravitational force
        res["F_grav"] = (
                self.model.mass
                * self.environment.g
                * self.environment.grav_vector
        )

        # TODO: Look up ground normal below the disc position, assume level ground for now
        up = np.array([0, 0, 1])
        zhat = res["unit_vectors"]["zhat"]

        ground_minus_zhat = up - zhat * np.dot(zhat, up)
        closest_point_from_center = np.array([0, 0, 0])
        if np.linalg.norm(ground_minus_zhat) > math.ulp(1):
            ground_minus_zhat *= -1
            closest_point_from_center = ground_minus_zhat / np.linalg.norm(ground_minus_zhat)
            closest_point_from_center *= self.model.diameter / 2
        edge_position = position + closest_point_from_center

        # TODO: lookup ground height below edge_position, assume 0 for now
        ground_height = 0

        dist_from_ground = edge_position[2] - ground_height
        f_spring = np.array([0, 0, 0])
        f_ground_drag = np.array([0, 0, 0])
        if self.environment.groundPlayEnabled and dist_from_ground < 0:
            spring_multiplier = -dist_from_ground * 1000 # 1g per mm
            ground_drag_constant = 0.5 # TODO: add a ground drag constant to the environment
            f_normal = self.model.mass * spring_multiplier * self.environment.g
            f_spring = f_normal * up
            # TODO: reduce drag to use static_friction coefficient if the disc is rolling
            f_ground_drag = -f_normal * ground_drag_constant * vhat
        res["F_ground_spring"] = f_spring
        res["F_ground_drag"] = f_ground_drag
        res["F_ground"] = f_spring + f_ground_drag
        res["ground_normal"] = up
        res["contact_point_from_center"] = closest_point_from_center

        res["F_total"] = res["F_lift"] + res["F_drag"] + res["F_grav"] + res["F_side"] + f_spring + f_ground_drag
        res["Acc"] = res["F_total"] / self.model.mass
        return res

    def compute_torques(
            self,
            velocity: np.ndarray,
            ang_velocity: np.ndarray,
            rotation: Rotation,
            res: Dict[str, Union[float, np.ndarray, Dict[str, np.ndarray]]],
    ) -> Dict[str, Union[float, np.ndarray, Dict[str, np.ndarray]]]:
        """
        Compute the turn, gyroscopic precession, and wobble dampening
        """

        aoa = res["angle_of_attack"]
        res["torque_amplitude"] = (
                0.5
                * self.environment.air_density
                * (velocity @ velocity)
                * self.model.diameter
                * self.model.area
        )

        i_xx = self.model.I_xx
        i_zz = self.model.I_zz
        torque = res["torque_amplitude"]
        wz = ang_velocity[2]
        v_norm = np.linalg.norm(velocity)


        w = res["w"]
        if abs(wz) > np.linalg.norm(w):
            # Turn is created by the pitching moment
            # We just modify angular velocity directly and pass it to the quaternion derivative
            pitching_moment = self.model.C_y(aoa)
            rolling_moment = self.model.C_x(aoa, v_norm, wz)
            roll = pitching_moment * torque * res["unit_vectors"]["xhat"]
            pitch_up = rolling_moment * torque * -res["unit_vectors"]["yhat"]
            w += (roll + pitch_up) / (i_zz * wz)

        # handle ground torque using gyroscopic precession
        # the zhat direction will produce spindown or spinup
        zhat = res["unit_vectors"]["zhat"]
        torque = np.cross(res["contact_point_from_center"], res["F_ground"])
        torque_zhat = zhat * np.dot(torque, zhat)
        torque_xy = torque - torque_zhat
        if np.linalg.norm(torque_xy) > math.ulp(1):
            #torque_xy = Rotation.from_rotvec(np.array([0, 0, 1]) * np.sign(wz) * math.pi / 2) * torque_xy
            #torque_xy = Rotation.from_euler('Z', math.pi/2 * np.sign(wz)) @ torque_xy
            #rotate torque_xy 90 deg depending on the direction of the spin
            torque_xy = np.array([torque_xy[1] * np.sign(wz), -torque_xy[0] * np.sign(wz), torque_xy[2]])
            w += torque_xy / (i_zz * wz)

        w_norm = np.linalg.norm(w)
        if w_norm < math.ulp(1.0):
            wquat = Rotation.from_quat([0, 0, 0, 0])
        else:
            # https://www.euclideanspace.com/physics/kinematics/angularvelocity/QuaternionDifferentiation2.pdf
            wquat = Rotation.from_quat([w[0]/w_norm, w[1]/w_norm, w[2]/w_norm, 0]) * rotation
        res["dq"] = wquat.as_quat() * w_norm / 2

        self.compute_angular_acc(ang_velocity, torque, res, aoa, v_norm)
        return res

    def compute_angular_acc(
            self,
            ang_velocity: np.ndarray,
            torque: float,
            res: Dict[str, Union[float, np.ndarray, Dict[str, np.ndarray]]],
            aoa: float,
            v_norm: float):
        """
        Compute the wobble precession, spindown, and wobble damping
        """
        i_xx = self.model.I_xx
        i_zz = self.model.I_zz
        wx, wy, wz = ang_velocity

        # Dampen angular velocity
        dampening = self.model.dampening_factor # wobble dampening
        dampening_z = self.model.dampening_z # spindown
        acc = np.array([wx * dampening / i_xx, wy * dampening / i_xx, wz * dampening_z / i_zz]) * torque

        wobble = res["w"]
        if abs(wz) > np.linalg.norm(wobble):
            # Handle wobble by precession of angular velocity. Torque is handled as presession of Q, not angular acc.
            delta_moment = self.model.I_zz - self.model.I_xx
            acc += delta_moment / i_xx * 2 * wz * np.array([-wy, wx, 0])
        else:
            pitching_moment = self.model.C_y(aoa)
            rolling_moment = self.model.C_x(aoa, v_norm, wz)
            acc += np.array([rolling_moment, pitching_moment, 0]) * torque / i_xx

        res["T"] = acc

    def compute_derivatives(
            self, time: float, coordinates: np.ndarray
    ) -> np.ndarray:
        """
        Right hand side of the ordinary differential equations. This is
        supplied to :meth:`scipy.integrate.solve_ivp`. See `this page
        <https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html#scipy.integrate.solve_ivp>`_
        for more information about its `fun` argument.

        Args:
          time (float): instantanious time of the system
          coordinates (np.ndarray): kinematic variables of the disc

        Returns:
          derivatives of all coordinates
        """
        x, y, z, vx, vy, vz, qx, qy, qz, qw, dphi, dtheta, dgamma = coordinates
        position = np.array([x, y, z])
        wind = self.environment.wind
        windVector = wind.get_wind_vector(time, position)
        velocity = np.array([vx, vy, vz])
        velocity -= windVector
        rotation: Rotation = Rotation.from_quat([qx, qy, qz, qw])
        # angular velocity is defined relative to the disc
        ang_velocity = np.array([dphi, dtheta, dgamma])
        result = self.compute_forces(position, rotation, velocity, ang_velocity)
        result = self.compute_torques(velocity, ang_velocity, rotation, result)
        derivatives = np.array(
            [
                vx,
                vy,
                vz,
                result["Acc"][0],  # x component of acceleration
                result["Acc"][1],  # y component of acceleration
                result["Acc"][2],  # z component of acceleration
                result["dq"][0],
                result["dq"][1],
                result["dq"][2],
                result["dq"][3],
                result["T"][0],  # x component of ang. acc.
                result["T"][1],  # y component of ang. acc.
                result["T"][2],  # gamma component of ang. acc. (only a dammpening factor)
            ]
        )
        return derivatives

    @staticmethod
    def expand_quaternion(qx: float, qy: float, qz: float, qw: float) -> Rotation:
        vector = np.array([qx, qy, qz, qw])
        return Rotation.from_quat(vector)

    @staticmethod
    def calculate_intermediate_quantities(
            rotation: Rotation,
            velocity: np.ndarray,
            ang_velocity: np.ndarray,
    ) -> Dict[str, Union[float, np.ndarray, Dict[str, np.ndarray]]]:
        """
        Compute intermediate quantities on the way to computing the time
        derivatives of the kinematic variables.
        """
        # Rotation matrix
        R = rotation.as_matrix()
        # Unit vectors
        zhat = R @ np.array([0, 0, 1])
        v_dot_zhat = velocity @ zhat
        v_in_plane = velocity - zhat * v_dot_zhat

        xhat = np.array([1, 0, 0])
        angle_of_attack = 0
        if np.linalg.norm(v_in_plane) > math.ulp(1.0):
            xhat = v_in_plane / np.linalg.norm(v_in_plane)
            angle_of_attack = -np.arctan(v_dot_zhat / np.linalg.norm(v_in_plane))
        yhat = np.cross(zhat, xhat)

        # wobble is only the in x and y axis relative to zhat
        w = R @ np.array([ang_velocity[0], ang_velocity[1], 0])
        return {
            "unit_vectors": {"xhat": xhat, "yhat": yhat, "zhat": zhat},
            "angle_of_attack": angle_of_attack,
            "w": w,
        }
