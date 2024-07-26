import pytest

from type_helper import to_decimal
from valuation import (
    _v,
    _v_double_prime,
    _v_prime,
    get_double_prime_for_interval,
    overline,
    underline,
)

from .algorithms.algorithm_test_utils import gen_flat_seg, gen_sloped_seg

EPSILON = to_decimal("1e-15")
TOLERANCE = to_decimal("1e-3")


def test_v():
    segs = [gen_flat_seg(0, 100, 10)]
    v = _v(segs, 0, 100)
    assert v == 1000


def test_v_zero_value():
    segs = [gen_flat_seg(0, 100, 0)]
    v = _v(segs, 0, 100)
    assert v == 0


def test_v_two_segs():
    segs = [
        gen_flat_seg(0, 50, 10),
        gen_flat_seg(50, 100, 5),
    ]

    v = _v(segs, 0, 100)
    assert v == 750


def test_v_two_segs_zero_value():
    segs = [
        gen_flat_seg(0, 50, 10),
        gen_flat_seg(50, 100, 0),
    ]

    v = _v(segs, 0, 100)
    assert v == 500


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
    assert v == pytest.approx(
        to_decimal(_v(segs, 0, 100) / 2 + EPSILON * abs(100 - 0)), abs=TOLERANCE
    )


def test_v_prime_two_segs():
    segs = [
        gen_flat_seg(0, 50, 10),
        gen_flat_seg(50, 100, 5),
    ]

    v = _v_prime(segs, to_decimal(0.1), 0, 100)
    assert v == pytest.approx(
        to_decimal(_v(segs, 0, 50) / 2 + to_decimal(0.1) * abs(50 - 0))
        + to_decimal(_v(segs, 50, 100) / 2 + to_decimal(0.1) * abs(100 - 50)),
        abs=TOLERANCE,
    )


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
    v = _v_prime(segs, to_decimal(0.1), 0, 100)
    assert v == pytest.approx(
        to_decimal(_v(segs, 0, 50) / 2 + to_decimal(0.1) * abs(50 - 0))
        + to_decimal(_v(segs, 50, 100) / 2 + to_decimal(0.1) * abs(100 - 50)),
        abs=TOLERANCE,
    )
    assert v == pytest.approx(to_decimal(197.5), abs=TOLERANCE)


def test_v_double_prime_one_seg():
    segs = [gen_flat_seg(0, 1, 10)]
    v = _v_double_prime(
        segs, EPSILON, to_decimal(0), to_decimal(1), cake_size=to_decimal(1)
    )
    assert v == pytest.approx(to_decimal(10), abs=TOLERANCE)


def test_v_double_prime_one_seg_by_interval():
    segs = [gen_flat_seg(0, 1, 10)]
    v = get_double_prime_for_interval(
        segs, EPSILON, to_decimal(0), to_decimal(1), cake_size=to_decimal(1)
    )
    assert v == pytest.approx(to_decimal(10), abs=TOLERANCE)
    assert v == _v_double_prime(
        segs, EPSILON, to_decimal(0), to_decimal(1), to_decimal(1)
    )


def test_v_double_prime_one_seg_by_interval_zero_value():
    segs = [gen_flat_seg(0, 1, 0)]
    v = get_double_prime_for_interval(
        segs, EPSILON, to_decimal(0), to_decimal(1), cake_size=to_decimal(1)
    )
    assert v == pytest.approx(to_decimal(0), abs=TOLERANCE)
    assert v == _v_double_prime(
        segs, EPSILON, to_decimal(0), to_decimal(1), to_decimal(1)
    )


def test_v_double_prime_two_flat_segs_by_interval():
    segs = [
        gen_flat_seg(to_decimal(0), to_decimal(1), to_decimal(10)),
        gen_flat_seg(to_decimal(1), to_decimal(2), to_decimal(10)),
    ]
    # All segments
    v = get_double_prime_for_interval(
        segs, EPSILON, to_decimal(0), to_decimal(2), cake_size=to_decimal(2)
    )
    assert v == pytest.approx(to_decimal(20), abs=TOLERANCE)
    assert v == _v_double_prime(
        segs, EPSILON, to_decimal(0), to_decimal(2), cake_size=to_decimal(2)
    )

    # First half
    v = get_double_prime_for_interval(
        segs, EPSILON, to_decimal(0), to_decimal(1), cake_size=to_decimal(2)
    )
    assert v == pytest.approx(to_decimal(10), abs=TOLERANCE)
    assert v == _v_double_prime(
        segs, EPSILON, to_decimal(0), to_decimal(1), cake_size=to_decimal(2)
    )

    # Second half
    v = get_double_prime_for_interval(
        segs, EPSILON, to_decimal(1), to_decimal(2), cake_size=to_decimal(2)
    )
    assert v == pytest.approx(to_decimal(10), abs=TOLERANCE)
    assert v == _v_double_prime(
        segs, EPSILON, to_decimal(1), to_decimal(2), cake_size=to_decimal(2)
    )


