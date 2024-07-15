from decimal import Decimal, InvalidOperation, getcontext

getcontext().prec = 15


def to_decimal(value) -> Decimal:
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError(f"InvalidOperation：{value}") from exc


def almost_equal(a: Decimal, b: Decimal, tolerance: Decimal) -> bool:
    return abs(a - b) <= tolerance


def scale_to_unit(a: Decimal, cake_size: Decimal) -> Decimal:
    """
    Adjust value from [0, cake_size] to [0, 1]
    """
    assert (
        to_decimal(0) <= a <= to_decimal(cake_size)
    ), f"a must be greater than or equal to 0 and less than cake_size: {cake_size}, got {a}"

    if cake_size == 1:
        return to_decimal(a)
    return to_decimal(a) / to_decimal(cake_size)


def scale_back_from_unit(a: Decimal, cake_size: Decimal) -> Decimal:
    """
    Adjust value from [0, 1] back to [0, cake_size]
    """
    assert (
        to_decimal(0) <= a <= to_decimal(1)
    ), f"a must be greater than or equal to 0 and less than 1, to transform back to [0, cake_size({cake_size}), got {a}], "

    if cake_size == 1:
        return to_decimal(a)
    return to_decimal(a) * to_decimal(cake_size)
