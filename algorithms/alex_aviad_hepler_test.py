from decimal import Decimal

import pytest

from ..type_helper import to_decimal
from ..valuation import get_double_prime_for_interval, get_values_for_cuts
from .alex_aviad_condition.condition_a import _find_cuts_and_k_for_condition_a
from .alex_aviad_hepler import (_binary_search_left_to_right,
                                _binary_search_right_to_left, equipartition)
from .algorithm_test_utils import gen_flat_seg, gen_sloped_seg

CAKE_SIZE: int = to_decimal(1)
EPSILON: Decimal = to_decimal(1e-15)
TOLERANCE: Decimal = to_decimal(1e-10)


def test_binary_search_left_to_right():
    cake_size = to_decimal(1)
    epsilon = to_decimal("1e-15")
    alpha = to_decimal(2.5)
    tolerance = to_decimal("1e-4")

    # if k == 3
    # [0, l] | [l, m] | [m, r] | [r, cake_size]
    #    1       2         3          *
    preference = [gen_flat_seg(0, cake_size, 10)]

    l = _binary_search_left_to_right(
        preference, epsilon, to_decimal(0), cake_size, alpha, tolerance
    )
    assert l == pytest.approx(to_decimal(0.25), rel=tolerance), "Wrong left cut point"

    m = _binary_search_left_to_right(
        preference, epsilon, l, cake_size, alpha, tolerance
    )
    assert m == pytest.approx(to_decimal(0.50), rel=tolerance), "Wrong mid cut point"

    r = _binary_search_left_to_right(
        preference, epsilon, m, cake_size, alpha, tolerance
    )
    assert r == pytest.approx(to_decimal(0.75), rel=tolerance), "Wrong right cut point"

    remained_value = get_double_prime_for_interval(preference, epsilon, r, cake_size)
    assert remained_value == pytest.approx(
        to_decimal(2.5), rel=tolerance
    ), "Wrong remained piece value"


def test_binary_search_right_to_left():
    cake_size = to_decimal(1)
    epsilon = to_decimal("1e-15")
    alpha = to_decimal(2.5)
    tolerance = to_decimal("1e-4")
    # if k == 0
    # [0, l] | [l, m] | [m, r] | [r, cake_size]
    #    *       3         2          1
    preference = [gen_flat_seg(0, cake_size, 10)]

    r = _binary_search_right_to_left(
        preference, epsilon, to_decimal(0), cake_size, alpha, tolerance
    )
    assert r == pytest.approx(to_decimal(0.75), rel=tolerance), "Wrong right cut point"

    m = _binary_search_right_to_left(
        preference, epsilon, to_decimal(0), r, alpha, tolerance
    )
    assert m == pytest.approx(to_decimal(0.50), rel=tolerance), "Wrong mid cut point"

    l = _binary_search_right_to_left(
        preference, epsilon, to_decimal(0), m, alpha, tolerance
    )
    assert l == pytest.approx(to_decimal(0.25), rel=tolerance), "Wrong left cut point"

    remained_value = get_double_prime_for_interval(
        preference, epsilon, to_decimal(0), l
    )
    assert remained_value == pytest.approx(
        to_decimal(2.5), rel=tolerance
    ), "Wrong remained piece value"


def test_find_cuts_for_condition_a():
    cake_size = to_decimal(1)
    epsilon = to_decimal("1e-15")
    alpha = to_decimal(2.5)
    tolerance = to_decimal("1e-4")

    preference = [gen_flat_seg(0, cake_size, 10)]

    result = _find_cuts_and_k_for_condition_a(
        alpha=alpha,
        cake_size=cake_size,
        preference=preference,
        epsilon=epsilon,
        tolerance=tolerance,
    )

    assert (
        len(result["cuts"]) == 3
    ), f"Wrong cuts length, expected 3, got {len(result['cuts'])}"

    assert result["cuts"][0] == pytest.approx(
        to_decimal(0.25), abs=tolerance
    ), "Wrong left cut point"
    assert result["cuts"][1] == pytest.approx(
        to_decimal(0.5), abs=tolerance
    ), "Wrong mid cut point"
    assert result["cuts"][2] == pytest.approx(
        to_decimal(0.75), abs=tolerance
    ), "Wrong right cut point"

    assert result["k"] == 3, f"Wrong k, expected 3, got {result['k']}"


def test_equipartition_one_piece_flat():
    preference = [
        gen_flat_seg(0, CAKE_SIZE, 10),
    ]

    cuts = equipartition(
        preference=preference, epsilon=EPSILON, start=to_decimal(0), end=CAKE_SIZE
    )

    slice_values = get_values_for_cuts(
        preference=preference, cuts=cuts, cake_size=CAKE_SIZE, epsilon=EPSILON
    )
    assert len(slice_values) == 4

    sum_value = sum(slice_values)
    assert sum_value == pytest.approx(
        to_decimal(10), TOLERANCE
    ), "sum value not equal to expected full cake value"

    average_value = sum_value / len(slice_values)
    expected_average_value = to_decimal(2.5)
    assert average_value == pytest.approx(expected_average_value, TOLERANCE)

    for slice_value in slice_values:
        assert slice_value == pytest.approx(
            expected_average_value, TOLERANCE
        ), f"slice {slice_value} not equal to average value {average_value}"


