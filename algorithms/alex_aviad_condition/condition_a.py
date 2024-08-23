import logging
from decimal import Decimal, getcontext
from typing import Any, Dict, List, Tuple

from base_types import AssignedSlice, Preferences, Segment
from type_helper import de_norm, to_decimal
from valuation import get_double_prime_for_interval
from values import get_value_for_interval

from ..alex_aviad_hepler import (
    _binary_search_left_to_right,
    _binary_search_right_to_left,
    _check_if_weakly_prefer_piece_k,
    get_range_by_cuts,
)
from ..algorithm_test_utils import find_envy_free_allocation

getcontext().prec = 15

POSIBLE_K = [0, 1, 2, 3]


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

    whole_cake_value = get_value_for_interval(
        segments=preference_a, start=to_decimal(0), end=cake_size
    )
    # Find cuts and identify k
    for k in POSIBLE_K:
        results = _find_cuts_and_k_for_condition_a(
            k=k,
            alpha=alpha,
            preference=preference_a,
            cake_size=to_decimal(cake_size),
            epsilon=epsilon,
            tolerance=tolerance,
        )
        if len(results) == 0:
            continue

        cuts = results["cuts"]
        k = results["k"]

        start_k, end_k = get_range_by_cuts(
            cuts=cuts, k=k, cake_size=to_decimal(cake_size)
        )

        v_1 = get_double_prime_for_interval(
            segments=preference_a,
            epsilon=epsilon,
            start=start_k,
            end=end_k,
            cake_size=cake_size,
        )

        v_1 = de_norm(v=v_1, whole_cake_value=whole_cake_value)

        weak_preference = [False for _ in range(len(preferences))]
        assert len(weak_preference) == 4

        weak_preference_idx = []
        # check if at least two of the other agents weakly prefer piece k
        for i in range(1, len(preferences)):
            logging.error(f"Check Conditonn A if agent {i} weakly prefer k")
            weak_preference[i] = _check_if_weakly_prefer_piece_k(
                preference=preferences[i],
                cake_size=to_decimal(cake_size),
                epsilon=epsilon,
                start=start_k,
                end=end_k,
                alpha=v_1,
            )
            if weak_preference[i]:
                weak_preference_idx.append(i)

        if sum(weak_preference) >= 2:
            logging.error(
                f"Test A successful, {k=}, other agents (i and i') are {weak_preference_idx}"
            )
            return (True, {"cuts": cuts, "k": k})
    return (False, {})


