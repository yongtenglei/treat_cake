from decimal import Decimal, getcontext
from typing import List

from base_types import FrozenUnassignedSlice, Preferences, Slice
from type_helper import de_norm, to_decimal
from valuation import get_double_prime_for_interval
from values import get_value_for_interval

getcontext().prec = 15


def cut_slice_origin(
    preferences: Preferences, start: Decimal, end: Decimal, id: int, note=None
) -> FrozenUnassignedSlice:
    if start > end:
        raise ValueError(
            f"Start cannot be before end. Start {start}, end {end}, preferences {str(preferences)}"
        )

    values = [get_value_for_interval(segments, start, end) for segments in preferences]

    return FrozenUnassignedSlice(
        start=Decimal(start), end=Decimal(end), values=values, id=id, note=note
    )


def cut_cake(
    preferences: Preferences,
    cake_size: Decimal,
    epsilon: Decimal,
    cuts: List[Decimal],
) -> List[FrozenUnassignedSlice]:

    slices = []
    start = to_decimal(0)

    for i, end in enumerate(cuts):
        slice = cut_slice(
            preferences=preferences,
            cake_size=cake_size,
            epsilon=epsilon,
            start=start,
            end=end,
            id=i,
            note=None,
        )
        slices.append(slice)
        start = end

    return slices


def cut_slice(
    preferences: Preferences,
    cake_size: Decimal,
    epsilon: Decimal,
    start: Decimal,
    end: Decimal,
    id: int,
    note=None,
) -> FrozenUnassignedSlice:
    if start > end:
        raise ValueError(
            f"Start cannot be before end. Start {start}, end {end}, preferences {str(preferences)}"
        )

    values = [
        de_norm(
            v=get_double_prime_for_interval(
                segments, epsilon, start, end, cake_size=cake_size
            ),
            whole_cake_value=get_value_for_interval(
                segments,
                to_decimal(0),
                to_decimal(cake_size),
            ),
        )
        for segments in preferences
    ]

    return FrozenUnassignedSlice(start=start, end=end, values=values, id=id, note=note)


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
