<div align="center">

# 💻 LAPTOP SPAREPART PRO
### *Modern Point of Sale (POS) & Bookkeeping Management System*

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Tkinter](https://img.shields.io/badge/Desktop_GUI-Tkinter-239120?style=for-the-badge&logo=windows&logoColor=white)](https://docs.python.org/3/library/tkinter.html)
[![Streamlit](https://img.shields.io/badge/Web_Demo-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![PDF Generator](https://img.shields.io/badge/Receipt-FPDF2-E11D48?style=for-the-badge)](https://pyfpdf.github.io/fpdf2/)
[![Excel Export](https://img.shields.io/badge/Export-OpenPyXL-107C41?style=for-the-badge&logo=microsoftexcel&logoColor=white)](https://openpyxl.readthedocs.io/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)

<br/>

**Sistem manajemen kasir, inventaris sparepart, dan pembukuan laba/rugi toko komputer yang dirancang dengan Arsitektur Ganda (*Dual Interface*): Aplikasi Desktop Offline Standalone (.exe) dan Web Dashboard Interaktif (Streamlit).**

[Live Web Demo](#-demo-web-online-streamlit) • [Fitur Utama](#-fitur-unggulan) • [Arsitektur Proyek](#-arsitektur-sistem) • [Panduan Instalasi](#-cara-menjalankan-proyek) • [Akun Demo](#-kredensial-login-bawaan)

---

</div>

## 📌 Sekilas Proyek

Aplikasi **Laptop Sparepart Pro** dikembangkan untuk menjawab kebutuhan toko fisik (*brick-and-mortar*) sparepart laptop yang membutuhkan pencatatan kasir cepat, kalkulasi kembalian akurat, kontrol stok real-time, cetak nota struk kasir termal 80mm, serta rekapitulasi laba bersih harian yang siap diekspor ke Microsoft Excel.

### 🌟 Keunggulan Arsitektur Ganda (*Dual-Interface Architecture*)
Proyek ini mengimplementasikan pemisahan antara **Core Business Logic** dengan **Presentation Layer**:
1. 🖥️ **Desktop POS Application (`main.py` / `.exe`)**: 
   - Dirancang untuk operasional harian kasir di toko fisik.
   - Bekerja secara *offline-first* dengan penyimpanan lokal yang aman tanpa ketergantungan internet.
   - Tersedia dalam format file mandiri `.exe` (*standalone executable*).
2. 🌐 **Web Cloud Application (`app_web.py`)**:
   - Antarmuka berbasis web responsif menggunakan **Streamlit**.
   - Dapat diakses dari browser maupun perangkat mobile/tablet untuk monitoring manajemen jarak jauh.
   - Siap dideploy ke cloud secara instan untuk kebutuhan pameran portofolio dan *live demonstration*.

---

## 🚀 Fitur Unggulan

| Modul | Deskripsi Kemampuan |
| :--- | :--- |
| **📊 Dashboard & Analitik** | Metrik real-time: Total Produk, Peringatan Stok Kritis ($\le 3$ unit), Total Omset Penjualan, dan Total Keuntungan Bersih (Laba). Dilengkapi tabel aktivitas 5 transaksi terbaru. |
| **📦 Manajemen Inventaris** | Pencarian instan (*live search*), filter kategori, indikator status stok visual (🟢 Aman, 🟠 Menipis, 🔴 Habis), serta operasi CRUD dengan validasi integritas data numerik. |
| **🛒 Kasir & POS Multi-Item** | Keranjang belanja multi-item terpadu dalam 1 nomor nota. Dilengkapi pengecekan stok otomatis, kalkulator uang kembalian, dan tombol shortcut nominal pembayaran cepat. |
| **📄 Cetak Nota Struk Otomatis** | Menghasilkan berkas nota struk PDF berukuran kasir termal 80mm secara otomatis dengan perincian item, subtotal, uang tunai, dan kembalian. |
| **📑 Pembukuan Laba & Export** | Menghitung laba bersih riil berdasarkan selisih Harga Jual dan HPP (Harga Modal). Dilengkapi filter periode (Hari Ini / Bulan Ini / Semua) dan fitur **Export ke Excel (.xlsx)** berformat tabel rapi. |
| **👥 Role-Based Access Control (RBAC)** | Pemisahan hak akses antara **Admin** (akses penuh termasuk manajemen akun dan laba) dengan **Karyawan/Kasir** (fokus transaksi penjualan). Dilengkapi fitur ganti password langsung dari UI. |

---

## 🛠️ Tech Stack & Library

* **Core Language:** Python 3.10+
* **Desktop GUI:** Tkinter & Custom TTK Styling
* **Web Interface:** Streamlit Framework
* **Data Manipulation:** Pandas & Python CSV Engine (DAO Pattern)
* **Receipt Generation:** FPDF2 (Thermal Receipt 80mm Page Layout)
* **Spreadsheet Reporting:** OpenPyXL (Styled Workbook with Dynamic Formatting)
* **Binary Packaging:** PyInstaller 6.x (Portable Windows PE Executable)

---

## 📂 Struktur Direktori

```text
├── 📁 data/                        # Database lokal berbasis CSV
│   ├── barang.csv                  # Katalog master data sparepart
│   ├── transaksi.csv               # Histori pembukuan riwayat penjualan & laba
│   └── user.csv                    # Kredensial akun dan hak akses peran (RBAC)
│
├── 📁 modules/                     # Layer logika bisnis & data access (Shared Core)
│   ├── __init__.py
│   ├── database.py                 # DAO layer (mendukung path script & frozen .exe)
│   ├── barang.py                   # Logika inventaris, validasi, & stok kritis
│   ├── transaksi.py                # Pemrosesan checkout atomic & generator nota PDF
│   ├── laporan.py                  # Agregasi keuangan, filter waktu, & exporter Excel
│   └── login.py                    # Dialog modal autentikasi desktop
│
├── 📁 nota/                        # Direktori output file nota struk kasir (PDF)
├── 📁 laporan_excel/               # Direktori output rekapitulasi laporan Excel (.xlsx)
├── 📁 dist/                        # Direktori binary aplikasi Windows (.exe)
│   └── TokoSparepartLaptop.exe     # Standalone Desktop Executable
│
├── app_web.py                      # Aplikasi Web Demo berbasis Streamlit
├── main.py                         # Aplikasi Desktop GUI berbasis Tkinter
├── Jalankan_Aplikasi.bat           # Launcher instan desktop tanpa jendela konsol
├── requirements.txt                # Daftar dependensi library Python
└── README.md                       # Dokumentasi resmi proyek
```

---

## 🔑 Kredensial Login Bawaan

Gunakan akun default berikut untuk masuk ke sistem:

| Username | Password | Role | Hak Akses |
| :---: | :---: | :---: | :--- |
| `faris` | `123456` | **Admin** | Akses penuh: Dashboard, Inventaris, Kasir, Laporan Laba, & Kelola User |

> 💡 *Admin dapat menambahkan akun baru dengan role **Karyawan** atau mengganti password melalui menu **Kelola User**.*

---

## 💻 Cara Menjalankan Proyek

### 1. Kloning Repository
```bash
git clone https://github.com/USERNAME/pembukuan-toko-sparepart-laptop.git
cd pembukuan-toko-sparepart-laptop
```

### 2. Pemasangan Dependensi
Pastikan Python 3.10+ sudah terpasang, lalu jalankan:
```bash
pip install -r requirements.txt
```

### 3. Menjalankan Versi yang Diinginkan

#### A. Menjalankan Versi Desktop GUI (Tkinter)
* **Melalui Terminal:**
  ```bash
  python main.py
  ```
* **Tanpa Terminal (Klik Ganda):**
  Klik dua kali file `Jalankan_Aplikasi.bat` atau buka file `TokoSparepartLaptop.exe`.

#### B. Menjalankan Versi Web (Streamlit)
```bash
streamlit run app_web.py
```
Aplikasi web akan terbuka otomatis di peramban Anda pada alamat `http://localhost:8501`.

---

## 🌐 Deployment Web Demo ke Streamlit Community Cloud

Aplikasi web `app_web.py` siap dideploy ke cloud gratis dalam 3 langkah:
1. Hubungkan repository GitHub Anda ke [Streamlit Community Cloud](https://share.streamlit.io/).
2. Buat aplikasi baru (*New App*), pilih branch `main`.
3. Set *Main file path* menjadi `app_web.py`, lalu klik **Deploy**.
4. Salin tautan publik yang dihasilkan untuk dipasang pada portofolio Anda.

---

## 📄 Lisensi

Proyek ini dilisensikan di bawah lisensi **MIT License**. Terbuka untuk pengembangan akademik, pembelajaran, dan modifikasi komersial.

<div align="center">
  <sub>Dibangun dengan dedikasi untuk memenuhi standar perangkat lunak komersial & portofolio profesional.</sub>
</div>
