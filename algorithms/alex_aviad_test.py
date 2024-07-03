from decimal import Decimal

import pytest

from treat_cake.algorithms.alex_aviad import (
    equipartition,
    alex_aviad,
)
from treat_cake.algorithms.algorithm_test_utils import gen_flat_seg, gen_sloped_seg
from treat_cake.type_helper import to_decimal
from treat_cake.valuation import get_double_prime_for_interval, get_values_for_cuts
from treat_cake.values import get_values_for_cuts_origin

CAKE_SIZE = to_decimal(1)
TOLERANCE = to_decimal(1e-6)
EPSILON = to_decimal("1e-15")


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
        ), f"Wrong cuts {cut[i]} yielded, expected {expected_cuts[i]}, got {cut[i]}"


def test_alex_aviad_same_evaluations_case():

    preferences = [
        [gen_flat_seg(0, CAKE_SIZE, 10)],
        [gen_flat_seg(0, CAKE_SIZE, 10)],
        [gen_flat_seg(0, CAKE_SIZE, 10)],
        [gen_flat_seg(0, CAKE_SIZE, 10)],
    ]

    result = alex_aviad(preferences, CAKE_SIZE, EPSILON)["solution"]
    assert len(result) == 4, "The result should have exactly four segments."
    print(f"{result=}")

    sum_of_first_values = sum(slice.values[0] for slice in result)

    expected_sum_of_first_values = get_double_prime_for_interval(
        preferences[0], EPSILON, to_decimal(0), to_decimal(1)
    )

    assert sum_of_first_values == pytest.approx(
        expected_sum_of_first_values, abs=TOLERANCE
    )


def test_alex_aviad_generic_case_should_fail():
    """SHOULD FAIL"""
    cake_size = 1
    epsilon = Decimal("1e-6")

    with pytest.raises(AssertionError) as expected_error:

        preferences = [
            [gen_flat_seg(0, cake_size, 2.5)],
            [gen_flat_seg(0, cake_size, 5)],
            [gen_flat_seg(0, cake_size, 7.5)],
            [gen_flat_seg(0, cake_size, 10)],
        ]

        result = alex_aviad(preferences, cake_size, epsilon)["solution"]
        print(f"{result=}")
        assert (
            len(result) == 4
        ), "SHOULD FAIL! The result should have exactly four segments."

        l, m, r = equipartition(preferences[0])
        sum_of_first_values = sum(slice.values[0] for slice in result)
        expected_sum_of_first_values = (
            get_double_prime_for_interval(preferences[0], epsilon, Decimal(0), l)
            + get_double_prime_for_interval(preferences[0], epsilon, l, m)
            + get_double_prime_for_interval(preferences[0], epsilon, m, r)
            + get_double_prime_for_interval(
                preferences[0], epsilon, r, Decimal(cake_size)
            )
        )

        # Test later
        # assert sum_of_first_values == pytest.approx(
        #     expected_sum_of_first_values, abs=TOLERANCE
        # )

        assert not "Should fail", "Should fail"

    assert "SHOULD FAIL" in str(
        expected_error.value
    ), f"Expected AssertionError with 'Should fail' message, but got different error: {expected_error}."
