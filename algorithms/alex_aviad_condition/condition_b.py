from decimal import Decimal
from typing import Any, Dict, List, Tuple

from base_types import AssignedSlice, Preferences, Segment
from type_helper import almost_equal, to_decimal
from valuation import get_double_prime_for_interval

from ..alex_aviad_hepler import (
    _binary_search_left_to_right,
    _binary_search_right_to_left,
    get_range_by_cuts,
)
from ..algorithm_test_utils import find_envy_free_allocation

POSSIBLE_K_AND_K_PRIME_COMBINATION_ON_CONDITION_B = [
    (0, 1, [2, 3]),
    (0, 2, [1, 3]),
    (0, 3, [1, 2]),
    (1, 2, [0, 3]),
    (1, 3, [0, 2]),
    (2, 3, [0, 1]),
]
POSSIBLE_PIECE_NUMBER = [0, 1, 2, 3]


def check_condition_b(
    alpha: Decimal,
    preferences: Preferences,
    cake_size: int,
    epsilon: Decimal,
    tolerance: Decimal,
) -> Tuple[bool, Dict[str, Any]]:
    alpha = to_decimal(alpha)
    epsilon = to_decimal(epsilon)
    tolerance = to_decimal(tolerance)

    preference_1 = preferences[0]

    # PERF: May accelerate this process by using "notebook", cache double values
    for i in range(1, len(preferences)):
        preference_i = preferences[i]
        results = _find_cuts_and_k_k_prime_for_agent_i_on_condition_b(
            alpha=alpha,
            cake_size=to_decimal(cake_size),
            preference_1=preference_1,
            preference_i=preference_i,
            epsilon=epsilon,
            tolerance=tolerance,
        )
        for result in results:
            cuts: List[Decimal] = result["cuts"]
            k: int = result["k"]
            k_prime: int = result["k_prime"]

            other_1: int
            other_2: int
            other_1, other_2 = result["others"]
            assert len(cuts) == 3, "Should have 3 cut points"
            assert (
                (k in POSSIBLE_PIECE_NUMBER)
                and (k_prime in POSSIBLE_PIECE_NUMBER)
                and (other_1 in POSSIBLE_PIECE_NUMBER)
                and (other_2 in POSSIBLE_PIECE_NUMBER)
                and (k != k_prime)
                and (k != other_1)
                and (k != other_2)
                and (k_prime != other_1)
                and (k_prime != other_2)
                and (other_1 != other_2)
            ), "Invalid k"

            start_k, end_k = get_range_by_cuts(
                cuts=cuts, k=k, cake_size=to_decimal(cake_size)
            )

            start_k_prime, end_k_prime = get_range_by_cuts(
                cuts=cuts, k=k_prime, cake_size=to_decimal(cake_size)
            )

            start_other_1, end_other_1 = get_range_by_cuts(
                cuts=cuts, k=other_1, cake_size=to_decimal(cake_size)
            )
            start_other_2, end_other_2 = get_range_by_cuts(
                cuts=cuts, k=other_2, cake_size=to_decimal(cake_size)
            )

            # Check condition, if Ok, return.
            # Otherwise, continue exploring.

            # ii. (v_i(P_k′) =)v_i(P_k) >= max_t v_i(P_t), and
            k_value_i = get_double_prime_for_interval(
                segments=preference_i,
                epsilon=epsilon,
                start=start_k,
                end=end_k,
                cake_size=to_decimal(cake_size),
            )
            k_prime_value_i = get_double_prime_for_interval(
                segments=preference_i,
                epsilon=epsilon,
                start=start_k_prime,
                end=end_k_prime,
                cake_size=to_decimal(cake_size),
            )
            if k_value_i != k_prime_value_i:
                continue
            other_1_value_i = get_double_prime_for_interval(
                segments=preference_i,
                epsilon=epsilon,
                start=start_other_1,
                end=end_other_1,
                cake_size=to_decimal(cake_size),
            )
            other_2_value_i = get_double_prime_for_interval(
                segments=preference_i,
                epsilon=epsilon,
                start=start_other_2,
                end=end_other_2,
                cake_size=to_decimal(cake_size),
            )
            others_max_value_i = max(other_1_value_i, other_2_value_i)
            if not (
                k_value_i >= others_max_value_i
                and k_prime_value_i >= others_max_value_i
            ):
                continue

            # i. v_1(P_k) <= α and v_1(P_k′) <= α, and
            k_value_1 = get_double_prime_for_interval(
                segments=preference_1,
                epsilon=epsilon,
                start=start_k,
                end=end_k,
                cake_size=to_decimal(cake_size),
            )
            k_prime_value_1 = get_double_prime_for_interval(
                segments=preference_1,
                epsilon=epsilon,
                start=start_k_prime,
                end=end_k_prime,
                cake_size=to_decimal(cake_size),
            )
            if not (k_value_1 <= alpha and k_prime_value_1 <= alpha):
                continue

            # iii. there exists i′ ∈ {2, 3, 4} ∖ {i} such that v_i′(P_k) ≥ max_t v_i′(P_t), and
            # iv. there exists i′ ∈ {2, 3, 4} ∖ {i} with v_i′(P_k′) ≥ max_t v_i′(P_t).
            for j in range(1, len(preferences)):
                if j == i:
                    continue
                preference_j = preferences[j]
                other_1_value_j = get_double_prime_for_interval(
                    segments=preference_j,
                    epsilon=epsilon,
                    start=start_other_1,
                    end=end_other_1,
                    cake_size=to_decimal(cake_size),
                )
                other_2_value_j = get_double_prime_for_interval(
                    segments=preference_j,
                    epsilon=epsilon,
                    start=start_other_2,
                    end=end_other_2,
                    cake_size=to_decimal(cake_size),
                )
                others_max_value_j = max(other_1_value_j, other_2_value_j)

                k_value_j = get_double_prime_for_interval(
                    segments=preference_j,
                    epsilon=epsilon,
                    start=start_k,
                    end=end_k,
                    cake_size=to_decimal(cake_size),
                )
                k_prime_value_j = get_double_prime_for_interval(
                    segments=preference_j,
                    epsilon=epsilon,
                    start=start_k_prime,
                    end=end_k_prime,
                    cake_size=to_decimal(cake_size),
                )
                if (
                    k_value_j >= others_max_value_j
                    and k_prime_value_j >= others_max_value_j
                ):
                    return (True, {"cuts": cuts, "k": k, "k_prime": k_prime})
    return (False, {})


