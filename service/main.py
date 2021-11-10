import math
import os

from flask import Flask, request, jsonify

from frispy import Disc, Model

app = Flask(__name__)

@app.route('/api/flight_path', methods=['POST'])
def flight_path():
    content = request.json
    model = Model()
    a, nose_up, hyzer = res.x
    disc = Disc(model, {"vx": math.cos(a * math.pi / 180) * v, "dgamma": rot, "vz": math.sin(a * math.pi / 180) * v,
                        "nose_up": nose_up, "hyzer": hyzer})

    result = disc.compute_trajectory(15.0, None, **{"max_step": .2})


@app.route("/")
def hello_world():
    name = os.environ.get("NAME", "World")
    return "Hello auto {}!".format(name)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
