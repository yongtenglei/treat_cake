from decimal import Decimal, getcontext
from typing import List

from pytest import raises

from base_types import Segment
from type_helper import scale_back_from_unit, scale_to_unit, to_decimal
from values import get_value_for_interval

getcontext().prec = 15


def _v(segments: List[Segment], a: Decimal, b: Decimal) -> Decimal:
    v = get_value_for_interval(segments, a, b)
    print(f"v={v}({a=}, {b=})")
    return v


def _v_prime(
    segments: List[Segment],
    epsilon: Decimal,
    a: Decimal,
    b: Decimal,
) -> Decimal:
    v = _v(segments, a, b) / 2 + epsilon * abs(b - a)
    print(f"v_prime={v}({a=}, {b=})")
    return v


def get_double_prime_for_interval(
    segments: List[Segment],
    epsilon: Decimal,
    start: Decimal,
    end: Decimal,
    cake_size: Decimal,
) -> Decimal:
    assert 0 <= start <= end, "start or end out of range"

    # Make sure using Decimal
    epsilon = to_decimal(epsilon)
    start = to_decimal(start)
    end = to_decimal(end)
    cake_size = to_decimal(cake_size)

    # Only one segment
    if end <= 1:
        return _v_double_prime(segments, epsilon, start, end, cake_size)

    # Multi-segments
    total = to_decimal(0)

    start_int = int(start)
    end_int = int(end)

    if start == start_int and end == end_int:
        return _v_double_prime(segments, epsilon, start, end, cake_size)

    # Start segments
    if start != start_int:
        first_segment_end = to_decimal(start_int + 1)
        total += _v_double_prime(segments, epsilon, start, first_segment_end, cake_size)

    # Intermediate segments
    if start_int + 1 < end_int:
        total += _v_double_prime(
            segments, epsilon, to_decimal(start_int + 1), to_decimal(end_int), cake_size
        )

    # Last segments
    if end != end_int:
        last_segment_start = to_decimal(end_int)
        total += _v_double_prime(segments, epsilon, last_segment_start, end, cake_size)

    return total


def _v_double_prime(
    segments: List[Segment],
    delta: Decimal,
    a: Decimal,
    b: Decimal,
    cake_size: Decimal,
) -> Decimal:
    # Letting delta := epsilon, so,
    # any epsilon-envy-free allocation for (v_double_prime) is 5*epsilon-envy-free for (v_prime) for each agent.

    a_unit = scale_to_unit(a, cake_size)
    b_unit = scale_to_unit(b, cake_size)

    print(f"{a_unit=}, {b_unit=}")

    delta = to_decimal(delta)
    a_unit = to_decimal(a_unit)
    b_unit = to_decimal(b_unit)

    # Get the grid points around a and b
    a_underline_unit = underline(a_unit, delta)
    a_overline_unit = overline(a_unit, delta)
    b_underline_unit = underline(b_unit, delta)
    b_overline_unit = overline(b_unit, delta)
    print(f"{a_underline_unit=}")
    print(f"{a_overline_unit=}")
    print(f"{b_underline_unit=}")
    print(f"{b_overline_unit=}")
    assert a_underline_unit <= a_unit <= a_overline_unit, "Wrong grid points"
    assert b_underline_unit <= b_unit <= b_overline_unit, "Wrong grid points"

    a_underline = scale_back_from_unit(a_underline_unit, cake_size)
    b_overline = scale_back_from_unit(b_overline_unit, cake_size)
    a_overline = scale_back_from_unit(a_overline_unit, cake_size)
    b_underline = scale_back_from_unit(b_underline_unit, cake_size)

    v_prime_a_under_b_over = _v_prime(segments, delta, a_underline, b_overline)
    v_prime_a_over_b_under = _v_prime(segments, delta, a_overline, b_underline)
    print(f"{v_prime_a_under_b_over=}({a_underline=}, {b_overline=})")
    print(f"{v_prime_a_over_b_under=}({a_overline=}, {b_underline=})")

    if a_overline_unit - a_unit >= b_unit - b_underline_unit:
        print("Case 1")
        v_prime_a_under_b_under = _v_prime(segments, delta, a_underline, b_underline)
        print(f"{v_prime_a_under_b_under=}({a_underline=}, {b_underline=})")
        v_double_prime = (
            ((a_overline_unit - a_unit) - (b_unit - b_underline_unit))
            / delta
            * v_prime_a_under_b_under
            + (b_unit - b_underline_unit) / delta * v_prime_a_under_b_over
            + (a_unit - a_underline_unit) / delta * v_prime_a_over_b_under
        )

        if (
            a_unit == 0
            and (a_unit - a_underline_unit) / delta * v_prime_a_over_b_under == 0
        ):
            # If start from 0, need to compensate the last term
            print(
                f"Start from 0, compensate the last term: {v_double_prime} + {v_prime_a_over_b_under}"
            )

            v_double_prime += v_prime_a_over_b_under
        print(f"v_double_prime={v_double_prime}({a_unit=}, {b_unit=})")
        print("====end====")
        return v_double_prime
    elif a_overline_unit - a_unit <= b_unit - b_underline_unit:
        print("Case 2")
        v_prime_a_over_b_over = _v_prime(segments, delta, a_overline, b_overline)
        print(f"{v_prime_a_over_b_over=}({a_overline=}, {b_overline=})")
        v_double_prime = (
            ((b_unit - b_underline_unit) - (a_overline_unit - a_unit))
            / delta
            * v_prime_a_over_b_over
            + (a_overline_unit - a_unit) / delta * v_prime_a_under_b_over
            + (b_overline_unit - b_unit) / delta * v_prime_a_over_b_under
        )
        print(f"v_double_prime={v_double_prime}({a_unit=}, {b_unit=})")
        print("====end====")

        return v_double_prime

    raise ValueError("Should not reach here")


def overline(x, delta, epsilon=Decimal("1e-10")) -> Decimal:
    assert 0 <= x <= 1, f"got {x}, expect it between [0, 1]"

    x = to_decimal(x)
    delta = to_decimal(delta)

    if x < delta or x == 0:
        return delta

    if x == 1:
        return x

    v = (x / delta).to_integral_value(rounding="ROUND_CEILING") * delta

    # If x is exactly a multiple of delta, step up to the next multiple
    # considering floating point precision issues
    if abs(x % delta) < epsilon or abs(delta - (x % delta)) < epsilon:
        v += delta

    return min(v, to_decimal(1))


def underline(x, delta, epsilon=Decimal("1e-10")) -> Decimal:
    assert 0 <= x <= 1, f"got {x}, expect it between [0, 1]"

    x = to_decimal(x)
    delta = to_decimal(delta)

    if x < delta or x == 0:
        return to_decimal(0)

    if x == 1:
        return x - delta

    # Check if x is an exact multiple of delta,
    # considering floating point precision issues
    if abs(x % delta) < epsilon or abs(delta - (x % delta)) < epsilon:
        v = (x / delta - 1).to_integral_value(rounding="ROUND_FLOOR") * delta
    else:
        v = (x / delta).to_integral_value(rounding="ROUND_FLOOR") * delta

    return max(v, to_decimal(0))


def get_values_for_cuts(
    preference: List[Segment], cuts: List[Decimal], cake_size: Decimal, epsilon: Decimal
) -> List[Decimal]:
    slice_values = []

    start = 0
    for end in cuts:
        value = get_double_prime_for_interval(
            preference, epsilon, start, end, cake_size=cake_size
        )
        slice_values.append(value)
        start = end
    # Last piece
    slice_values.append(get_value_for_interval(preference, cuts[-1], cake_size))
    return slice_values
