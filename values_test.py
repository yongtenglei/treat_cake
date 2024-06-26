from typing import List

from treat_cake.algorithms.algorithm_test_utils import gen_flat_seg
from treat_cake.base_types import Segment
from treat_cake.values_bak import find_cut_line_by_percent


def test_find_cut_line_by_percent():
    cake_size = 1

    preferences: list[Segment] = [gen_flat_seg(0, cake_size, 10)]
    cut = find_cut_line_by_percent(preferences, 0.25)
    assert cut == 0.25
