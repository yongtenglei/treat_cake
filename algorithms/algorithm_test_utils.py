import logging
import random
from decimal import Decimal
from itertools import permutations
from typing import List

from base_types import AssignedSlice, Preferences, Segment
from cut import cut_slice
from type_helper import de_norm, to_decimal
from values import get_value_for_interval

halfway_point_of_triangle_area = 70.710678

id_counter = 0

from decimal import getcontext

getcontext().prec = 15


def gen_flat_seg(start: Decimal, end: Decimal, value: Decimal) -> Segment:
    start = to_decimal(start)
    end = to_decimal(end)
    value = to_decimal(value)

    global id_counter
    id_counter += 1
    return Segment(
        id=id_counter, start=start, end=end, start_value=value, end_value=value
    )


def gen_sloped_seg(
    start: Decimal, end: Decimal, start_value: Decimal, end_value: Decimal
) -> Segment:
    start = to_decimal(start)
    end = to_decimal(end)
    start_value = to_decimal(start_value)
    end_value = to_decimal(end_value)

    global id_counter
    id_counter += 1
    return Segment(
        id=id_counter,
        start=start,
        end=end,
        start_value=start_value,
        end_value=end_value,
    )


def rand(max: int) -> int:
    """
    Generates pseudo-random whole numbers between 0 and `max`
    """
    return random.randint(0, max)


def gen_random_segs(cake_size: int) -> List[Segment]:
    """
    Generates a set of continuous, random segments fitting a `cakeSize` cake.
    This can represent the preferences for one person.
    """
    segs = []
    base_num = 4
    base_num_to_gen = cake_size - 1 if cake_size < base_num else base_num

    num_to_gen = 1 + rand(base_num_to_gen)
    seg_width = to_decimal(cake_size // num_to_gen)

    last_end = to_decimal(0)
    for _ in range(num_to_gen):
        if rand(1) == 1:
            segs.append(
                gen_flat_seg(last_end, last_end + seg_width, to_decimal(rand(10)))
            )
        else:
            segs.append(
                gen_sloped_seg(
                    last_end,
                    last_end + seg_width,
                    to_decimal(rand(10)),
                    to_decimal(rand(10)),
                )
            )
        last_end += seg_width
    return segs


def check_if_envy_free_allocation_origin(num_people: int, result: List[AssignedSlice]):
    for a in range(num_people):
        total_values = [0] * num_people
        for slice in result:
            total_values[slice.owner] += slice.values[a]

        obtained_value = total_values[a]
        fudge_factor = to_decimal("1e-12")
        for value in total_values:
            assert (
                value - fudge_factor <= obtained_value
            ), f"Person {a} envies another person's slices"


def generate_all_possible_allocations(cuts: List[Decimal], num_agents: int):
    slices = list(range(len(cuts) + 1))
    assert len(slices) == num_agents

    for perm in permutations(slices, num_agents):
        allocation = [[] for _ in range(num_agents)]
        for i, slice_index in enumerate(perm):
            allocation[i % num_agents].append(slice_index)
        yield allocation


def check_if_envy_free(
    num_agents: int,
    allocation: List[AssignedSlice],
    epsilon: Decimal,
    preferences: List[List[Segment]],
) -> bool:
    """O(m * n): m: number of Assigned Slice, n: number of agents"""
    fudge_factor = to_decimal(epsilon)
    logging.error(f"{allocation=}")
    for slice in allocation:
        owner_value = slice.values[slice.owner]
        owner_whole_cake_value = get_value_for_interval(
            segments=preferences[slice.owner], start=slice.start, end=slice.end
        )
        owner_fudge_value = de_norm(
            v=fudge_factor, whole_cake_value=owner_whole_cake_value
        )
        logging.error(
            f"check_if_envy_free: fudge_factor = {owner_fudge_value}, {epsilon=}"
        )

        # Check if the owner envies any other agent's value of the slice
        for i in range(num_agents):
            if i != slice.owner and slice.values[i] > owner_value + owner_fudge_value:
                return False

    return True


def find_envy_free_allocation(
    cuts: List[Decimal],
    num_agents: int,
    cake_size: Decimal,
    preferences: Preferences,
    epsilon: Decimal,
) -> List[AssignedSlice]:
    cake_size = to_decimal(cake_size)
    for allocation in generate_all_possible_allocations(cuts, num_agents):
        envy_free_allocation = []
        for agent_id, slices in enumerate(allocation):
            for slice_index in slices:
                if slice_index == 0:
                    start = 0
                else:
                    start = cuts[slice_index - 1]
                if slice_index == len(cuts):
                    # TODO:be careful
                    end = cake_size
                else:
                    end = cuts[slice_index]
                unassigned_slice = cut_slice(
                    preferences=preferences,
                    cake_size=to_decimal(cake_size),
                    epsilon=epsilon,
                    start=to_decimal(start),
                    end=to_decimal(end),
                    id=slice_index,
                    note=None,
                )
                envy_free_allocation.append(unassigned_slice.assign(agent_id))
        if check_if_envy_free(
            num_agents,
            envy_free_allocation,
            epsilon=epsilon,
            preferences=preferences,
        ):
            return envy_free_allocation
    return None