def test_equipartition_one_piece_slope():
    preference = [
        gen_sloped_seg(0, CAKE_SIZE, 10, 0),
    ]

    cuts = equipartition(
        preference=preference, epsilon=EPSILON, start=to_decimal(0), end=CAKE_SIZE
    )
    print(f"{cuts=}")

    slice_values = get_values_for_cuts(
        preference=preference, cuts=cuts, cake_size=CAKE_SIZE, epsilon=EPSILON
    )
    assert len(slice_values) == 4

    sum_value = sum(slice_values)
    assert sum_value == pytest.approx(
        to_decimal(5), TOLERANCE
    ), "sum value not equal to expected full cake value"

    average_value = sum_value / len(slice_values)
    expected_average_value = to_decimal(1.25)
    assert average_value == pytest.approx(expected_average_value, TOLERANCE)

    for slice_value in slice_values:
        assert slice_value == pytest.approx(
            expected_average_value, TOLERANCE
        ), f"slice {slice_value} not equal to average value {average_value}"


def test_equipartition_seesaw_like_graph():
    """TODO:multi-segments case should be investigated later"""

    preference = [
        gen_flat_seg(0, CAKE_SIZE // 2, 10),
        gen_flat_seg(CAKE_SIZE // 2, CAKE_SIZE, 5),
    ]

    v = get_double_prime_for_interval(
        segments=preference, epsilon=EPSILON, start=to_decimal(0), end=to_decimal(1)
    )
    v1 = get_double_prime_for_interval(
        segments=preference, epsilon=EPSILON, start=to_decimal(0), end=to_decimal(0.5)
    )
    v2 = get_double_prime_for_interval(
        segments=preference, epsilon=EPSILON, start=to_decimal(0.5), end=to_decimal(1)
    )
    print(f"{v=}")
    print(f"{v1=}")
    print(f"{v2=}")

    assert 1 == 2, "Should see this error"

    # cuts = equipartition(
    #     preference=preference, epsilon=EPSILON, start=to_decimal(0), end=CAKE_SIZE
    # )
    #
    # slice_values = get_values_for_cuts(
    #     preference=preference, cuts=cuts, cake_size=CAKE_SIZE, epsilon=EPSILON
    # )
    # assert len(slice_values) == 4
    #
    # average_value = sum(slice_values) / len(slice_values)
    # expected_average_value = to_decimal(1.875)  # 750 / 4
    # assert average_value == pytest.approx(expected_average_value, TOLERANCE)
    #
    # for slice_value in slice_values:
    #     assert slice_value == pytest.approx(
    #         expected_average_value, TOLERANCE
    #     ), f"Slice {slice_value} not equal to average value {average_value}"


def test_equipartition_seesaw_sloped_graph():
    tolerance = to_decimal(0.0001)

    assert 1 == 2, "Should see this error"

    preference = [
        gen_sloped_seg(0, CAKE_SIZE // 2, 0, 10),
        gen_sloped_seg(CAKE_SIZE // 2, CAKE_SIZE, 10, 0),
    ]

    cuts = equipartition(preference)
    print(f"{cuts=}")

    slice_values = get_values_for_cuts_origin(preference, cuts, CAKE_SIZE)
    print(f"{slice_values=}")

    assert len(slice_values) == 4, "The number of slices should be exactly four."

    expected_total_value = to_decimal(500)
    expected_average_value = expected_total_value / 4

    assert expected_total_value == pytest.approx(
        to_decimal(sum(slice_values)), tolerance
    ), "The sum of slice values should equal the total cake value."

    for slice_value in slice_values:
        assert slice_value == pytest.approx(
            expected_average_value, tolerance
        ), f"Slice value {slice_value} not approximately equal to expected average value {expected_average_value}"


def test_equipartition():
    preferences = [gen_flat_seg(0, CAKE_SIZE, 10)]
    cuts = equipartition(
        preference=preferences, epsilon=EPSILON, start=to_decimal(0), end=CAKE_SIZE
    )
    assert len(cuts) == 3, "Should yield 3 cuts"
    expected_cuts = [
        to_decimal(0.25),
        to_decimal(0.5),
        to_decimal(0.75),
    ]

    cut = {0: "l", 1: "m", 2: "r"}
    for i in range(len(cuts)):
        assert cuts[i] == pytest.approx(
            expected_cuts[i], abs=TOLERANCE
        ), f"Wrong cuts {cut[i]} yielded, expected {expected_cuts[i]}, got {cuts[i]}"
