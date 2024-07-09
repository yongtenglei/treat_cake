from decimal import Decimal
from typing import Any, Dict

from cut import cut_slice_origin
from utils import make_percentage
from values import find_cut_line_by_percent, get_total_value
from .algorithm_types import make_step


def cut_and_choose(preferences, cake_size: int) -> Dict[str, Any]:
    if len(preferences) != 2:
        raise ValueError("Cut and choose only works with two agents")

    steps = []
    cut_point = find_cut_line_by_percent(preferences[0], 0.5)
    percent_cut = make_percentage(cut_point / cake_size, 3)
    steps.append(make_step(0, f"judges the middle of the resource to be {percent_cut}"))

    slice1 = cut_slice_origin(preferences, Decimal(0), cut_point, 1)
    slice2 = cut_slice_origin(preferences, cut_point, Decimal(cake_size), 2)
    steps.append(
        make_step(
            0, f"cut the resource into two pieces at {percent_cut}", [slice1, slice2]
        )
    )

    agent1_total_value = get_total_value(preferences[1])
    if slice1.values[1] >= slice2.values[1]:
        percent_value = make_percentage(slice1.values[1] / agent1_total_value, 3)
        steps.append(
            make_step(
                1,
                f"chooses piece 1 because it is worth {percent_value} of the resource to them",
                [slice1],
                True,
            )
        )
        steps.append(make_step(0, "takes remaining piece", [slice2], True))
        solution = [slice1.assign(1), slice2.assign(0)]
    else:
        percent_value = make_percentage(slice2.values[1] / agent1_total_value, 3)
        steps.append(
            make_step(
                1,
                f"chooses piece 2 because it is worth {percent_value} of the resource to them",
                [slice2],
                True,
            )
        )
        steps.append(make_step(0, "takes remaining piece", [slice1], True))
        solution = [slice1.assign(0), slice2.assign(1)]

    return {"solution": solution, "steps": steps}
