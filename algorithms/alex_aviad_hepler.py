from typing import List

from treat_cake.base_types import Segment, AssignedSlice
from treat_cake.values import get_values_for_cuts


def check_condition_a(
    alpha: float,
    preference: List[Segment],
    current_cuts: List[float],
    cake_size: int,
    epsilon: float,
) -> bool:
    k = _find_k(preference, current_cuts, cake_size, epsilon)

    return False


def _find_k(
    preference: List[Segment], cuts: List[float], cake_size: int, epsilon: float
) -> int:

    values = get_values_for_cuts(preference, cuts, cake_size, epsilon)

    min_index = values.index(min(values))

    print(f"4 pieces have values {values}, find the last preferred k: {min_index}")

    return min_index


def _find_cuts_for_condition_a():
    # if k ==0
    pass


def find_allocation_on_condition_a() -> List[AssignedSlice]:
    return []


def check_condition_b(
    alpha: float,
    preference: List[Segment],
    current_cuts: List[float],
    cake_size: int,
    epsilon: float,
) -> bool:
    k = _find_k(preference, current_cuts, cake_size, epsilon)

    return False


def find_allocation_on_condition_b() -> List[AssignedSlice]:
    return []
