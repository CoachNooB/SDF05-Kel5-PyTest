import pytest

from pricing import (
    add_tax,
    apply_member_discount,
    calculate_subtotal,
    calculate_total,
    write_receipt,
)


@pytest.mark.parametrize(
    "unit_price, quantity, expected",
    [(10_000, 3, 30_000), (125, 1, 125), (2.5, 4, 10.0), (0.1, 3, 0.3)],
    ids=["multiple-items", "single-item", "decimal-price", "floating-point"],
)
def test_subtotal_multiplies_price_by_quantity(unit_price, quantity, expected):
    assert calculate_subtotal(unit_price, quantity) == pytest.approx(expected)


def test_subtotal_accepts_zero_price():
    assert calculate_subtotal(0, 5) == 0


@pytest.mark.parametrize("unit_price", [-1, -0.01])
def test_subtotal_rejects_negative_price(unit_price):
    with pytest.raises(ValueError, match="^unit_price must not be negative$"):
        calculate_subtotal(unit_price, 2)


def test_subtotal_rejects_zero_quantity():
    with pytest.raises(ValueError, match="^quantity must be positive$"):
        calculate_subtotal(10_000, 0)


@pytest.mark.parametrize("quantity", [-1, -5])
def test_subtotal_rejects_negative_quantity(quantity):
    with pytest.raises(ValueError, match="^quantity must be positive$"):
        calculate_subtotal(10_000, quantity)


def test_member_receives_ten_percent_discount():
    assert apply_member_discount(100_000, True) == pytest.approx(90_000)


def test_non_member_pays_full_subtotal():
    assert apply_member_discount(100_000, False) == 100_000


def test_member_discount_handles_decimal_subtotal():
    assert apply_member_discount(19.99, True) == pytest.approx(17.991)


@pytest.mark.parametrize("is_member", [True, False])
def test_discount_preserves_zero_subtotal(is_member):
    assert apply_member_discount(0, is_member) == 0


def test_tax_adds_eleven_percent():
    assert add_tax(100_000) == pytest.approx(111_000)


def test_tax_handles_decimal_amount():
    assert add_tax(0.1) == pytest.approx(0.111)


def test_tax_preserves_zero_amount():
    assert add_tax(0) == 0


def test_total_for_member_includes_discount_and_tax():
    # Subtotal 100_000 -> diskon 90_000 -> pajak 9_900 -> total 99_900.
    assert calculate_total(50_000, 2, True) == pytest.approx(99_900)


def test_total_for_non_member_includes_tax_without_discount():
    assert calculate_total(50_000, 2, False) == pytest.approx(111_000)


def test_total_defaults_to_non_member():
    assert calculate_total(50_000, 2) == pytest.approx(111_000)


def test_total_handles_decimal_price():
    assert calculate_total(19.99, 3, True) == pytest.approx(59.91003)


@pytest.mark.parametrize("is_member", [True, False])
def test_total_accepts_zero_price(is_member):
    assert calculate_total(0, 3, is_member) == 0


def test_total_propagates_negative_price_error():
    with pytest.raises(ValueError, match="^unit_price must not be negative$"):
        calculate_total(-1, 2, True)


@pytest.mark.parametrize("quantity", [0, -1])
def test_total_propagates_invalid_quantity_error(quantity):
    with pytest.raises(ValueError, match="^quantity must be positive$"):
        calculate_total(10_000, quantity)


def test_receipt_ends_every_line_with_newline(tmp_path):
    receipt = tmp_path / "receipt.txt"
    write_receipt(receipt, ["Subtotal: 100000", "Total: 99900"])
    assert receipt.read_bytes() == b"Subtotal: 100000\nTotal: 99900\n"


def test_receipt_with_single_line_has_final_newline(tmp_path):
    receipt = tmp_path / "receipt.txt"
    write_receipt(receipt, ["Total: 111000"])
    assert receipt.read_bytes() == b"Total: 111000\n"


def test_receipt_preserves_utf8_text(tmp_path):
    receipt = tmp_path / "receipt.txt"
    write_receipt(receipt, ["Kopi café", "Terima kasih ✓"])
    assert receipt.read_bytes() == "Kopi café\nTerima kasih ✓\n".encode("utf-8")


def test_receipt_overwrites_existing_file(tmp_path):
    receipt = tmp_path / "receipt.txt"
    receipt.write_text("Isi lama yang lebih panjang\n", encoding="utf-8")
    write_receipt(receipt, ["Baru"])
    assert receipt.read_bytes() == b"Baru\n"


def test_receipt_with_empty_lines_writes_one_newline(tmp_path):
    # Perilaku acuan: join([]) + "\n" menghasilkan satu baris baru.
    receipt = tmp_path / "receipt.txt"
    write_receipt(receipt, [])
    assert receipt.read_bytes() == b"\n"
