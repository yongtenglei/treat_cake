import pytest

from treat_cake.algorithms.algorithm_test_utils import gen_flat_seg
from treat_cake.valuation import (
    _v_prime,
    _v,
    overline,
    underline,
    v_double_prime_for_interval,
)

EPSILON = 1e-1
TOLERANCE = 1e-6


def test_v():
    segs = [gen_flat_seg(0, 100, 10)]
    v = _v(segs, 0, 100)
    assert v == 1000


def test_v_prime():
    segs = [gen_flat_seg(0, 100, 10)]
    v = _v_prime(segs, EPSILON, 0, 100)
    assert v == 510


def test_v_double_prime_one_seg():
    segs = [gen_flat_seg(0, 1, 10)]
    v = v_double_prime_for_interval(segs, EPSILON, 0, 1)
    assert v == 5.1


def test_v_double_prime_two_seesaw_like_segs():
    segs = [
        gen_flat_seg(0, 1, 10),
        gen_flat_seg(1, 2, 5),
    ]


def test_overline():
    assert overline(0.1, 0.05) == pytest.approx(0.15, TOLERANCE)

    assert overline(0.02, 0.01) == 0.03

    assert overline(0.775, 0.025) == 0.8

    assert overline(0.333, 0.333) == 0.666

    assert overline(0.9999999, 0.002) <= 1
    assert overline(0.9999999, 0.002) == pytest.approx(1, TOLERANCE)
    assert overline(0.9999999, 0.002) == 1

    assert overline(1, 0.333) <= 1
    assert overline(1, 0.333) == pytest.approx(1, TOLERANCE)
    assert overline(1, 0.333) == 1


def test_underline():
    assert underline(0.1, 0.05) == 0.05

    assert underline(0.02, 0.01) == 0.01

    assert underline(0.775, 0.025) == 0.75

    assert underline(0.9999999, 0.002) == pytest.approx(0.998, TOLERANCE)

    assert underline(0.333, 0.333) >= 0
    assert underline(0.333, 0.333) == pytest.approx(0, TOLERANCE)
    assert underline(0.333, 0.333) == 0

    assert underline(0.000002, 0.02) >= 0
    assert underline(0.000002, 0.02) == pytest.approx(0, TOLERANCE)
    assert underline(0.000002, 0.02) == 0

    assert underline(0, 0.02) >= 0
    assert underline(0, 0.02) == pytest.approx(0, TOLERANCE)
    assert underline(0, 0.02) == 0
