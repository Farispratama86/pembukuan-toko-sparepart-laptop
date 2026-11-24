import datetime
import os
from modules.database import read_csv, write_csv

BARANG_FILE = "barang.csv"
TRANS_FILE = "transaksi.csv"
BARANG_FIELDS = ["kode", "nama", "kategori", "stok", "harga_beli", "harga_jual"]
TRANS_FIELDS = ["kode_transaksi", "tanggal", "kode_barang", "nama_barang", "jumlah", "total", "laba"]

def hitung_kode_transaksi_berikutnya():
    transaksi = read_csv(TRANS_FILE)
    if not transaksi:
        return "TRX001"
    
    # Ambil nomor tertinggi dari format TRX001, TRX002, dst
    angka_list = []
    for t in transaksi:
        kode = t.get("kode_transaksi", "")
        if kode.startswith("TRX"):
            try:
                num = int(kode.replace("TRX", "").strip())
                angka_list.append(num)
            except ValueError:
                pass
    
    next_num = (max(angka_list) + 1) if angka_list else (len(transaksi) + 1)
    return f"TRX{next_num:03d}"

def proses_checkout(items, bayar_tunai=0, nama_kasir="Kasir"):
    """
    items: list of dict [
        {"kode": "...", "nama": "...", "qty": int, "harga_beli": int, "harga_jual": int, "subtotal": int, "laba": int}
    ]
    bayar_tunai: nominal uang yang diberikan pembeli
    """
    if not items:
        return False, "Keranjang belanja masih kosong!", None, 0

    daftar_barang = read_csv(BARANG_FILE)
    transaksi = read_csv(TRANS_FILE)
    
    # Map barang untuk pengecekan cepat
    barang_map = {b["kode"].strip().upper(): b for b in daftar_barang}

    # 1. Validasi stok untuk seluruh item terlebih dahulu (Atomic check)
    for itm in items:
        k = itm["kode"].strip().upper()
        if k not in barang_map:
            return False, f"Barang '{itm['nama']}' tidak ditemukan di database!", None, 0
        
        stok_tersedia = int(barang_map[k].get("stok", 0))
        if itm["qty"] > stok_tersedia:
            return False, f"Stok untuk '{itm['nama']}' tidak mencukupi! (Sisa: {stok_tersedia}, Dibeli: {itm['qty']})", None, 0

    # 2. Hitung total belanja dan kembalian
    total_belanja = sum(int(itm["subtotal"]) for itm in items)
    if bayar_tunai < total_belanja:
        return False, f"Uang pembayaran kurang! (Total: Rp {total_belanja:,}, Dibayar: Rp {bayar_tunai:,})", None, 0

    kembalian = bayar_tunai - total_belanja
    kode_trx = hitung_kode_transaksi_berikutnya()
    tanggal = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

    # 3. Potong stok barang
    for itm in items:
        k = itm["kode"].strip().upper()
        stok_sekarang = int(barang_map[k].get("stok", 0))
        barang_map[k]["stok"] = str(max(0, stok_sekarang - itm["qty"]))

        # 4. Simpan ke daftar transaksi
        transaksi.append({
            "kode_transaksi": kode_trx,
            "tanggal": tanggal,
            "kode_barang": itm["kode"],
            "nama_barang": itm["nama"],
            "jumlah": itm["qty"],
            "total": itm["subtotal"],
            "laba": itm.get("laba", (itm["harga_jual"] - itm["harga_beli"]) * itm["qty"])
        })

    # Simpan perubahan barang dan riwayat transaksi ke CSV
    write_csv(BARANG_FILE, list(barang_map.values()), BARANG_FIELDS)
    write_csv(TRANS_FILE, transaksi, TRANS_FIELDS)

    # 5. Cetak nota struk PDF terpadu (1 struk untuk seluruh item)
    path_nota = cetak_nota_pdf(kode_trx, tanggal, items, total_belanja, bayar_tunai, kembalian, nama_kasir)

    return True, f"Transaksi {kode_trx} berhasil diproses!", path_nota, kembalian

