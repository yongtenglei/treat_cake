from decimal import Decimal
from typing import Dict, Any
from typing import List

from .algorithm_test_utils import (
    find_envy_free_allocation,
)
from .alex_aviad_hepler import (
    check_condition_a,
    check_condition_b,
    find_allocation_on_condition_a,
    find_allocation_on_condition_b,
    _binary_search_left_to_right,
)
from ..base_types import Segment, Preferences
from ..type_helper import to_decimal
from ..valuation import get_double_prime_for_interval


def equipartition(
    preference: List[Segment], epsilon: Decimal, start: Decimal, end: Decimal
) -> List[Decimal]:
    epsilon = Decimal(epsilon)
    start = Decimal(start)
    end = Decimal(end)

    total_v = get_double_prime_for_interval(
        segments=preference, epsilon=epsilon, start=start, end=end
    )
    segment_value = total_v / 4

    # Finding cuts at 1/4, 1/2, and 3/4 of the cake
    first_cut = _binary_search_left_to_right(
        preference=preference,
        epsilon=epsilon,
        start=start,
        end=end,
        target=segment_value,
    )
    second_cut = _binary_search_left_to_right(
        preference=preference,
        epsilon=epsilon,
        start=first_cut,
        end=end,
        target=segment_value,
    )
    third_cut = _binary_search_left_to_right(
        preference=preference,
        epsilon=epsilon,
        start=second_cut,
        end=end,
        target=segment_value,
    )

    return [first_cut, second_cut, third_cut]


def alex_aviad(
    preferences: Preferences, cake_size: int, epsilon: Decimal = 0.1
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
    alpha_overline = 1

    meet_condition = "A"
    while abs(alpha_overline - alpha_underline) <= (epsilon**4 / 12):
        alpha = (alpha_underline + alpha_overline) / 2
        if check_condition_a(
            alpha=alpha,
            preference=preferences[0],
            current_cuts=cuts,
            cake_size=cake_size,
            epsilon=epsilon,
        ):
            meet_condition = "A"
            alpha_underline = alpha
        elif check_condition_b(
            alpha=alpha,
            preference=preferences[0],
            current_cuts=cuts,
            cake_size=cake_size,
            epsilon=epsilon,
        ):
            meet_condition = "B"
            alpha_underline = alpha
        else:
            alpha_overline = alpha

    allocation = None
    if meet_condition == "A":
        allocation = find_allocation_on_condition_a()
    elif meet_condition == "B":
        allocation = find_allocation_on_condition_b()

    return {"solution": allocation, "steps": steps}
