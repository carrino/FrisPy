import json
import math
import os
from pprint import pprint

from flask import Flask, request, jsonify

from frispy import Disc, Model, Discs

app = Flask(__name__)

@app.route('/api/flight_path', methods=['POST'])
def flight_path():
    content = request.json
    model = Discs.from_string(content['disc_name'])
    v = content['v']
    rot = content['rot']
    a = content['uphill_degrees'] * math.pi / 180
    hyzer = content['hyzer_degrees']
    nose_up = content['nose_up_degrees']
    disc = Disc(model, {"vx": math.cos(a) * v, "dgamma": -rot, "vz": math.sin(a) * v,
                        "nose_up": nose_up, "hyzer": hyzer})

    result = disc.compute_trajectory(15.0, **{"max_step": .2})
    return json.dumps(result)


@app.route("/")
def hello_world():
    name = os.environ.get("NAME", "World")
    return "Hello auto {}!".format(name)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
