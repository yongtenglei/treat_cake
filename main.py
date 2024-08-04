from decimal import getcontext

from flask import Flask, jsonify, request
from flask_cors import CORS

from algorithms.alex_aviad import alex_aviad
from algorithms.alex_aviad_result_helper import build_solution
from base_types import Segment
from type_helper import to_decimal

app = Flask(__name__)


# Allow all domains
# CORS(app)

# Allow specific domain
cors = CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})


@app.before_request
def set_decimal_precision():
    getcontext().prec = 15


@app.route("/alex_aviad", methods=["POST"])
def handle_alex_aviad():
    data = request.json
    preferences = [
        [
            Segment(
                id=segment["id"],
                start=to_decimal(segment["start"]),
                end=to_decimal(segment["end"]),
                start_value=to_decimal(segment["startValue"]),
                end_value=to_decimal(segment["endValue"]),
            )
            for segment in preference
        ]
        for preference in data["preferences"]
    ]
    cake_size = to_decimal(data["cake_size"])
    assert preferences and cake_size, "Should work"

    epsilon = to_decimal("1e-15")
    tolerance = to_decimal("1e-6")

    result = alex_aviad(
        preferences=preferences,
        cake_size=int(cake_size),
        epsilon=epsilon,
        tolerance=tolerance,
    )

    response = build_solution(
        preferences=preferences,
        cake_size=to_decimal(cake_size),
        epsilon=epsilon,
        result=result["solution"],
        steps=result["steps"],
    )

    print(f"{result=}")
    print("preferences", preferences)
    print("cake_size", cake_size)
    print(f"{response=}")

    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True, port=5000)
