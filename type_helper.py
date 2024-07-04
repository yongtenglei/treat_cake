from decimal import Decimal


def to_decimal(value):
    return Decimal(str(value))


def almost_equal(a: Decimal, b: Decimal, tolerance: Decimal) -> bool:
    return abs(a - b) <= tolerance
