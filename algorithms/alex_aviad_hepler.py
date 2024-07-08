from decimal import Decimal
from typing import List, Tuple

from ..base_types import Segment
from ..type_helper import to_decimal
from ..valuation import get_double_prime_for_interval


def _binary_search_left_to_right(
    preference: List[Segment],
    epsilon: Decimal,
    start: Decimal,
    end: Decimal,
    target: Decimal,
    tolerance: Decimal = to_decimal(1e-10),
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
    tolerance: Decimal = to_decimal(1e-10),
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
    cuts: List[Decimal],
    k: int,
    cake_size: Decimal,
) -> Tuple[Decimal, Decimal]:
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
