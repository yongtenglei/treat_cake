from math import isfinite


def make_percentage(num: float, precision: int = 8) -> str:
    return f"{format_number(num * 100, precision)}%"


def format_number(num: float, precision: int = 8) -> str:
    if not (isinstance(num, float) or isinstance(num, int)) or not isfinite(num):
        num = 0
    num_str = f"{num:.{precision}f}"
    num_length = len(num_str.replace(".", ""))
    if num_length < precision:
        return num_str.strip("0").rstrip(".")
    return f"{num:.{precision}g}"


def get_ordinal_ending(num: int) -> str:
    if 11 <= (num % 100) <= 13:
        return "th"
    elif num % 10 == 1:
        return "st"
    elif num % 10 == 2:
        return "nd"
    elif num % 10 == 3:
        return "rd"
    else:
        return "th"