def _handle_adjacent(
    k: int,
    k_prime: int,
    alpha: Decimal,
    preference_1: List[Segment],
    preference_i: List[Segment],
    epsilon: Decimal,
    cake_size: Decimal,
    tolerance: Decimal,
) -> List[Decimal]:
    # if k, k' = (0, 1)
    #    0        1        2            3
    # [0, l] | [l, m] | [m, r] | [r, cake_size]
    #   (3      3)         2          1
    if k == 0 and k_prime == 1:
        r = _binary_search_right_to_left(
            preference=preference_1,
            cake_size=cake_size,
            epsilon=epsilon,
            start=to_decimal(0),
            end=cake_size,
            target=alpha,
            tolerance=tolerance,
        )

        m = _binary_search_right_to_left(
            preference=preference_1,
            cake_size=cake_size,
            epsilon=epsilon,
            start=to_decimal(0),
            end=r,
            target=alpha,
            tolerance=tolerance,
        )

        remained_value = get_double_prime_for_interval(
            segments=preference_i,
            epsilon=epsilon,
            start=to_decimal(0),
            end=m,
            cake_size=to_decimal(cake_size),
        )

        desired_half_value = remained_value / 2

        l = _binary_search_left_to_right(
            preference=preference_i,
            cake_size=cake_size,
            epsilon=epsilon,
            start=to_decimal(0),
            end=m,
            target=desired_half_value,
            tolerance=tolerance,
        )

        # NOTE: For testing
        first_half_value = get_double_prime_for_interval(
            segments=preference_i,
            epsilon=epsilon,
            start=to_decimal(0),
            end=l,
            cake_size=to_decimal(cake_size),
        )
        second_half_value = get_double_prime_for_interval(
            segments=preference_i,
            epsilon=epsilon,
            start=l,
            end=m,
            cake_size=to_decimal(cake_size),
        )
        assert almost_equal(
            first_half_value, second_half_value, tolerance=tolerance
        ), "Should have almost the same value under the view of agent i"

        return [l, m, r]
    # if k, k' = (1, 2)
    #    0        1        2            3
    # [0, l] | [l, m] | [m, r] | [r, cake_size]
    #    1      (3         3)          2
    elif k == 1 and k_prime == 2:
        l = _binary_search_left_to_right(
            preference=preference_1,
            cake_size=cake_size,
            epsilon=epsilon,
            start=to_decimal(0),
            end=cake_size,
            target=alpha,
            tolerance=tolerance,
        )

        r = _binary_search_right_to_left(
            preference=preference_1,
            epsilon=epsilon,
            start=l,
            end=cake_size,
            target=alpha,
            tolerance=tolerance,
        )

        remained_value = get_double_prime_for_interval(
            segments=preference_i,
            epsilon=epsilon,
            start=l,
            end=r,
            cake_size=to_decimal(cake_size),
        )

        desired_half_value = remained_value / 2

        m = _binary_search_left_to_right(
            preference=preference_i,
            cake_size=cake_size,
            epsilon=epsilon,
            start=l,
            end=r,
            target=desired_half_value,
            tolerance=tolerance,
        )

        # NOTE: For testing
        first_half_value = get_double_prime_for_interval(
            segments=preference_i,
            epsilon=epsilon,
            start=l,
            end=m,
            cake_size=to_decimal(cake_size),
        )
        second_half_value = get_double_prime_for_interval(
            segments=preference_i,
            epsilon=epsilon,
            start=m,
            end=r,
            cake_size=to_decimal(cake_size),
        )
        assert almost_equal(
            first_half_value, second_half_value, tolerance=tolerance
        ), "Should have almost the same value under the view of agent i"

        return [l, m, r]
    # if k, k' = (2, 3)
    #    0        1        2            3
    # [0, l] | [l, m] | [m, r] | [r, cake_size]
    #    1      2         (3          3)
    elif k == 2 and k_prime == 3:
        l = _binary_search_left_to_right(
            preference=preference_1,
            cake_size=cake_size,
            epsilon=epsilon,
            start=to_decimal(0),
            end=cake_size,
            target=alpha,
            tolerance=tolerance,
        )

        m = _binary_search_left_to_right(
            preference=preference_i,
            cake_size=cake_size,
            epsilon=epsilon,
            start=l,
            end=cake_size,
            target=alpha,
            tolerance=tolerance,
        )

        remained_value = get_double_prime_for_interval(
            segments=preference_i,
            epsilon=epsilon,
            start=m,
            end=cake_size,
            cake_size=to_decimal(cake_size),
        )

        desired_half_value = remained_value / 2

        r = _binary_search_left_to_right(
            preference=preference_i,
            cake_size=cake_size,
            epsilon=epsilon,
            start=m,
            end=cake_size,
            target=desired_half_value,
            tolerance=tolerance,
        )

        # NOTE: For testing
        first_half_value = get_double_prime_for_interval(
            segments=preference_i,
            epsilon=epsilon,
            start=m,
            end=r,
            cake_size=to_decimal(cake_size),
        )
        second_half_value = get_double_prime_for_interval(
            segments=preference_i,
            epsilon=epsilon,
            start=r,
            end=cake_size,
            cake_size=to_decimal(cake_size),
        )
        assert almost_equal(
            first_half_value, second_half_value, tolerance=tolerance
        ), "Should have almost the same value under the view of agent i"

        return [l, m, r]
    else:
        raise ValueError("Invalid k and k'")


def _find_m_given_l(
    l: Decimal,
    r: Decimal,
    alpha: Decimal,
    preference_1: List[Segment],
    cake_size: Decimal,
    epsilon: Decimal,
    tolerance: Decimal = to_decimal(1e-10),
) -> Decimal:
    """find m given l: m(l), so that v_1(l, m(l)) = alpha (second piece)"""
    return _binary_search_left_to_right(
        preference=preference_1,
        cake_size=cake_size,
        epsilon=epsilon,
        start=to_decimal(l),
        end=to_decimal(r),
        target=alpha,
        tolerance=tolerance,
    )


