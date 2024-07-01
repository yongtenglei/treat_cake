from decimal import Decimal
from typing import List

from treat_cake.base_types import Segment, AssignedSlice
from treat_cake.type_helper import to_decimal
from treat_cake.valuation import get_double_prime_for_interval, get_values_for_cuts


def check_condition_a(
    alpha: Decimal,
    preference: List[Segment],
    current_cuts: List[Decimal],
    cake_size: int,
    epsilon: Decimal,
) -> bool:
    k = _find_k(preference, current_cuts, cake_size, epsilon)

    return False


def _find_k(
    preference: List[Segment], cuts: List[Decimal], cake_size: int, epsilon: Decimal
) -> int:

    values = get_values_for_cuts(preference, cuts, cake_size, epsilon)

    min_index = values.index(min(values))

    print(f"4 pieces have values {values}, find the last preferred k: {min_index}")

    return min_index


def _find_cuts_for_condition_a(
    alpha: Decimal,
    preference: List[Segment],
    cake_size: int,
    epsilon: Decimal,
    start: Decimal,
    end: Decimal,
    tolerant: Decimal = 1e-3,
):
    # if k == 0
    # [0, l] | [l, m] | [m, r] | [r, cake_size]
    #    *       3         2          1
    r = _binary_search_left_to_right(preference, epsilon, start, end, alpha, tolerant)

    # if k == 1
    # [0, l] | [l, m] | [m, r] | [r, cake_size]
    #    1       *         3          2

    # if k == 2
    # [0, l] | [l, m] | [m, r] | [r, cake_size]
    #    1       2         *          3

    # if k == 3
    # [0, l] | [l, m] | [m, r] | [r, cake_size]
    #    1       2         3          *
    pass


def find_allocation_on_condition_a() -> List[AssignedSlice]:
    return []


def check_condition_b(
    alpha: Decimal,
    preference: List[Segment],
    current_cuts: List[Decimal],
    cake_size: int,
    epsilon: Decimal,
) -> bool:
    k = _find_k(preference, current_cuts, cake_size, epsilon)

    return False


def find_allocation_on_condition_b() -> List[AssignedSlice]:
    return []


def _binary_search_left_to_right(
    preference: List[Segment],
    epsilon: Decimal,
    start: Decimal,
    end: Decimal,
    target: Decimal,
    tolerant: Decimal = 1e-10,
    max_iterations: int = 1000,
) -> Decimal:
    original_start = start
    iteration = 0

    while end - start > tolerant and iteration < max_iterations:
        mid = to_decimal((start + end) / 2)
        searched_value = get_double_prime_for_interval(
            preference, epsilon, original_start, mid
        )
        print("***********")
        print(f"{mid=}, {searched_value=}, {start=}, {end=}")
        print("***********")

        if abs(searched_value - target) < tolerant:
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
    tolerant: Decimal = 1e-10,
    max_iterations: int = 1000,
) -> Decimal:
    original_end = end
    iteration = 0

    while end - start > tolerant and iteration < max_iterations:
        mid = to_decimal((start + end) / 2)
        searched_value = get_double_prime_for_interval(
            preference, epsilon, mid, original_end
        )
        print("***********")
        print(f"{mid=}, {searched_value=}, {start=}, {end=}")
        print("***********")

        if abs(searched_value - target) < tolerant:
            return mid

        if searched_value < target:
            end = mid
        else:
            start = mid

        iteration = iteration + 1
    return to_decimal((start + end) / 2)
