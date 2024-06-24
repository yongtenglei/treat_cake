from ..base_types import Portion, Slice, AssignedSlice, FrozenUnassignedSlice
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass


# Enumerating the algorithm names in Python, similar to TypeScript's enum but using class attributes
class AlgoName:
    cut_and_choose = "cutAndChoose"
    selfridge_conway = "selfridgeConway"


@dataclass
class Algorithm:
    key: str
    name: str
    num_agents_text: str
    min_agents: int
    max_agents: int
    short_description: str


@dataclass
class Step:
    # The form of a step is [agent number (0-indexed), action taken]
    actor: int
    action: str
    pieces: List[Slice]
    assign: bool


@dataclass
class Result:
    solution: List[Portion]
    steps: List[Step]


def make_step(
    actor: int,
    action: str,
    pieces: List[FrozenUnassignedSlice] = [],
    assign: bool = False,
) -> Step:
    return Step(actor, action, pieces, assign)


# Dictionary to store algorithms' metadata
algorithms: Dict[str, Algorithm] = {
    AlgoName.cut_and_choose: Algorithm(
        key="cutAndChoose",
        name="Cut and Choose",
        num_agents_text="2 people",
        min_agents=2,
        max_agents=2,
        short_description="A simple method for envy-free division between two people. One cuts, the other chooses.",
    ),
    AlgoName.selfridge_conway: Algorithm(
        key="selfridgeConway",
        name="Selfridge-Conway",
        num_agents_text="3 people",
        min_agents=3,
        max_agents=3,
        short_description="A method for envy-free division between three people. Maximum of five cuts.",
    ),
}
