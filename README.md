# Tugas Praktik Sesi 10 — Python dan pytest

Implementasi berdasarkan `SDF_Ass_10.pdf`. `pricing.py` disalin dari kode acuan dalam dokumen tanpa mengubah logikanya. Test mencakup enam aturan bisnis, kasus tepi, dan jalur kesalahan.

## Menjalankan pengujian

Jalankan dari direktori tugas:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
pytest -v
```

Lingkungan `.venv` sudah disiapkan pada workspace ini. Untuk menjalankan tanpa aktivasi:

```bash
.venv/bin/pytest -v
```

Perintah `pytest` tanpa argumen juga menemukan seluruh test melalui `pytest.ini`. Terdapat **24 fungsi test** yang menghasilkan **32 kasus test** setelah parametrization. Eksekusi pada Python 3.14.7 dan pytest 9.1.1 menghasilkan **32 passed**. Keluaran lengkap tersedia di [reports/pytest-v.txt](reports/pytest-v.txt); opsi `--color=no` hanya menonaktifkan warna pada log.

## Artefak

| Berkas | Isi |
| --- | --- |
| [pricing.py](pricing.py) | Kode acuan dari dokumen |
| [tests/test_pricing.py](tests/test_pricing.py) | Seluruh unit test dan test integrasi total |
| [reports/pytest-v.txt](reports/pytest-v.txt) | Bukti pengujian pada kode benar |
| [reports/mutation_results.md](reports/mutation_results.md) | Tabel tiga mutasi beserta nama test yang benar-benar gagal |
| [run_mutations.py](run_mutations.py) | Skrip untuk mengulang eksperimen mutasi |
| README.md | Petunjuk, pemetaan persyaratan, dan jawaban analisis |

## Cakupan dan fitur pytest

| Persyaratan | Implementasi |
| --- | --- |
| Subtotal = harga × kuantitas | Empat kombinasi harga/kuantitas dan harga nol |
| Harga negatif ditolak | Harga negatif bulat/desimal, serta propagasi kesalahan melalui total |
| Kuantitas nol/negatif ditolak | Test terpisah untuk nol dan negatif, serta propagasi melalui total |
| Diskon anggota 10%; non-anggota penuh | Test diskon positif, desimal, nol, dan kedua status keanggotaan |
| Pajak 11% atas nilai setelah diskon | Test pajak langsung dan total anggota/non-anggota; nilai harapan dihitung manual |
| Struk dengan newline termasuk baris terakhir | Pemeriksaan isi byte persis untuk beberapa baris dan satu baris |
| Kasus tambahan struk | UTF-8, penimpaan isi lama, dan daftar baris kosong sesuai perilaku kode acuan |
| `pytest.mark.parametrize` ≥ 3 kombinasi | `test_subtotal_multiplies_price_by_quantity`: empat kombinasi |
| `pytest.raises` pada ≥ 2 fungsi test | Lima fungsi test memeriksa `ValueError` beserta pesannya |
| `pytest.approx` | Digunakan pada subtotal, diskon, pajak, dan total dengan floating point |
| Fixture `tmp_path` | Seluruh lima test struk menggunakan direktori sementara masing-masing |

Nilai harapan menggunakan angka yang dihitung dari aturan bisnis, bukan konstanta atau fungsi produksi yang sedang diuji. Dengan demikian, perubahan tarif pada kode produksi tidak ikut mengubah nilai harapan test.

## Pengujian mutasi

Setelah mengaktifkan virtual environment:

```bash
python run_mutations.py
```

Skrip membuat salinan sementara yang berbeda untuk setiap mutasi, menyalin suite test yang sama, lalu menjalankan pytest secara berurutan. Kode acuan tidak diedit. Log dan tabel hasil diperbarui di direktori `reports`.

Hasil eksekusi nyata:

| Kerusakan buatan | Jumlah kasus gagal | Log |
| --- | --- | --- |
| Menghapus penerapan diskon di `calculate_total` | 2 | [01_no_discount.txt](reports/01_no_discount.txt) |
| Mengubah pajak 11% menjadi 12% | 6 | [02_wrong_tax.txt](reports/02_wrong_tax.txt) |
| Menghapus validasi kuantitas | 5 | [03_missing_quantity_validation.txt](reports/03_missing_quantity_validation.txt) |

Nama lengkap setiap test yang gagal dan kesimpulan daya deteksinya terdapat pada [tabel hasil mutasi](reports/mutation_results.md). Kegagalan dalam ketiga log tersebut merupakan hasil yang diharapkan pada kode yang sengaja dirusak.

## Jawaban pertanyaan analisis

### 1. Mengapa menggunakan `pytest.approx` untuk floating point?

Sebagian pecahan desimal tidak dapat direpresentasikan tepat dalam format biner floating point. Misalnya, `0.1 * 3` dapat menghasilkan `0.30000000000000004`, sehingga perbandingan langsung dengan `0.3` gagal walaupun perhitungannya sesuai maksud bisnis. `pytest.approx(0.3)` menerima selisih kecil dalam batas toleransi. Toleransi tersebut tetap cukup ketat untuk mendeteksi perubahan tarif dari 11% menjadi 12%, sebagaimana dibuktikan eksperimen mutasi.

### 2. Mengapa berkas nyata di direktori proyek lebih berisiko daripada `tmp_path`?

Nama berkas tetap di direktori proyek dapat menimpa data pengguna, berbenturan dengan test lain, atau menyisakan isi dari eksekusi sebelumnya. Akibatnya, hasil dapat bergantung pada urutan test atau kondisi mesin. Fixture `tmp_path` menyediakan direktori sementara yang unik untuk setiap pemanggilan test sehingga data terisolasi. Pengelolaan direktori sementara dilakukan pytest, termasuk kebijakan retensi; tidak perlu menganggap semua berkas langsung dihapus begitu sebuah test selesai.

### 3. Test mana yang paling lemah, dan bagaimana memperbaikinya?

`test_tax_preserves_zero_amount` paling lemah jika dinilai sebagai pendeteksi kesalahan tarif pajak: nol dikali faktor pajak apa pun tetap nol. Bahkan implementasi rusak `return 0` akan lulus test ini. Test tersebut tetap berguna untuk menjaga kasus tepi nol, tetapi perlu dilengkapi masukan positif dengan hasil konkret, seperti 100.000 → 111.000, serta masukan desimal. Suite ini sudah melengkapinya melalui `test_tax_adds_eleven_percent` dan `test_tax_handles_decimal_amount`. Jika ingin memperkuat satu fungsi test itu sendiri, parametrisasikan nol, nilai positif, dan desimal beserta nilai harapannya.

### 4. Bagaimana mutasi mengubah penilaian kualitas test?

Semua test lulus pada kode benar belum membuktikan bahwa assertion mampu menangkap kesalahan. Mutasi memeriksa apakah test benar-benar gagal saat perilaku bisnis dirusak. Hilangnya diskon terdeteksi oleh dua kasus total anggota, perubahan pajak oleh enam kasus, dan hilangnya validasi oleh lima kasus pengecualian. Contohnya, test diskon langsung tetap lulus ketika pemanggilan diskon di `calculate_total` dihapus; test integrasi total anggota diperlukan untuk mendeteksinya. Ketiga mutan terbunuh (3/3), tetapi angka tersebut hanya berlaku bagi tiga kerusakan yang dicoba dan bukan jaminan semua bug terdeteksi.

### 5. Apa padanan fitur pytest dalam JUnit 5?

| pytest | JUnit 5 | Kegunaan |
| --- | --- | --- |
| `pytest.raises(ValueError)` | `assertThrows(IllegalArgumentException.class, ...)` untuk implementasi Java yang memakai pengecualian tersebut | Memastikan operasi melempar tipe pengecualian yang diharapkan |
| `pytest.mark.parametrize` | `@ParameterizedTest` dengan `@ValueSource`, `@CsvSource`, atau `@MethodSource` | Menjalankan test dengan beberapa data masukan |
| Fixture `@pytest.fixture` untuk penyiapan | `@BeforeEach` untuk penyiapan tiap test; `@AfterEach` untuk pembersihan | Menyiapkan sumber daya yang diperlukan test |
| Fixture `tmp_path` | `@TempDir` pada `Path` atau `File` | Menyediakan direktori sementara untuk pengujian berkas |

Padanan fixture tidak sepenuhnya satu banding satu: fixture pytest mendukung injeksi berdasarkan nama dan beberapa scope. Pada JUnit 5, kebutuhan yang lebih kompleks dapat memakai extension dan `ParameterResolver`.

### 6. Mengapa total anggota tidak selalu lebih besar daripada subtotal?

Misalkan subtotal adalah `S`. Diskon 10% menghasilkan `0,90 × S`, kemudian pajak 11% atas nilai itu menghasilkan:

```text
total anggota = S × 0,90 × 1,11
              = S × 0,999
```

Untuk subtotal positif, total anggota justru 0,1% lebih kecil daripada subtotal. Contoh: subtotal Rp100.000, setelah diskon Rp90.000, pajak Rp9.900, sehingga total Rp99.900. Jika subtotal nol, total juga nol. Kasus Rp100.000 → Rp99.900 diperiksa oleh `test_total_for_member_includes_discount_and_tax`.
