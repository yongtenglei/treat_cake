from ..type_helper import to_decimal
from .algorithm_test_utils import generate_all_possible_allocations


def test_all_allocations():
    cuts = [to_decimal(0.25), to_decimal(0.5), to_decimal(0.75)]
    num_agents = 4

    generated_allocations = [
        allocation for allocation in generate_all_possible_allocations(cuts, num_agents)
    ]
    # number of permutation = n! where n = 4
    expected_number_of_allocations = 24
    print(generated_allocations)
    assert len(generated_allocations) == expected_number_of_allocations
