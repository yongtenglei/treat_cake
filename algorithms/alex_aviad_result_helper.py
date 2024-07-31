from decimal import Decimal
from typing import List

from algorithms.algorithm_types import Result, Step
from base_types import Portion, Preferences
from type_helper import to_decimal
from valuation import get_double_prime_for_interval

from .algorithm_types import make_step


def build_solution(
    preferences: Preferences,
    cake_size: Decimal,
    epsilon: Decimal,
    result: List,
    steps: List,
) -> Result:
    assert 4 == len(preferences), "Should only work for 4 agents for now"
    num_people = 4
    cake_size = to_decimal(cake_size)
    epsilon = to_decimal(epsilon)

    total_values = []
    for preference in preferences:
        double_prime_v = get_double_prime_for_interval(
            segments=preference,
            epsilon=epsilon,
            start=Decimal(0),
            end=Decimal(cake_size),
            cake_size=Decimal(cake_size),
        )
        total_values.append(double_prime_v)

    portions = [
        Portion(owner=i, percent_values=[Decimal(0)] * num_people, edges=[])
        for i in range(num_people)
    ]

    for slice in result:
        owner = slice.owner

        if portions[owner] is None:
            assert 1 == 2, "Should not reach here"
            portions[owner] = Portion(
                owner=owner, percent_values=[Decimal(0)] * len(total_values), edges=[]
            )

        portions[owner].edges.append((slice.start, slice.end))

        for i, slice_value in enumerate(slice.values):
            portions[owner].percent_values[i] += Decimal(slice_value) / total_values[i]

    for i in range(len(portions)):
        portions[i].edges.sort(key=lambda x: x[0])
        portions[i] = portions[i].to_dict()

    return Result(
        solution=portions,
        steps=steps,
    )
