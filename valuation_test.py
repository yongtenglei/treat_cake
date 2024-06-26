import pytest

from treat_cake.algorithms.algorithm_test_utils import gen_flat_seg, gen_sloped_seg
from treat_cake.valuation import (
    _v_prime,
    _v,
    overline,
    underline,
    _v_double_prime,
    get_double_prime_for_interval,
)

EPSILON = 1e-1
TOLERANCE = 1e-6


def test_v():
    segs = [gen_flat_seg(0, 100, 10)]
    v = _v(segs, 0, 100)
    assert v == 1000


def test_v_two_segs():
    segs = [
        gen_flat_seg(0, 50, 10),
        gen_flat_seg(50, 100, 5),
    ]

    v = _v(segs, 0, 100)
    assert v == 750


def test_v_seesaw_like_gragh():
    segs = [
        gen_sloped_seg(
            0,
            50,
            0,
            10,
        ),
        gen_sloped_seg(50, 100, 5, 0),
    ]
    v = _v(segs, 0, 100)
    assert v == 375


def test_v_prime():
    segs = [gen_flat_seg(0, 100, 10)]
    v = _v_prime(segs, EPSILON, 0, 100)
    assert v == 510


def test_v_prime_two_segs():
    segs = [
        gen_flat_seg(0, 50, 10),
        gen_flat_seg(50, 100, 5),
    ]

    v = _v_prime(segs, 0.1, 0, 100)
    assert v == 385


def test_v_prime_seesaw_like_gragh():
    segs = [
        gen_sloped_seg(
            0,
            50,
            0,
            10,
        ),
        gen_sloped_seg(50, 100, 5, 0),
    ]
    v = _v_prime(segs, 0.1, 0, 100)
    assert v == 197.5


def test_v_double_prime_one_seg():
    segs = [gen_flat_seg(0, 1, 10)]
    v = _v_double_prime(segs, EPSILON, 0, 1)
    assert v == pytest.approx(5.1, abs=TOLERANCE)


def test_v_double_prime_one_seg_by_interval():
    segs = [gen_flat_seg(0, 1, 10)]
    v = get_double_prime_for_interval(segs, EPSILON, 0, 1)
    assert v == pytest.approx(5.1, abs=TOLERANCE)


def test_v_double_prime_various_cases():
    segs = [gen_flat_seg(0, 1, 10)]

    test_cases = [
        (0, 1, 5.1),
        (0.4, 0.5, 1.54),
        (0, 0.5, 3.06),
    ]
    # test_cases = [(0, 1), (0.4, 5.5), (0, 0.5), (1.5, 4), (2, 2.5)]

    for start, end, expected in test_cases:
        print(f"\n======case {start}, {end}======")
        result = get_double_prime_for_interval(segs, EPSILON, start, end)
        assert result == pytest.approx(expected, abs=TOLERANCE)
        print(
            f"get_double_prime_for_interval(segments, epsilon, {start}, {end}) = {result}"
        )


# def test_v_double_prime_two_seesaw_like_segs():
#     # TODO:Only focus on one segmentation.
#     segs = [
#         gen_flat_seg(0, 1, 10),
#         gen_flat_seg(1, 2, 5),
#     ]


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
    assert underline(0.4, 0.1) == pytest.approx(0.3, abs=TOLERANCE)
    assert underline(0.5, 0.1) == pytest.approx(0.4, abs=TOLERANCE)

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
