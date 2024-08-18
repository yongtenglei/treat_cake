import logging
from decimal import Decimal
from typing import Any, Dict, List, Tuple

from base_types import AssignedSlice, Preferences, Segment
from type_helper import almost_equal, to_decimal
from valuation import get_double_prime_for_interval

from ..alex_aviad_hepler import (
    _binary_search_left_to_right,
    _binary_search_right_to_left,
    _check_if_weakly_prefer_piece_k,
    get_range_by_cuts,
)
from ..algorithm_test_utils import find_envy_free_allocation


def check_condition_a(
    alpha: Decimal,
    preferences: Preferences,
    cake_size: Decimal,
    epsilon: Decimal,
    tolerance: Decimal,
) -> Tuple[bool, Dict[str, Any]]:
    alpha = to_decimal(alpha)
    epsilon = to_decimal(epsilon)
    tolerance = to_decimal(tolerance)
    cake_size = to_decimal(cake_size)

    preference_a = preferences[0]

    # Find cuts and identify k
    results = _find_cuts_and_k_for_condition_a(
        alpha=alpha,
        preference=preference_a,
        cake_size=to_decimal(cake_size),
        epsilon=epsilon,
        tolerance=tolerance,
    )
    if len(results) == 0:
        return (False, {})

    cuts = results["cuts"]
    k = results["k"]

    start_k, end_k = get_range_by_cuts(cuts=cuts, k=k, cake_size=to_decimal(cake_size))

    weak_preference = [False for _ in range(len(preferences))]
    assert len(weak_preference) == 4

    weak_preference_idx = []
    # check if at least two of the other agents weakly prefer piece k
    for i in range(1, len(preferences)):
        weak_preference[i] = _check_if_weakly_prefer_piece_k(
            preference=preferences[i],
            cake_size=to_decimal(cake_size),
            epsilon=epsilon,
            start=start_k,
            end=end_k,
            alpha=alpha,
        )
        if weak_preference[i]:
            weak_preference_idx.append(i)

    if sum(weak_preference) >= 2:
        logging.info(
            f"Test A successful, {k=}, other agents (i and i') are {weak_preference_idx}"
        )
        return (True, {"cuts": cuts, "k": k})
    else:
        return (False, {})


