from itertools import permutations

from ..base_types import Segment, AssignedSlice, Preferences
from typing import List
import random

from ..cut import cut_slice, cut_slice_origin

halfway_point_of_triangle_area = 70.710678

id_counter = 0


def gen_flat_seg(start: int, end: int, value: float) -> Segment:
    global id_counter
    id_counter += 1
    return Segment(
        id=id_counter, start=start, end=end, start_value=value, end_value=value
    )


def gen_sloped_seg(
    start: int, end: int, start_value: float, end_value: float
) -> Segment:
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
    seg_width = cake_size // num_to_gen

    last_end = 0
    for _ in range(num_to_gen):
        if rand(1) == 1:
            segs.append(gen_flat_seg(last_end, last_end + seg_width, rand(10)))
        else:
            segs.append(
                gen_sloped_seg(last_end, last_end + seg_width, rand(10), rand(10))
            )
        last_end += seg_width
    return segs


def check_if_envy_free_allocation_origin(num_people: int, result: List[AssignedSlice]):
    for a in range(num_people):
        total_values = [0] * num_people
        for slice in result:
            total_values[slice.owner] += slice.values[a]

        obtained_value = total_values[a]
        fudge_factor = 1e-12
        for value in total_values:
            assert (
                value - fudge_factor <= obtained_value
            ), f"Person {a} envies another person's slices"


def generate_all_possible_allocations(cuts: List[float], num_agents: int):
    slices = list(range(len(cuts) + 1))
    assert len(slices) == num_agents

    for perm in permutations(slices, num_agents):
        allocation = [[] for _ in range(num_agents)]
        for i, slice_index in enumerate(perm):
            allocation[i % num_agents].append(slice_index)
        yield allocation


def check_if_envy_free(num_agents: int, allocation: List[AssignedSlice]) -> bool:
    total_values = [0] * num_agents
    for slice in allocation:
        for agent_id in range(num_agents):
            total_values[agent_id] += slice.values[agent_id]

    for a in range(num_agents):
        obtained_value = total_values[a]
        fudge_factor = 1e-12
        for value in total_values:
            if value - fudge_factor > obtained_value:
                return False
    return True


# def check_if_envy_free(
#     num_agents: int, allocation: List[List[int]], preferences: Preferences
# ) -> bool:
#     total_values = [0] * num_agents
#     for agent_id, slices in enumerate(allocation):
#         for slice_id in slices:
#             total_values[agent_id] += preferences[agent_id][slice_id]
#
#     for a in range(num_agents):
#         obtained_value = total_values[a]
#         for value in total_values:
#             if value > obtained_value:
#                 return False
#     return True


def find_envy_free_allocation(
    cuts: List[float],
    num_agents: int,
    cake_size: int,
    preferences: Preferences,
    epsilon,
) -> List[AssignedSlice]:
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
                    preferences, epsilon, start, end, slice_index
                )
                envy_free_allocation.append(unassigned_slice.assign(agent_id))
        if check_if_envy_free(num_agents, envy_free_allocation):
            return envy_free_allocation
    return None


def find_envy_free_allocation_using_original_evaluation_func(
    cuts: List[float],
    num_agents: int,
    cake_size: int,
    preferences: Preferences,
) -> List[AssignedSlice]:
    """TESTING ONLY"""
    for allocation in generate_all_possible_allocations(cuts, num_agents):
        envy_free_allocation = []
        for agent_id, slices in enumerate(allocation):
            for slice_index in slices:
                if slice_index == 0:
                    start = 0
                else:
                    start = cuts[slice_index - 1]
                if slice_index == len(cuts):
                    end = cake_size
                else:
                    end = cuts[slice_index]
                unassigned_slice = cut_slice_origin(
                    preferences, start, end, slice_index
                )
                envy_free_allocation.append(unassigned_slice.assign(agent_id))
        if check_if_envy_free(num_agents, envy_free_allocation):
            return envy_free_allocation
    return None
