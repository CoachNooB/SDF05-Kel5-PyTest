# Hasil pengujian mutasi

Tiga mutasi dijalankan berurutan pada salinan sementara yang terpisah. Setiap salinan dimulai dari kode acuan yang sama. pricing.py asli tidak diubah.

Perintah untuk setiap salinan: `python -m pytest -v --color=no`. Kegagalan di bawah berasal dari eksekusi nyata; log lengkap tersedia dalam berkas 01–03 di direktori ini.

| Kerusakan buatan | Test yang gagal | Kesimpulan daya deteksi |
| --- | --- | --- |
| Menghapus penerapan diskon pada calculate_total | `tests/test_pricing.py::test_total_for_member_includes_discount_and_tax`<br>`tests/test_pricing.py::test_total_handles_decimal_price` | Terdeteksi: Test total anggota mendeteksi hilangnya diskon, termasuk input desimal. |
| Mengubah tarif pajak dari 11% menjadi 12% | `tests/test_pricing.py::test_tax_adds_eleven_percent`<br>`tests/test_pricing.py::test_tax_handles_decimal_amount`<br>`tests/test_pricing.py::test_total_for_member_includes_discount_and_tax`<br>`tests/test_pricing.py::test_total_for_non_member_includes_tax_without_discount`<br>`tests/test_pricing.py::test_total_defaults_to_non_member`<br>`tests/test_pricing.py::test_total_handles_decimal_price` | Terdeteksi: Test pajak dan integrasi total mendeteksi tarif yang salah. |
| Menghapus validasi kuantitas nol atau negatif | `tests/test_pricing.py::test_subtotal_rejects_zero_quantity`<br>`tests/test_pricing.py::test_subtotal_rejects_negative_quantity[-1]`<br>`tests/test_pricing.py::test_subtotal_rejects_negative_quantity[-5]`<br>`tests/test_pricing.py::test_total_propagates_invalid_quantity_error[0]`<br>`tests/test_pricing.py::test_total_propagates_invalid_quantity_error[-1]` | Terdeteksi: Test pengecualian mendeteksi masukan tidak valid yang diterima tanpa ValueError. |

Ketiga mutan terdeteksi (3/3, 100% untuk tiga mutasi ini). Hasil ini tidak membuktikan bahwa semua kemungkinan kerusakan pasti terdeteksi.
