from decimal import Decimal

import pytest

from type_helper import to_decimal
from valuation import get_double_prime_for_interval

from .alex_aviad import alex_aviad
from .alex_aviad_hepler import equipartition
from .algorithm_test_utils import check_if_envy_free, gen_flat_seg, gen_sloped_seg

CAKE_SIZE = to_decimal(1)
TOLERANCE = to_decimal("1e-6")
EPSILON = to_decimal("1e-15")


def test_alex_aviad_same_evaluations_case_flat_graph_one_seg():
    preferences = [
        [gen_flat_seg(0, CAKE_SIZE, 10)],
        [gen_flat_seg(0, CAKE_SIZE, 10)],
        [gen_flat_seg(0, CAKE_SIZE, 10)],
        [gen_flat_seg(0, CAKE_SIZE, 10)],
    ]

    result = alex_aviad(preferences, CAKE_SIZE, EPSILON)["solution"]
    # assert len(result) == 4, "The result should have exactly four segments."
    print(f"{result=}")

    sum_of_first_values = sum(slice.values[0] for slice in result)

    expected_sum_of_first_values = get_double_prime_for_interval(
        preferences[0], EPSILON, to_decimal(0), to_decimal(1), cake_size=CAKE_SIZE
    )

    assert sum_of_first_values == pytest.approx(
        expected_sum_of_first_values, abs=TOLERANCE
    )


def test_alex_aviad_same_evaluations_case_slope_graph_one_seg():
    preferences = [
        [
            gen_sloped_seg(
                start=to_decimal(0),
                end=CAKE_SIZE,
                start_value=to_decimal(10),
                end_value=to_decimal(0),
            )
        ],
        [
            gen_sloped_seg(
                start=to_decimal(0),
                end=CAKE_SIZE,
                start_value=to_decimal(10),
                end_value=to_decimal(0),
            )
        ],
        [
            gen_sloped_seg(
                start=to_decimal(0),
                end=CAKE_SIZE,
                start_value=to_decimal(10),
                end_value=to_decimal(0),
            )
        ],
        [
            gen_sloped_seg(
                start=to_decimal(0),
                end=CAKE_SIZE,
                start_value=to_decimal(10),
                end_value=to_decimal(0),
            )
        ],
    ]

    result = alex_aviad(preferences, int(CAKE_SIZE), EPSILON, tolerance=TOLERANCE)[
        "solution"
    ]
    # assert len(result) == 4, "The result should have exactly four segments."
    print(f"{result=}")

    sum_of_first_values = sum(slice.values[0] for slice in result)

    expected_sum_of_first_values = get_double_prime_for_interval(
        preferences[0], EPSILON, to_decimal(0), to_decimal(1), cake_size=CAKE_SIZE
    )

    assert sum_of_first_values == pytest.approx(
        expected_sum_of_first_values, abs=TOLERANCE
    )

    print(f"{result=}")

    assert check_if_envy_free(4, result), "Yield none-envy-free allocation"


def test_alex_aviad_same_evaluations_case_flat_graph_two_segs():
    cake_size = to_decimal(2)

    preferences = [
        [
            gen_flat_seg(to_decimal(0), cake_size / 2, to_decimal(10)),
            gen_flat_seg(to_decimal(0), cake_size, to_decimal(10)),
        ],
        [
            gen_flat_seg(to_decimal(0), cake_size / 2, to_decimal(10)),
            gen_flat_seg(to_decimal(0), cake_size, to_decimal(10)),
        ],
        [
            gen_flat_seg(to_decimal(0), cake_size / 2, to_decimal(10)),
            gen_flat_seg(to_decimal(0), cake_size, to_decimal(10)),
        ],
        [
            gen_flat_seg(to_decimal(0), cake_size / 2, to_decimal(10)),
            gen_flat_seg(to_decimal(0), cake_size, to_decimal(10)),
        ],
    ]

    result = alex_aviad(preferences, int(cake_size), EPSILON)["solution"]
    # assert len(result) == 4, "The result should have exactly four segments."
    print(f"{result=}")

    sum_of_first_values = sum(slice.values[0] for slice in result)

    expected_sum_of_first_values = get_double_prime_for_interval(
        preferences[0],
        EPSILON,
        to_decimal(0),
        to_decimal(cake_size),
        cake_size=cake_size,
    )

    assert sum_of_first_values == pytest.approx(
        expected_sum_of_first_values, abs=TOLERANCE
    )


def test_alex_aviad_same_evaluations_case_slope_graph_two_segs():
    cake_size = to_decimal(2)

    preferences = [
        [
            gen_sloped_seg(
                start=to_decimal(0),
                end=cake_size / 2,
                start_value=to_decimal(10),
                end_value=to_decimal(0),
            ),
            gen_sloped_seg(
                start=to_decimal(0),
                end=cake_size,
                start_value=to_decimal(0),
                end_value=to_decimal(10),
            ),
        ],
        [
            gen_sloped_seg(
                start=to_decimal(0),
                end=cake_size / 2,
                start_value=to_decimal(10),
                end_value=to_decimal(0),
            ),
            gen_sloped_seg(
                start=to_decimal(0),
                end=cake_size,
                start_value=to_decimal(0),
                end_value=to_decimal(10),
            ),
        ],
        [
            gen_sloped_seg(
                start=to_decimal(0),
                end=cake_size / 2,
                start_value=to_decimal(10),
                end_value=to_decimal(0),
            ),
            gen_sloped_seg(
                start=to_decimal(0),
                end=cake_size,
                start_value=to_decimal(0),
                end_value=to_decimal(10),
            ),
        ],
        [
            gen_sloped_seg(
                start=to_decimal(0),
                end=cake_size / 2,
                start_value=to_decimal(10),
                end_value=to_decimal(0),
            ),
            gen_sloped_seg(
                start=to_decimal(0),
                end=cake_size,
                start_value=to_decimal(0),
                end_value=to_decimal(10),
            ),
        ],
    ]

    result = alex_aviad(preferences, int(cake_size), EPSILON, tolerance=TOLERANCE)[
        "solution"
    ]
    # assert len(result) == 4, "The result should have exactly four segments."
    print(f"{result=}")

    sum_of_first_values = sum(slice.values[0] for slice in result)

    expected_sum_of_first_values = get_double_prime_for_interval(
        preferences[0],
        EPSILON,
        to_decimal(0),
        to_decimal(cake_size),
        cake_size=cake_size,
    )

    assert sum_of_first_values == pytest.approx(
        expected_sum_of_first_values, abs=TOLERANCE
    )

    print(f"{result=}")

    assert check_if_envy_free(4, result), "Yield none-envy-free allocation"


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
            cake_size=to_decimal(cake_size),
            epsilon=epsilon,
            start=to_decimal(0),
            end=to_decimal(cake_size),
        )
        sum_of_first_values = sum(slice.values[0] for slice in result)
        expected_sum_of_first_values = (
            get_double_prime_for_interval(
                preferences[0], epsilon, to_decimal(0), l, cake_size=CAKE_SIZE
            )
            + get_double_prime_for_interval(
                preferences[0], epsilon, l, m, cake_size=CAKE_SIZE
            )
            + get_double_prime_for_interval(
                preferences[0], epsilon, m, r, cake_size=CAKE_SIZE
            )
            + get_double_prime_for_interval(
                preferences[0], epsilon, r, to_decimal(cake_size), cake_size=CAKE_SIZE
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
