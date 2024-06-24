from ..base_types import Segment, AssignedSlice
from typing import List
import random


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


def check_if_envy_free(num_people: int, result: List[AssignedSlice]):
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
