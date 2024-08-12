import logging
from decimal import Decimal, getcontext

import pytest

from type_helper import de_norm, to_decimal
from valuation import get_double_prime_for_interval

from .alex_aviad import alex_aviad
from .alex_aviad_hepler import _binary_search_left_to_right, equipartition
from .algorithm_test_utils import check_if_envy_free, gen_flat_seg, gen_sloped_seg

getcontext().prec = 15

CAKE_SIZE = to_decimal(1)
TOLERANCE = to_decimal("1e-9")
EPSILON = to_decimal("1e-15")


def test_alex_aviad_same_evaluations_case_flat_graph_one_seg():
    preferences = [
        [gen_flat_seg(to_decimal(0), CAKE_SIZE, to_decimal(10))],
        [gen_flat_seg(to_decimal(0), CAKE_SIZE, to_decimal(10))],
        [gen_flat_seg(to_decimal(0), CAKE_SIZE, to_decimal(10))],
        [gen_flat_seg(to_decimal(0), CAKE_SIZE, to_decimal(10))],
    ]

    result = alex_aviad(preferences, int(CAKE_SIZE), EPSILON)["solution"]
    # assert len(result) == 4, "The result should have exactly four segments."
    logging.info(f"{result=}")

    sum_of_first_values = sum(slice.values[0] for slice in result)

    expected_sum_of_first_values = get_double_prime_for_interval(
        preferences[0], EPSILON, to_decimal(0), to_decimal(1), cake_size=CAKE_SIZE
    )

    assert sum_of_first_values == pytest.approx(
        de_norm(expected_sum_of_first_values, 10), abs=TOLERANCE
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
    logging.info(f"{result=}")

    sum_of_first_values = sum(slice.values[0] for slice in result)

    expected_sum_of_first_values = get_double_prime_for_interval(
        preferences[0], EPSILON, to_decimal(0), to_decimal(1), cake_size=CAKE_SIZE
    )

    assert sum_of_first_values == pytest.approx(
        de_norm(expected_sum_of_first_values, to_decimal(5)), abs=TOLERANCE
    )

    logging.info(f"{result=}")

    assert check_if_envy_free(4, result), "Yield none-envy-free allocation"


def test_alex_aviad_same_evaluations_case_flat_graph_two_segs():
    cake_size = to_decimal(2)

    preferences = [
        [
            gen_flat_seg(to_decimal(0), cake_size / 2, to_decimal(10)),
            gen_flat_seg(to_decimal(cake_size / 2), cake_size, to_decimal(10)),
        ],
        [
            gen_flat_seg(to_decimal(0), cake_size / 2, to_decimal(10)),
            gen_flat_seg(to_decimal(cake_size / 2), cake_size, to_decimal(10)),
        ],
        [
            gen_flat_seg(to_decimal(0), cake_size / 2, to_decimal(10)),
            gen_flat_seg(to_decimal(cake_size / 2), cake_size, to_decimal(10)),
        ],
        [
            gen_flat_seg(to_decimal(0), cake_size / 2, to_decimal(10)),
            gen_flat_seg(to_decimal(cake_size / 2), cake_size, to_decimal(10)),
        ],
    ]

    result = alex_aviad(preferences, int(cake_size), EPSILON)["solution"]
    # assert len(result) == 4, "The result should have exactly four segments."
    logging.info(f"{result=}")

    sum_of_first_values = sum(slice.values[0] for slice in result)

    expected_sum_of_first_values = get_double_prime_for_interval(
        preferences[0],
        EPSILON,
        to_decimal(0),
        to_decimal(cake_size),
        cake_size=cake_size,
    )

    assert sum_of_first_values == pytest.approx(
        de_norm(expected_sum_of_first_values, to_decimal(20)), abs=TOLERANCE
    )
    logging.info(f"{result=}")
    assert check_if_envy_free(4, result), "Yield none-envy-free allocation"


def test_alex_aviad_same_evaluations_case_flat_graph_three_segs():
    cake_size = to_decimal(3)

    preferences = [
        [
            gen_sloped_seg(
                start=Decimal("0"),
                end=Decimal("3"),
                start_value=Decimal("10"),
                end_value=Decimal("10"),
            )
        ],
        [
            gen_sloped_seg(
                start=Decimal("0"),
                end=Decimal("3"),
                start_value=Decimal("10"),
                end_value=Decimal("10"),
            )
        ],
        [
            gen_sloped_seg(
                start=Decimal("0"),
                end=Decimal("3"),
                start_value=Decimal("10"),
                end_value=Decimal("10"),
            )
        ],
        [
            gen_sloped_seg(
                start=Decimal("0"),
                end=Decimal("3"),
                start_value=Decimal("10"),
                end_value=Decimal("10"),
            )
        ],
    ]

    result = alex_aviad(preferences, int(cake_size), EPSILON, tolerance=TOLERANCE)[
        "solution"
    ]
    assert len(result) == 4, "The result should have exactly four segments."

    sum_of_first_values = sum(slice.values[0] for slice in result)

    expected_sum_of_first_values = get_double_prime_for_interval(
        preferences[0],
        EPSILON,
        to_decimal(0),
        to_decimal(cake_size),
        cake_size=cake_size,
    )
    logging.info(expected_sum_of_first_values)

    assert sum_of_first_values == pytest.approx(
        de_norm(expected_sum_of_first_values, to_decimal(30)), abs=TOLERANCE
    )
    logging.info(f"{result=}")
    assert check_if_envy_free(4, result), "Yield none-envy-free allocation"


def test_alex_aviad_same_evaluations_case_slope_graph_two_segs():
    # TODO: Weried... works perfectly on front-end, but cannot passed here.
    assert (
        1 == 2
    ), "Fix this later...works perfectly on front-end, but cannot passed here."
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
                start=cake_size / 2,
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
                start=cake_size / 2,
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
                start=cake_size / 2,
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
                start=cake_size / 2,
                end=cake_size,
                start_value=to_decimal(0),
                end_value=to_decimal(10),
            ),
        ],
    ]

    total_v = get_double_prime_for_interval(
        segments=preferences[0],
        epsilon=EPSILON,
        start=to_decimal(0),
        end=to_decimal(cake_size),
        cake_size=cake_size,
    )
    logging.info(f"{total_v=}")
    segment_value = total_v / 4
    logging.info(f"{segment_value=}")

    first_cut = _binary_search_left_to_right(
        preference=preferences[0],
        cake_size=cake_size,
        epsilon=EPSILON,
        start=to_decimal(0),
        end=to_decimal(cake_size),
        target=segment_value,
        tolerance=TOLERANCE,
    )
    logging.info(f"find l cut: {first_cut}")

    v_1 = get_double_prime_for_interval(
        segments=preferences[0],
        epsilon=EPSILON,
        start=to_decimal(0),
        end=to_decimal(first_cut),
        cake_size=cake_size,
    )
    assert v_1 == pytest.approx(segment_value, abs=TOLERANCE)

    second_cut = _binary_search_left_to_right(
        preference=preferences[0],
        cake_size=cake_size,
        epsilon=EPSILON,
        start=first_cut,
        end=to_decimal(cake_size),
        target=segment_value,
        tolerance=TOLERANCE,
    )
    logging.info(f"find m cut: {second_cut}")
    v_2 = get_double_prime_for_interval(
        segments=preferences[0],
        epsilon=EPSILON,
        start=to_decimal(first_cut),
        end=to_decimal(second_cut),
        cake_size=cake_size,
    )
    assert v_2 == pytest.approx(segment_value, abs=TOLERANCE)

    third_cut = _binary_search_left_to_right(
        preference=preferences[0],
        cake_size=cake_size,
        epsilon=EPSILON,
        start=second_cut,
        end=to_decimal(cake_size),
        target=segment_value,
        tolerance=TOLERANCE,
    )
    logging.info(f"find r cut: {third_cut}")
    v_3 = get_double_prime_for_interval(
        segments=preferences[0],
        epsilon=EPSILON,
        start=to_decimal(second_cut),
        end=to_decimal(third_cut),
        cake_size=cake_size,
    )
    assert v_3 == pytest.approx(segment_value, abs=TOLERANCE)

    v_4 = get_double_prime_for_interval(
        segments=preferences[0],
        epsilon=EPSILON,
        start=to_decimal(third_cut),
        end=to_decimal(cake_size),
        cake_size=cake_size,
    )
    assert v_4 == pytest.approx(segment_value, abs=TOLERANCE)

    # cuts = equipartition(
    #     preferences[0], cake_size, EPSILON, to_decimal(0), cake_size, TOLERANCE
    # )
    # logging.info(cuts)
    #
    # values = get_values_for_cuts(preferences[0], cuts, cake_size, EPSILON)
    # logging.info(values)

    # logging.info(1)
    # result = alex_aviad(preferences, int(cake_size), EPSILON, tolerance=TOLERANCE)[
    #     "solution"
    # ]
    # assert len(result) == 4, "The result should have exactly four segments."
    # logging.info(f"{result=}")
    #
    # logging.info(2)
    # sum_of_first_values = sum(slice.values[0] for slice in result)
    #
    # expected_sum_of_first_values = get_double_prime_for_interval(
    #     preferences[0],
    #     EPSILON,
    #     to_decimal(0),
    #     to_decimal(cake_size),
    #     cake_size=cake_size,
    # )
    # logging.info(f"{result=}")
    # assert sum_of_first_values == pytest.approx(
    #     expected_sum_of_first_values, abs=TOLERANCE * 10
    # )
    #
    # logging.info(f"{result=}")
    # logging.info(4)
    #
    # assert check_if_envy_free(4, result), "Yield none-envy-free allocation"


