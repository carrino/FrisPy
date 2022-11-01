import math
import os

from flask import Flask, request
from frispy import Disc, Discs
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# same as flight_path, but with multiple discs
@app.route('/api/flight_paths', methods=['POST'])
def flight_paths():
    content = request.json
    discs = content.get('disc_names')
    res = {}
    if discs:
        for disc in discs:
            content['disc_name'] = disc
            res[disc] = flight_path_helper(content)
    else:
        discs = content.get('disc_numbers')
        for index, disc in enumerate(discs):
            content['flight_numbers'] = disc
            res[index] = flight_path_helper(content)

    return res


# this method assumes the disc velocity is in the X direction.
# This library uses Z as up so Y points to the left (if X is straight ahead)
# This does not handle rotation of the disc in the resulting quaternion
# but a gamma param is sent to rotate after.
# units are all in SI units. m, m/s, rad/s, unless noted in the name.
@app.route('/api/flight_path', methods=['POST'])
def flight_path():
    content = request.json
    return flight_path_helper(content)


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

    a = content['uphill_degrees'] * math.pi / 180
    hyzer = content['hyzer_degrees']
    nose_up = content['nose_up_degrees']
    disc = Disc(model, {"vx": math.cos(a) * v,
                        "dgamma": spin,
                        "dphi": wx,
                        "dtheta": wy,
                        "vz": math.sin(a) * v,
                        "z": z,
                        "nose_up": nose_up,
                        "hyzer": hyzer
    })

    hz = abs(spin) / math.pi / 2
    # In order to get a smooth output for the rotation of the disc
    # we need to have enough samples to spin in the correct direction
    max_step = 0.1
    if hz > 4.5:
      max_step = 0.45 / hz
    result = disc.compute_trajectory(30, **{"max_step": max_step, "rtol": 5e-4, "atol": 1e-7})
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
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
