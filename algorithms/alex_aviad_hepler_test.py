import pytest

from treat_cake.algorithms.alex_aviad_hepler import (
    _binary_search_left_to_right,
    _binary_search_right_to_left,
)
from treat_cake.algorithms.algorithm_test_utils import gen_flat_seg
from treat_cake.type_helper import to_decimal
from treat_cake.valuation import get_double_prime_for_interval


def test_binary_search_left_to_right():
    cake_size = to_decimal(1)
    epsilon = to_decimal("1e-15")
    alpha = to_decimal(2.5)
    tolerant = to_decimal("1e-4")

    # if k == 3
    # [0, l] | [l, m] | [m, r] | [r, cake_size]
    #    1       2         3          *
    preference = [gen_flat_seg(0, cake_size, 10)]

    l = _binary_search_left_to_right(
        preference, epsilon, to_decimal(0), cake_size, alpha, tolerant
    )
    assert l == pytest.approx(to_decimal(0.25), rel=tolerant), "Wrong left cut point"

    m = _binary_search_left_to_right(preference, epsilon, l, cake_size, alpha, tolerant)
    assert m == pytest.approx(to_decimal(0.50), rel=tolerant), "Wrong mid cut point"

    r = _binary_search_left_to_right(preference, epsilon, m, cake_size, alpha, tolerant)
    assert r == pytest.approx(to_decimal(0.75), rel=tolerant), "Wrong right cut point"

    remained_value = get_double_prime_for_interval(preference, epsilon, r, cake_size)
    assert remained_value == pytest.approx(
        to_decimal(2.5), rel=tolerant
    ), "Wrong remained piece value"


def test_binary_search_right_to_left():
    cake_size = to_decimal(1)
    epsilon = to_decimal("1e-15")
    alpha = to_decimal(2.5)
    tolerant = to_decimal("1e-4")
    # if k == 0
    # [0, l] | [l, m] | [m, r] | [r, cake_size]
    #    *       3         2          1
    preference = [gen_flat_seg(0, cake_size, 10)]

    r = _binary_search_right_to_left(
        preference, epsilon, to_decimal(0), cake_size, alpha, tolerant
    )
    assert r == pytest.approx(to_decimal(0.75), rel=tolerant), "Wrong right cut point"

    m = _binary_search_right_to_left(
        preference, epsilon, to_decimal(0), r, alpha, tolerant
    )
    assert m == pytest.approx(to_decimal(0.50), rel=tolerant), "Wrong mid cut point"

    l = _binary_search_right_to_left(
        preference, epsilon, to_decimal(0), m, alpha, tolerant
    )
    assert l == pytest.approx(to_decimal(0.25), rel=tolerant), "Wrong left cut point"

    remained_value = get_double_prime_for_interval(
        preference, epsilon, to_decimal(0), l
    )
    assert remained_value == pytest.approx(
        to_decimal(2.5), rel=tolerant
    ), "Wrong remained piece value"
