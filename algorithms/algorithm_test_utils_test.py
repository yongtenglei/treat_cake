from itertools import permutations

from treat_cake.algorithms.algorithm_test_utils import generate_all_possible_allocations


def test_all_allocations():
    cuts = [0.25, 0.5, 0.75]
    num_agents = 4

    generated_allocations = [
        allocation for allocation in generate_all_possible_allocations(cuts, num_agents)
    ]
    # number of permutation = n! where n = 4
    expected_number_of_allocations = 24
    print(generated_allocations)
    assert len(generated_allocations) == expected_number_of_allocations