def _binary_search_case_0_2(
    preference_1: List[Segment],
    preference_i: List[Segment],
    epsilon: Decimal,
    l_start: Decimal,
    l_end: Decimal,
    alpha: Decimal,
    cake_size: Decimal,
    tolerance: Decimal = to_decimal(1e-10),
    max_iterations: int = 1000,
) -> Decimal:
    original_l_end = to_decimal(l_end)  # namely r
    iteration = 0

    while l_end - l_start > tolerance and iteration < max_iterations:
        l = (l_start + l_end) / 2
        m_for_l = _find_m_given_l(
            l=l,
            r=original_l_end,
            alpha=alpha,
            preference_1=preference_1,
            cake_size=cake_size,
            epsilon=epsilon,
            tolerance=tolerance,
        )
        a = get_double_prime_for_interval(
            segments=preference_1,
            epsilon=epsilon,
            start=l,
            end=m_for_l,
            cake_size=to_decimal(cake_size),
        )
        b = get_double_prime_for_interval(
            segments=preference_1,
            epsilon=epsilon,
            start=original_l_end,
            end=to_decimal(cake_size),
            cake_size=to_decimal(cake_size),
        )

        # TODO: DELETE LATER FOR TESTING
        # give l, find m(l), where v_1([l, m(l)]) = alpha (second piece) = v_1([r, cake_size])
        assert almost_equal(
            a,
            b,
            tolerance=tolerance,
        ), f"[l:{l}, m(l):{m_for_l}] = {a=}, [r:{original_l_end}, {cake_size}]{b=}, ({alpha})"

        searched_value = get_double_prime_for_interval(
            segments=preference_i,
            epsilon=epsilon,
            start=to_decimal(0),
            end=l,
            cake_size=to_decimal(cake_size),
        )
        print("***********")
        print("Handle_one_between: binary search")
        print(f"{l=}, {searched_value=}, {l=}, {m_for_l=}")
        print("***********")

        # Want v_i[(0, l)]= v_i[(m(l), r)]
        desired_value = get_double_prime_for_interval(
            segments=preference_i,
            epsilon=epsilon,
            start=m_for_l,
            end=original_l_end,
            cake_size=to_decimal(cake_size),
        )
        if almost_equal(a=searched_value, b=desired_value, tolerance=tolerance):
            return l

        if searched_value < desired_value:
            l_start = l
        else:
            l_end = l

        iteration = iteration + 1

    return to_decimal((l_start + l_end) / 2)


def _find_m_given_r(
    l: Decimal,
    r: Decimal,
    alpha: Decimal,
    preference_1: List[Segment],
    cake_size: Decimal,
    epsilon: Decimal,
    tolerance: Decimal = to_decimal(1e-10),
) -> Decimal:
    """find m given r: m(r), so that v_1(m(r), r) = alpha (third piece)"""
    return _binary_search_left_to_right(
        preference=preference_1,
        cake_size=cake_size,
        epsilon=epsilon,
        start=to_decimal(l),
        end=to_decimal(r),
        target=alpha,
        tolerance=tolerance,
    )


def _binary_search_case_1_3(
    preference_1: List[Segment],
    preference_i: List[Segment],
    epsilon: Decimal,
    r_start: Decimal,
    r_end: Decimal,
    alpha: Decimal,
    cake_size: Decimal,
    tolerance: Decimal = to_decimal(1e-10),
    max_iterations: int = 1000,
) -> Decimal:
    original_r_start = to_decimal(r_start)  # namely l
    iteration = 0

    while r_end - r_start > tolerance and iteration < max_iterations:
        r = (r_start + r_end) / 2
        m_for_r = _find_m_given_r(
            l=original_r_start,
            r=r,
            alpha=alpha,
            preference_1=preference_1,
            epsilon=epsilon,
        )
        # TODO: DELETE LATER FOR TESTING
        # give r, find m(r), where v_1([m(r), r]) = alpha (third piece) = v_1([(0, l)])
        assert almost_equal(
            a=get_double_prime_for_interval(
                segments=preference_1,
                epsilon=epsilon,
                start=m_for_r,
                end=r,
                cake_size=to_decimal(cake_size),
            ),
            b=get_double_prime_for_interval(
                segments=preference_1,
                epsilon=epsilon,
                start=to_decimal(0),
                end=original_r_start,
                cake_size=to_decimal(cake_size),
            ),
            tolerance=tolerance,
        )

        searched_value = get_double_prime_for_interval(
            segments=preference_i,
            epsilon=epsilon,
            start=r,
            end=to_decimal(cake_size),
            cake_size=to_decimal(cake_size),
        )
        print("***********")
        print(f"{r=}, {searched_value=}, {r=}, {cake_size=}")
        print("***********")

        # Want v_i([l, m(r)])= v_i([(r, cake_size])
        desired_value = get_double_prime_for_interval(
            segments=preference_i,
            epsilon=epsilon,
            start=original_r_start,
            end=m_for_r,
            cake_size=to_decimal(cake_size),
        )

        if almost_equal(a=searched_value, b=desired_value, tolerance=tolerance):
            return r

        if searched_value < desired_value:
            r_end = r
        else:
            r_start = r

        iteration = iteration + 1

    return to_decimal((r_start + r_end) / 2)


def _handle_one_between(
    k: int,
    k_prime: int,
    alpha: Decimal,
    preference_1: List[Segment],
    preference_i: List[Segment],
    epsilon: Decimal,
    cake_size: Decimal,
    tolerance: Decimal = to_decimal(1e-10),
) -> List[Decimal]:
    # if k, k' = (0, 2)
    #    0        1        2            3
    # [0, l] | [l, m] | [m, r] | [r, cake_size]
    #                                   1
    # give l, find m(l), where v_1([l, m(l)]) = alpha (second piece)
    # keep move l, making v_i([0, l]) = v_i([m(l), r])
    if k == 0 and k_prime == 2:
        try:
            r = _binary_search_right_to_left(
                preference=preference_1,
                cake_size=cake_size,
                epsilon=epsilon,
                start=to_decimal(0),
                end=cake_size,
                target=alpha,
                tolerance=tolerance,
            )
            l_start = to_decimal(0)
            l_end = r
            l = _binary_search_case_0_2(
                preference_1=preference_1,
                preference_i=preference_i,
                epsilon=epsilon,
                l_start=l_start,
                l_end=l_end,
                alpha=alpha,
                cake_size=cake_size,
                tolerance=tolerance,
            )
            m = _find_m_given_l(
                l=l,
                r=r,
                alpha=alpha,
                preference_1=preference_1,
                cake_size=cake_size,
                epsilon=epsilon,
                tolerance=tolerance,
            )
            return [l, m, r]
        except Exception as e:
            pass
    else:
        raise ValueError("Invalid k and k'")
    # if k, k' = (1, 3)
    #    0        1        2            3
    # [0, l] | [l, m] | [m, r] | [r, cake_size]
    #    1
    # give r, find m(r), where v_1([m(r), r]) = alpha (third piece) = v_1([(0, l)])
    # keep move r, making v_i([l, m(r)]) = v_i([r, cake_size])
    if k == 1 and k_prime == 3:
        try:
            l = _binary_search_left_to_right(
                preference=preference_1,
                cake_size=cake_size,
                epsilon=epsilon,
                start=to_decimal(0),
                end=cake_size,
                target=alpha,
                tolerance=tolerance,
            )
            r_start = to_decimal(l)
            r_end = to_decimal(cake_size)
            r = _binary_search_case_1_3(
                preference_1=preference_1,
                preference_i=preference_i,
                epsilon=epsilon,
                r_start=r_start,
                r_end=r_end,
                cake_size=to_decimal(cake_size),
                alpha=alpha,
                tolerance=tolerance,
            )
            m = _find_m_given_r(
                l=l,
                r=r,
                alpha=alpha,
                preference_1=preference_1,
                cake_size=cake_size,
                epsilon=epsilon,
                tolerance=tolerance,
            )
            return [l, m, r]
        except Exception as e:
            pass
    else:
        raise ValueError("Invalid k and k'")


