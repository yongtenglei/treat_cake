from decimal import Decimal
from typing import Any, Dict, List

from treat_cake.base_types import AssignedSlice, Preferences, Segment
from treat_cake.type_helper import almost_equal, to_decimal
from treat_cake.valuation import get_double_prime_for_interval, get_values_for_cuts


def check_condition_a(
    alpha: Decimal,
    preferences: Preferences,
    cake_size: int,
    epsilon: Decimal,
    tolerance: Decimal,
) -> bool:
    alpha = to_decimal(alpha)
    epsilon = to_decimal(epsilon)
    tolerance = to_decimal(tolerance)

    preference_a = preferences[0]

    # Find cuts and identify k
    results = _find_cuts_and_k_for_condition_a(
        alpha=alpha,
        preference=preference_a,
        cake_size=cake_size,
        epsilon=epsilon,
        tolerance=tolerance,
    )

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
            epsilon=epsilon,
            start=start_k,
            end=end_k,
            alpha=alpha,
        )
        if weak_preference[i]:
            weak_preference_idx.append(i)

    if sum(weak_preference) >= 2:
        print(
            f"Test A successful, {k=}, other agents (i and i') are {weak_preference_idx}"
        )
        return True
    else:
        return False


def _find_cuts_and_k_for_condition_a(
    alpha: Decimal,
    cake_size: int,
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
        epsilon=epsilon,
        start=start,
        end=end,
        target=alpha,
        tolerance=tolerance,
    )

    m = _binary_search_right_to_left(
        preference=preference,
        epsilon=epsilon,
        start=start,
        end=r,
        target=alpha,
        tolerance=tolerance,
    )

    l = _binary_search_right_to_left(
        preference=preference,
        epsilon=epsilon,
        start=start,
        end=m,
        target=alpha,
        tolerance=tolerance,
    )

    remained_value = get_double_prime_for_interval(
        segments=preference, epsilon=epsilon, start=start, end=l
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
        epsilon=epsilon,
        start=start,
        end=end,
        target=alpha,
        tolerance=tolerance,
    )

    r = _binary_search_right_to_left(
        preference=preference,
        epsilon=epsilon,
        start=l,
        end=end,
        target=alpha,
        tolerance=tolerance,
    )

    m = _binary_search_right_to_left(
        preference=preference,
        epsilon=epsilon,
        start=l,
        end=r,
        target=alpha,
        tolerance=tolerance,
    )

    remained_value = get_double_prime_for_interval(
        segments=preference, epsilon=epsilon, start=l, end=m
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
        epsilon=epsilon,
        start=start,
        end=end,
        target=alpha,
        tolerance=tolerance,
    )

    m = _binary_search_left_to_right(
        preference=preference,
        epsilon=epsilon,
        start=l,
        end=end,
        target=alpha,
        tolerance=tolerance,
    )

    r = _binary_search_right_to_left(
        preference=preference,
        epsilon=epsilon,
        start=m,
        end=end,
        target=alpha,
        tolerance=tolerance,
    )

    remained_value = get_double_prime_for_interval(
        segments=preference, epsilon=epsilon, start=m, end=r
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
        epsilon=epsilon,
        start=start,
        end=end,
        target=alpha,
        tolerance=tolerance,
    )

    m = _binary_search_left_to_right(
        preference=preference,
        epsilon=epsilon,
        start=l,
        end=end,
        target=alpha,
        tolerance=tolerance,
    )

    r = _binary_search_left_to_right(
        preference=preference,
        epsilon=epsilon,
        start=m,
        end=end,
        target=alpha,
        tolerance=tolerance,
    )

    remained_value = get_double_prime_for_interval(
        segments=preference, epsilon=epsilon, start=r, end=end
    )

    if remained_value < alpha:
        return {"cuts": [l, m, r], "k": 3}
    elif almost_equal(remained_value, alpha, tolerance=tolerance):
        equals.append(True)

    if len(equals) == 4 and all(equals) is True:
        print("All segments have the same value, treat the last piece as k")
        return {"cuts": [l, m, r], "k": 3}
    else:
        raise ValueError("Cannot find a valid cuts, CHECK IMPLEMENTATION")


