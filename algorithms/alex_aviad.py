from decimal import Decimal
from typing import Any, Dict

from ..base_types import Preferences
from ..type_helper import to_decimal
from ..valuation import get_double_prime_for_interval
from .alex_aviad_condition.condition_a import check_condition_a
from .alex_aviad_condition.condition_b import check_condition_b
from .alex_aviad_hepler import equipartition
from .algorithm_test_utils import find_envy_free_allocation


def alex_aviad(
    preferences: Preferences,
    cake_size: int,
    epsilon: Decimal = 0.1,
    tolerance: Decimal = Decimal("1e-6"),
) -> Dict[str, Any]:
    assert len(preferences) == 4, "Need 4 agents here"

    solution = []
    steps = []

    # Find the equipartition by Agent1
    cuts = equipartition(
        preference=preferences[0],
        epsilon=epsilon,
        start=to_decimal(0),
        end=to_decimal(cake_size),
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
    meet_condition = "A"
    print(
        f"abs(alpha_overline - alpha_underline) = {abs(alpha_overline - alpha_underline)}\n (epsilon**4 / 12) = {(epsilon**4 / 12)}"
    )
    while abs(alpha_overline - alpha_underline) >= (epsilon**4 / 12):
        alpha = (alpha_underline + alpha_overline) / 2
        if check_condition_a(
            alpha=alpha,
            preferences=preferences,
            cake_size=cake_size,
            epsilon=epsilon,
            tolerance=tolerance,
        ):
            meet_condition = "A"
            alpha_underline = alpha
            info.append(f"meet A, alpha_underline:{alpha_underline} = {alpha}")
        elif check_condition_b(
            alpha=alpha,
            preferences=preferences,
            cake_size=cake_size,
            epsilon=epsilon,
            tolerance=tolerance,
        ):
            meet_condition = "B"
            alpha_underline = alpha
            info.append(f"meet B, alpha_underline:{alpha_underline} = {alpha}")
        else:
            alpha_overline = alpha
            info.append(f"Missed conditions, alpha_overline:{alpha_overline} = {alpha}")

    allocation = None
    if meet_condition == "A":
        allocation = find_allocation_on_condition_a()
    elif meet_condition == "B":
        allocation = find_allocation_on_condition_b()

    for i in info:
        print(i)

    return {"solution": allocation, "steps": steps}
