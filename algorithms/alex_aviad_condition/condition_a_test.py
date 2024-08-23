from decimal import ROUND_DOWN, Decimal

import pytest

from algorithms.alex_aviad_condition.condition_a import check_condition_a
from type_helper import to_decimal

from ..algorithm_test_utils import check_if_envy_free, gen_flat_seg


def test_check_condition_a():
    cake_size = to_decimal(1)
    epsilon = to_decimal("1e-15")
    tolerance = to_decimal("1e-10")

    preferences = [
        [gen_flat_seg(to_decimal(0), to_decimal(cake_size), to_decimal(10))],
        [gen_flat_seg(to_decimal(0), to_decimal(cake_size), to_decimal(10))],
        [gen_flat_seg(to_decimal(0), to_decimal(cake_size), to_decimal(10))],
        [gen_flat_seg(to_decimal(0), to_decimal(cake_size), to_decimal(10))],
    ]

    is_meet, info = check_condition_a(
        alpha=to_decimal(0.25000043535345),
        preferences=preferences,
        cake_size=cake_size,
        epsilon=epsilon,
        tolerance=tolerance,
    )

    expected_info = {
        "cuts": [to_decimal(0.25), to_decimal(0.5), to_decimal(0.75)],
        "k": 3,
    }

    assert is_meet is True, "Should meet Condition A"

    assert (
        len(info["cuts"]) == len(expected_info["cuts"])
        and info["k"] == expected_info["k"]
    ), f"Expected info {expected_info}, got {info}"

    for i in range(len(expected_info["cuts"])):
        assert info["cuts"][i].quantize(
            Decimal("0.01"), rounding=ROUND_DOWN
        ) == pytest.approx(
            expected_info["cuts"][i],
            abs=tolerance,
        )
