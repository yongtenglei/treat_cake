from decimal import ROUND_HALF_UP, Decimal, getcontext

getcontext().prec = 15


def to_decimal(value):
    return Decimal(str(value))


def almost_equal(a: Decimal, b: Decimal, tolerance: Decimal) -> bool:
    return abs(a - b) <= tolerance


def scale_to_unit(value: Decimal, cake_size: Decimal) -> Decimal:
    """
    Adjust value from [1, cake_size] to [0, 1]
    """
    return (to_decimal(value) - to_decimal(1)) / (to_decimal(cake_size) - to_decimal(1))


def scale_back_from_unit(value: Decimal, cake_size: Decimal) -> Decimal:
    """
    Adjust value from [0, 1] back to [1, cake_size]
    """
    scaled_value = to_decimal(1) + to_decimal(value) * (
        to_decimal(cake_size) - to_decimal(1)
    )
    # return to_decimal(scaled_value.to_integral_value(rounding=ROUND_HALF_UP))
    return to_decimal(scaled_value.to_integral_value())
