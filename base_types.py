from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional, Tuple


@dataclass
class Segment:
    """
    startValue and endValue [0-10] (increments of 0.1)
    start and end [0-100] (increments of 1)
    """

    id: int
    start: Decimal
    end: Decimal
    start_value: Decimal
    end_value: Decimal


@dataclass
class DrawnSegment:
    """
    a drawn segment is the pixel version of a segment, its values are in absolute pixels
    """

    id: int
    x1: Decimal
    x2: Decimal
    y1: Decimal
    y2: Decimal
    currently_drawing: Optional[bool] = None


Preferences = List[List[Segment]]


@dataclass
class Slice:
    """
    Equivalent to UnassignedSlice implemented by Andy by adding assign function.

    `UnassignedSlice`s don't belong to anyone, so store a `values` array with the
    slice value for each of the agents.
    Use `.assign()` to turn a `UnassignedSlice` into a `Slice`.
    `Slice`s are assigned to given agent but still keep the `values` array for all agents.

    Note that `UnassignedSlice` and `Slice` cannot be turned back into `Segment`
    objects and are immutable.

    These should only be used internally in algorithm code
    """

    start: Decimal
    end: Decimal
    values: List[Decimal]
    id: int
    note: Optional[str] = None

    def assign(self, agent: int) -> "AssignedSlice":
        """Allocate a slice to a specific agent and create an immutable copy as AssignedSlice."""
        return AssignedSlice(
            self.start, self.end, self.values, self.id, agent, self.note
        )


@dataclass(frozen=True)
class FrozenUnassignedSlice:
    start: Decimal
    end: Decimal
    values: List[Decimal]
    id: int
    note: Optional[str] = None

    def assign(self, agent, note_override=None):
        return AssignedSlice(
            self.start,
            self.end,
            self.values,
            self.id,
            agent,
            note_override or self.note,
        )


@dataclass(frozen=True)
class AssignedSlice:
    start: Decimal
    end: Decimal
    values: List[Decimal]
    id: int
    owner: int
    note: Optional[str] = None


@dataclass
class Portion:
    """
    This represents all slices assigned to a certain person.
    This is more useful for presenting info than `Slice`s.
    """

    owner: int
    percent_values: List[float]
    edges: List[Tuple[int, int]]


@dataclass
class SectionLabel:
    """
    A label in the graph such as "chocolate"
    """

    id: int
    name: str
    start: int
    end: int
    color: str
