from decimal import Decimal
from typing import List, Dict, Any

from treat_cake.base_types import Segment, AssignedSlice, Preferences
from treat_cake.type_helper import to_decimal, almost_equal
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

    l, m, r = results["cuts"]
    k = results["k"]

    start_k: Decimal = to_decimal(-1)
    end_k: Decimal = to_decimal(-1)

    if k == 0:
        start_k = to_decimal(0)
        end_k = to_decimal(l)
    elif k == 1:
        start_k = to_decimal(l)
        end_k = to_decimal(m)
    elif k == 2:
        start_k = to_decimal(m)
        end_k = to_decimal(r)
    elif k == 3:
        start_k = to_decimal(r)
        end_k = to_decimal(cake_size)

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
    tolerance: Decimal = 1e-3,
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


def find_allocation_on_condition_a() -> List[AssignedSlice]:
    return []


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

    for i in range(1, len(preferences)):
        preference = preferences[i]
        results = _find_cuts_and_k_k_prime_for_agent_i_on_condition_b(
            alpha=alpha,
            cake_size=cake_size,
            preference=preference,
            epsilon=epsilon,
            tolerance=tolerance,
        )

        l, m, r = results["cuts"]
        k = results["k"]

        start_k: Decimal = to_decimal(-1)
        end_k: Decimal = to_decimal(-1)

        if k == 0:
            start_k = to_decimal(0)
            end_k = to_decimal(l)
        elif k == 1:
            start_k = to_decimal(l)
            end_k = to_decimal(m)
        elif k == 2:
            start_k = to_decimal(m)
            end_k = to_decimal(r)
        elif k == 3:
            start_k = to_decimal(r)
            end_k = to_decimal(cake_size)

        weak_preference = [False for _ in range(len(preferences))]
        assert len(weak_preference) == 4

        weak_preference_idx = []
        # check if at least two of the other agents weakly prefer piece k
        # i. v_1(P_k) <= α and v_1(P_k′) <= α, and
        # ii. (v_i(P_k′) =)v_i(P_k) >= max_t v_i(P_t), and
        # iii. there exists i′ ∈ {2, 3, 4} ∖ {i} such that v_i′(P_k) ≥ max_t v_i′(P_t), and
        # iv. there exists i′ ∈ {2, 3, 4} ∖ {i} with v_i′(P_k′) ≥ max_t v_i′(P_t).
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

        # TODO: NEED to IMPLEMENT
        if sum(weak_preference) >= 2:
            print(
                f"Test A successful, {k=}, other agents (i and i') are {weak_preference_idx}"
            )
            return True
        else:
            return False

    return False


POSSIBLE_PIECES_ON_CONDITION_B = [
    (0, 1),
    (0, 2),
    (0, 3),
    (1, 2),
    (1, 3),
    (2, 3),
]


def _handle_adjacent(k: int, k_prime: int) -> Dict[str, Any]:
    print(f"Handling adjacent: ({k}, {k_prime})")


def _handle_one_between(k: int, k_prime: int) -> Dict[str, Any]:
    print(f"Handling one piece between: ({k}, {k_prime})")


def _handle_leftmost_rightmost(k: int, k_prime: int) -> Dict[str, Any]:
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
    preference: List[Segment],
    epsilon: Decimal,
    tolerance: Decimal = 1e-3,
) -> Dict[str, Any]:
    """Could simplify code, but lost readability."""

    alpha = to_decimal(alpha)
    start = to_decimal(0)
    end = to_decimal(cake_size)

    for k, k_prime in POSSIBLE_PIECES_ON_CONDITION_B:
        handler = CODITION_B_Handlers.get((k, k_prime))
        if handler:
            handler(k, k_prime)
        else:
            print(f"No handler for combination: ({k}, {k_prime})")


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
