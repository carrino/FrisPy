import json
import math
import os
import logging
from pprint import pprint

import numpy as np
from flask import Flask, request
from frispy import Disc, Discs, Environment
from frispy.wind import ConstantWind
from flask_cors import CORS
from flask_sock import Sock
from frispy.disc import FrisPyResults

# import google.cloud.logging
# client = google.cloud.logging.Client()
# client.setup_logging()

app = Flask(__name__)
CORS(app)
sock = Sock(app)

@sock.route('/api/ws/flight_path')
def echo(sock):
    input = sock.receive()

    # parse string input as json
    content = json.loads(input)
    content['flight_max_seconds'] = 1
    gamma = content.get('gamma', 0)
    resultsAndDisc = flight_path_helper(content)
    results = resultsAndDisc[0]
    disc = resultsAndDisc[1]
    sock.send(to_result(gamma, results))
    disc.set_initial_conditions_from_prev_results(results)
    while results.z[-1] > 0.0001:
        endTime = results.times[-1]
        results = disc.compute_trajectory(t_span=(endTime, endTime + 1))
        sock.send(to_result(gamma, results))
        disc.set_initial_conditions_from_prev_results(results)

    sock.close()


# same as flight_path, but with multiple discs
@app.route('/api/flight_paths', methods=['POST'])
def flight_paths():
    content = request.json
    discs = content.get('disc_names')
    res = {}
    if discs:
        for disc in discs:
            content['disc_name'] = disc
            fpr = flight_path_helper(content)
            res[disc] = to_result(content.get('gamma', 0), fpr[0])
    else:
        discs = content.get('disc_numbers')
        for index, disc in enumerate(discs):
            content['flight_numbers'] = disc
            fpr = flight_path_helper(content)
            res[index] = to_result(content.get('gamma', 0), fpr[0])

    return res


# this method assumes the disc velocity is in the X direction.
# This library uses Z as up so Y points to the left (if X is straight ahead)
# This does not handle rotation of the disc in the resulting quaternion
# but a gamma param is sent to rotate after.
# units are all in SI units. m, m/s, rad/s, unless noted in the name.
@app.route('/api/flight_path', methods=['POST'])
def flight_path():
    content = request.json
    return flight_path_helper(content)[0]


def flight_path_helper(content) -> [FrisPyResults, Disc]:
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
        return [disc.compute_trajectory(flight_max_seconds, **{"max_step": max_step, "rtol": 5e-4, "atol": 1e-7}), disc]
    except Exception as e:
        logging.error("failed to process flight e: %s, content: %s, result: %s", e, content, result)

        # add retry on exception
        return [disc.compute_trajectory(flight_max_seconds, **{"max_step": max_step, "rtol": 5e-4, "atol": 1e-7}), disc]


def to_result(gamma, result):
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


@app.route("/")
def hello_world():
    return "Frispy service!"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
