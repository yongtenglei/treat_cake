from decimal import Decimal
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
from .algorithm_types import Step


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
        epsilon=epsilon,
        start=to_decimal(0),
        end=to_decimal(cake_size),
        tolerance=tolerance,
    )
    solution = find_envy_free_allocation(
        cuts=cuts,
        num_agents=4,
        cake_size=cake_size,
        preferences=preferences,
        epsilon=epsilon,
    )
    if solution is not None:
        return {"solution": solution, "steps": steps}

    alpha_underline = get_double_prime_for_interval(
        segments=preferences[0], epsilon=epsilon, start=to_decimal(0), end=cuts[0]
    )
    alpha_overline = get_double_prime_for_interval(
        segments=preferences[0],
        epsilon=epsilon,
        start=to_decimal(0),
        end=to_decimal(cake_size),
    )

    info = []
    alpha = -1
    condition_info = {
        "A": {"cuts": [], "k": -1},
        "B": {"cuts": [], "k": -1, "k_prime": -1},
    }
    meet_condition = "A"
    print(
        f"abs(alpha_overline - alpha_underline) = {abs(alpha_overline - alpha_underline)}\n (epsilon**4 / 12) = {(epsilon**4 / 12)}"
    )
    while abs(alpha_overline - alpha_underline) >= (epsilon**4 / 12):
        alpha = (alpha_underline + alpha_overline) / 2
        meet_a, condition_a_info = check_condition_a(
            alpha=alpha,
            preferences=preferences,
            cake_size=cake_size,
            epsilon=epsilon,
            tolerance=tolerance,
        )
        if meet_a:
            meet_condition = "A"
            alpha_underline = alpha
            condition_info["A"] = condition_a_info
            info.append(
                f"meet A, alpha_underline:{alpha_underline} = {alpha}\n\t{condition_info=}"
            )
            continue

        meet_b, condition_b_info = check_condition_b(
            alpha=alpha,
            preferences=preferences,
            cake_size=cake_size,
            epsilon=epsilon,
            tolerance=tolerance,
        )
        if meet_b:
            meet_condition = "B"
            alpha_underline = alpha
            condition_info["B"] = condition_b_info
            info.append(
                f"meet B, alpha_underline:{alpha_underline} = {alpha}\n\t{condition_info=}"
            )
            continue

        alpha_overline = alpha
        info.append(
            f"Missed conditions, alpha_overline:{alpha_overline} = {alpha}\n\t{condition_info=}"
        )

    allocation = None
    if meet_condition == "A":
        assert condition_info["A"]["cuts"] and condition_info["A"]["k"], "Should work"
        allocation = find_allocation_on_condition_a(
            preferences=preferences,
            cuts=condition_info["A"]["cuts"],
            episilon=epsilon,
            k=condition_info["A"]["k"],
        )
    elif meet_condition == "B":
        assert (
            condition_info["B"]["cuts"]
            and condition_info["B"]["k"]
            and condition_info["B"]["k_prime"]
        ), "Should work"
        allocation = find_allocation_on_condition_b(
            cuts=condition_info["B"]["cuts"],
            episilon=epsilon,
            k=condition_info["B"]["k"],
            k_prime=condition_info["B"]["k_prime"],
            preferences=preferences,
        )

    for i in info:
        print(i)

    return {"solution": allocation, "steps": steps}
