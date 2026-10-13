"""Jalankan tiga mutasi pada salinan sementara, tanpa mengubah pricing.py."""

from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parent
MUTATIONS = [
    (
        "01_no_discount",
        "Menghapus penerapan diskon pada calculate_total",
        "discounted = apply_member_discount(subtotal, is_member)",
        "discounted = subtotal",
        "Test total anggota mendeteksi hilangnya diskon, termasuk input desimal.",
    ),
    (
        "02_wrong_tax",
        "Mengubah tarif pajak dari 11% menjadi 12%",
        "TAX_RATE = 0.11",
        "TAX_RATE = 0.12",
        "Test pajak dan integrasi total mendeteksi tarif yang salah.",
    ),
    (
        "03_missing_quantity_validation",
        "Menghapus validasi kuantitas nol atau negatif",
        '    if quantity <= 0:\n        raise ValueError("quantity must be positive")\n',
        "",
        "Test pengecualian mendeteksi masukan tidak valid yang diterima tanpa ValueError.",
    ),
]


def main():
    source = (ROOT / "pricing.py").read_text(encoding="utf-8")
    report_dir = ROOT / "reports"
    report_dir.mkdir(exist_ok=True)
    rows = []
    for slug, description, original, replacement, conclusion in MUTATIONS:
        if source.count(original) != 1:
            raise RuntimeError(f"Target mutasi {slug} harus ditemukan tepat sekali")
        # Setiap mutan berasal dari kode acuan; mutasi tidak ditumpuk.
        with tempfile.TemporaryDirectory(prefix=f"pricing_{slug}_") as temporary:
            workdir = Path(temporary)
            (workdir / "pricing.py").write_text(
                source.replace(original, replacement, 1), encoding="utf-8"
            )
            shutil.copytree(ROOT / "tests", workdir / "tests", ignore=shutil.ignore_patterns("__pycache__"))
            shutil.copy2(ROOT / "pytest.ini", workdir / "pytest.ini")
            result = subprocess.run(
                [sys.executable, "-m", "pytest", "-v", "--color=no"],
                cwd=workdir,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                check=False,
            )
        (report_dir / f"{slug}.txt").write_text(result.stdout, encoding="utf-8")
        failed = re.findall(r"^FAILED (\S+)", result.stdout, flags=re.MULTILINE)
        if result.returncode != 1 or not failed:
            raise RuntimeError(
                f"Mutasi {slug} tidak menghasilkan kegagalan test yang diharapkan; "
                f"periksa reports/{slug}.txt (exit code {result.returncode})"
            )
        test_names = "<br>".join(f"`{name}`" for name in failed)
        rows.append(f"| {description} | {test_names} | Terdeteksi: {conclusion} |")
        print(f"{slug}: terdeteksi oleh {len(failed)} kasus test")

    report = "\n".join([
        "# Hasil pengujian mutasi",
        "",
        "Tiga mutasi dijalankan berurutan pada salinan sementara yang terpisah. "
        "Setiap salinan dimulai dari kode acuan yang sama. pricing.py asli tidak diubah.",
        "",
        "Perintah untuk setiap salinan: `python -m pytest -v --color=no`. "
        "Kegagalan di bawah berasal dari eksekusi nyata; log lengkap tersedia dalam berkas 01–03 di direktori ini.",
        "",
        "| Kerusakan buatan | Test yang gagal | Kesimpulan daya deteksi |",
        "| --- | --- | --- |",
        *rows,
        "",
        "Ketiga mutan terdeteksi (3/3, 100% untuk tiga mutasi ini). "
        "Hasil ini tidak membuktikan bahwa semua kemungkinan kerusakan pasti terdeteksi.",
        "",
    ])
    (report_dir / "mutation_results.md").write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