def test_alex_aviad_generic_case_one_seg():
    # TODO: Weried... works perfectly on front-end, but cannot passed here.
    assert (
        1 == 2
    ), "Fix this later...works perfectly on front-end, but cannot passed here."
    cake_size = 1
    epsilon = Decimal("1e-6")

    preferences = [
        [gen_flat_seg(to_decimal(0), to_decimal(cake_size), to_decimal(2.5))],
        [gen_flat_seg(to_decimal(0), to_decimal(cake_size), to_decimal(5))],
        [gen_flat_seg(to_decimal(0), to_decimal(cake_size), to_decimal(7.5))],
        [gen_flat_seg(to_decimal(0), to_decimal(cake_size), to_decimal(10))],
    ]

    result = alex_aviad(preferences, cake_size, epsilon)["solution"]
    logging.info(f"{result=}")
    assert len(result) == 4, "The result should have exactly four segments."

    l, m, r = equipartition(
        preference=preferences[0],
        cake_size=to_decimal(cake_size),
        epsilon=epsilon,
        start=to_decimal(0),
        end=to_decimal(cake_size),
    )
    sum_of_first_values = sum(slice.values[0] for slice in result)
    expected_sum_of_first_values = get_double_prime_for_interval(
        preferences[0], epsilon, to_decimal(0), CAKE_SIZE, cake_size=CAKE_SIZE
    )
    assert sum_of_first_values == pytest.approx(
        expected_sum_of_first_values, abs=TOLERANCE
    )
