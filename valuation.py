import math
from typing import List

from treat_cake.base_types import Segment
from treat_cake.values_bak import get_value_for_interval


def _v(segments: List[Segment], a: float, b: float) -> float:
    v = get_value_for_interval(segments, a, b)
    print(f"v={v}({a=}, {b=})")
    return v


def _v_prime(
    segments: List[Segment],
    epsilon: float,
    a: float,
    b: float,
):
    # v is the original valuation function
    # v_prime = base_value / 2 + perturbation
    v = _v(segments, a, b) / 2 + epsilon * abs(b - a)
    print(f"v_prime={v}({a=}, {b=})")
    return v


# def get_double_prime_for_interval(
#     segments: List[Segment], epsilon: float, start: float, end: float
# ) -> float:
#     """
#     Returns the total double prime value of an interval,
#     even if covers several segments or splits segments in half.
#     """
#     total = 0
#     for seg in segments:
#         if seg.end <= start or seg.start >= end:
#             # this segment not relevant
#             continue
#
#         total += _v_double_prime(seg, epsilon, start, end)
#     return total


def get_double_prime_for_interval(
    segments: List[Segment], epsilon: float, start: float, end: float
) -> float:
    """
    Returns the total double prime value of an interval,
    even if covers several segments or splits segments in half.
    """
    assert 0 <= start <= end, "start or end out of range"

    total = 0

    start_int = int(start)
    end_int = int(end)

    # Only one segment
    if end <= 1:
        return _v_double_prime(segments, epsilon, start, end)

    if start == start_int and end == end_int:
        return _v_double_prime(segments, epsilon, start, end)

    # Start segments
    if start != start_int:
        first_segment_end = start_int + 1
        total += _v_double_prime(segments, epsilon, start, first_segment_end)

    # Intermedia segments
    if start_int + 1 < end_int:
        total += _v_double_prime(segments, epsilon, start_int + 1, end_int)

    # Last segments
    if end != end_int:
        last_segment_start = end_int
        total += _v_double_prime(segments, epsilon, last_segment_start, end)

    return total


def _v_double_prime(segments: List[Segment], delta: float, a: float, b: float) -> float:

    # Letting delta := epsilon, so,
    # any epsilon-envy-free allocation for (v_double_prime) is 5*epsilon-envy-free for (v_prime) for each agent.

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


def overline(x, delta, epsilon=1e-10):
    assert 0 <= x <= 1

    if x < delta or x == 0:
        return delta

    if x == 1:
        return x

    v = math.ceil(x / delta) * delta

    # If x is exactly a multiple of delta, step up to the next multiple
    # considering floating point precision issues
    if abs(x % delta) < epsilon or abs(delta - (x % delta)) < epsilon:
        v += delta

    return min(v, 1)


def underline(x, delta, epsilon=1e-10):
    assert 0 <= x <= 1

    if x < delta or x == 0:
        return 0

    if x == 1:
        return x - epsilon

    # Check if x is an exact multiple of delta,
    # considering floating point precision issues
    if abs(x % delta) < epsilon or abs(delta - (x % delta)) < epsilon:
        v = (math.floor(x / delta) - 1) * delta
    else:
        v = math.floor(x / delta) * delta

    return max(v, 0)


# def underline(x, delta):
#     assert 0 <= x <= 1
#     if x < delta:
#         return 0
#
#     if x == 0 or x == 1:
#         return x
#
#     v = (
#         (math.floor(x / delta) - 1) * delta
#         if x % delta == 0
#         else math.floor(x / delta) * delta
#     )
#
#     return v if v >= 0 else 0


# def equipartition(v, cake_start, cake_end):
#     """
#     根据Agent1的价值函数将蛋糕均分成四个部分。
#
#     :param v: Agent1的价值函数，接受两个参数（a, b）并返回a和b之间的价值
#     :param cake_start: 蛋糕的起始点
#     :param cake_end: 蛋糕的结束点
#     :return: 四个分割点的列表
#     """
#     total_value = v(cake_start, cake_end)
#     part_value = total_value / 4
#     cut_points = [cake_start]
#
#     current_value = 0
#     current_start = cake_start
#
#     for i in range(3):  # 需要找到三个分割点
#         low = current_start
#         high = cake_end
#
#         # 二分法找到合适的分割点，使得每部分的价值接近于part_value
#         while high - low > 1e-5:  # 假设精度为1e-5
#             mid = (low + high) / 2
#             value = v(current_start, mid)
#
#             if value < part_value:
#                 low = mid
#             else:
#                 high = mid
#
#         cut_point = (low + high) / 2
#         cut_points.append(cut_point)
#         current_start = cut_point
#
#     cut_points.append(cake_end)
#     return cut_points
