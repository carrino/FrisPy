from spin_sdk.http import IncomingHandler, Request, Response
import json
from pprint import pprint
from frispy import Disc, Discs, Environment
from frispy.wind import ConstantWind
import numpy as np

class IncomingHandler(IncomingHandler):
    def handle_request(self, request: Request) -> Response:
        body_content = json.loads(request.body.decode('utf-8'))
        pprint(body_content)
        self.flight_path_helper(body_content)
        return Response(
            200,
            {"content-type": "application/json"},
            bytes("Hello from Python!", "utf-8")
        )

    def flight_path_helper(content):
        model = Discs.from_string(content.get('disc_name'))
        if not model:
            model = Discs.from_flight_numbers(content['flight_numbers'])
        v = content['v']
        spin = content['spin']
        wx = 0
        if "wx" in content:
            wx = content["wx"]
    
        wy = 0
        if "wy" in content:
            wy = content["wy"]
        z = 1
        if "z" in content:
            z = content["z"]
    
        gamma = 0
        if "gamma" in content:
            gamma = content["gamma"]
    
        flight_max_seconds: float = 15.0
        if "flight_max_seconds" in content:
            flight_max_seconds = min(content["flight_max_seconds"], flight_max_seconds)
    
        # m/s
        wind_speed = 0
        if "wind_speed" in content:
            wind_speed = content["wind_speed"]
    
        # 0 wind angle means tail wind, 90 deg is right to left
        # radians
        wind_angle = 0
        if "wind_angle" in content:
            wind_angle = content["wind_angle"]
    
        wind = ConstantWind(np.array([math.cos(wind_angle), math.sin(wind_angle), 0]) * wind_speed)
    
        # measured in kg/m^3
        air_density = 1.225  # 15C / 59F
        if "air_density" in content:
            air_density = content["air_density"]
    
        a = content['uphill_degrees'] * math.pi / 180
        hyzer = content['hyzer_degrees']
        nose_up = content['nose_up_degrees']
        disc = Disc(model,
                    {"vx": math.cos(a) * v,
                            "dgamma": spin,
                            "dphi": wx,
                            "dtheta": wy,
                            "vz": math.sin(a) * v,
                            "z": z,
                            "nose_up": nose_up,
                            "hyzer": hyzer
                    },
                    environment=Environment(wind=wind, air_density=air_density))
    
        hz = abs(spin) / math.pi / 2
        # In order to get a smooth output for the rotation of the disc
        # we need to have enough samples to spin in the correct direction
        max_step = 0.1
        if hz > 4.5:
            max_step = 0.45 / hz
        result = None
        try:
            result = disc.compute_trajectory(flight_max_seconds, **{"max_step": max_step, "rtol": 5e-4, "atol": 1e-7})
            res = {
                'p': result.pos,
                't': [i.tolist() for i in result.times],
                'v': [i.tolist() for i in result.v],
                'qx': result.qx.tolist(),
                'qy': result.qy.tolist(),
                'qz': result.qz.tolist(),
                'qw': result.qw.tolist(),
                'gamma': [i + gamma for i in result.gamma],
            }
            return res
        except Exception as e:
            logging.error("failed to process flight e: %s, content: %s, result: %s", e, content, result)
            raise
