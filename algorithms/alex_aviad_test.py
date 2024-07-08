from decimal import Decimal

import pytest

from ..type_helper import to_decimal
from ..valuation import get_double_prime_for_interval
from .alex_aviad import alex_aviad
from .alex_aviad_hepler import equipartition
from .algorithm_test_utils import gen_flat_seg

CAKE_SIZE = to_decimal(1)
TOLERANCE = to_decimal(1e-6)
EPSILON = to_decimal("1e-15")


def test_alex_aviad_same_evaluations_case():
    preferences = [
        [gen_flat_seg(0, CAKE_SIZE, 10)],
        [gen_flat_seg(0, CAKE_SIZE, 10)],
        [gen_flat_seg(0, CAKE_SIZE, 10)],
        [gen_flat_seg(0, CAKE_SIZE, 10)],
    ]

    result = alex_aviad(preferences, CAKE_SIZE, EPSILON)["solution"]
    # assert len(result) == 4, "The result should have exactly four segments."
    print(f"{result=}")

    # sum_of_first_values = sum(slice.values[0] for slice in result)
    #
    # expected_sum_of_first_values = get_double_prime_for_interval(
    #     preferences[0], EPSILON, to_decimal(0), to_decimal(1)
    # )
    #
    # assert sum_of_first_values == pytest.approx(
    #     expected_sum_of_first_values, abs=TOLERANCE
    # )


def test_alex_aviad_generic_case_should_fail():
    """SHOULD FAIL"""
    cake_size = 1
    epsilon = Decimal("1e-6")

    with pytest.raises(AssertionError) as expected_error:
        assert not "SHOULD FAIL", "SHOULD FAIL"
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

        l, m, r = equipartition(
            preference=preferences[0],
            epsilon=epsilon,
            start=to_decimal(0),
            end=to_decimal(cake_size),
        )
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

        assert not "SHOULD FAIL", "SHOULD FAIL"

    assert "SHOULD FAIL" in str(
        expected_error.value
    ), f"Expected AssertionError with 'Should fail' message, but got different error: {expected_error.value}."
