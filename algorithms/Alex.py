from ..base_types import Segment

from typing import List

from ..values import find_cut_line_by_percent


def equipartition(preference: List[Segment]) -> List[float]:
    # Finding cuts at 1/4, 1/2, and 3/4 of the cake
    first_cut = find_cut_line_by_percent(preference, 0.25)
    second_cut = find_cut_line_by_percent(preference, 0.50)
    third_cut = find_cut_line_by_percent(preference, 0.75)

    return [first_cut, second_cut, third_cut]
