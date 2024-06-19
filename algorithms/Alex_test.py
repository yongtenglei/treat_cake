import pytest

from treat_cake.algorithms.Alex import equipartition
from treat_cake.algorithms.algorithm_test_utils import gen_flat_seg, gen_sloped_seg

from treat_cake.values import get_values_for_cuts

CAKE_SIZE = 100


def test_equipartition_one_piece():
    tolerance: float = 0.0001

    preference = [
        gen_flat_seg(0, CAKE_SIZE, 10),
    ]

    cuts = equipartition(preference)
    slice_values = get_values_for_cuts(
        preference=preference, cuts=cuts, cake_size=CAKE_SIZE
    )
    assert len(slice_values) == 4

    average_value = sum(slice_values) / len(slice_values)
    expected_average_value = 250
    assert average_value == pytest.approx(expected_average_value, tolerance)

    for slice_value in slice_values:
        assert slice_value == pytest.approx(
            expected_average_value, tolerance
        ), f"slice {slice_value} not equal to average value {average_value}"


def test_equipartition_seesaw_like_graph():
    tolerance: float = 0.0001

    preference = [
        gen_flat_seg(0, CAKE_SIZE // 2, 10),
        gen_flat_seg(CAKE_SIZE // 2, CAKE_SIZE, 5),
    ]

    cuts = equipartition(preference)
    slice_values = get_values_for_cuts(
        preference=preference, cuts=cuts, cake_size=CAKE_SIZE
    )
    assert len(slice_values) == 4

    average_value = sum(slice_values) / len(slice_values)
    expected_average_value = 187.5  # 750 / 4
    assert average_value == pytest.approx(expected_average_value, tolerance)

    for slice_value in slice_values:
        assert slice_value == pytest.approx(
            expected_average_value, tolerance
        ), f"Slice {slice_value} not equal to average value {average_value}"


def test_equipartition_seesaw_sloped_graph():
    tolerance = 0.0001

    preference = [
        gen_sloped_seg(0, CAKE_SIZE // 2, 0, 10),
        gen_sloped_seg(CAKE_SIZE // 2, CAKE_SIZE, 10, 0),
    ]

    cuts = equipartition(preference)

    slice_values = get_values_for_cuts(preference, cuts, CAKE_SIZE)

    assert len(slice_values) == 4, "The number of slices should be exactly four."

    expected_total_value = 500
    expected_average_value = expected_total_value / 4

    assert expected_total_value == pytest.approx(
        sum(slice_values), tolerance
    ), "The sum of slice values should equal the total cake value."

    for slice_value in slice_values:
        assert slice_value == pytest.approx(
            expected_average_value, tolerance
        ), f"Slice value {slice_value} not approximately equal to expected average value {expected_average_value}"