def find_allocation_on_condition_a() -> List[AssignedSlice]:
    return []


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
) -> bool:
    alpha = to_decimal(alpha)
    epsilon = to_decimal(epsilon)
    tolerance = to_decimal(tolerance)

    preference_1 = preferences[0]

    # PERF: May accelerate this process by using "notebook", cache double values
    for i in range(1, len(preferences)):
        preference_i = preferences[i]
        results = _find_cuts_and_k_k_prime_for_agent_i_on_condition_b(
            alpha=alpha,
            cake_size=cake_size,
            preference_1=preference_1,
            preference_i=preference_i,
            epsilon=epsilon,
            tolerance=tolerance,
        )
        for result in results:
            cuts = result["cuts"]
            k = result["k"]
            k_prime = result["k_prime"]
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
                segments=preference_i, epsilon=epsilon, start=start_k, end=end_k
            )
            k_prime_value_i = get_double_prime_for_interval(
                segments=preference_i,
                epsilon=epsilon,
                start=start_k_prime,
                end=end_k_prime,
            )
            if k_value_i != k_prime_value_i:
                continue
            other_1_value_i = get_double_prime_for_interval(
                segments=preference_i,
                epsilon=epsilon,
                start=start_other_1,
                end=end_other_1,
            )
            other_2_value_i = get_double_prime_for_interval(
                segments=preference_i,
                epsilon=epsilon,
                start=start_other_2,
                end=end_other_2,
            )
            others_max_value_i = max(other_1_value_i, other_2_value_i)
            if not (
                k_value_i >= others_max_value_i
                and k_prime_value_i >= others_max_value_i
            ):
                continue

            # i. v_1(P_k) <= α and v_1(P_k′) <= α, and
            k_value_1 = get_double_prime_for_interval(
                segments=preference_1, epsilon=epsilon, start=start_k, end=end_k
            )
            k_prime_value_1 = get_double_prime_for_interval(
                segments=preference_1,
                epsilon=epsilon,
                start=start_k_prime,
                end=end_k_prime,
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
                )
                other_2_value_j = get_double_prime_for_interval(
                    segments=preference_j,
                    epsilon=epsilon,
                    start=start_other_2,
                    end=end_other_2,
                )
                others_max_value_j = max(other_1_value_j, other_2_value_j)

                k_value_j = get_double_prime_for_interval(
                    segments=preference_j, epsilon=epsilon, start=start_k, end=end_k
                )
                k_prime_value_j = get_double_prime_for_interval(
                    segments=preference_j,
                    epsilon=epsilon,
                    start=start_k_prime,
                    end=end_k_prime,
                )
                if (
                    k_value_j >= others_max_value_j
                    and k_prime_value_j >= others_max_value_j
                ):
                    return True
    return False


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
            epsilon=epsilon,
            start=to_decimal(0),
            end=cake_size,
            target=alpha,
            tolerance=tolerance,
        )

        m = _binary_search_right_to_left(
            preference=preference_1,
            epsilon=epsilon,
            start=to_decimal(0),
            end=r,
            target=alpha,
            tolerance=tolerance,
        )

        remained_value = get_double_prime_for_interval(
            segments=preference_i, epsilon=epsilon, start=to_decimal(0), end=m
        )

        desired_half_value = remained_value / 2

        l = _binary_search_left_to_right(
            preference=preference_i,
            epsilon=epsilon,
            start=to_decimal(0),
            end=m,
            target=desired_half_value,
            tolerance=tolerance,
        )

        # NOTE: For testing
        first_half_value = get_double_prime_for_interval(
            segments=preference_i, epsilon=epsilon, start=to_decimal(0), end=l
        )
        second_half_value = get_double_prime_for_interval(
            segments=preference_i, epsilon=epsilon, start=l, end=m
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
            segments=preference_i, epsilon=epsilon, start=l, end=r
        )

        desired_half_value = remained_value / 2

        m = _binary_search_left_to_right(
            preference=preference_i,
            epsilon=epsilon,
            start=l,
            end=r,
            target=desired_half_value,
            tolerance=tolerance,
        )

        # NOTE: For testing
        first_half_value = get_double_prime_for_interval(
            segments=preference_i, epsilon=epsilon, start=l, end=m
        )
        second_half_value = get_double_prime_for_interval(
            segments=preference_i, epsilon=epsilon, start=m, end=r
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
            epsilon=epsilon,
            start=to_decimal(0),
            end=cake_size,
            target=alpha,
            tolerance=tolerance,
        )

        m = _binary_search_left_to_right(
            preference=preference_i,
            epsilon=epsilon,
            start=l,
            end=cake_size,
            target=alpha,
            tolerance=tolerance,
        )

        remained_value = get_double_prime_for_interval(
            segments=preference_i, epsilon=epsilon, start=m, end=cake_size
        )

        desired_half_value = remained_value / 2

        r = _binary_search_left_to_right(
            preference=preference_i,
            epsilon=epsilon,
            start=m,
            end=cake_size,
            target=desired_half_value,
            tolerance=tolerance,
        )

        # NOTE: For testing
        first_half_value = get_double_prime_for_interval(
            segments=preference_i, epsilon=epsilon, start=m, end=r
        )
        second_half_value = get_double_prime_for_interval(
            segments=preference_i, epsilon=epsilon, start=r, end=cake_size
        )
        assert almost_equal(
            first_half_value, second_half_value, tolerance=tolerance
        ), "Should have almost the same value under the view of agent i"