def _find_cuts_and_k_for_condition_a(
    alpha: Decimal,
    cake_size: Decimal,
    preference: List[Segment],
    epsilon: Decimal,
    tolerance: Decimal = to_decimal(1e-3),
) -> Dict[str, Any]:
    """Could simplify code, but lost readability."""

    alpha = to_decimal(alpha)
    start = to_decimal(0)
    end = to_decimal(cake_size)

    equals: List[bool] = []

    # if k == 0
    # [0, l] | [l, m] | [m, r] | [r, cake_size]
    #    *       3         2          1
    r = _binary_search_right_to_left(
        preference=preference,
        cake_size=cake_size,
        epsilon=epsilon,
        start=start,
        end=end,
        target=alpha,
        tolerance=tolerance,
    )

    m = _binary_search_right_to_left(
        preference=preference,
        cake_size=cake_size,
        epsilon=epsilon,
        start=start,
        end=r,
        target=alpha,
        tolerance=tolerance,
    )

    l = _binary_search_right_to_left(
        preference=preference,
        cake_size=cake_size,
        epsilon=epsilon,
        start=start,
        end=m,
        target=alpha,
        tolerance=tolerance,
    )

    remained_value = get_double_prime_for_interval(
        segments=preference,
        epsilon=epsilon,
        start=start,
        end=l,
        cake_size=to_decimal(cake_size),
    )

    if remained_value < alpha:
        return {"cuts": [l, m, r], "k": 0}
    elif almost_equal(remained_value, alpha, tolerance=tolerance):
        equals.append(True)

    # if k == 1
    # [0, l] | [l, m] | [m, r] | [r, cake_size]
    #    1       *         3          2

    l = _binary_search_left_to_right(
        preference=preference,
        cake_size=cake_size,
        epsilon=epsilon,
        start=start,
        end=end,
        target=alpha,
        tolerance=tolerance,
    )

    r = _binary_search_right_to_left(
        preference=preference,
        cake_size=cake_size,
        epsilon=epsilon,
        start=l,
        end=end,
        target=alpha,
        tolerance=tolerance,
    )

    m = _binary_search_right_to_left(
        preference=preference,
        cake_size=cake_size,
        epsilon=epsilon,
        start=l,
        end=r,
        target=alpha,
        tolerance=tolerance,
    )

    remained_value = get_double_prime_for_interval(
        segments=preference,
        epsilon=epsilon,
        start=l,
        end=m,
        cake_size=to_decimal(cake_size),
    )

    if remained_value < alpha:
        return {"cuts": [l, m, r], "k": 1}
    elif almost_equal(remained_value, alpha, tolerance=tolerance):
        equals.append(True)

    # if k == 2
    # [0, l] | [l, m] | [m, r] | [r, cake_size]
    #    1       2         *          3
    l = _binary_search_left_to_right(
        preference=preference,
        cake_size=cake_size,
        epsilon=epsilon,
        start=start,
        end=end,
        target=alpha,
        tolerance=tolerance,
    )

    m = _binary_search_left_to_right(
        preference=preference,
        cake_size=cake_size,
        epsilon=epsilon,
        start=l,
        end=end,
        target=alpha,
        tolerance=tolerance,
    )

    r = _binary_search_right_to_left(
        preference=preference,
        cake_size=cake_size,
        epsilon=epsilon,
        start=m,
        end=end,
        target=alpha,
        tolerance=tolerance,
    )

    remained_value = get_double_prime_for_interval(
        segments=preference,
        epsilon=epsilon,
        start=m,
        end=r,
        cake_size=to_decimal(cake_size),
    )

    if remained_value < alpha:
        return {"cuts": [l, m, r], "k": 2}
    elif almost_equal(remained_value, alpha, tolerance=tolerance):
        equals.append(True)

    # if k == 3
    # [0, l] | [l, m] | [m, r] | [r, cake_size]
    #    1       2         3          *
    l = _binary_search_left_to_right(
        preference=preference,
        cake_size=cake_size,
        epsilon=epsilon,
        start=start,
        end=end,
        target=alpha,
        tolerance=tolerance,
    )

    m = _binary_search_left_to_right(
        preference=preference,
        cake_size=cake_size,
        epsilon=epsilon,
        start=l,
        end=end,
        target=alpha,
        tolerance=tolerance,
    )

    r = _binary_search_left_to_right(
        preference=preference,
        cake_size=cake_size,
        epsilon=epsilon,
        start=m,
        end=end,
        target=alpha,
        tolerance=tolerance,
    )

    remained_value = get_double_prime_for_interval(
        segments=preference,
        epsilon=epsilon,
        start=r,
        end=end,
        cake_size=to_decimal(cake_size),
    )

    if remained_value < alpha:
        return {"cuts": [l, m, r], "k": 3}
    elif almost_equal(remained_value, alpha, tolerance=tolerance):
        equals.append(True)

    if len(equals) == 4 and all(equals) is True:
        logging.info("All segments have the same value, treat the last piece as k")
        return {"cuts": [l, m, r], "k": 3}
    else:
        return {}
        # raise ValueError("Cannot find a valid cuts, CHECK IMPLEMENTATION")


def find_allocation_on_condition_a(
    preferences: Preferences,
    cake_size: Decimal,
    cuts: List[Decimal],
    k: int,
    episilon: Decimal,
) -> List[AssignedSlice]:
    allocation = find_envy_free_allocation(
        cuts=cuts,
        num_agents=4,
        cake_size=cake_size,
        preferences=preferences,
        epsilon=episilon,
    )
    assert (
        allocation is not None
    ), "Should always find a final allocation on condition a"
    # allocation: List[AssignedSlice] = [None for _ in range(len(preferences))]
    #
    # unassigned_slices = cut_cake(
    #     preferences=preferences, cake_size=cake_size, epsilon=episilon, cuts=cuts
    # )
    #
    # # First piece for agent 1
    # allocation[0] = unassigned_slices[0].assign(0)
    #
    # # FIX: Partial Implementation
    # for i in range(1, len(unassigned_slices)):
    #     allocation[i] = unassigned_slices[i].assign(i)
    #
    # assert all(a is not None for a in allocation)
    return allocation
