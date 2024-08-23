from decimal import Decimal, getcontext
from typing import List

from base_types import Segment
from type_helper import to_decimal
from valuation import get_double_prime_for_interval

getcontext().prec = 15


def _find_balanced_cut_for_adjacent(
    preference: List[Segment],
    cake_size: Decimal,
    epsilon: Decimal,
    left: Decimal,
    right: Decimal,
    tolerance: Decimal = Decimal("1e-10"),
    max_iterations: int = 1000,
) -> Decimal:
    getcontext().prec = 15
    tolerance = to_decimal("1e-7")
    start = left
    end = right
    iteration = 0

    while end - start > tolerance / to_decimal(1000) and iteration < max_iterations:
        m = (start + end) / 2

        first_half_value = get_double_prime_for_interval(
            segments=preference,
            epsilon=epsilon,
            start=left,
            end=m,
            cake_size=cake_size,
        )
        second_half_value = get_double_prime_for_interval(
            segments=preference,
            epsilon=epsilon,
            start=m,
            end=right,
            cake_size=cake_size,
        )

        if abs(first_half_value - second_half_value) < tolerance:
            return m

        if first_half_value < second_half_value:
            start = m
        else:
            end = m

        iteration += 1

    return (start + end) / 2
