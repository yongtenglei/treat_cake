from decimal import Decimal, getcontext

getcontext().prec = 15


def to_decimal(value):
    return Decimal(str(value))


def almost_equal(a: Decimal, b: Decimal, tolerance: Decimal) -> bool:
    return abs(a - b) <= tolerance
