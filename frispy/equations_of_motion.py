from pprint import pprint
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
            airVelocity: np.ndarray,
            velocity: np.ndarray,
            ang_velocity: np.ndarray,
            gamma: float = 0,
    ) -> Dict[str, Union[float, np.ndarray, Dict[str, np.ndarray]]]:
        """
        Compute the lift, drag, and gravitational forces on the disc.
        """
        res = EOM.calculate_intermediate_quantities(rotation, airVelocity, ang_velocity, gamma)
        aoa = res["angle_of_attack"]
        v_norm = np.linalg.norm(airVelocity)
        vhat = np.array([1, 0, 0])
        if v_norm > math.ulp(1):
            vhat = airVelocity / v_norm
        force_amplitude = (
                0.5
                * self.environment.air_density
                * (airVelocity @ airVelocity)
                * self.model.area
        )

        zhat = res["unit_vectors"]["zhat"]
        lift_direction = zhat - np.dot(zhat, vhat) * vhat
        if np.linalg.norm(lift_direction) > math.ulp(1):
            lift_direction /= np.linalg.norm(lift_direction)

        # Compute the lift and drag forces
        res["F_lift"] = (
                self.model.C_lift(aoa)
                * force_amplitude
                * lift_direction
        )
        wz = ang_velocity[2]
        res["F_side"] = (
                self.model.C_side(aoa, v_norm, wz)
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
            # TODO: Look up wing edge depth above/below center of mass
            closest_point_from_center += zhat * -0.003
        edge_position = position + closest_point_from_center

        # TODO: lookup ground height below edge_position, assume 0 for now
        ground_height = 0

        dist_from_ground = edge_position[2] - ground_height
        f_spring = np.array([0, 0, 0])
        f_ground_drag = np.array([0, 0, 0])
        zhat_dot_up = np.dot(zhat, up)
        f_ground_drag_fraction = 1
        if self.environment.groundPlayEnabled and dist_from_ground < 0:
            spring_multiplier = -dist_from_ground * 100 # 1g per mm
            ground_drag_constant = 0.5 # TODO: add a ground drag parameter to the environment
            f_normal = self.model.mass * spring_multiplier * self.environment.g
            f_spring = f_normal * up
            w = res["w"]
            edgeVelocity = np.cross(ang_velocity[2] * zhat, closest_point_from_center)
            #edgeVelocityHat = edgeVelocity / np.linalg.norm(edgeVelocity)

            discEdgeVelocity = velocity + edgeVelocity
            discEdgeDotUp = np.dot(discEdgeVelocity, up)
            discEdgeVelocityNormal = discEdgeVelocity - discEdgeDotUp * up
            # drag_direction = -velocity
            # norm_v = np.linalg.norm(velocity)
            # norm_edge = np.linalg.norm(discEdgeVelocity)
            # if norm_v > norm_edge:
            #     drag_direction = -discEdgeVelocity
            #     f_ground_drag_fraction *= norm_edge / norm_v
            drag_direction = -discEdgeVelocity

            if np.linalg.norm(drag_direction) > 1:
                drag_direction /= np.linalg.norm(drag_direction)

            f_ground_drag = f_normal * ground_drag_constant * drag_direction
            if np.linalg.norm(discEdgeVelocityNormal) < 0.25:
                # this means we are rolling, replace the drag with a rolling friction
                # rolling friction in the direction of rolling and static friction in the direction of the normal
                spinningEnergy = 0.5 * np.dot(w, w) * self.model.I_zz
                translationalEnergy = 0.5 * np.dot(velocity, velocity) * self.model.mass
                #f_ground_drag *= 2
                # change rolling friction to apply to the center of mass and update the wz to match the rolling rate
        res["F_ground_spring"] = f_spring
        res["F_ground_drag"] = f_ground_drag
        res["F_ground"] = f_spring + f_ground_drag * f_ground_drag_fraction
        res["ground_normal"] = up
        res["contact_point_from_center"] = closest_point_from_center

        res["F_total"] = res["F_lift"] + res["F_drag"] + res["F_grav"] + res["F_side"] + f_spring + f_ground_drag
        res["Acc"] = res["F_total"] / self.model.mass
        return res

    def compute_torques(
            self,
            airVelocity: np.ndarray,
            ang_velocity: np.ndarray,
            rotation: Rotation,
            res: Dict[str, Union[float, np.ndarray, Dict[str, np.ndarray]]],
    ) -> Dict[str, Union[float, np.ndarray, Dict[str, np.ndarray]]]:
        """
        Compute the turn, gyroscopic precession, and wobble damping
        """

        aoa = res["angle_of_attack"]
        res["torque_amplitude"] = (
                0.5
                * self.environment.air_density
                * (airVelocity @ airVelocity)
                * self.model.diameter
                * self.model.area
        )

        i_xx = self.model.I_xx
        i_zz = self.model.I_zz
        torque = res["torque_amplitude"]
        wz = ang_velocity[2]
        v_norm = np.linalg.norm(airVelocity)


        w = res["w_xy"]
        xhat = res["unit_vectors"]["xhat"]
        yhat = res["unit_vectors"]["yhat"]
        fhat = res["unit_vectors"]["fhat"]
        lhat = res["unit_vectors"]["lhat"]

        # if np.linalg.norm(wz) > 2 * np.linalg.norm(w):
        #     ground_torque = np.cross(res["contact_point_from_center"], res["F_ground"])
        #     torque_x = np.dot(ground_torque, xhat) * yhat  # NB: x torque produces y angular velocity
        #     torque_y = np.dot(ground_torque, yhat) * -xhat  # NB: y torque produces -x angular velocity
        #     w += (torque_x + torque_y) / (i_zz * wz)
        #
        #     pitching_moment = self.model.C_y(aoa) * res["torque_amplitude"]
        #     roll = pitching_moment * fhat
        #     w += roll / (i_zz * wz)

        w_norm = np.linalg.norm(w)
        if w_norm < math.ulp(1.0):
            wquat = Rotation.from_quat([0, 0, 0, 1])
        else:
            # https://www.euclideanspace.com/physics/kinematics/angularvelocity/QuaternionDifferentiation2.pdf
            wquat = Rotation.from_quat([w[0]/w_norm, w[1]/w_norm, w[2]/w_norm, 0]) * rotation
        res["dq"] = wquat.as_quat() * w_norm / 2

        self.compute_angular_acc(ang_velocity, res, aoa, v_norm)
        return res

    def compute_angular_acc(
            self,
            ang_velocity: np.ndarray,
            res: Dict[str, Union[float, np.ndarray, Dict[str, np.ndarray]]],
            aoa: float,
            v_norm: float):
        """
        Compute the wobble precession, spindown, and wobble damping
        """
        i_xx = self.model.I_xx
        i_zz = self.model.I_zz
        wx, wy, wz = ang_velocity

        # Damp angular velocity
        damping = self.model.dampening_factor # wobble damping
        damping_z = self.model.dampening_z # spindown


        acc = np.array([0.0, 0.0, 0.0])

        # add damping due to air
        acc += np.array([wx * damping / i_xx, wy * damping / i_xx, wz * damping_z / i_zz]) * res["torque_amplitude"]

        #add damping from ground
        if np.linalg.norm(res["F_ground"]) > 0:
            acc += np.array([0, 0, -wz * 0.1])

        plastic_damp = 0.0 # 10% per second
        # add damping due to plastic deformation
        acc += np.array([-wx * plastic_damp, -wy * plastic_damp, 0])

        # use eulers rigid body equations to compute precession of angular velocity
        acc += np.array([wy * wz * (1-plastic_damp) * (i_xx - i_zz) / i_xx, wx * wz * (1-plastic_damp) * (i_zz - i_xx) / i_xx, 0])

        xhat = res["unit_vectors"]["xhat"]
        yhat = res["unit_vectors"]["yhat"]
        zhat = res["unit_vectors"]["zhat"]
        vhat = res["unit_vectors"]["vhat"]
        lhat = res["unit_vectors"]["lhat"]

        ground_torque = np.cross(res["contact_point_from_center"], res["F_ground"])

        acc += np.array([0, 0, np.dot(ground_torque, zhat) / i_zz])
        # if np.linalg.norm(wz) <= 2 * np.linalg.norm(res["w_xy"]):
        acc += np.array([np.dot(ground_torque, xhat) / i_xx, np.dot(ground_torque, yhat) / i_xx, 0])
        pitching_moment = self.model.C_y(aoa) * res["torque_amplitude"]
        pitching_torque = -pitching_moment * lhat
        acc += np.array([np.dot(pitching_torque, xhat) / i_xx, np.dot(pitching_torque, yhat) / i_xx, 0])

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
        x, y, z, vx, vy, vz, qx, qy, qz, qw, dphi, dtheta, dgamma, gamma = coordinates
        position = np.array([x, y, z])
        wind = self.environment.wind
        windVector = wind.get_wind_vector(time, position)
        velocity = np.array([vx, vy, vz])
        airVelocity = velocity - windVector
        rotation: Rotation = Rotation.from_quat([qx, qy, qz, qw])
        # angular velocity is defined relative to the disc
        ang_velocity = np.array([dphi, dtheta, dgamma])
        result = self.compute_forces(position, rotation, airVelocity, velocity, ang_velocity, gamma)
        result = self.compute_torques(airVelocity, ang_velocity, rotation, result)
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
                result["T"][2],  # spin component of ang. acc.
                dgamma,
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
            airVelocity: np.ndarray,
            ang_velocity: np.ndarray,
            gamma: float = 0,
    ) -> Dict[str, Union[float, np.ndarray, Dict[str, np.ndarray]]]:
        """
        Compute intermediate quantities on the way to computing the time
        derivatives of the kinematic variables.
        """
        # Rotation matrix
        R = rotation.as_matrix()
        # Unit vectors
        zhat = R @ np.array([0, 0, 1])
        v_dot_zhat = airVelocity @ zhat
        v_in_plane = airVelocity - zhat * v_dot_zhat

        vhat = airVelocity
        if np.linalg.norm(airVelocity) > math.ulp(1.0):
            vhat = airVelocity / np.linalg.norm(airVelocity)

        fhat = vhat
        angle_of_attack = 0
        if np.linalg.norm(v_in_plane) > math.ulp(1.0):
            fhat = v_in_plane / np.linalg.norm(v_in_plane)
            angle_of_attack = -np.arctan(v_dot_zhat / np.linalg.norm(v_in_plane))

        xhat = R @ np.array([1, 0, 0])
        yhat = R @ np.array([0, 1, 0])
        lhat = np.cross(zhat, fhat)

        # rotate xhat and yhat around zhat by gamma
        R_gamma = Rotation.from_rotvec(zhat * gamma)
        xhat = R_gamma.apply(xhat)
        yhat = R_gamma.apply(yhat)

        # wobble is only the in x and y axis relative to zhat
        w_xy = ang_velocity[0] * xhat + ang_velocity[1] * yhat
        w = w_xy + ang_velocity[2] * zhat
        return {
            # zhat points toward the top of the flight plate
            # xhat is where the original leading edge of the disc is now pointing
            # yhat is perpendicular to zhat and xhat, it lies on the flight plate plane
            # fhat is the edge of the disc that is leading in the direction of travel
            # lhat is the edge of the disc that is to the left in the direction of travel
            "unit_vectors": {"xhat": xhat, "yhat": yhat, "zhat": zhat, "vhat": vhat, "lhat": lhat, "fhat": fhat },
            "angle_of_attack": angle_of_attack,
            "w_xy": w_xy,
            "w": w,
        }
