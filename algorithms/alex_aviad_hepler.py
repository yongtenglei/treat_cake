import logging
from decimal import Decimal, getcontext
from typing import List, Tuple

from base_types import Segment
from type_helper import de_norm, to_decimal
from valuation import get_double_prime_for_interval
from values import get_value_for_interval

getcontext().prec = 15


def _binary_search_left_to_right(
    preference: List[Segment],
    cake_size: Decimal,
    epsilon: Decimal,
    start: Decimal,
    end: Decimal,
    target: Decimal,
    tolerance: Decimal = to_decimal(1e-10),
    max_iterations: int = 1000,
) -> Decimal:
    cake_size = to_decimal(cake_size)
    epsilon = to_decimal(epsilon)
    start = to_decimal(start)
    end = to_decimal(end)
    target = to_decimal(target)
    # getcontext().prec = 15
    tolerance = to_decimal("1e-10") if tolerance < to_decimal("1e-10") else tolerance
    epsilon = to_decimal("1e-15") if epsilon < to_decimal("1e-15") else epsilon

    full_cake = get_double_prime_for_interval(
        segments=preference,
        epsilon=epsilon,
        start=start,
        end=end,
        cake_size=cake_size,
    )
    if full_cake < target:
        # logging.warning(
        #     f"binary search left to right: {start=}, {end=}, {target=}, but {cake_size=}, {full_cake=}, returned {end=}"
        # )
        return end

    original_start = start
    iteration = 0

    while end - start > tolerance and iteration < max_iterations:
        mid = to_decimal((start + end) / 2)
        searched_value = get_double_prime_for_interval(
            segments=preference,
            epsilon=epsilon,
            start=original_start,
            end=mid,
            cake_size=cake_size,
        )
        logging.info("***********")
        logging.info(f"{mid=}, {searched_value=}, {original_start=}, {mid=}")
        logging.info("***********")

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
    cake_size: Decimal,
    epsilon: Decimal,
    start: Decimal,
    end: Decimal,
    target: Decimal,
    tolerance: Decimal = to_decimal(1e-10),
    max_iterations: int = 1000,
) -> Decimal:
    cake_size = to_decimal(cake_size)
    epsilon = to_decimal(epsilon)
    start = to_decimal(start)
    end = to_decimal(end)
    target = to_decimal(target)
    getcontext().prec = 15
    # tolerance = to_decimal("1e-10") if tolerance < to_decimal("1e-10") else tolerance
    epsilon = to_decimal("1e-15")

    full_cake = get_double_prime_for_interval(
        segments=preference,
        epsilon=epsilon,
        start=start,
        end=end,
        cake_size=cake_size,
    )
    if full_cake < target:
        # logging.warning(
        #     f"binary search right to left: {start=}, {end=}, {target=}, but {cake_size=}, {full_cake=}, returned {start=}"
        # )
        return start

    original_end = end
    iteration = 0

    while end - start > tolerance and iteration < max_iterations:
        mid = to_decimal((start + end) / 2)

        searched_value = get_double_prime_for_interval(
            segments=preference,
            epsilon=epsilon,
            start=mid,
            end=original_end,
            cake_size=to_decimal(cake_size),
        )
        logging.info("***********")
        logging.info(f"{mid=}, {searched_value=}, {mid=}, {original_end=}")
        logging.info("***********")

        if abs(searched_value - target) < tolerance:
            return mid

        if searched_value < target:
            end = mid
        else:
            start = mid

        iteration = iteration + 1

    return to_decimal((start + end) / 2)


def equipartition(
    preference: List[Segment],
    cake_size: Decimal,
    epsilon: Decimal,
    start: Decimal,
    end: Decimal,
    tolerance: Decimal = to_decimal(1e-10),
) -> List[Decimal]:
    # tolerance = to_decimal("1e-10")
    epsilon = Decimal(epsilon)
    epsilon = to_decimal("1e-15")
    start = Decimal(start)
    end = Decimal(end)

    total_v = get_double_prime_for_interval(
        segments=preference, epsilon=epsilon, start=start, end=end, cake_size=cake_size
    )
    segment_value = total_v / 4

    # Finding cuts at 1/4, 1/2, and 3/4 of the cake
    first_cut = _binary_search_left_to_right(
        preference=preference,
        cake_size=cake_size,
        epsilon=epsilon,
        start=start,
        end=end,
        target=segment_value,
        tolerance=tolerance,
    )
    logging.info(f"find l cut: {first_cut}")
    logging.error(f"find l cut: {first_cut}")

    second_cut = _binary_search_left_to_right(
        preference=preference,
        cake_size=cake_size,
        epsilon=epsilon,
        start=first_cut,
        end=end,
        target=segment_value,
        tolerance=tolerance,
    )
    logging.info(f"find m cut: {second_cut}")
    logging.error(f"find m cut: {second_cut}")

    third_cut = _binary_search_left_to_right(
        preference=preference,
        cake_size=cake_size,
        epsilon=epsilon,
        start=second_cut,
        end=end,
        target=segment_value,
        tolerance=tolerance,
    )
    logging.info(f"find r cut: {third_cut}")
    logging.error(f"find r cut: {third_cut}")

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
    cake_size: Decimal,
    epsilon: Decimal,
    start: Decimal,
    end: Decimal,
    alpha: Decimal,
) -> bool:
    whole_cake_value = get_value_for_interval(
        segments=preference, start=to_decimal(0), end=to_decimal(end)
    )
    v = de_norm(
        v=get_double_prime_for_interval(
            segments=preference,
            epsilon=epsilon,
            start=start,
            end=end,
            cake_size=to_decimal(cake_size),
        ),
        whole_cake_value=whole_cake_value,
    )
    logging.error(f"_check_if_weakly_prefer_piece_k: ({start}-{end}), {alpha=}, {v=}")
    return alpha <= v
