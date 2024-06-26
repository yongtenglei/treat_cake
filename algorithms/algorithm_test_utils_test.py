from itertools import permutations

from treat_cake.algorithms.algorithm_test_utils import generate_all_possible_allocations


def test_all_allocations():
    cuts = [0.25, 0.5, 0.75]
    num_agents = 4

    expected_number_of_allocations = len(
        list(permutations(range(len(cuts) + 1), num_agents))
    )

    generated_allocations = sorted(
        [
            sorted(allocation)
            for allocation in generate_all_possible_allocations(cuts, num_agents)
        ]
    )

    unique_allocations = sorted(
        [
            sorted([sorted(slices) for slices in allocation])
            for allocation in generate_all_possible_allocations(cuts, num_agents)
        ]
    )

    assert len(generated_allocations) == expected_number_of_allocations
    assert len(generated_allocations) == len(unique_allocations)
    assert generated_allocations == unique_allocations
