from decimal import Decimal
from typing import Dict, Any
from typing import List

from .algorithm_test_utils import (
    find_envy_free_allocation,
    find_envy_free_allocation_using_original_evaluation_func,
)
from .alex_aviad_hepler import (
    check_condition_a,
    check_condition_b,
    find_allocation_on_condition_a,
    find_allocation_on_condition_b,
)
from ..base_types import Segment, Preferences
from ..values import find_cut_line_by_percent
from ..valuation import get_double_prime_for_interval


def equipartition(preference: List[Segment]) -> List[Decimal]:
    # Finding cuts at 1/4, 1/2, and 3/4 of the cake
    first_cut = find_cut_line_by_percent(preference, 0.25)
    second_cut = find_cut_line_by_percent(preference, 0.50)
    third_cut = find_cut_line_by_percent(preference, 0.75)

    return [first_cut, second_cut, third_cut]


def alex_aviad(
    preferences: Preferences, cake_size: int, epsilon: Decimal = 0.1
) -> Dict[str, Any]:
    assert len(preferences) == 4, "Need 4 agents here"

    solution = []
    steps = []

    # Find the equipartition by Agent1
    cuts = equipartition(preference=preferences[0])
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
        segments=preferences[0], epsilon=epsilon, start=0, end=cuts[0]
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


def alex_aviad_using_original_valuation_func(
    preferences: Preferences, cake_size: int
) -> Dict[str, Any]:
    """TESTING ONLY"""
    assert len(preferences) == 4, "Need 4 agents here"

    solution = []
    steps = []

    # Find the equipartition by Agent1
    cuts = equipartition(preference=preferences[0])
    solution = find_envy_free_allocation_using_original_evaluation_func(
        cuts=cuts,
        num_agents=4,
        cake_size=cake_size,
        preferences=preferences,
    )
    if solution is not None:
        return {"solution": solution, "steps": steps}

    assert 1 == 2, "NOT IMPLEMENTED YET"
    # return {"solution": solution, "steps": steps}
