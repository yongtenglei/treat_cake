import pytest

from treat_cake.algorithms.alex_aviad_hepler import (
    _binary_search_left_to_right,
    _binary_search_right_to_left,
)
from treat_cake.algorithms.algorithm_test_utils import gen_flat_seg
from treat_cake.valuation import get_double_prime_for_interval


def test_binary_search_left_to_right():
    cake_size = 1
    epsilon = 1e-10
    alpha = 2.5
    tolerant = 1e-10

    # if k == 3
    # [0, l] | [l, m] | [m, r] | [r, cake_size]
    #    1       2         3          *
    preference = [gen_flat_seg(0, cake_size, 10)]
    l = _binary_search_left_to_right(preference, epsilon, 0, cake_size, alpha, tolerant)
    assert l == pytest.approx(0.25, abs=1e-3), "Wrong left cut point"
    print(f"==={l=}===")

    m = _binary_search_left_to_right(preference, epsilon, l, cake_size, alpha, tolerant)
    assert m == pytest.approx(0.50, abs=1e-3), "Wrong mid cut point"

    # r = _binary_search_left_to_right(preference, epsilon, m, cake_size, alpha, tolerant)
    # assert r == pytest.approx(0.75, abs=1e-3), "Wrong right cut point"
    #
    # remained_value = get_double_prime_for_interval(preference, epsilon, r, cake_size)
    # assert remained_value == pytest.approx(2.5, abs=1e-3), "Wrong remained piece value"


def test_binary_search_right_to_left():
    cake_size = 1
    epsilon = 1e-10
    alpha = 2.5
    tolerant = 1e-10

    # if k == 0
    # [0, l] | [l, m] | [m, r] | [r, cake_size]
    #    *       3         2          1
    preference = [gen_flat_seg(0, cake_size, 10)]
    r = _binary_search_right_to_left(preference, epsilon, 0, cake_size, alpha, tolerant)
    assert r == pytest.approx(0.75, abs=1e-3), "Wrong right cut point"
    print(f"==={r=}===")

    m = _binary_search_right_to_left(preference, epsilon, 0, r, alpha, tolerant)
    assert m == pytest.approx(0.50, abs=1e-3), "Wrong mid cut point"
    #
    # l = _binary_search_right_to_left(preference, epsilon, 0, m, alpha, tolerant)
    # assert l == pytest.approx(0.25, abs=1e-3), "Wrong left cut point"
