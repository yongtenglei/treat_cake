import pytest
from treat_cake.algorithms.cut_and_choose import cut_and_choose
from treat_cake.algorithms.algorithm_test_utils import (
    gen_flat_seg,
    check_if_envy_free,
    gen_sloped_seg,
    halfway_point_of_triangle_area,
    gen_random_segs,
)
from treat_cake.types import AssignedSlice

CAKE_SIZE = 100


def test_splits_uniform_flat_value_graph_evenly_in_half():
    # Setup for person 1 and 2 with each having uniform value over the cake
    person1 = [
        gen_flat_seg(0, 100, 10)
    ]  # Represents a flat segment with value 10 over the length 0 to 100
    person2 = [gen_flat_seg(0, 100, 10)]

    result = cut_and_choose([person1, person2], CAKE_SIZE)["solution"]

    assert len(result) == 2, "The result should have exactly two segments."

    expected_segment_1 = AssignedSlice(
        owner=1, start=0, end=50, values=[500, 500], id=1
    )
    expected_segment_2 = AssignedSlice(
        owner=0, start=50, end=100, values=[500, 500], id=2
    )
    print("{result[0}=}")
    assert result[0] == expected_segment_1, "First segment does not match expected"
    assert result[1] == expected_segment_2, "Second segment does not match expected"

    check_if_envy_free(2, result)


def test_splits_seesaw_like_graph():
    person1 = [
        gen_flat_seg(0, 50, 10),
        gen_flat_seg(50, 100, 5),
    ]
    person2 = [
        gen_flat_seg(0, 50, 5),
        gen_flat_seg(50, 100, 10),
    ]

    result = cut_and_choose([person1, person2], CAKE_SIZE)["solution"]
    assert len(result) == 2, "The result should have exactly two segments."

    expected_segment_1 = AssignedSlice(owner=0, start=0, end=37.5, id=1, values=None)
    expected_segment_2 = AssignedSlice(owner=1, start=37.5, end=100, id=2, values=None)
    assert (
        result[0].owner == expected_segment_1.owner
        and result[0].start == expected_segment_1.start
        and result[0].end == expected_segment_1.end
    ), "First segment does not match expected"
    assert (
        result[1].owner == expected_segment_2.owner
        and result[1].start == expected_segment_2.start
        and result[1].end == expected_segment_2.end
    ), "Second segment does not match expected"

    check_if_envy_free(2, result)


def test_splits_seesaw_like_sloped_graph():
    # 500, halfway point is ~30%
    person1 = [gen_sloped_seg(0, 100, 10, 0)]
    # 500, halfway point is ~70%
    person2 = [gen_sloped_seg(0, 100, 0, 10)]

    result = cut_and_choose([person1, person2], CAKE_SIZE)["solution"]
    assert len(result) == 2, "The result should have exactly two segments."

    assert (
        result[0].owner == 0
        and result[0].end == pytest.approx(100 - halfway_point_of_triangle_area, 0.01)
        and result[0].values[0] == pytest.approx(250, 0.01)
    ), "First segment does not match expected"
    assert result[1].owner == 1, "Second segment does not match expected"

    check_if_envy_free(2, result)


def test_splits_tricky_case():
    # This case fails if we only slice on whole numbers

    person1 = [
        gen_flat_seg(0, 40, 1),
        gen_flat_seg(40, 65, 8.3),
        gen_flat_seg(65, 100, 1),
    ]
    person2 = [
        gen_flat_seg(0, 30, 4),
        gen_flat_seg(30, 50, 8),
        gen_flat_seg(50, 70, 6),
        gen_flat_seg(70, 90, 8),
        gen_flat_seg(90, 100, 0),
    ]

    result = cut_and_choose([person1, person2], CAKE_SIZE)["solution"]
    assert len(result) == 2, "The result should have exactly two segments."

    check_if_envy_free(2, result)


def test_splits_tricky_sloped_case():
    person1 = [gen_flat_seg(0, 45, 3.5), gen_sloped_seg(45, 100, 7.5, 6.5)]
    person2 = [gen_sloped_seg(0, 60, 8, 9.5), gen_sloped_seg(60, 100, 2.5, 5.5)]

    result = cut_and_choose([person1, person2], CAKE_SIZE)["solution"]
    assert len(result) == 2, "The result should have exactly two segments."

    check_if_envy_free(2, result)


def test_splits_randomly_generated_preferences_fairly():
    segs = [gen_random_segs(CAKE_SIZE), gen_random_segs(CAKE_SIZE)]

    result = cut_and_choose(segs, CAKE_SIZE)["solution"]
    check_if_envy_free(2, result)


def test_splits_randomly_generated_preferences_fairly_on_smaller_cake_size():
    small_cake = 3
    segs = [gen_random_segs(small_cake), gen_random_segs(small_cake)]

    result = cut_and_choose(segs, small_cake)["solution"]
    check_if_envy_free(2, result)