def test_v_double_prime_two_flat_segs_by_interval_zero_value():
    segs = [
        gen_flat_seg(to_decimal(0), to_decimal(1), to_decimal(10)),
        gen_flat_seg(to_decimal(1), to_decimal(2), to_decimal(0)),
    ]
    # All segments
    v = get_double_prime_for_interval(
        segs, EPSILON, to_decimal(0), to_decimal(2), cake_size=to_decimal(2)
    )
    assert v == pytest.approx(to_decimal(10), abs=TOLERANCE)
    assert v == _v_double_prime(
        segs, EPSILON, to_decimal(0), to_decimal(2), cake_size=to_decimal(2)
    )

    # First half
    v = get_double_prime_for_interval(
        segs, EPSILON, to_decimal(0), to_decimal(1), cake_size=to_decimal(2)
    )
    assert v == pytest.approx(to_decimal(10), abs=TOLERANCE)
    assert v == _v_double_prime(
        segs, EPSILON, to_decimal(0), to_decimal(1), cake_size=to_decimal(2)
    )

    # Second half
    v = get_double_prime_for_interval(
        segs, EPSILON, to_decimal(1), to_decimal(2), cake_size=to_decimal(2)
    )
    assert v == pytest.approx(to_decimal(0), abs=TOLERANCE)
    assert v == _v_double_prime(
        segs, EPSILON, to_decimal(1), to_decimal(2), cake_size=to_decimal(2)
    )


def test_v_double_prime_two_slop_segs_by_interval():
    segs = [
        gen_sloped_seg(to_decimal(0), to_decimal(1), to_decimal(10), to_decimal(0)),
        gen_sloped_seg(to_decimal(1), to_decimal(2), to_decimal(0), to_decimal(10)),
    ]
    # All segments
    v = get_double_prime_for_interval(
        segs, EPSILON, to_decimal(0), to_decimal(2), cake_size=to_decimal(2)
    )
    assert v == pytest.approx(to_decimal(10), abs=TOLERANCE)
    assert v == _v_double_prime(
        segs, EPSILON, to_decimal(0), to_decimal(2), cake_size=to_decimal(2)
    )

    # First half
    v = get_double_prime_for_interval(
        segs, EPSILON, to_decimal(0), to_decimal(1), cake_size=to_decimal(2)
    )
    assert v == pytest.approx(to_decimal(5), abs=TOLERANCE)
    assert v == _v_double_prime(
        segs, EPSILON, to_decimal(0), to_decimal(1), cake_size=to_decimal(2)
    )

    # Second half
    v = get_double_prime_for_interval(
        segs, EPSILON, to_decimal(1), to_decimal(2), cake_size=to_decimal(2)
    )
    assert v == pytest.approx(to_decimal(5), abs=TOLERANCE)
    assert v == _v_double_prime(
        segs, EPSILON, to_decimal(1), to_decimal(2), cake_size=to_decimal(2)
    )


def test_v_double_prime_two_slop_segs_by_interval_zero_value():
    segs = [
        gen_sloped_seg(to_decimal(0), to_decimal(1), to_decimal(0), to_decimal(0)),
        gen_sloped_seg(to_decimal(1), to_decimal(2), to_decimal(0), to_decimal(10)),
    ]
    # All segments
    v = get_double_prime_for_interval(
        segs, EPSILON, to_decimal(0), to_decimal(2), cake_size=to_decimal(2)
    )
    assert v == pytest.approx(to_decimal(5), abs=TOLERANCE)
    assert v == _v_double_prime(
        segs, EPSILON, to_decimal(0), to_decimal(2), cake_size=to_decimal(2)
    )

    # First half
    v = get_double_prime_for_interval(
        segs, EPSILON, to_decimal(0), to_decimal(1), cake_size=to_decimal(2)
    )
    assert v == pytest.approx(to_decimal(0), abs=TOLERANCE)
    assert v == _v_double_prime(
        segs, EPSILON, to_decimal(0), to_decimal(1), cake_size=to_decimal(2)
    )

    # Second half
    v = get_double_prime_for_interval(
        segs, EPSILON, to_decimal(1), to_decimal(2), cake_size=to_decimal(2)
    )
    assert v == pytest.approx(to_decimal(5), abs=TOLERANCE)
    assert v == _v_double_prime(
        segs, EPSILON, to_decimal(1), to_decimal(2), cake_size=to_decimal(2)
    )


# =====================Test for a weird case, precision of floating points may cause weird thing
def test_v_double_prime_one_seg_by_interval_weird_case():
    segs = [gen_flat_seg(0, 1, 10)]
    v = get_double_prime_for_interval(
        segs, EPSILON, to_decimal(0.25), to_decimal(0.625), cake_size=to_decimal(1)
    )
    v_2 = get_double_prime_for_interval(
        segs,
        EPSILON,
        to_decimal(0.25000000002910383),
        to_decimal(0.6250000000145519),
        cake_size=to_decimal(1),
    )
    assert v == pytest.approx(v_2, abs=TOLERANCE), "You should see this failed case"
    # assert v == _v, "Should be equal"
    # assert v == pytest.approx(Decimal(3.75), abs=TOLERANCE)