def _find_m_and_r_given_l(
    l: Decimal,
    cake_size: Decimal,
    alpha: Decimal,
    preference_1: List[Segment],
    epsilon: Decimal,
    tolerance: Decimal = to_decimal(1e-10),
) -> List[Decimal]:
    """find m and r given l: m(l) and r(l), so that v_1([l, m(l)]) = v_1([m(l), r(l)]) = alpha"""
    m_for_l = _binary_search_left_to_right(
        preference=preference_1,
        cake_size=cake_size,
        epsilon=epsilon,
        start=to_decimal(l),
        end=to_decimal(cake_size),
        target=alpha,
        tolerance=tolerance,
    )

    r_for_l = _binary_search_left_to_right(
        preference=preference_1,
        cake_size=cake_size,
        epsilon=epsilon,
        start=to_decimal(m_for_l),
        end=to_decimal(cake_size),
        target=alpha,
        tolerance=tolerance,
    )

    return [m_for_l, r_for_l]


def _binary_search_find_l(
    preference_1: List[Segment],
    preference_i: List[Segment],
    epsilon: Decimal,
    l_start: Decimal,
    l_end: Decimal,
    alpha: Decimal,
    cake_size: Decimal,
    tolerance: Decimal = to_decimal(1e-10),
    max_iterations: int = 1000,
) -> Decimal:
    cake_start = to_decimal(0)
    cake_end = to_decimal(cake_size)

    iteration = 0

    while l_end - l_start > tolerance and iteration < max_iterations:
        l = (l_start + l_end) / 2
        m_for_l, r_for_l = _find_m_and_r_given_l(
            l=l,
            cake_size=to_decimal(cake_size),
            alpha=alpha,
            preference_1=preference_1,
            epsilon=epsilon,
        )
        # TODO: DELETE LATER FOR TESTING
        # give l, find m(l) and r(l), where v_1([l, m(l)]) = v_1([m(l), r(l)]) = alpha
        assert almost_equal(
            a=get_double_prime_for_interval(
                segments=preference_1,
                epsilon=epsilon,
                start=l,
                end=m_for_l,
                cake_size=to_decimal(cake_size),
            ),
            b=get_double_prime_for_interval(
                segments=preference_1,
                epsilon=epsilon,
                start=m_for_l,
                end=r_for_l,
                cake_size=to_decimal(cake_size),
            ),
            tolerance=tolerance,
        ), "Should work"

        searched_value = get_double_prime_for_interval(
            segments=preference_i,
            epsilon=epsilon,
            start=cake_start,
            end=l,
            cake_size=to_decimal(cake_size),
        )

        print("***********")
        print(f"{l=}, {searched_value=}, {cake_start=}, {l=}")
        print("***********")

        # Want v_i([0, l])= v_i([(r(l), cake_size])
        desired_value = get_double_prime_for_interval(
            segments=preference_i,
            epsilon=epsilon,
            start=r_for_l,
            end=cake_end,
            cake_size=to_decimal(cake_size),
        )

        if almost_equal(a=searched_value, b=desired_value, tolerance=tolerance):
            return l

        if searched_value < desired_value:
            l_start = l
        else:
            l_end = l

        iteration = iteration + 1

    return to_decimal((l_start + l_end) / 2)


def _expand_range_around_l(
    found_l: Decimal,
    preference_1: List[Segment],
    preference_i: List[Segment],
    epsilon: Decimal,
    alpha: Decimal,
    cake_size: Decimal,
    tolerance: Decimal = to_decimal(1e-10),
) -> Tuple[Decimal, Decimal]:
    cake_start = to_decimal(0)
    cake_end = to_decimal(cake_size)

    # Expand the range to find the lower bound
    lower_bound = found_l
    while lower_bound - epsilon >= cake_start:
        lower_bound_candidate = lower_bound - epsilon
        m_for_l, r_for_l = _find_m_and_r_given_l(
            l=lower_bound_candidate,
            cake_size=to_decimal(cake_size),
            alpha=alpha,
            preference_1=preference_1,
            epsilon=epsilon,
        )

        # TODO: DELETE LATER FOR TESTING
        # give l, find m(l) and r(l), where v_1([l, m(l)]) = v_1([m(l), r(l)]) = alpha
        assert almost_equal(
            a=get_double_prime_for_interval(
                segments=preference_1,
                epsilon=epsilon,
                start=lower_bound_candidate,
                end=m_for_l,
                cake_size=to_decimal(cake_size),
            ),
            b=get_double_prime_for_interval(
                segments=preference_1,
                epsilon=epsilon,
                start=m_for_l,
                end=r_for_l,
                cake_size=to_decimal(cake_size),
            ),
            tolerance=tolerance,
        ), "Should work"

        searched_value = get_double_prime_for_interval(
            segments=preference_i,
            epsilon=epsilon,
            start=cake_start,
            end=lower_bound_candidate,
            cake_size=to_decimal(cake_size),
        )

        print("***********")
        print(
            f"{lower_bound_candidate=}, {searched_value=}, {cake_start=}, {lower_bound_candidate=}"
        )
        print("***********")

        # Want v_i([0, l])= v_i([(r(l), cake_size])
        desired_value = get_double_prime_for_interval(
            segments=preference_i,
            epsilon=epsilon,
            start=r_for_l,
            end=cake_end,
            cake_size=to_decimal(cake_size),
        )

        if almost_equal(a=searched_value, b=desired_value, tolerance=tolerance):
            lower_bound = lower_bound_candidate
        else:
            break

    # Expand the range to find the upper bound
    upper_bound = found_l
    while upper_bound + epsilon <= cake_end:
        upper_bound_candidate = upper_bound + epsilon
        m_for_l, r_for_l = _find_m_and_r_given_l(
            l=upper_bound_candidate,
            cake_size=to_decimal(cake_size),
            alpha=alpha,
            preference_1=preference_1,
            epsilon=epsilon,
        )

        assert almost_equal(
            a=get_double_prime_for_interval(
                segments=preference_1,
                epsilon=epsilon,
                start=upper_bound_candidate,
                end=m_for_l,
                cake_size=to_decimal(cake_size),
            ),
            b=get_double_prime_for_interval(
                segments=preference_1,
                epsilon=epsilon,
                start=m_for_l,
                end=r_for_l,
                cake_size=to_decimal(cake_size),
            ),
            tolerance=tolerance,
        ), "Should work"

        searched_value = get_double_prime_for_interval(
            segments=preference_i,
            epsilon=epsilon,
            start=cake_start,
            end=upper_bound_candidate,
            cake_size=to_decimal(cake_size),
        )

        print("***********")
        print(
            f"{upper_bound_candidate=}, {searched_value=}, {cake_start=}, {upper_bound_candidate=}"
        )
        print("***********")

        # Want v_i([0, l])= v_i([(r(l), cake_size])
        desired_value = get_double_prime_for_interval(
            segments=preference_i,
            epsilon=epsilon,
            start=r_for_l,
            end=cake_end,
            cake_size=to_decimal(cake_size),
        )

        if almost_equal(a=searched_value, b=desired_value, tolerance=tolerance):
            upper_bound = upper_bound_candidate
        else:
            break

    return lower_bound, upper_bound


