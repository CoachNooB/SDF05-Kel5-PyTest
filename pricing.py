TAX_RATE = 0.11
MEMBER_DISCOUNT_RATE = 0.10


def calculate_subtotal(unit_price, quantity):
    if unit_price < 0:
        raise ValueError("unit_price must not be negative")
    if quantity <= 0:
        raise ValueError("quantity must be positive")
    return unit_price * quantity


def apply_member_discount(subtotal, is_member):
    if is_member:
        return subtotal * (1 - MEMBER_DISCOUNT_RATE)
    return subtotal


def add_tax(amount):
    return amount * (1 + TAX_RATE)


def calculate_total(unit_price, quantity, is_member=False):
    subtotal = calculate_subtotal(unit_price, quantity)
    discounted = apply_member_discount(subtotal, is_member)
    return add_tax(discounted)


def write_receipt(path, lines):
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines) + "\n")
