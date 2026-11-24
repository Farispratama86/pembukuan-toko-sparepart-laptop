import datetime
import os
from modules.database import read_csv

TRANS_FILE = "transaksi.csv"
BARANG_FILE = "barang.csv"

def ambil_semua_transaksi():
    """Mengambil semua transaksi dengan perhitungan estimasi laba jika belum ada"""
    data = read_csv(TRANS_FILE)
    barang = {b["kode"].strip().upper(): b for b in read_csv(BARANG_FILE)}

    hasil = []
    for row in data:
        t = dict(row)
        # Parse angka
        try:
            total = int(t.get("total", 0))
        except ValueError:
            total = 0
        try:
            qty = int(t.get("jumlah", 1))
        except ValueError:
            qty = 1

        # Cek kolom laba
        if "laba" in t and str(t["laba"]).strip() != "":
            try:
                laba = int(t["laba"])
            except ValueError:
                laba = 0
        else:
            # Hitung laba berdasarkan master barang jika di row lama belum ada kolom laba
            kode_b = t.get("kode_barang", "").strip().upper()
            if kode_b in barang:
                hb = int(barang[kode_b].get("harga_beli", 0))
                hj = int(barang[kode_b].get("harga_jual", 0))
                laba = (hj - hb) * qty
            else:
                laba = 0
        
        t["total_val"] = total
        t["laba_val"] = laba
        t["qty_val"] = qty
        hasil.append(t)
    return hasil

def ringkasan_keuangan(data=None):
    """Menghitung metrik ringkasan: Total Transaksi unik, Total Omset, dan Total Laba"""
    if data is None:
        data = ambil_semua_transaksi()

    total_omset = sum(row.get("total_val", 0) for row in data)
    total_laba = sum(row.get("laba_val", 0) for row in data)
    transaksi_unik = len(set(row.get("kode_transaksi", "") for row in data if row.get("kode_transaksi")))

    return {
        "total_transaksi": transaksi_unik,
        "total_omset": total_omset,
        "total_laba": total_laba,
        "total_item_terjual": sum(row.get("qty_val", 0) for row in data)
    }

def filter_transaksi_berdasarkan_periode(periode="Semua"):
    """
    periode: 'Hari Ini', '7 Hari Terakhir', 'Bulan Ini', 'Semua'
    """
    data = ambil_semua_transaksi()
    if periode == "Semua":
        return data

    now = datetime.datetime.now()
    hari_ini_str = now.strftime("%d-%m-%Y")
    bulan_ini_str = now.strftime("%m-%Y")

    filtered = []
    for row in data:
        tgl_str = row.get("tanggal", "")
        # Format tanggal bisa '08-11-2025 06:03:54' atau '2025-11-03'
        if periode == "Hari Ini":
            if tgl_str.startswith(hari_ini_str) or now.strftime("%Y-%m-%d") in tgl_str:
                filtered.append(row)
        elif periode == "Bulan Ini":
            if f"-{bulan_ini_str}" in tgl_str or now.strftime("%Y-%m") in tgl_str:
                filtered.append(row)
        else:
            filtered.append(row)

    return filtered

def export_laporan_excel(data=None):
    """Ekspor laporan riwayat transaksi dan pembukuan laba ke Excel"""
    if data is None:
        data = ambil_semua_transaksi()

    if not data:
        return False, "Tidak ada data transaksi untuk diekspor!"

    try:
        import openpyxl
        from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    except ImportError:
        return False, "Library 'openpyxl' belum terpasang. Jalankan: pip install openpyxl"

    folder = "laporan_excel"
    if not os.path.exists(folder):
        os.makedirs(folder)

    tanggal_file = datetime.datetime.now().strftime("%d-%m-%Y_%H%M%S")
    filepath = os.path.join(folder, f"Laporan_Penjualan_{tanggal_file}.xlsx")

    wb = openpyxl.Workbook()
    sheet = wb.active
    sheet.title = "Laporan Penjualan & Laba"

    # Styling
    header_fill = PatternFill(start_color="1E293B", end_color="1E293B", fill_type="solid")
    header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
    bold_font = Font(name="Segoe UI", size=10, bold=True)
    normal_font = Font(name="Segoe UI", size=10)
    center_align = Alignment(horizontal="center", vertical="center")
    right_align = Alignment(horizontal="right", vertical="center")
    left_align = Alignment(horizontal="left", vertical="center")

    thin_border = Border(
        left=Side(style='thin', color='CBD5E1'),
        right=Side(style='thin', color='CBD5E1'),
        top=Side(style='thin', color='CBD5E1'),
        bottom=Side(style='thin', color='CBD5E1')
    )

    # Title Banner
    sheet.merge_cells("A1:G1")
    sheet["A1"] = "LAPORAN PENJUALAN & PEMBUKUAN LABA TOKO SPAREPART LAPTOP"
    sheet["A1"].font = Font(name="Segoe UI", size=14, bold=True, color="0F172A")
    sheet["A1"].alignment = left_align

    sheet["A2"] = f"Dicetak pada: {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
    sheet["A2"].font = Font(name="Segoe UI", size=9, italic=True, color="64748B")

    # Table Header
    headers = [
        "Kode Transaksi", "Tanggal & Waktu", "Kode Barang", 
        "Nama Sparepart", "Qty", "Total Omset (Rp)", "Keuntungan / Laba (Rp)"
    ]
    start_row = 4
    for col_idx, header in enumerate(headers, 1):
        cell = sheet.cell(row=start_row, column=col_idx, value=header)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = center_align

    current_row = start_row + 1
    total_omset_semua = 0
    total_laba_semua = 0

    for tr in data:
        omset = tr.get("total_val", 0)
        laba = tr.get("laba_val", 0)
        total_omset_semua += omset
        total_laba_semua += laba

        row_vals = [
            tr.get("kode_transaksi", ""),
            tr.get("tanggal", ""),
            tr.get("kode_barang", ""),
            tr.get("nama_barang", ""),
            tr.get("jumlah", 1),
            omset,
            laba
        ]

        for col_idx, val in enumerate(row_vals, 1):
            cell = sheet.cell(row=current_row, column=col_idx, value=val)
            cell.font = normal_font
            cell.border = thin_border
            if col_idx in (1, 2, 3, 5):
                cell.alignment = center_align
            elif col_idx in (6, 7):
                cell.alignment = right_align
                cell.number_format = "#,##0"
            else:
                cell.alignment = left_align
        current_row += 1

    # Total Row
    total_row = current_row
    sheet.cell(row=total_row, column=1, value="TOTAL KESELURUHAN")
    sheet.merge_cells(start_row=total_row, start_column=1, end_row=total_row, end_column=5)
    sheet.cell(row=total_row, column=1).font = bold_font
    sheet.cell(row=total_row, column=1).alignment = right_align

    cell_tot_omset = sheet.cell(row=total_row, column=6, value=total_omset_semua)
    cell_tot_omset.font = bold_font
    cell_tot_omset.alignment = right_align
    cell_tot_omset.number_format = "#,##0"

    cell_tot_laba = sheet.cell(row=total_row, column=7, value=total_laba_semua)
    cell_tot_laba.font = bold_font
    cell_tot_laba.alignment = right_align
    cell_tot_laba.number_format = "#,##0"

    for c in range(1, 8):
        sheet.cell(row=total_row, column=c).border = thin_border

    # Auto-adjust column widths
    for col in sheet.columns:
        max_len = max(len(str(cell.value or '')) for cell in col)
        col_letter = col[0].column_letter
        sheet.column_dimensions[col_letter].width = max(max_len + 4, 12)

    wb.save(filepath)
    return True, filepath