def _handle_one_between(
    k: int,
    k_prime: int,
    alpha: Decimal,
    preference_1: List[Segment],
    preference_i: List[Segment],
    epsilon: Decimal,
    cake_size: Decimal,
    tolerance: Decimal,
) -> List[Decimal]:
    # if k, k' = (0, 2)
    #    0        1        2            3
    # [0, l] | [l, m] | [m, r] | [r, cake_size]
    #                                   1
    # give l, find m(l), where v_1([l, m(l)]) = alpha (second piece)
    # keep move l, making v_i([0, l]) = v_i([m(l), r])
    if k == 0 and k_prime == 2:

        def find_m_given_l(
            l: Decimal,
            r: Decimal,
            alpha: Decimal,
            preference_1: List[Segment],
            epsilon: Decimal,
        ) -> Decimal:
            """find m given l: m(l), so that v_1(l, m(l)) = alpha (second piece)"""
            return _binary_search_left_to_right(
                preference=preference_1,
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
                m_for_l = find_m_given_l(
                    l=l,
                    r=original_l_end,
                    alpha=alpha,
                    preference_1=preference_1,
                    epsilon=epsilon,
                )
                # TODO: DELETE LATER FOR TESTING
                # give l, find m(l), where v_1([l, m(l)]) = alpha (second piece) = v_1([r, cake_size])
                assert almost_equal(
                    a=get_double_prime_for_interval(
                        segments=preference_1,
                        epsilon=epsilon,
                        start=l,
                        end=m_for_l,
                    ),
                    b=get_double_prime_for_interval(
                        segments=preference_1,
                        epsilon=epsilon,
                        start=original_l_end,
                        end=to_decimal(cake_size),
                    ),
                    tolerance=tolerance,
                )

                searched_value = get_double_prime_for_interval(
                    segments=preference_i, epsilon=epsilon, start=to_decimal(0), end=l
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
                )
                if almost_equal(a=searched_value, b=desired_value, tolerance=tolerance):
                    return l

                if searched_value < desired_value:
                    l_start = l
                else:
                    l_end = l

                iteration = iteration + 1

            return to_decimal((l_start + l_end) / 2)

        r = _binary_search_right_to_left(
            preference=preference_1,
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
        m = find_m_given_l(
            l=l,
            r=r,
            alpha=alpha,
            preference_1=preference_1,
            epsilon=epsilon,
        )
        return [l, m, r]

    # if k, k' = (1, 3)
    #    0        1        2            3
    # [0, l] | [l, m] | [m, r] | [r, cake_size]
    #    1
    # give r, find m(r), where v_1([m(r), r]) = alpha (third piece) = v_1([(0, l)])
    # keep move r, making v_i([l, m(r)]) = v_i([r, cake_size])
    if k == 1 and k_prime == 3:

        def find_m_given_r(
            l: Decimal,
            r: Decimal,
            alpha: Decimal,
            preference_1: List[Segment],
            epsilon: Decimal,
        ) -> Decimal:
            """find m given r: m(r), so that v_1(m(r), r) = alpha (third piece)"""
            return _binary_search_left_to_right(
                preference=preference_1,
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
                m_for_r = find_m_given_r(
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
                    ),
                    b=get_double_prime_for_interval(
                        segments=preference_1,
                        epsilon=epsilon,
                        start=to_decimal(0),
                        end=original_r_start,
                    ),
                    tolerance=tolerance,
                )

                searched_value = get_double_prime_for_interval(
                    segments=preference_i,
                    epsilon=epsilon,
                    start=r,
                    end=to_decimal(cake_size),
                )
                print("***********")
                print("Handle_one_between: binary search")
                print(f"{r=}, {searched_value=}, {r=}, {cake_size=}")
                print("***********")

                # Want v_i([l, m(r)])= v_i([(r, cake_size])
                desired_value = get_double_prime_for_interval(
                    segments=preference_i, epsilon=epsilon, start=l, end=m_for_r
                )

                if almost_equal(a=searched_value, b=desired_value, tolerance=tolerance):
                    return r

                if searched_value < desired_value:
                    r_end = r
                else:
                    r_start = r

                iteration = iteration + 1

            return to_decimal((r_start + r_end) / 2)

        l = _binary_search_left_to_right(
            preference=preference_1,
            epsilon=epsilon,
            start=to_decimal(0),
            end=cake_size,
            target=alpha,
            tolerance=tolerance,
        )
        r_start = to_decimal(l)
        l_end = to_decimal(cake_size)
        r = _binary_search_case_1_3(
            preference_1=preference_1,
            preference_i=preference_i,
            epsilon=epsilon,
            r_start=r_start,
            r_end=l_end,
            cake_size=to_decimal(cake_size),
            alpha=alpha,
            tolerance=tolerance,
        )
        m = find_m_given_r(
            l=l,
            r=r,
            alpha=alpha,
            preference_1=preference_1,
            epsilon=epsilon,
        )
        return [l, m, r]


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
    # if k, k' = (0, 3)
    #    0        1        2            3
    # [0, l] | [l, m] | [m, r] | [r, cake_size]

    def find_m_and_r_given_l(
        l: Decimal,
        cake_size: Decimal,
        alpha: Decimal,
        preference_1: List[Segment],
        epsilon: Decimal,
    ) -> List[Decimal]:
        """find m and r given l: m(l) and r(l), so that v_1([l, m(l)]) = v_1([m(l), r(l)]) = alpha"""
        m_for_l = _binary_search_left_to_right(
            preference=preference_1,
            epsilon=epsilon,
            start=to_decimal(l),
            end=to_decimal(cake_size),
            target=alpha,
            tolerance=tolerance,
        )

        r_for_l = _binary_search_left_to_right(
            preference=preference_1,
            epsilon=epsilon,
            start=to_decimal(m_for_l),
            end=to_decimal(cake_size),
            target=alpha,
            tolerance=tolerance,
        )

        return [m_for_l, r_for_l]

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
    cake_size: int,
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
            cuts = handler(
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
        else:
            raise ValueError(f"No handler for combination: ({k}, {k_prime})")


def find_allocation_on_condition_b() -> List[AssignedSlice]:
    return []


def _binary_search_left_to_right(
    preference: List[Segment],
    epsilon: Decimal,
    start: Decimal,
    end: Decimal,
    target: Decimal,
    tolerance: Decimal = 1e-10,
    max_iterations: int = 1000,
) -> Decimal:
    original_start = start
    iteration = 0

    while end - start > tolerance and iteration < max_iterations:
        mid = to_decimal((start + end) / 2)
        searched_value = get_double_prime_for_interval(
            preference, epsilon, original_start, mid
        )
        print("***********")
        print(f"{mid=}, {searched_value=}, {start=}, {end=}")
        print("***********")

        if abs(searched_value - target) < tolerance:
            return mid

        if searched_value < target:
            start = mid
        else:
            end = mid

        iteration = iteration + 1
    return to_decimal((start + end) / 2)


def _binary_search_right_to_left(
    preference: List[Segment],
    epsilon: Decimal,
    start: Decimal,
    end: Decimal,
    target: Decimal,
    tolerance: Decimal = 1e-10,
    max_iterations: int = 1000,
) -> Decimal:
    original_end = end
    iteration = 0

    while end - start > tolerance and iteration < max_iterations:
        mid = to_decimal((start + end) / 2)
        searched_value = get_double_prime_for_interval(
            preference, epsilon, mid, original_end
        )
        print("***********")
        print(f"{mid=}, {searched_value=}, {start=}, {end=}")
        print("***********")

        if abs(searched_value - target) < tolerance:
            return mid

        if searched_value < target:
            end = mid
        else:
            start = mid

        iteration = iteration + 1
    return to_decimal((start + end) / 2)


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


def get_range_by_cuts(
    cuts: List[Decimal], k: int, cake_size: Decimal
) -> (Decimal, Decimal):
    assert len(cuts) == 3, "Should have 3 cut points"

    l, m, r = cuts

    start: Decimal = to_decimal(-1)
    end: Decimal = to_decimal(-1)

    if k == 0:
        start = to_decimal(0)
        end = to_decimal(l)
    elif k == 1:
        start = to_decimal(l)
        end = to_decimal(m)
    elif k == 2:
        start = to_decimal(m)
        end = to_decimal(r)
    elif k == 3:
        start = to_decimal(r)
        end = to_decimal(cake_size)

    return start, end


def _check_if_weakly_prefer_piece_k(
    preference: List[Segment],
    epsilon: Decimal,
    start: Decimal,
    end: Decimal,
    alpha: Decimal,
) -> bool:
    return alpha <= get_double_prime_for_interval(
        segments=preference, epsilon=epsilon, start=start, end=end
    )