def _find_cuts_and_k_for_condition_a(
    k: int,
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

    # equals: List[bool] = []

    if k == 0:
        # [0, l] | [l, m] | [m, r] | [r, cake_size]
        #    *       3         2          1
        logging.error(f"******{k=}")
        r = _binary_search_right_to_left(
            preference=preference,
            cake_size=cake_size,
            epsilon=epsilon,
            start=start,
            end=end,
            target=alpha,
            tolerance=tolerance,
        )
        logging.error(f"******{r=}")

        m = _binary_search_right_to_left(
            preference=preference,
            cake_size=cake_size,
            epsilon=epsilon,
            start=start,
            end=r,
            target=alpha,
            tolerance=tolerance,
        )
        logging.error(f"******{m=}")

        l = _binary_search_right_to_left(
            preference=preference,
            cake_size=cake_size,
            epsilon=epsilon,
            start=start,
            end=m,
            target=alpha,
            tolerance=tolerance,
        )
        logging.error(f"******{l=}")

        remained_value = get_double_prime_for_interval(
            segments=preference,
            epsilon=epsilon,
            start=start,
            end=l,
            cake_size=to_decimal(cake_size),
        )
        logging.error(f"******{remained_value=}, should < {alpha=}")

        if remained_value <= alpha:
            logging.error(f"11111111111111111111111111111111111111111111, k = 0")
            return {"cuts": [l, m, r], "k": 0}
        # elif almost_equal(remained_value, alpha, tolerance=tolerance):
        #     equals.append(True)
        else:
            return {}

    if k == 1:
        # [0, l] | [l, m] | [m, r] | [r, cake_size]
        #    1       *         3          2
        logging.error(f"******{k=}")
        l = _binary_search_left_to_right(
            preference=preference,
            cake_size=cake_size,
            epsilon=epsilon,
            start=start,
            end=end,
            target=alpha,
            tolerance=tolerance,
        )
        logging.error(f"******{l=}")

        r = _binary_search_right_to_left(
            preference=preference,
            cake_size=cake_size,
            epsilon=epsilon,
            start=l,
            end=end,
            target=alpha,
            tolerance=tolerance,
        )
        logging.error(f"******{r=}")

        m = _binary_search_right_to_left(
            preference=preference,
            cake_size=cake_size,
            epsilon=epsilon,
            start=l,
            end=r,
            target=alpha,
            tolerance=tolerance,
        )
        logging.error(f"******{m=}")

        remained_value = get_double_prime_for_interval(
            segments=preference,
            epsilon=epsilon,
            start=l,
            end=m,
            cake_size=to_decimal(cake_size),
        )
        logging.error(f"******{remained_value=}, should < {alpha=}")

        if remained_value <= alpha:
            logging.error(f"22222222222222222222222222222222222222222222222222, k = 1")
            return {"cuts": [l, m, r], "k": 1}
        # elif almost_equal(remained_value, alpha, tolerance=tolerance):
        #     equals.append(True)
        else:
            return {}

    if k == 2:
        # [0, l] | [l, m] | [m, r] | [r, cake_size]
        #    1       2         *          3
        logging.error(f"******{k=}")
        l = _binary_search_left_to_right(
            preference=preference,
            cake_size=cake_size,
            epsilon=epsilon,
            start=start,
            end=end,
            target=alpha,
            tolerance=tolerance,
        )
        logging.error(f"******{l=}")

        m = _binary_search_left_to_right(
            preference=preference,
            cake_size=cake_size,
            epsilon=epsilon,
            start=l,
            end=end,
            target=alpha,
            tolerance=tolerance,
        )
        logging.error(f"******{m=}")

        r = _binary_search_right_to_left(
            preference=preference,
            cake_size=cake_size,
            epsilon=epsilon,
            start=m,
            end=end,
            target=alpha,
            tolerance=tolerance,
        )
        logging.error(f"******{r=}")

        remained_value = get_double_prime_for_interval(
            segments=preference,
            epsilon=epsilon,
            start=m,
            end=r,
            cake_size=to_decimal(cake_size),
        )
        logging.error(f"******{remained_value=}, should < {alpha=}")

        if remained_value <= alpha:
            logging.error("3333333333333333333333333333333333333333333333333, k =2")
            return {"cuts": [l, m, r], "k": 2}
        # elif almost_equal(remained_value, alpha, tolerance=tolerance):
        #     equals.append(True)
        else:
            return {}

    if k == 3:
        # [0, l] | [l, m] | [m, r] | [r, cake_size]
        #    1       2         3          *
        logging.error(f"******{k=}")
        l = _binary_search_left_to_right(
            preference=preference,
            cake_size=cake_size,
            epsilon=epsilon,
            start=start,
            end=end,
            target=alpha,
            tolerance=tolerance,
        )
        logging.error(f"******{l=}")

        m = _binary_search_left_to_right(
            preference=preference,
            cake_size=cake_size,
            epsilon=epsilon,
            start=l,
            end=end,
            target=alpha,
            tolerance=tolerance,
        )
        logging.error(f"******{m=}")

        r = _binary_search_left_to_right(
            preference=preference,
            cake_size=cake_size,
            epsilon=epsilon,
            start=m,
            end=end,
            target=alpha,
            tolerance=tolerance,
        )
        logging.error(f"******{r=}")

        remained_value = get_double_prime_for_interval(
            segments=preference,
            epsilon=epsilon,
            start=r,
            end=end,
            cake_size=to_decimal(cake_size),
        )
        logging.error(f"******{remained_value=}, should < {alpha=}")

        if remained_value <= alpha:
            logging.error("4444444444444444444444444444444444444444444444444444, k =3")
            return {"cuts": [l, m, r], "k": 3}
        # elif almost_equal(remained_value, alpha, tolerance=tolerance):
        #     equals.append(True)
        else:
            return {}

    # if len(equals) == 4 and all(equals) is True:
    #     logging.warning("All segments have the same value, treat the last piece as k")
    #     return {"cuts": [l, m, r], "k": 3}
    # else:
    #     logging.error("Cannot find a valid cuts for Condition A")
    #     return {}
    # raise ValueError("Cannot find a valid cuts, CHECK IMPLEMENTATION")


def find_allocation_on_condition_a(
    preferences: Preferences,
    cake_size: Decimal,
    epsilon: Decimal,
    alpha: Decimal,
    tolerance: Decimal,
) -> List[AssignedSlice]:
    meet_a, info = check_condition_a(
        alpha=alpha,
        preferences=preferences,
        cake_size=cake_size,
        epsilon=epsilon,
        tolerance=tolerance,
    )
    assert (
        meet_a is True
    ), "find_allocation_on_condition_a: Should meet Condition A at this stage"
    assert (
        len(info) != 0
    ), "find_allocation_on_condition_a: Should have necessary info at this stage"
    cuts, k = info["cuts"], info["k"]
    logging.error(f"find_allocation_on_condition_a: {cuts=}, {k=}, {alpha=}")

    allocation = find_envy_free_allocation(
        cuts=cuts,
        num_agents=4,
        cake_size=cake_size,
        preferences=preferences,
        epsilon=epsilon,
    )
    assert (
        allocation is not None
    ), "Should always find a final allocation on condition a"
    return allocation


def find_allocation_on_condition_a_bak(
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
    return allocation
