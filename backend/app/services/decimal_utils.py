from decimal import Decimal, ROUND_HALF_UP

D2 = Decimal("0.01")
D3 = Decimal("0.001")


def money(value: Decimal | int | float | str) -> Decimal:
    return Decimal(str(value)).quantize(D2, rounding=ROUND_HALF_UP)


def qty(value: Decimal | int | float | str) -> Decimal:
    return Decimal(str(value)).quantize(D3, rounding=ROUND_HALF_UP)


def split_inclusive_tax(gross: Decimal, gst_rate: Decimal) -> tuple[Decimal, Decimal]:
    if gst_rate <= 0:
        return money(gross), Decimal("0.00")
    taxable = money(gross * Decimal("100") / (Decimal("100") + gst_rate))
    tax = money(gross - taxable)
    return taxable, tax
