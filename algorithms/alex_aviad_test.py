from decimal import Decimal

import pytest

from treat_cake.algorithms.alex_aviad import (
    equipartition,
    alex_aviad,
    alex_aviad_using_original_valuation_func,
)
from treat_cake.algorithms.algorithm_test_utils import gen_flat_seg, gen_sloped_seg
from treat_cake.type_helper import to_decimal
from treat_cake.valuation import get_double_prime_for_interval
from treat_cake.values import get_values_for_cuts_origin

CAKE_SIZE = to_decimal(100)
TOLERANCE = to_decimal(1e-6)


def test_equipartition_one_piece():
    tolerance: float = 0.0001

    preference = [
        gen_flat_seg(0, CAKE_SIZE, 10),
    ]

    cuts = equipartition(preference)
    slice_values = get_values_for_cuts_origin(
        preference=preference, cuts=cuts, cake_size=CAKE_SIZE
    )
    assert len(slice_values) == 4

    average_value = sum(slice_values) / len(slice_values)
    expected_average_value = 250
    assert average_value == pytest.approx(expected_average_value, tolerance)

    for slice_value in slice_values:
        assert slice_value == pytest.approx(
            expected_average_value, tolerance
        ), f"slice {slice_value} not equal to average value {average_value}"


def test_equipartition_seesaw_like_graph():
    tolerance: float = 0.0001

    preference = [
        gen_flat_seg(0, CAKE_SIZE // 2, 10),
        gen_flat_seg(CAKE_SIZE // 2, CAKE_SIZE, 5),
    ]

    cuts = equipartition(preference)
    slice_values = get_values_for_cuts_origin(
        preference=preference, cuts=cuts, cake_size=CAKE_SIZE
    )
    assert len(slice_values) == 4

    average_value = sum(slice_values) / len(slice_values)
    expected_average_value = 187.5  # 750 / 4
    assert average_value == pytest.approx(expected_average_value, tolerance)

    for slice_value in slice_values:
        assert slice_value == pytest.approx(
            expected_average_value, tolerance
        ), f"Slice {slice_value} not equal to average value {average_value}"


def test_equipartition_seesaw_sloped_graph():
    tolerance = to_decimal(0.0001)

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
    cake_size = 1

    preferences = [gen_flat_seg(0, cake_size, 10)]
    cuts = equipartition(preferences)
    assert len(cuts) == 3, "Should yield 3 cuts"
    assert cuts == [0.25, 0.5, 0.75], "wrong cuts yielded"


def test_alex_aviad_using_original_evaluation_func():
    """TESTING ONLY"""
    cake_size = 1

    preferences = [
        [gen_flat_seg(0, cake_size, 10)],
        [gen_flat_seg(0, cake_size, 10)],
        [gen_flat_seg(0, cake_size, 10)],
        [gen_flat_seg(0, cake_size, 10)],
    ]

    result = alex_aviad_using_original_valuation_func(preferences, cake_size)[
        "solution"
    ]
    assert len(result) == 4, "The result should have exactly four segments."
    print(f"{result=}")

    sum_of_first_values = sum(slice.values[0] for slice in result)
    assert sum_of_first_values == pytest.approx(10, abs=TOLERANCE)


def test_alex_aviad_same_evaluations_case():
    cake_size = 1
    epsilon = 1e-6

    preferences = [
        [gen_flat_seg(0, cake_size, 10)],
        [gen_flat_seg(0, cake_size, 10)],
        [gen_flat_seg(0, cake_size, 10)],
        [gen_flat_seg(0, cake_size, 10)],
    ]

    result = alex_aviad(preferences, cake_size, epsilon)["solution"]
    assert len(result) == 4, "The result should have exactly four segments."
    print(f"{result=}")

    sum_of_first_values = sum(slice.values[0] for slice in result)
    expected_sum_of_first_values = (
        get_double_prime_for_interval(preferences[0], epsilon, 0, 0.25)
        + get_double_prime_for_interval(preferences[0], epsilon, 0.25, 0.5)
        + get_double_prime_for_interval(preferences[0], epsilon, 0.5, 0.75)
        + get_double_prime_for_interval(preferences[0], epsilon, 0.75, cake_size)
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