def cetak_nota_pdf(kode_transaksi, tanggal, items, total, bayar_tunai, kembalian, nama_kasir="Kasir"):
    """Mencetak struk belanja kasir format 80mm PDF"""
    folder = "nota"
    if not os.path.exists(folder):
        os.makedirs(folder)

    file_path = os.path.join(folder, f"{kode_transaksi}.pdf")

    try:
        from fpdf import FPDF
    except ImportError:
        # Jika library fpdf belum terinstall, lewati pembuatan PDF tanpa error crash
        return None

    try:
        # Format thermal 80mm x panjang dinamis (panjang bertambah sesuai jumlah item)
        panjang_halaman = max(180, 110 + (len(items) * 12))
        pdf = FPDF("P", "mm", (80, panjang_halaman))
        pdf.set_auto_page_break(auto=True, margin=5)
        pdf.add_page()

        # Header Toko
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 5, "TOKO SPAREPART LAPTOP", ln=True, align="C")
        pdf.set_font("Arial", "", 8)
        pdf.cell(0, 4, "Spesialis Sparepart, Upgrade & Aksesoris", ln=True, align="C")
        pdf.cell(0, 4, "Telp/WA: 0812-3456-7890", ln=True, align="C")
        pdf.ln(1)
        pdf.cell(0, 1, "=" * 36, ln=True, align="C")
        pdf.ln(1)

        # Info Transaksi
        pdf.set_font("Arial", "", 8)
        pdf.cell(0, 4, f"No. Nota : {kode_transaksi}", ln=True)
        pdf.cell(0, 4, f"Tanggal  : {tanggal}", ln=True)
        pdf.cell(0, 4, f"Kasir    : {nama_kasir}", ln=True)
        pdf.ln(1)
        pdf.cell(0, 1, "-" * 36, ln=True, align="C")
        pdf.ln(2)

        # Rincian Barang
        pdf.set_font("Arial", "B", 8)
        pdf.cell(32, 4, "Barang")
        pdf.cell(10, 4, "Qty", align="C")
        pdf.cell(0, 4, "Subtotal", align="R", ln=True)
        pdf.set_font("Arial", "", 8)

        for itm in items:
            # Baris 1: Nama barang (bila panjang, batasi karakter)
            nama_tampil = itm["nama"][:22]
            pdf.cell(0, 4, nama_tampil, ln=True)
            # Baris 2: Qty @Harga Satuan  -->  Subtotal
            qty_harga = f"  {itm['qty']} x Rp {itm['harga_jual']:,}"
            sub_str = f"Rp {itm['subtotal']:,}"
            pdf.cell(42, 4, qty_harga)
            pdf.cell(0, 4, sub_str, align="R", ln=True)

        pdf.ln(2)
        pdf.cell(0, 1, "-" * 36, ln=True, align="C")
        pdf.ln(2)

        # Ringkasan Pembayaran
        pdf.set_font("Arial", "B", 9)
        pdf.cell(35, 5, "TOTAL")
        pdf.cell(0, 5, f"Rp {total:,}", align="R", ln=True)

        pdf.set_font("Arial", "", 8)
        pdf.cell(35, 4, "TUNAI")
        pdf.cell(0, 4, f"Rp {bayar_tunai:,}", align="R", ln=True)

        pdf.cell(35, 4, "KEMBALI")
        pdf.cell(0, 4, f"Rp {kembalian:,}", align="R", ln=True)

        pdf.ln(3)
        pdf.cell(0, 1, "=" * 36, ln=True, align="C")
        pdf.ln(3)

        # Catatan & Garansi
        pdf.set_font("Arial", "", 8)
        pdf.cell(0, 4, "Terima kasih atas kunjungan Anda!", ln=True, align="C")
        pdf.cell(0, 4, "Garansi toko berlaku sesuai ketentuan.", ln=True, align="C")
        pdf.cell(0, 4, "Barang yg dibeli tidak dapat ditukar", ln=True, align="C")
        pdf.cell(0, 4, "tanpa nota resmi ini.", ln=True, align="C")

        pdf.output(file_path)
        return file_path
    except Exception as e:
        print(f"Error saat membuat PDF nota: {e}")
        return None