def _find_range_l(
    preference_1: List[Segment],
    preference_i: List[Segment],
    epsilon: Decimal,
    l_start: Decimal,
    l_end: Decimal,
    alpha: Decimal,
    cake_size: Decimal,
    tolerance: Decimal = to_decimal(1e-10),
    max_iterations: int = 1000,
) -> Tuple[Decimal, Decimal]:
    found_l = _binary_search_find_l(
        preference_1=preference_1,
        preference_i=preference_i,
        epsilon=epsilon,
        l_start=l_start,
        l_end=l_end,
        alpha=alpha,
        cake_size=cake_size,
        tolerance=tolerance,
        max_iterations=max_iterations,
    )

    lower_bound, upper_bound = _expand_range_around_l(
        found_l=found_l,
        preference_1=preference_1,
        preference_i=preference_i,
        epsilon=epsilon,
        alpha=alpha,
        cake_size=cake_size,
        tolerance=tolerance,
    )

    return lower_bound, upper_bound


def _find_l_and_m_given_r(
    r: Decimal,
    cake_size: Decimal,
    alpha: Decimal,
    preference_1: List[Segment],
    epsilon: Decimal,
    tolerance: Decimal = to_decimal(1e-10),
) -> List[Decimal]:
    """find l and m given r: l(r) and m(r), so that v_1([l(r), m(r)]) = v_1([m(r), r]) = alpha"""
    m_for_r = _binary_search_right_to_left(
        preference=preference_1,
        cake_size=cake_size,
        epsilon=epsilon,
        start=to_decimal(0),
        end=to_decimal(r),
        target=alpha,
        tolerance=tolerance,
    )

    l_for_r = _binary_search_right_to_left(
        preference=preference_1,
        cake_size=cake_size,
        epsilon=epsilon,
        start=to_decimal(0),
        end=to_decimal(m_for_r),
        target=alpha,
        tolerance=tolerance,
    )

    return [l_for_r, m_for_r]


def _binary_search_find_r(
    preference_1: List[Segment],
    preference_i: List[Segment],
    epsilon: Decimal,
    r_start: Decimal,
    r_end: Decimal,
    alpha: Decimal,
    cake_size: Decimal,
    tolerance: Decimal = to_decimal(1e-10),
    max_iterations: int = 1000,
) -> Decimal:
    cake_start = to_decimal(0)
    cake_end = to_decimal(cake_size)

    iteration = 0

    while r_end - r_start > tolerance and iteration < max_iterations:
        r = (r_start + r_end) / 2
        l_for_r, m_for_r = _find_l_and_m_given_r(
            r=r,
            cake_size=to_decimal(cake_size),
            alpha=alpha,
            preference_1=preference_1,
            epsilon=epsilon,
            tolerance=tolerance,
        )
        # TODO: DELETE LATER FOR TESTING
        # give r, find l(r) and m(r), so that v_1([l(r), m(r)]) = v_1([m(r), r]) = alpha
        assert almost_equal(
            a=get_double_prime_for_interval(
                segments=preference_1,
                epsilon=epsilon,
                start=l_for_r,
                end=m_for_r,
                cake_size=to_decimal(cake_size),
            ),
            b=get_double_prime_for_interval(
                segments=preference_1,
                epsilon=epsilon,
                start=m_for_r,
                end=r,
                cake_size=to_decimal(cake_size),
            ),
            tolerance=tolerance,
        ), "Should work"

        searched_value = get_double_prime_for_interval(
            segments=preference_i,
            epsilon=epsilon,
            start=r,
            end=to_decimal(cake_size),
            cake_size=to_decimal(cake_size),
        )

        print("***********")
        print(f"{r=}, {searched_value=}, {r=}, {cake_size=}")
        print("***********")

        # Want v_i([0, l(r)])= v_i([(r, cake_size])
        desired_value = get_double_prime_for_interval(
            segments=preference_i,
            epsilon=epsilon,
            start=to_decimal(0),
            end=l_for_r,
            cake_size=to_decimal(cake_size),
        )

        if almost_equal(a=searched_value, b=desired_value, tolerance=tolerance):
            return r

        if searched_value < desired_value:
            r_end = r
        else:
            r_start = r

        iteration = iteration + 1

    return to_decimal((r_start + r_end) / 2)


