import logging
from decimal import Decimal, getcontext
from typing import Any, Dict, List

from base_types import Preferences
from type_helper import to_decimal
from valuation import get_double_prime_for_interval

from .alex_aviad_condition.condition_a import (
    check_condition_a,
    find_allocation_on_condition_a,
)
from .alex_aviad_condition.condition_b import (
    check_condition_b,
    find_allocation_on_condition_b,
)
from .alex_aviad_hepler import equipartition
from .algorithm_test_utils import find_envy_free_allocation
from .algorithm_types import Step, make_step

getcontext().prec = 15


def alex_aviad(
    preferences: Preferences,
    cake_size: int,
    epsilon: Decimal = to_decimal("1e-15"),
    tolerance: Decimal = to_decimal("1e-10"),
) -> Dict[str, Any]:
    assert len(preferences) == 4, "Need 4 agents here"

    solution = []
    steps: List[Step] = []

    # Find the equipartition by Agent1
    cuts = equipartition(
        preference=preferences[0],
        cake_size=to_decimal(cake_size),
        epsilon=epsilon,
        start=to_decimal(0),
        end=to_decimal(cake_size),
        tolerance=tolerance,
    )
    solution = find_envy_free_allocation(
        cuts=cuts,
        num_agents=4,
        cake_size=to_decimal(cake_size),
        preferences=preferences,
        epsilon=epsilon,
    )
    if solution is not None:
        steps.append(
            make_step(
                0,
                f"Find equipartition by Agent 1, yieding an ε-envy-free allocation, where ε={epsilon}",
                pieces=solution,
            )
        )
        steps.append(
            make_step(
                0,
                f"Piece {solution[0].id} was assigned to Agent 1",
                pieces=[solution[0]],
                assign=True,
            )
        )
        steps.append(
            make_step(
                1,
                f"Piece {solution[1].id} was assigned to Agent 2",
                pieces=[solution[1]],
                assign=True,
            )
        )
        steps.append(
            make_step(
                2,
                f"Piece {solution[2].id} was assigned to Agent 3",
                pieces=[solution[2]],
                assign=True,
            )
        )
        steps.append(
            make_step(
                3,
                f"Piece {solution[3].id} was assigned to Agent 4",
                pieces=[solution[3]],
                assign=True,
            )
        )
        return {"solution": solution, "steps": steps}

    alpha_underline = get_double_prime_for_interval(
        segments=preferences[0],
        epsilon=epsilon,
        start=to_decimal(0),
        end=cuts[0],
        cake_size=to_decimal(cake_size),
    )

    # Should be 1, sometimes gets 1.00000000000000000001 due to precision problem
    # alpha_overline = to_decimal(1)
    alpha_overline = get_double_prime_for_interval(
        segments=preferences[0],
        epsilon=epsilon,
        start=to_decimal(0),
        end=to_decimal(cake_size),
        cake_size=to_decimal(cake_size),
    )
    assert (
        alpha_overline == 1
    ), f"Initial alpha_overline should be 1, got {alpha_overline}"

    info = []
    alpha = -1
    condition_info = {
        "A": {"cuts": [], "k": -1, "alpha_underline": -1},
        "B": {"cuts": [], "k": -1, "k_prime": -1, "alpha_underline": -1},
    }
    meet_condition = ""
    logging.info(
        f"abs(alpha_overline - alpha_underline) = {abs(alpha_overline - alpha_underline)}\n (epsilon**4 / 12) = {(epsilon**4 / 12)}"
    )
    counter = 0
    try:
        while (
            abs(alpha_overline - alpha_underline) > (epsilon**4 / 12) and counter <= 12
        ):
            alpha = (alpha_underline + alpha_overline) / 2
            logging.error(
                f"Iteration {counter}: alpha_overline = {alpha_overline}, alpha_underline = {alpha_underline}, {epsilon**4 / 12}, {alpha=}"
            )

            logging.warning(f"alpha = {alpha}, {alpha_overline=}, {alpha_underline=}")
            if to_decimal(0.25) <= alpha < Decimal("1") / Decimal("3"):
                logging.warning(
                    "**********************************************************"
                )
                logging.warning("Check Condition A")
                logging.warning(
                    "**********************************************************"
                )
                meet_a, condition_a_info = check_condition_a(
                    alpha=alpha,
                    preferences=preferences,
                    cake_size=to_decimal(cake_size),
                    epsilon=epsilon,
                    tolerance=tolerance,
                )
                if meet_a:
                    # assert "OHHHHH" == "", "GOODDDDD, meet conditon A"
                    meet_condition = "A"
                    condition_info["A"] = condition_a_info
                    condition_info["A"]["alpha_underline"] = alpha_underline
                    alpha_underline = alpha
                    info.append(
                        f"meet A, alpha_underline:{alpha_underline} = {alpha}\n\t{condition_info=}"
                    )
                    counter += 1
                    logging.warning("Meet Condition A")
                    continue

            if to_decimal(0.25) <= alpha < to_decimal(0.5):
                meet_b, condition_b_info = check_condition_b(
                    alpha=alpha,
                    preferences=preferences,
                    cake_size=to_decimal(cake_size),
                    epsilon=epsilon,
                    tolerance=tolerance,
                )
                if meet_b:
                    # assert "OHHHHH" == "", "GOODDDDD, meet conditon B"
                    meet_condition = "B"
                    condition_info["B"] = condition_b_info
                    condition_info["B"]["alpha_underline"] = alpha_underline
                    alpha_underline = alpha
                    info.append(
                        f"meet B, alpha_underline:{alpha_underline} = {alpha}\n\t{condition_info=}"
                    )
                    logging.warning("Meet Condition B")
                    counter += 1
                    continue

            alpha_overline = alpha
            info.append(
                f"Missed conditions, alpha_overline:{alpha_overline} = {alpha}\n\t{condition_info=}"
            )
            counter += 1
            logging.warning(f"Counter: {counter}")

        logging.warning("exit the main loop")
        allocation = None
        assert (
            len(meet_condition) != 0
        ), "At least one condition should be met when exit the loop"
        logging.warning(f"Finding Allocation on Condition {meet_condition}")
        if meet_condition == "A":
            assert (
                condition_info["A"]["cuts"] and condition_info["A"]["k"]
            ), "Should have necessary information of condition A to yied a final allocation"
            allocation = find_allocation_on_condition_a(
                preferences=preferences,
                alpha=condition_info["A"]["alpha_underline"],
                cake_size=to_decimal(cake_size),
                epsilon=epsilon,
                tolerance=tolerance,
            )
        elif meet_condition == "B":
            assert (
                condition_info["B"]["cuts"]
                and condition_info["B"]["k"]
                and condition_info["B"]["k_prime"]
            ), "Should have necessary information of condition B to yied a final allocation"
            allocation = find_allocation_on_condition_b(
                alpha=condition_info["B"]["alpha_underline"],
                cake_size=to_decimal(cake_size),
                epsilon=epsilon,
                preferences=preferences,
                tolerance=tolerance,
            )
        for i in info:
            logging.error(f"info: {i}")
        return {"solution": allocation, "steps": steps}
    except Exception as e:
        logging.error(f"error from algorithm: {e}")
        logging.error("exit")
