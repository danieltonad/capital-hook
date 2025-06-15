import math

def round_trade_size(value):
    """
    Rounds down the trade size based on Capital.com-like rules.
    For large values, it applies specific rounding bases, while smaller values are rounded to whole numbers.
    """
    abs_value = abs(value) 
    if abs_value < 1:
        # Round small values to 2 decimal places
        return math.floor(value * 100) / 100
    elif abs_value < 100:
        # Round to whole numbers
        return math.floor(value)
    elif abs_value < 1_000_000:
        rounding_base = 100
    elif abs_value < 10_000_000:
        rounding_base = 10_000
    elif abs_value < 100_000_000:
        rounding_base = 10_000
    else:
        rounding_base = 1_000_000

    rounded = math.floor(value / rounding_base) * rounding_base
    return rounded