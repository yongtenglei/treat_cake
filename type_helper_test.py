from decimal import Decimal

from .type_helper import to_decimal


def test_to_decimal():
    a = to_decimal(4)
    assert a == Decimal("4")

    a = Decimal(4)
    assert a == to_decimal(4)
