import logging

import pytest

from type_helper import almost_equal, to_decimal
from valuation import get_double_prime_for_interval

from ..alex_aviad_hepler import _binary_search_right_to_left
from ..algorithm_test_utils import gen_flat_seg
from .condition_b import (
    _find_m_and_r_given_l,
    _find_m_given_l,
    _find_m_given_r,
    _handle_adjacent,
)


def test_handle_adjacent():
    alpha = to_decimal(0.25)
    cake_size = to_decimal(1)
    epsilon = to_decimal("1e-15")
    tolerance = to_decimal("1e-10")

    preferences = [
        [gen_flat_seg(to_decimal(0), to_decimal(cake_size), to_decimal(10))],
        [gen_flat_seg(to_decimal(0), to_decimal(cake_size), to_decimal(7))],
    ]

    l, m, r = _handle_adjacent(
        k=0,
        k_prime=1,
        alpha=alpha,
        preference_1=preferences[0],
        preference_i=preferences[1],
        epsilon=epsilon,
        cake_size=cake_size,
        tolerance=tolerance,
    )
    assert l == pytest.approx(to_decimal(0.25), abs=tolerance)
    assert r == pytest.approx(to_decimal(0.75), abs=tolerance)
    assert m == pytest.approx(to_decimal(0.50), abs=tolerance)

    l, m, r = _handle_adjacent(
        k=1,
        k_prime=2,
        alpha=alpha,
        preference_1=preferences[0],
        preference_i=preferences[1],
        epsilon=epsilon,
        cake_size=cake_size,
        tolerance=tolerance,
    )
    assert l == pytest.approx(to_decimal(0.25), abs=tolerance)
    assert r == pytest.approx(to_decimal(0.75), abs=tolerance)
    assert m == pytest.approx(to_decimal(0.50), abs=tolerance)

    l, m, r = _handle_adjacent(
        k=2,
        k_prime=3,
        alpha=alpha,
        preference_1=preferences[0],
        preference_i=preferences[1],
        epsilon=epsilon,
        cake_size=cake_size,
        tolerance=tolerance,
    )
    assert l == pytest.approx(to_decimal(0.25), abs=tolerance)
    assert r == pytest.approx(to_decimal(0.75), abs=tolerance)
    assert m == pytest.approx(to_decimal(0.50), abs=tolerance)


def test_binary_search_case_0_2():
    pass


def test_find_m_given_l():
    cake_size = to_decimal(1)
    epsilon = to_decimal("1e-15")
    tolerance = to_decimal("1e-10")

    preferences = [
        [gen_flat_seg(to_decimal(0), to_decimal(cake_size), to_decimal(10))],
    ]
    l = to_decimal(0.25)
    r = to_decimal(0.75)
    alpha = to_decimal(0.25)
    m_for_l = _find_m_given_l(
        l=l,
        r=r,
        alpha=alpha,
        preference_1=preferences[0],
        cake_size=cake_size,
        epsilon=epsilon,
        tolerance=tolerance,
    )
    assert m_for_l == pytest.approx(
        to_decimal(0.50), abs=tolerance
    ), f"expected 0.5, got {m_for_l}"

    l = to_decimal("0.37481689453125")
    r = to_decimal("0.7496337890625")
    alpha = to_decimal("0.250366210937500")
    m_for_l = _find_m_given_l(
        l=l,
        r=r,
        alpha=alpha,
        preference_1=preferences[0],
        cake_size=cake_size,
        epsilon=epsilon,
        tolerance=tolerance,
    )
    assert m_for_l == pytest.approx(
        to_decimal("0.625183105468685"), abs=tolerance * 1000
    ), f"expected 0.5, got {m_for_l}"

    v = get_double_prime_for_interval(
        segments=preferences[0],
        epsilon=epsilon,
        start=l,
        end=m_for_l,
        cake_size=cake_size,
    )
    assert v == pytest.approx(alpha, abs=tolerance * 1000), f"expected {alpha}, got {v}"


def test_find_m_given_r():
    cake_size = to_decimal(1)
    epsilon = to_decimal("1e-15")
    tolerance = to_decimal("1e-10")

    preferences = [
        [gen_flat_seg(to_decimal(0), to_decimal(cake_size), to_decimal(10))],
    ]
    l = to_decimal(0.25)
    r = to_decimal(cake_size)
    alpha = to_decimal(0.25)
    m_for_r = _find_m_given_r(
        l=l,
        r=r,
        alpha=alpha,
        preference_1=preferences[0],
        cake_size=cake_size,
        epsilon=epsilon,
        tolerance=tolerance,
    )
    assert m_for_r == pytest.approx(
        to_decimal(0.75), abs=tolerance * 100
    ), f"expected 0.75, got {m_for_r}"

    l = to_decimal("0.250061165541411")
    r = to_decimal("0.71877293707803")
    alpha = to_decimal("0.250091552734375")
    m_for_r = _find_m_given_r(
        l=l,
        r=r,
        alpha=alpha,
        preference_1=preferences[0],
        cake_size=cake_size,
        epsilon=epsilon,
        tolerance=tolerance,
    )
    assert m_for_r == pytest.approx(
        to_decimal("0.468681384422364"), abs=tolerance * 100
    ), f"expected 0.468681384422364, got {m_for_r}"

    v = get_double_prime_for_interval(
        segments=preferences[0],
        epsilon=epsilon,
        start=m_for_r,
        end=r,
        cake_size=cake_size,
    )
    assert almost_equal(v, alpha, tolerance)
    assert v == pytest.approx(alpha, abs=tolerance * 100), f"expected {alpha}, got {v}"

    m_for_r = to_decimal("0.469769801328437")
    v = get_double_prime_for_interval(
        segments=preferences[0],
        epsilon=epsilon,
        start=m_for_r,
        end=r,
        cake_size=cake_size,
    )
    assert almost_equal(v, alpha, tolerance), f"got: {v}, alpha: {alpha}"


def test_find_m_and_r_given_l():
    cake_size = to_decimal(1)
    epsilon = to_decimal("1e-15")
    tolerance = to_decimal("1e-10")
    alpha = to_decimal(0.25)
    l = to_decimal(0.25)

    preferences = [
        [gen_flat_seg(to_decimal(0), to_decimal(cake_size), to_decimal(10))],
    ]

    m_for_l, r_for_l = _find_m_and_r_given_l(
        l=l,
        cake_size=to_decimal(cake_size),
        alpha=alpha,
        preference_1=preferences[0],
        epsilon=epsilon,
        tolerance=tolerance,
    )
    assert m_for_l == pytest.approx(to_decimal(0.50), abs=tolerance)
    assert r_for_l == pytest.approx(to_decimal(0.75), abs=tolerance)
