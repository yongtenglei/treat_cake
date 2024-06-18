# from typing import List, Optional
#
# # Assuming Segment and other functions are defined as you provided or imported.
#
#
# def Equipartition(segments: List[Segment]) -> List[float]:
#     total_value = get_total_value(segments)
#     quarter_value = total_value / 4
#
#     # Finding the first cut
#     first_cut = find_cut_line_by_value(segments, quarter_value)
#
#     # Finding the second cut
#     second_cut = find_cut_line_by_value(
#         segments, 2 * quarter_value, options=BoundaryOptions(first_cut, float("inf"))
#     )
#
#     # Finding the third cut
#     third_cut = find_cut_line_by_value(
#         segments, 3 * quarter_value, options=BoundaryOptions(second_cut, float("inf"))
#     )
#
#     return [first_cut, second_cut, third_cut]
#
#
# # Example usage
# segments = [
#     Segment(0, 10, 1, 10),  # Example segment
#     # Add more segments as required
# ]
#
# cuts = Equipartition(segments)
# print("Cut positions:", cuts)
#


from ..types import Segment

from typing import List, Optional

from ..values import find_cut_line_by_percent, get_value_for_interval


def equipartition(preference: List[Segment], cake_size: float) -> List[float]:
    # Finding cuts at 1/4, 1/2, and 3/4 of the cake's physical length
    first_cut = find_cut_line_by_percent(preference, 0.25)
    second_cut = find_cut_line_by_percent(preference, 0.50)
    third_cut = find_cut_line_by_percent(preference, 0.75)

    get_value_for_interval(preference, 0, first_cut)
    return [first_cut, second_cut, third_cut]


# Example usage
segments = [
    Segment(0, 10, 1, 10)  # Example segment
    # Add more segments as required
]

cuts = EquipartitionByPercent(segments, 10)
print("Cut positions:", cuts)
