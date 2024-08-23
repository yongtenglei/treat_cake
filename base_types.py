from dataclasses import dataclass, field
from decimal import Decimal, getcontext
from typing import List, Optional, Tuple

from type_helper import to_decimal

getcontext().prec = 15


@dataclass
class Segment:
    """
    startValue and endValue [0-10] (increments of 0.1)
    start and end [0-100] (increments of 1)
    """

    id: int
    start: Decimal = field(default_factory=Decimal)
    end: Decimal = field(default_factory=Decimal)
    start_value: Decimal = field(default_factory=Decimal)
    end_value: Decimal = field(default_factory=Decimal)

    def __post_init__(self):
        self.start = to_decimal(self.start)
        self.end = to_decimal(self.end)
        self.start_value = to_decimal(self.start_value)
        self.end_value = to_decimal(self.end_value)


@dataclass
class DrawnSegment:
    """
    a drawn segment is the pixel version of a segment, its values are in absolute pixels
    """

    id: int
    x1: Decimal = field(default_factory=Decimal)
    x2: Decimal = field(default_factory=Decimal)
    y1: Decimal = field(default_factory=Decimal)
    y2: Decimal = field(default_factory=Decimal)
    currently_drawing: Optional[bool] = None

    def __post_init__(self):
        self.x1 = to_decimal(self.x1)
        self.x2 = to_decimal(self.x2)
        self.y1 = to_decimal(self.y1)
        self.y2 = to_decimal(self.y2)


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

    id: int
    note: Optional[str] = None
    start: Decimal = field(default_factory=Decimal)
    end: Decimal = field(default_factory=Decimal)
    values: List[Decimal] = field(default_factory=list)

    def __post_init__(self):
        self.start = to_decimal(self.start)
        self.end = to_decimal(self.end)
        self.values = [to_decimal(v) for v in self.values]

    def assign(self, agent: int) -> "AssignedSlice":
        """Allocate a slice to a specific agent and create an immutable copy as AssignedSlice."""
        return AssignedSlice(
            start=self.start,
            end=self.end,
            values=self.values,
            id=self.id,
            owner=agent,
            note=self.note,
        )


@dataclass(frozen=True)
class FrozenUnassignedSlice:
    id: int
    note: Optional[str] = None
    start: Decimal = field(default_factory=Decimal)
    end: Decimal = field(default_factory=Decimal)
    values: List[Decimal] = field(default_factory=list)

    def __post_init__(self):
        object.__setattr__(self, "start", to_decimal(self.start))
        object.__setattr__(self, "end", to_decimal(self.end))
        object.__setattr__(self, "values", [to_decimal(v) for v in self.values])

    def assign(self, agent, note_override=None):
        return AssignedSlice(
            start=self.start,
            end=self.end,
            values=self.values,
            id=self.id,
            owner=agent,
            note=note_override or self.note,
        )


@dataclass(frozen=True)
class AssignedSlice:
    id: int
    owner: int
    note: Optional[str] = None
    start: Decimal = field(default_factory=Decimal)
    end: Decimal = field(default_factory=Decimal)
    values: List[Decimal] = field(default_factory=list)

    def __post_init__(self):
        object.__setattr__(self, "start", to_decimal(self.start))
        object.__setattr__(self, "end", to_decimal(self.end))
        object.__setattr__(self, "values", [to_decimal(v) for v in self.values])


@dataclass
class Portion:
    """
    This represents all slices assigned to a certain person.
    This is more useful for presenting info than `Slice`s.
    """

    owner: int
    percent_values: List[Decimal]
    edges: List[Tuple[Decimal, Decimal]]

    def to_dict(self):
        return {
            "owner": self.owner,
            "percentValues": [float(val) for val in self.percent_values],
            "edges": [[float(edge[0]), float(edge[1])] for edge in self.edges],
        }


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
