import math
import logging
import numpy as np
from typing import Dict, List, Optional

from scipy.integrate import solve_ivp
from scipy.spatial.transform import Rotation

from frispy.environment import Environment
from frispy.equations_of_motion import EOM
from frispy.model import Model


class FrisPyResults:
    """
    An object to hold the results of computing a trajectory
    """

    __slots__ = [
        "x",
        "y",
        "z",
        "vx",
        "vy",
        "vz",
        "qx",
        "qy",
        "qz",
        "qw",
        "dphi", # phi is rotation around X axis aka anhyzer for backhand
        "dtheta", # theta is rotation around Y aka nose_down
        "dgamma", # gamma is rotation around Z
        "phi",
        "theta",
        "gamma",
        "rot",
        "pos",
        "times",
        "v", # velocity vector [vx, vy, vz]
        "aoa",  # angle of attack
    ]

    def __str__(self):
        attr_values = {attr: getattr(self, attr, None) for attr in self.__slots__}
        return f"FrisPyResults({attr_values})"



class Disc:
    """Flying spinning disc object. The disc object contains only physical
    parameters of the disc and environment that it exists (e.g. gravitational
    acceleration and air density). Note that the default area, mass, and
    inertial moments are for Discraft Ultrastars (175 grams or 0.175 kg).

    All masses are kg, lengths are meters (m) and times are seconds (s). That
    is, these files all use `mks` units. Angular units use radians (rad), and
    angular velocities are in rad/s.

    Args:
      eom (EOM, optional): the equations of motion
      initial_conditions (Dict, optional): initial conditions of the disc in
        flight units are in in "mks" and angles are in radians. By defualt,
        the initial conditions will be that the disc is 1 meter off the
        ground (`z=1`), moving at 10 meters/sec in the `x` direction
        (`vx=10`) and is spinning about it's vertical axis at approximately
        10 revolutions per second (approx. 62 rad/sec, or `dgamma=62`).
        All other kinematic variables are set to 0. This configuration
        results in an angle of attack of 0.
    """

    def __init__(
        self,
        model: Optional[Model] = None,
        initial_conditions: Optional[Dict[str, float]] = None,
        environment: Environment = Environment(),
    ):
        self._model = model or Model()
        self._environment = environment
        self._eom = EOM(model=self._model, environment=self._environment)
        self.set_default_initial_conditions(initial_conditions)
        self.reset_initial_conditions()

    def compute_trajectory(self, flight_time: float = 7.0, **solver_kwargs) -> FrisPyResults:
        """Call the differential equation solver to compute
        the trajectory. The kinematic variables and timesteps are saved
        as the `current_trajectory` attribute, which is a dictionary,
        which is also returned by this function.

        See `these scipy docs <https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html#scipy.integrate.solve_ivp>`_
        for more information on the solver.

        .. todo::

           Type this correctly.

        .. warning::

           You cannot pass a `flight_time` if `t_span` is a key in
           `solver_args`.

        Args:
          flight_time (float, optional): time in seconds that the simulation
            will run over. Default is 3 seconds.
          solver_args (Dict[str, Any]): extra arguments to pass
            to the :meth:`scipy.integrate.solver_ivp` method used to solve
            the differential equation.
        """
        if "t_span" in solver_kwargs:
            assert (
                flight_time is None
            ), "cannot have t_span in solver_kwargs if flight_time is not None"
            t_span = solver_kwargs.pop("t_span")
        else:
            t_span = (0, flight_time)

        def hit_ground(t, y):
            z = y[2]
            vx = y[3]
            vy = y[4]
            vz = y[5]
            wz = y[12]
            if not self.environment.groundPlayEnabled:
                # ground play is disabled
                return z
            v_norm = np.linalg.norm([vx, vy, vz])
            # once the disc slows down to below 1mm/s, we end the simulation
            return v_norm - 0.001
            #return math.fabs(wz) + v_norm - 0.01
        hit_ground.terminal = True
        result = solve_ivp(
            fun=self.eom.compute_derivatives,
            t_span=t_span,
            y0=self.initial_conditions_as_ordered_list,
            events=hit_ground,
            **solver_kwargs,
        )

        try:
            # Create the results object
            fpr = FrisPyResults()
            fpr.times = result.t
            for i, key in enumerate(self.ordered_coordinate_names):
                setattr(fpr, key, result.y[i])
            n = len(result.t)
            pos = [None] * n
            rot = [None] * n
            phi = [None] * n
            theta = [None] * n
            gamma = [None] * n
            v = [None] * n
            aoa = [None] * n
            fpr.pos = pos
            fpr.rot = rot
            fpr.gamma = gamma
            fpr.phi = phi
            fpr.theta = theta
            fpr.v = v
            fpr.aoa = aoa
            gamma_sum = 0
            last_t = 0
            for i, t in enumerate(result.t):
                gamma_sum += fpr.dgamma[i] * (t - last_t)
                last_t = t
                gamma[i] = gamma_sum
                r: Rotation = Rotation.from_quat([fpr.qx[i], fpr.qy[i], fpr.qz[i], fpr.qw[i]])
                gamma_rot = Rotation.from_euler('Z', gamma_sum)
                r = r * gamma_rot
                rot[i] = r
                euler = r.as_euler('zyx')
                phi[i] = euler[2]
                theta[i] = euler[1]
                velocity = np.array([fpr.vx[i], fpr.vy[i], fpr.vz[i]])
                position = [fpr.x[i], fpr.y[i], fpr.z[i]]
                v[i] = velocity
                pos[i] = position
                angles = EOM.calculate_intermediate_quantities(r, velocity, [0, 0])
                aoa[i] = angles["angle_of_attack"]

            return fpr
        except Exception as e:
            logging.error("failed to parse results of ivp e: %s result: %s", e, result)
            raise

    def reset_initial_conditions(self) -> None:
        """
        Set the initial_conditions of the disc to the default and
        clear the trajectory.
        """
        self.initial_conditions = self.default_initial_conditions
        return

    def set_default_initial_conditions(
        self, initial_conditions: Optional[Dict[str, float]]
    ) -> None:
        base_ICs = {
            "x": 0,
            "y": 0,
            "z": 1.0,
            "vx": 25.0,
            "vy": 0,
            "vz": 0,
            "qx": 0,
            "qy": 0,
            "qz": 0,
            "qw": 1,
            "dphi": 0,
            "dtheta": 0,
            "dgamma": -120.0, # spin, negative is RHBH or clockwise from above
        }
        for i in base_ICs:
            if initial_conditions is not None and i in initial_conditions:
                base_ICs[i] = initial_conditions[i]

        anhyzer = 0
        if initial_conditions is not None and "hyzer" in initial_conditions:
            anhyzer = initial_conditions["hyzer"] * math.pi / 180 * math.copysign(1, initial_conditions["dgamma"])

        downhill = math.atan2(-base_ICs["vz"], base_ICs["vx"])
        nose_down = 0;
        if initial_conditions is not None and "nose_up" in initial_conditions:
            nose_down -= initial_conditions["nose_up"] * math.pi / 180

        rotation = Rotation.from_euler("YXY", [downhill, anhyzer, nose_down])

        # if initial_conditions is not None and "gamma" in initial_conditions:
        #     gamma = initial_conditions["gamma"]
        #     rotation = rotation * Rotation.from_euler("Z", gamma)
        quat = rotation.as_quat()
        base_ICs["qx"] = quat[0]
        base_ICs["qy"] = quat[1]
        base_ICs["qz"] = quat[2]
        base_ICs["qw"] = quat[3]
        self._default_initial_conditions = base_ICs

    @property
    def ordered_coordinate_names(self) -> List[str]:
        return [
            "x",
            "y",
            "z",
            "vx",
            "vy",
            "vz",
            "qx",
            "qy",
            "qz",
            "qw",
            "dphi",
            "dtheta",
            "dgamma",
        ]

    @property
    def default_initial_conditions(self) -> Dict[str, float]:
        return self._default_initial_conditions

    @property
    def initial_conditions_as_ordered_list(self) -> List:
        return [
            self.initial_conditions[key] for key in self.ordered_coordinate_names
        ]

    @property
    def environment(self) -> Environment:
        return self._eom.environment

    @property
    def eom(self) -> EOM:
        return self._eom

    @property
    def model(self) -> Model:
        return self._model

    @property
    def environment(self) -> Environment:
        return self._environment