def _expand_range_around_r(
    found_r: Decimal,
    preference_1: List[Segment],
    preference_i: List[Segment],
    epsilon: Decimal,
    alpha: Decimal,
    cake_size: Decimal,
    tolerance: Decimal = to_decimal(1e-10),
) -> Tuple[Decimal, Decimal]:
    cake_start = to_decimal(0)
    cake_end = to_decimal(cake_size)

    # Expand the range to find the lower bound
    lower_bound = found_r
    while lower_bound - epsilon >= cake_start:
        lower_bound_candidate = lower_bound - epsilon
        l_for_r, m_for_r = _find_l_and_m_given_r(
            r=lower_bound_candidate,
            cake_size=to_decimal(cake_size),
            alpha=alpha,
            preference_1=preference_1,
            epsilon=epsilon,
            tolerance=tolerance,
        )

        # TODO: DELETE LATER FOR TESTING
        # give r, find l(r) and m(r), so that v_1([l(r), m(r)]) = v_1([m(r), r]) = alpha
        assert almost_equal(
            a=get_double_prime_for_interval(
                segments=preference_1,
                epsilon=epsilon,
                start=l_for_r,
                end=m_for_r,
                cake_size=to_decimal(cake_size),
            ),
            b=get_double_prime_for_interval(
                segments=preference_1,
                epsilon=epsilon,
                start=m_for_r,
                end=lower_bound_candidate,
                cake_size=to_decimal(cake_size),
            ),
            tolerance=tolerance,
        ), "Should work"

        searched_value = get_double_prime_for_interval(
            segments=preference_i,
            epsilon=epsilon,
            start=lower_bound_candidate,
            end=to_decimal(cake_size),
            cake_size=to_decimal(cake_size),
        )

        print("***********")
        print(
            f"{lower_bound_candidate=}, {searched_value=}, {lower_bound_candidate=}, {cake_size=}"
        )
        print("***********")

        # Want v_i([0, l(r)])= v_i([(r, cake_size])
        desired_value = get_double_prime_for_interval(
            segments=preference_i,
            epsilon=epsilon,
            start=to_decimal(0),
            end=l_for_r,
            cake_size=to_decimal(cake_size),
        )

        if almost_equal(a=searched_value, b=desired_value, tolerance=tolerance):
            lower_bound = lower_bound_candidate
        else:
            break

    # Expand the range to find the upper bound
    upper_bound = found_r
    while upper_bound + epsilon <= cake_end:
        upper_bound_candidate = upper_bound + epsilon
        l_for_r, m_for_r = _find_l_and_m_given_r(
            r=upper_bound_candidate,
            cake_size=to_decimal(cake_size),
            alpha=alpha,
            preference_1=preference_1,
            epsilon=epsilon,
            tolerance=tolerance,
        )

        # TODO: DELETE LATER FOR TESTING
        # give r, find l(r) and m(r), so that v_1([l(r), m(r)]) = v_1([m(r), r]) = alpha
        assert almost_equal(
            a=get_double_prime_for_interval(
                segments=preference_1,
                epsilon=epsilon,
                start=l_for_r,
                end=m_for_r,
                cake_size=to_decimal(cake_size),
            ),
            b=get_double_prime_for_interval(
                segments=preference_1,
                epsilon=epsilon,
                start=m_for_r,
                end=upper_bound_candidate,
                cake_size=to_decimal(cake_size),
            ),
            tolerance=tolerance,
        ), "Should work"

        searched_value = get_double_prime_for_interval(
            segments=preference_i,
            epsilon=epsilon,
            start=upper_bound_candidate,
            end=to_decimal(cake_size),
            cake_size=to_decimal(cake_size),
        )

        print("***********")
        print(
            f"{upper_bound_candidate=}, {searched_value=}, {upper_bound_candidate=}, {cake_size=}"
        )
        print("***********")

        # Want v_i([0, l(r)])= v_i([(r, cake_size])
        desired_value = get_double_prime_for_interval(
            segments=preference_i,
            epsilon=epsilon,
            start=to_decimal(0),
            end=l_for_r,
            cake_size=to_decimal(cake_size),
        )

        if almost_equal(a=searched_value, b=desired_value, tolerance=tolerance):
            upper_bound = upper_bound_candidate
        else:
            break

    return lower_bound, upper_bound


def _find_range_r(
    preference_1: List[Segment],
    preference_i: List[Segment],
    epsilon: Decimal,
    r_start: Decimal,
    r_end: Decimal,
    alpha: Decimal,
    cake_size: Decimal,
    tolerance: Decimal = to_decimal(1e-10),
    max_iterations: int = 1000,
) -> Tuple[Decimal, Decimal]:
    found_l = _binary_search_find_r(
        preference_1=preference_1,
        preference_i=preference_i,
        epsilon=epsilon,
        r_start=r_start,
        r_end=r_end,
        alpha=alpha,
        cake_size=cake_size,
        tolerance=tolerance,
        max_iterations=max_iterations,
    )

    lower_bound, upper_bound = _expand_range_around_r(
        found_r=found_l,
        preference_1=preference_1,
        preference_i=preference_i,
        epsilon=epsilon,
        alpha=alpha,
        cake_size=cake_size,
        tolerance=tolerance,
    )

    return lower_bound, upper_bound


def _find_l_and_r_given_m(
    m: Decimal,
    cake_size: Decimal,
    alpha: Decimal,
    preference_1: List[Segment],
    epsilon: Decimal,
    tolerance: Decimal = to_decimal(1e-10),
) -> List[Decimal]:
    """find l and r given m: l(m) and r(m), so that v_1([l(m), m]) = v_1([m, r(m)]) = alpha"""
    l_for_m = _binary_search_left_to_right(
        preference=preference_1,
        cake_size=cake_size,
        epsilon=epsilon,
        start=to_decimal(0),
        end=to_decimal(m),
        target=alpha,
        tolerance=tolerance,
    )

    r_for_m = _binary_search_right_to_left(
        preference=preference_1,
        cake_size=cake_size,
        epsilon=epsilon,
        start=to_decimal(m),
        end=to_decimal(cake_size),
        target=alpha,
        tolerance=tolerance,
    )

    return [r_for_m, l_for_m]


