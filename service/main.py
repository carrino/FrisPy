import math
import os

from flask import Flask, request

from frispy import Disc, Discs

app = Flask(__name__)


@app.route('/api/flight_path', methods=['POST'])
def flight_path():
    content = request.json
    model = Discs.from_string(content['disc_name'])
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
                        "hyzer": hyzer,
                        "gamma": gamma,
                        })

    hz = abs(spin) / math.pi / 2
    # In order to get a smooth output for the rotation of the disc
    # we need to have enough samples to spin in the correct direction
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
        'gamma': result.gamma,
    }
    return res


@app.route("/")
def hello_world():
    return "Frispy service!"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
