from typing import List

from treat_cake.types import Preferences, FrozenUnassignedSlice, Slice
from treat_cake.values import get_value_for_interval


def cut_slice(
    preferences: Preferences, start: int, end: int, id: int, note=None
) -> FrozenUnassignedSlice:
    if start > end:
        raise ValueError(
            f"Start cannot be before end. Start {start}, end {end}, preferences {str(preferences)}"
        )

    values = [get_value_for_interval(segments, start, end) for segments in preferences]

    return FrozenUnassignedSlice(start, end, values, id, note)


def sort_slices_descending(agent: int, slices: List[Slice]):
    return sorted(slices, key=lambda slice: slice.values[agent], reverse=True)


def find_best_slice(agent: int, slices: List[Slice]):
    return max(slices, key=lambda slice: slice.values[agent])


def remove_slice(slice: Slice, slices: List[Slice]):
    remaining = slices.copy()
    remaining.remove(slice)
    return slice, remaining


def remove_best_slice(agent: int, slices: List[Slice]):
    best_slice = find_best_slice(agent, slices)
    return remove_slice(best_slice, slices)