def _binary_search_find_m(
    preference_1: List[Segment],
    preference_i: List[Segment],
    epsilon: Decimal,
    m_start: Decimal,
    m_end: Decimal,
    alpha: Decimal,
    cake_size: Decimal,
    tolerance: Decimal = to_decimal(1e-10),
    max_iterations: int = 1000,
) -> Decimal:
    cake_start = to_decimal(0)
    cake_end = to_decimal(cake_size)

    iteration = 0

    while m_end - m_start > tolerance and iteration < max_iterations:
        m = (m_start + m_end) / 2
        l_for_m, r_for_m = _find_l_and_r_given_m(
            m=m,
            cake_size=to_decimal(cake_size),
            alpha=alpha,
            preference_1=preference_1,
            epsilon=epsilon,
            tolerance=tolerance,
        )
        # TODO: DELETE LATER FOR TESTING
        # give m, l(m) and r(m), so that v_1([l(m), m]) = v_1([m, r(m)]) = alpha
        assert almost_equal(
            a=get_double_prime_for_interval(
                segments=preference_1,
                epsilon=epsilon,
                start=l_for_m,
                end=m,
                cake_size=to_decimal(cake_size),
            ),
            b=get_double_prime_for_interval(
                segments=preference_1,
                epsilon=epsilon,
                start=m,
                end=r_for_m,
                cake_size=to_decimal(cake_size),
            ),
            tolerance=tolerance,
        ), "Should work"

        searched_value = get_double_prime_for_interval(
            segments=preference_i,
            epsilon=epsilon,
            start=cake_start,
            end=l_for_m,
            cake_size=to_decimal(cake_size),
        )

        print("***********")
        print(f"{m=}, {searched_value=}, {cake_start=}, {l_for_m=}")
        print("***********")

        # Want v_i([0, l(m)])= v_i([(r(m), cake_size])
        desired_value = get_double_prime_for_interval(
            segments=preference_i,
            epsilon=epsilon,
            start=r_for_m,
            end=cake_end,
            cake_size=to_decimal(cake_size),
        )

        if almost_equal(a=searched_value, b=desired_value, tolerance=tolerance):
            return m

        if searched_value < desired_value:
            m_start = m
        else:
            m_end = m

        iteration = iteration + 1

    return to_decimal((m_start + m_end) / 2)


def _expand_range_around_m(
    found_m: Decimal,
    preference_1: List[Segment],
    preference_i: List[Segment],
    epsilon: Decimal,
    alpha: Decimal,
    cake_size: Decimal,
    tolerance: Decimal = to_decimal(1e-10),
) -> Tuple[Decimal, Decimal]:
    cake_start = to_decimal(0)
    cake_end = to_decimal(cake_size)

    # Expand the range to find the lower bound
    lower_bound = found_m
    while lower_bound - epsilon >= cake_start:
        lower_bound_candidate = lower_bound - epsilon
        l_for_m, r_for_m = _find_l_and_r_given_m(
            m=lower_bound_candidate,
            cake_size=to_decimal(cake_size),
            alpha=alpha,
            preference_1=preference_1,
            epsilon=epsilon,
            tolerance=tolerance,
        )

        # TODO: DELETE LATER FOR TESTING
        # give m, l(m) and r(m), so that v_1([l(m), m]) = v_1([m, r(m)]) = alpha
        assert almost_equal(
            a=get_double_prime_for_interval(
                segments=preference_1,
                epsilon=epsilon,
                start=l_for_m,
                end=lower_bound_candidate,
                cake_size=to_decimal(cake_size),
            ),
            b=get_double_prime_for_interval(
                segments=preference_1,
                epsilon=epsilon,
                start=lower_bound_candidate,
                end=r_for_m,
                cake_size=to_decimal(cake_size),
            ),
            tolerance=tolerance,
        ), "Should work"

        searched_value = get_double_prime_for_interval(
            segments=preference_i,
            epsilon=epsilon,
            start=cake_start,
            end=l_for_m,
            cake_size=to_decimal(cake_size),
        )

        print("***********")
        print(
            f"{lower_bound_candidate=}, {searched_value=}, {lower_bound_candidate=}, {cake_size=}"
        )
        print("***********")

        # Want v_i([0, l(m)])= v_i([(r(m), cake_size])
        desired_value = get_double_prime_for_interval(
            segments=preference_i,
            epsilon=epsilon,
            start=r_for_m,
            end=cake_end,
            cake_size=to_decimal(cake_size),
        )

        if almost_equal(a=searched_value, b=desired_value, tolerance=tolerance):
            lower_bound = lower_bound_candidate
        else:
            break

    # Expand the range to find the upper bound
    upper_bound = found_m
    while upper_bound + epsilon <= cake_end:
        upper_bound_candidate = upper_bound + epsilon
        l_for_m, r_for_m = _find_l_and_r_given_m(
            m=upper_bound_candidate,
            cake_size=to_decimal(cake_size),
            alpha=alpha,
            preference_1=preference_1,
            epsilon=epsilon,
            tolerance=tolerance,
        )

        # TODO: DELETE LATER FOR TESTING
        # give m, l(m) and r(m), so that v_1([l(m), m]) = v_1([m, r(m)]) = alpha
        assert almost_equal(
            a=get_double_prime_for_interval(
                segments=preference_1,
                epsilon=epsilon,
                start=l_for_m,
                end=upper_bound_candidate,
                cake_size=to_decimal(cake_size),
            ),
            b=get_double_prime_for_interval(
                segments=preference_1,
                epsilon=epsilon,
                start=upper_bound_candidate,
                end=r_for_m,
                cake_size=to_decimal(cake_size),
            ),
            tolerance=tolerance,
        ), "Should work"

        searched_value = get_double_prime_for_interval(
            segments=preference_i,
            epsilon=epsilon,
            start=cake_start,
            end=l_for_m,
            cake_size=to_decimal(cake_size),
        )

        print("***********")
        print(f"{upper_bound_candidate=}, {searched_value=}, {cake_start=}, {l_for_m=}")
        print("***********")

        # Want v_i([0, l(m)])= v_i([(r(m), cake_size])
        desired_value = get_double_prime_for_interval(
            segments=preference_i,
            epsilon=epsilon,
            start=r_for_m,
            end=cake_end,
            cake_size=to_decimal(cake_size),
        )

        if almost_equal(a=searched_value, b=desired_value, tolerance=tolerance):
            upper_bound = upper_bound_candidate
        else:
            break

    return lower_bound, upper_bound


def _find_range_m(
    preference_1: List[Segment],
    preference_i: List[Segment],
    epsilon: Decimal,
    m_start: Decimal,
    m_end: Decimal,
    alpha: Decimal,
    cake_size: Decimal,
    tolerance: Decimal = to_decimal(1e-10),
    max_iterations: int = 1000,
) -> Tuple[Decimal, Decimal]:
    found_m = _binary_search_find_m(
        preference_1=preference_1,
        preference_i=preference_i,
        epsilon=epsilon,
        m_start=m_start,
        m_end=m_end,
        alpha=alpha,
        cake_size=cake_size,
        tolerance=tolerance,
        max_iterations=max_iterations,
    )

    lower_bound, upper_bound = _expand_range_around_m(
        found_m=found_m,
        preference_1=preference_1,
        preference_i=preference_i,
        epsilon=epsilon,
        alpha=alpha,
        cake_size=cake_size,
        tolerance=tolerance,
    )

    return lower_bound, upper_bound