def test_v_double_prime_one_seg_by_interval_weird_case_1():
    segs = [gen_flat_seg(0, 1, 10)]
    v = get_double_prime_for_interval(
        segs, EPSILON, to_decimal(0.25), to_decimal(0.625), cake_size=to_decimal(1)
    )
    _v = _v_double_prime(
        segs,
        EPSILON,
        to_decimal(0.25),
        to_decimal(0.625),
        to_decimal(1),
    )
    assert v == _v, "Should be equal"
    assert v == pytest.approx(
        to_decimal(3.75), abs=TOLERANCE
    ), "You should see this failed case"


def test_v_double_prime_one_seg_by_interval_weird_case_2():
    segs = [gen_flat_seg(0, 1, 10)]
    v = get_double_prime_for_interval(
        segs,
        EPSILON,
        to_decimal(0.25000000002910383),
        to_decimal(0.6250000000145519),
        cake_size=to_decimal(1),
    )
    _v = _v_double_prime(
        segs,
        EPSILON,
        to_decimal(0.25000000002910383),
        to_decimal(0.6250000000145519),
        cake_size=to_decimal(1),
    )
    assert v == _v, "Should be equal"
    assert v == pytest.approx(
        to_decimal(3.75), abs=TOLERANCE
    ), "You should see this failed case"


def test_tmp():
    segs = [gen_flat_seg(0, 1, 10)]
    # v = get_double_prime_for_interval(
    #     segs,
    #     to_decimal("1e-15"),
    #     to_decimal("0.4999389648874057456851005554"),
    #     to_decimal("0.7499694824437028728425502775"),
    # )
    # v = get_double_prime_for_interval(
    #     segs,
    #     to_decimal("1e-15"),
    #     to_decimal("0.4999389648874057456851005554"),
    #     to_decimal("0.666605631568932821331861717"),
    # )

    v = get_double_prime_for_interval(
        segs,
        to_decimal("1e-15"),
        to_decimal("0.25"),
        to_decimal("0.4999389649310614913702011108"),
        cake_size=to_decimal(1),
    )

    assert v == pytest.approx(to_decimal("2.5"), abs=TOLERANCE), "NOOOO"


# =====================


def test_v_double_prime_various_cases():
    # Need more patience to pass the test
    TOLERANCE = to_decimal("1e-3")

    segs = [gen_flat_seg(0, 1, 10)]

    test_cases = [
        (to_decimal(0), to_decimal(1), 10),
        (to_decimal(0.4), to_decimal(0.5), 1),
        (to_decimal(0), to_decimal(0.5), 5),
    ]

    for start, end, expected in test_cases:
        print(f"\n======case {start}, {end}======")
        result = get_double_prime_for_interval(
            segs, EPSILON, start, end, cake_size=to_decimal(1)
        )
        assert result == pytest.approx(to_decimal(expected), abs=TOLERANCE)
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
    TOLERANCE = to_decimal("1e-10")

    assert overline(0.1, 0.05) == pytest.approx(to_decimal(0.15), abs=TOLERANCE)

    assert overline(0.02, 0.01) == pytest.approx(to_decimal(0.03), abs=TOLERANCE)

    assert overline(0.775, 0.025) == pytest.approx(to_decimal(0.8), abs=TOLERANCE)

    assert overline(0.333, 0.333) == pytest.approx(to_decimal(0.666), abs=TOLERANCE)

    assert overline(0.9999999, 0.002) <= 1
    assert overline(0.9999999, 0.002) == pytest.approx(1, abs=TOLERANCE)
    assert overline(0.9999999, 0.002) == 1

    assert overline(1, 0.333) <= 1
    assert overline(1, 0.333) == pytest.approx(1, abs=TOLERANCE)
    assert overline(1, 0.333) == 1


def test_underline():
    TOLERANCE = to_decimal("1e-10")

    assert underline(0.4, 0.1) == pytest.approx(to_decimal(0.3), abs=TOLERANCE)
    assert underline(0.5, 0.1) == pytest.approx(to_decimal(0.4), abs=TOLERANCE)

    assert underline(0.1, 0.05) == pytest.approx(to_decimal(0.05), abs=TOLERANCE)

    assert underline(0.02, 0.01) == pytest.approx(to_decimal(0.01), abs=TOLERANCE)

    assert underline(0.775, 0.025) == pytest.approx(to_decimal(0.75), abs=TOLERANCE)

    assert underline(0.9999999, 0.002) == pytest.approx(to_decimal(0.998), TOLERANCE)

    assert underline(0.333, 0.333) >= 0
    assert underline(0.333, 0.333) == pytest.approx(0, TOLERANCE)
    assert underline(0.333, 0.333) == 0

    assert underline(0.000002, 0.02) >= 0
    assert underline(0.000002, 0.02) == pytest.approx(0, TOLERANCE)
    assert underline(0.000002, 0.02) == 0

    assert underline(0, 0.02) >= 0
    assert underline(0, 0.02) == pytest.approx(0, TOLERANCE)
    assert underline(0, 0.02) == 0
