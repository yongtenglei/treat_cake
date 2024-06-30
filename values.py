from dataclasses import dataclass
from decimal import Decimal
from typing import List, Optional

from treat_cake.base_types import Segment


@dataclass
class BoundaryOptions:
    start_bound: int
    end_bound: int


def find_cut_line_by_percent(
    segments: List[Segment],
    target_percent_val: float,
    options: Optional[BoundaryOptions] = None,
) -> Decimal:
    start = options.start_bound if options else 0
    end = options.end_bound if options else float("inf")
    total_cake_value = get_value_for_interval(segments, Decimal(start), Decimal(end))
    target_value = total_cake_value * Decimal(target_percent_val)
    return find_cut_line_by_value(segments, target_value, options)


def find_cut_line_by_value(
    segments: List[Segment],
    target_value: Decimal,
    options: Optional[BoundaryOptions] = None,
) -> Decimal:
    running_total = Decimal(0)
    for seg in segments:
        seg_value = (
            _measure_partial_segment(
                seg, Decimal(options.start_bound), Decimal(options.end_bound)
            )
            if options
            else measure_segment(seg)
        )
        if running_total + seg_value >= target_value:
            return _find_segment_cutline(seg, target_value - running_total, options)
        running_total += seg_value
    raise ValueError("No cut line in segment")


def _find_segment_cutline(
    seg: Segment, target_area: Decimal, options: Optional[BoundaryOptions] = None
) -> Decimal:
    """
    Finds the cutline up to ~10e-13 precision which is the error with floating point numbers.
    Could get more precise with a math library but that's already extremely good.
    """
    if options:
        start_bound = max(options.start_bound, seg.start)
        end_bound = min(options.end_bound, seg.end)
    else:
        start_bound, end_bound = seg.start, seg.end
    slope = Decimal((seg.end_value - seg.start_value) / (seg.end - seg.start))

    start_bound = Decimal(start_bound)
    end_bound = Decimal(end_bound)

    if seg.start_value == seg.end_value:  # Flat segment
        seg_value = _measure_partial_segment(seg, start_bound, end_bound)
        target_area_percent = target_area / seg_value if seg_value > 0 else 0
        return start_bound + (end_bound - start_bound) * target_area_percent
    else:  # Sloped segment
        start_val = Decimal(
            seg.start_value
            + ((start_bound - seg.start) * slope if start_bound > seg.start else 0)
        )
        # Thanks to Bence Szilágyi for help with the math here.
        # The formula is the result of adding a triangle and rectangle together,
        # then solving for the width and one side (endValue):
        # triangle area = (endValue * width) / 2
        # rectangle area = startValue * width
        # total area = (endValue * width) / 2 + (startValue * width)
        # The endValue can be found with the width and slope:
        # endValue = width * slope
        #
        # The rectangle and triangle definitions "assume" that the slope is positive
        # but this actually works even if the slope is negative because in that case the
        # area of the triangle will be negative.
        target_end = (
            -start_val + (start_val**2 + Decimal(2) * slope * target_area).sqrt()
        ) / slope
        return start_bound + target_end


def get_value_for_interval(
    segments: List[Segment], start: Decimal, end: Decimal
) -> Decimal:
    """
    Returns the total value of an interval,
    even if covers several segments or splits segments in half.
    """
    total = Decimal(0)
    for seg in segments:
        if seg.end <= start or seg.start >= end:
            # this segment not relevant
            continue

        total += _measure_partial_segment(seg, start, end)
    return total


def _measure_partial_segment(seg: Segment, start: Decimal, end: Decimal) -> Decimal:
    """
    Measures the area of a segment
    Works with flat or sloped sections, whole numbers and decimals.
    """
    start_cap = max(start, Decimal(seg.start))
    end_cap = min(end, Decimal(seg.end))
    measuring_width = Decimal(end_cap - start_cap)

    if measuring_width <= 0:
        # Nothing to measure
        return Decimal(0)
    if seg.start_value == seg.end_value:
        # Flat section
        return Decimal(seg.start_value) * measuring_width
    else:
        # Sloped section
        segment_width = seg.end - seg.start
        slope = Decimal((seg.end_value - seg.start_value) / segment_width)
        start_val = Decimal(seg.start_value) + slope * (start_cap - Decimal(seg.start))
        end_val = Decimal(seg.end_value) - slope * (Decimal(seg.end) - end_cap)
        avg_value = (start_val + end_val) / 2
        return Decimal(measuring_width * avg_value)


def measure_segment(seg: Segment) -> Decimal:
    return _measure_partial_segment(seg, Decimal(seg.start), Decimal(seg.end))


def get_total_value(segments: List[Segment]) -> Decimal:
    return get_value_for_interval(segments, Decimal(0), Decimal(float("inf")))


# TODO: May delete
def get_value_at_point(segments: List[Segment], point: int) -> float:
    for seg in segments:
        if seg.end <= point or seg.start >= point:
            continue
        if seg.start_value == seg.end_value:
            return seg.start_value
        else:
            slope = (seg.end_value - seg.start_value) / (seg.end - seg.start)
            return seg.start_value + slope * (point - seg.start)


def get_values_for_cuts_origin(
    preference: List[Segment], cuts: List[float], cake_size: float
) -> List[float]:
    slice_values = []

    start = 0
    for end in cuts:
        value = get_value_for_interval(preference, start, end)
        slice_values.append(value)
        start = end
    # Last piece
    slice_values.append(get_value_for_interval(preference, cuts[-1], cake_size))
    return slice_values