def _find_best_cuts_by_range(
    lower_l: Decimal,
    upper_l: Decimal,
    lower_m: Decimal,
    upper_m: Decimal,
    lower_r: Decimal,
    upper_r: Decimal,
) -> List[Decimal]:
    assert lower_l <= upper_l, "Wrong l cut range"
    assert lower_m <= upper_m, "Wrong m cut range"
    assert lower_r <= upper_r, "Wrong r cut range"

    return [upper_l, (lower_m + upper_m) / 2, lower_r]


def _handle_leftmost_rightmost(
    k: int,
    k_prime: int,
    alpha: Decimal,
    preference_1: List[Segment],
    preference_i: List[Segment],
    epsilon: Decimal,
    cake_size: Decimal,
    tolerance: Decimal,
) -> List[Decimal]:
    lower_l, upper_l = _find_range_l(
        preference_1=preference_1,
        preference_i=preference_i,
        epsilon=epsilon,
        l_start=to_decimal(0),
        l_end=to_decimal(cake_size),
        alpha=alpha,
        cake_size=cake_size,
        tolerance=tolerance,
    )

    lower_r, upper_r = _find_range_r(
        preference_1=preference_1,
        preference_i=preference_i,
        epsilon=epsilon,
        r_start=to_decimal(0),
        r_end=to_decimal(cake_size),
        alpha=alpha,
        cake_size=cake_size,
        tolerance=tolerance,
    )

    lower_m, upper_m = _find_range_m(
        preference_1=preference_1,
        preference_i=preference_i,
        epsilon=epsilon,
        m_start=to_decimal(0),
        m_end=to_decimal(cake_size),
        alpha=alpha,
        cake_size=cake_size,
        tolerance=tolerance,
    )

    return _find_best_cuts_by_range(
        lower_l=lower_l,
        upper_l=upper_l,
        lower_m=lower_m,
        upper_m=upper_m,
        lower_r=lower_r,
        upper_r=upper_r,
    )
    # if k, k' = (0, 3)
    #    0        1        2            3
    # [0, l] | [l, m] | [m, r] | [r, cake_size]

    # def _binary_search_find_range_l(
    #     preference_1: List[Segment],
    #     preference_i: List[Segment],
    #     epsilon: Decimal,
    #     l_start: Decimal,
    #     l_end: Decimal,
    #     alpha: Decimal,
    #     cake_size: Decimal,
    #     tolerance: Decimal = to_decimal(1e-10),
    #     max_iterations: int = 1000,
    # ) -> Decimal:
    #     cake_start = to_decimal(0)
    #     cake_end = to_decimal(cake_size)
    #
    #     iteration = 0
    #
    #     while l_start - l_end > tolerance and iteration < max_iterations:
    #         l = (l_start + l_end) / 2
    #         m_for_l, r_for_l = find_m_and_r_given_l(
    #             l=l,
    #             cake_size=to_decimal(cake_size),
    #             alpha=alpha,
    #             preference_1=preference_1,
    #             epsilon=epsilon,
    #         )
    #         # TODO: DELETE LATER FOR TESTING
    #         # give l, find m(l) and r(l), where v_1([l, m(l)]) = v_1([m(l), r(l)]) = alpha
    #         assert almost_equal(
    #             a=get_double_prime_for_interval(
    #                 segments=preference_1,
    #                 epsilon=epsilon,
    #                 start=l,
    #                 end=m_for_l,
    #             ),
    #             b=get_double_prime_for_interval(
    #                 segments=preference_1,
    #                 epsilon=epsilon,
    #                 start=m_for_l,
    #                 end=r_for_l,
    #             ),
    #             tolerance=tolerance,
    #         )
    #
    #         searched_value = get_double_prime_for_interval(
    #             segments=preference_i,
    #             epsilon=epsilon,
    #             start=cake_start,
    #             end=l,
    #         )
    #         print("***********")
    #         print("Handle_one_between: binary search")
    #         print(f"{l=}, {searched_value=}, {l=}, {cake_end=}")
    #         print("***********")
    #
    #         # Want v_i([0, l])= v_i([(r(l), cake_size])
    #         desired_value = get_double_prime_for_interval(
    #             segments=preference_i, epsilon=epsilon, start=r_for_l, end=cake_end
    #         )
    #
    #         if almost_equal(a=searched_value, b=desired_value, tolerance=tolerance):
    #             return l
    #
    #         if searched_value < desired_value:
    #             l_start = l
    #         else:
    #             l_end = l
    #
    #         iteration = iteration + 1
    #
    #     return to_decimal((l_start + l_end) / 2)

    print(f"Handling leftmost and rightmost: ({k}, {k_prime})")


CODITION_B_Handlers = {
    (0, 1): _handle_adjacent,
    (1, 2): _handle_adjacent,
    (2, 3): _handle_adjacent,
    (0, 2): _handle_one_between,
    (1, 3): _handle_one_between,
    (0, 3): _handle_leftmost_rightmost,
}


def _find_cuts_and_k_k_prime_for_agent_i_on_condition_b(
    alpha: Decimal,
    cake_size: Decimal,
    preference_1: List[Segment],
    preference_i: List[Segment],
    epsilon: Decimal,
    tolerance: Decimal = to_decimal("1e-3"),
) -> Dict[str, Any]:
    alpha = to_decimal(alpha)
    start = to_decimal(0)
    end = to_decimal(cake_size)

    for k, k_prime, others in POSSIBLE_K_AND_K_PRIME_COMBINATION_ON_CONDITION_B:
        handler = CODITION_B_Handlers.get((k, k_prime))
        if handler:
            try:
                cuts: List[Decimal] = handler(
                    k=k,
                    k_prime=k_prime,
                    alpha=alpha,
                    preference_1=preference_1,
                    preference_i=preference_i,
                    epsilon=epsilon,
                    cake_size=to_decimal(cake_size),
                    tolerance=tolerance,
                )
                yield {"cuts": cuts, "k": k, "k_prime": k_prime, "others": others}
            except Exception as e:
                print(f"Error processing handler for ({k}, {k_prime}): {e}")

        else:
            raise ValueError(f"No handler for combination: ({k}, {k_prime})")


def find_allocation_on_condition_b(
    preferences: Preferences,
    cake_size: Decimal,
    cuts: List[Decimal],
    k: int,
    k_prime: int,
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
