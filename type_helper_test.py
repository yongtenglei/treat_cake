from decimal import Decimal

from pytest import approx

from type_helper import scale_back_from_unit, scale_to_unit, to_decimal

TOLERANCE = Decimal("1e-6")


def test_to_decimal():
    a = to_decimal(4)
    assert a == Decimal("4")

    a = Decimal(4)
    assert a == to_decimal(4)


def test_scale_to_unit_cake_1():
    tolerance = to_decimal("1e-1")

    cake_size = to_decimal(1)

    a = to_decimal(0)
    unit = scale_to_unit(a, cake_size)
    expected = to_decimal(0)
    assert unit == expected, f"expect: {expected}, got: {unit}"

    b = to_decimal(cake_size)
    unit = scale_to_unit(b, cake_size)
    expected = to_decimal(1)
    assert unit == expected, f"expect: {expected}, got: {unit}"

    c = to_decimal(cake_size / 2)
    unit = scale_to_unit(c, cake_size)
    expected = to_decimal(0.5)
    assert unit == approx(expected, rel=tolerance), f"expect: {expected}, got: {unit}"


def test_scale_to_unit_cake_100():
    tolerance = to_decimal("1e-1")

    cake_size = to_decimal(100)

    a = to_decimal(0)
    unit = scale_to_unit(a, cake_size)
    expected = to_decimal(0)
    assert unit == expected, f"expect: {expected}, got: {unit}"

    b = to_decimal(cake_size)
    unit = scale_to_unit(b, cake_size)
    expected = to_decimal(1)
    assert unit == expected, f"expect: {expected}, got: {unit}"

    c = to_decimal(cake_size / 2)
    unit = scale_to_unit(c, cake_size)
    expected = to_decimal(0.5)
    assert unit == approx(expected, rel=tolerance), f"expect: {expected}, got: {unit}"


def test_scale_back_from_unit_cake_1():
    cake_size = to_decimal(1)

    a = to_decimal(0)
    origin = scale_back_from_unit(a, cake_size)
    expected = to_decimal(0)
    assert origin == expected, f"expect: {expected}, got: {origin}"

    b = to_decimal(cake_size)
    origin = scale_back_from_unit(b, cake_size)
    expected = to_decimal(cake_size)
    assert origin == expected, f"expect: {expected}, got: {origin}"

    c = to_decimal(0.5)
    origin = scale_back_from_unit(c, cake_size)
    expected = to_decimal(cake_size / 2)
    assert origin == approx(
        expected, rel=TOLERANCE
    ), f"expect: {expected}, got: {origin}"


def test_scale_back_from_unit_cake_100():
    cake_size = to_decimal(100)

    a = to_decimal(0)
    origin = scale_back_from_unit(a, cake_size)
    expected = to_decimal(0)
    assert origin == expected, f"expect: {expected}, got: {origin}"

    b = to_decimal(1)
    origin = scale_back_from_unit(b, cake_size)
    expected = to_decimal(cake_size)
    assert origin == expected, f"expect: {expected}, got: {origin}"

    c = to_decimal(0.5)
    origin = scale_back_from_unit(c, cake_size)
    expected = to_decimal(cake_size / 2)
    assert origin == approx(
        expected, rel=TOLERANCE
    ), f"expect: {expected}, got: {origin}"
