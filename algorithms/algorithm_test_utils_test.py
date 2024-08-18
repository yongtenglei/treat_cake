import logging

from base_types import AssignedSlice
from type_helper import to_decimal

from .algorithm_test_utils import check_if_envy_free, generate_all_possible_allocations


def test_all_allocations():
    cuts = [to_decimal(0.25), to_decimal(0.5), to_decimal(0.75)]
    num_agents = 4

    generated_allocations = [
        allocation for allocation in generate_all_possible_allocations(cuts, num_agents)
    ]
    # number of permutation = n! where n = 4
    expected_number_of_allocations = 24
    logging.info(generated_allocations)
    assert len(generated_allocations) == expected_number_of_allocations


def test_if_envy_free():
    allocation = [
        AssignedSlice(
            id=0,
            owner=0,
            values=[
                to_decimal(0.25),
                to_decimal(0),
                to_decimal(0),
                to_decimal(0),
            ],
            start=to_decimal(0),
            end=to_decimal(0.25),
        ),
        AssignedSlice(
            id=1,
            owner=1,
            values=[
                to_decimal(0),
                to_decimal(0.25),
                to_decimal(0),
                to_decimal(0),
            ],
            start=to_decimal(0.25),
            end=to_decimal(0.5),
        ),
        AssignedSlice(
            id=2,
            owner=2,
            values=[
                to_decimal(0),
                to_decimal(0),
                to_decimal(0.25),
                to_decimal(0),
            ],
            start=to_decimal(0.5),
            end=to_decimal(0.75),
        ),
        AssignedSlice(
            id=3,
            owner=3,
            values=[
                to_decimal(0),
                to_decimal(0),
                to_decimal(0.75),
                to_decimal(0.25),
            ],
            start=to_decimal(0.75),
            end=to_decimal(1),
        ),
    ]

    if_envy_free = check_if_envy_free(num_agents=4, allocation=allocation)
    assert if_envy_free, "Should be envy free"
