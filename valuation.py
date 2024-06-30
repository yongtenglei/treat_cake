from decimal import Decimal, getcontext
from typing import List

from treat_cake.base_types import Segment
from treat_cake.values import get_value_for_interval

# 设置全局浮点数精度
getcontext().prec = 50


def _v(segments: List[Segment], a: Decimal, b: Decimal) -> Decimal:
    v = get_value_for_interval(segments, float(a), float(b))
    print(f"v={v}({a=}, {b=})")
    return Decimal(v)


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
    segments: List[Segment], epsilon: Decimal, start: Decimal, end: Decimal
) -> Decimal:

    assert 0 <= start <= end, "start or end out of range"

    # Only one segment
    if end <= 1:
        return _v_double_prime(segments, epsilon, start, end)

    # Multi-segments
    total = Decimal(0)

    start_int = int(start)
    end_int = int(end)

    if start == start_int and end == end_int:
        return _v_double_prime(segments, epsilon, start, end)

    # Start segments
    if start != start_int:
        first_segment_end = Decimal(start_int + 1)
        total += _v_double_prime(segments, epsilon, start, first_segment_end)

    # Intermedia segments
    if start_int + 1 < end_int:
        total += _v_double_prime(
            segments, epsilon, Decimal(start_int + 1), Decimal(end_int)
        )

    # Last segments
    if end != end_int:
        last_segment_start = Decimal(end_int)
        total += _v_double_prime(segments, epsilon, last_segment_start, end)

    return total


def _v_double_prime(
    segments: List[Segment], delta: Decimal, a: Decimal, b: Decimal
) -> Decimal:

    # Letting delta := epsilon, so,
    # any epsilon-envy-free allocation for (v_double_prime) is 5*epsilon-envy-free for (v_prime) for each agent.

    print(f"{a=}, {b=}")

    # Get the grid points around a and b
    a_underline = underline(a, delta)
    a_overline = overline(a, delta)
    b_underline = underline(b, delta)
    b_overline = overline(b, delta)
    print(f"{a_underline=}")
    print(f"{a_overline=}")
    print(f"{b_underline=}")
    print(f"{b_overline=}")
    assert a_underline <= a <= a_overline, "Wrong grid points"
    assert b_underline <= b <= b_overline, "Wrong grid points"

    v_prime_a_under_b_over = _v_prime(segments, delta, a_underline, b_overline)
    v_prime_a_over_b_under = _v_prime(segments, delta, a_overline, b_underline)
    print(f"{v_prime_a_under_b_over=}({a_underline=}, {b_overline=})")
    print(f"{v_prime_a_over_b_under=}({a_overline=}, {b_underline=})")

    if a_overline - a >= b - b_underline:
        print("Case 1")
        v_prime_a_under_b_under = _v_prime(segments, delta, a_underline, b_underline)
        print(f"{v_prime_a_under_b_under=}({a_underline=}, {b_underline=})")
        v_double_prime = (
            ((a_overline - a) - (b - b_underline)) / delta * v_prime_a_under_b_under
            + (b - b_underline) / delta * v_prime_a_under_b_over
            + (a - a_underline) / delta * v_prime_a_over_b_under
        )
        print(f"v_double_prime={v_double_prime}({a=}, {b=})")
        print("====end====")
        return v_double_prime
    elif a_overline - a <= b - b_underline:
        print("Case 2")
        v_prime_a_over_b_over = _v_prime(segments, delta, a_overline, b_overline)
        print(f"{v_prime_a_over_b_over=}({a_overline=}, {b_overline=})")
        v_double_prime = (
            ((b - b_underline) - (a_overline - a)) / delta * v_prime_a_over_b_over
            + (a_overline - a) / delta * v_prime_a_under_b_over
            + (b_overline - b) / delta * v_prime_a_over_b_under
        )
        print(f"v_double_prime={v_double_prime}({a=}, {b=})")
        print("====end====")

        return v_double_prime


def overline(x, delta, epsilon=Decimal("1e-10")):
    x = Decimal(x)
    delta = Decimal(delta)
    assert 0 <= x <= 1

    if x < delta or x == 0:
        return delta

    if x == 1:
        return x

    v = (x / delta).to_integral_value(rounding="ROUND_CEILING") * delta

    # If x is exactly a multiple of delta, step up to the next multiple
    # considering floating point precision issues
    if abs(x % delta) < epsilon or abs(delta - (x % delta)) < epsilon:
        v += delta

    return min(v, Decimal(1))


def underline(x, delta, epsilon=Decimal("1e-10")):
    x = Decimal(x)
    delta = Decimal(delta)
    assert 0 <= x <= 1

    if x < delta or x == 0:
        return Decimal(0)

    if x == 1:
        return x - delta

    # Check if x is an exact multiple of delta,
    # considering floating point precision issues
    if abs(x % delta) < epsilon or abs(delta - (x % delta)) < epsilon:
        v = (x / delta - 1).to_integral_value(rounding="ROUND_FLOOR") * delta
    else:
        v = (x / delta).to_integral_value(rounding="ROUND_FLOOR") * delta

    return max(v, Decimal(0))


def get_values_for_cuts(
    preference: List[Segment], cuts: List[float], cake_size: float, epsilon: float
) -> List[float]:
    slice_values = []

    start = 0
    for end in cuts:
        value = get_double_prime_for_interval(preference, epsilon, start, end)
        slice_values.append(value)
        start = end
    # Last piece
    slice_values.append(get_value_for_interval(preference, cuts[-1], cake_size))
    return slice_values
