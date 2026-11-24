from modules.database import read_csv, write_csv

FILENAME = "barang.csv"
FIELDS = ["kode", "nama", "kategori", "stok", "harga_beli", "harga_jual"]

def ambil_semua_barang():
    data = read_csv(FILENAME)
    for b in data:
        # Normalisasi integer untuk stok dan harga
        try:
            b["stok_val"] = int(b.get("stok", 0))
        except ValueError:
            b["stok_val"] = 0
        try:
            b["harga_beli_val"] = int(b.get("harga_beli", 0))
        except ValueError:
            b["harga_beli_val"] = 0
        try:
            b["harga_jual_val"] = int(b.get("harga_jual", 0))
        except ValueError:
            b["harga_jual_val"] = 0
    return data

def cari_barang(keyword=""):
    data = ambil_semua_barang()
    if not keyword:
        return data
    k = keyword.lower()
    return [
        b for b in data
        if k in b.get("kode", "").lower() 
        or k in b.get("nama", "").lower() 
        or k in b.get("kategori", "").lower()
    ]

def ambil_stok_kritis(threshold=3):
    """Mengembalikan barang yang stoknya kurang dari atau sama dengan threshold"""
    data = ambil_semua_barang()
    return [b for b in data if b["stok_val"] <= threshold]

def simpan_barang_baru(kode, nama, kategori, stok, harga_beli, harga_jual):
    kode = kode.strip().upper()
    data = read_csv(FILENAME)
    
    # Validasi kode unik
    if any(b.get("kode", "").strip().upper() == kode for b in data):
        return False, f"Kode barang '{kode}' sudah terdaftar!"

    data.append({
        "kode": kode,
        "nama": nama.strip(),
        "kategori": kategori.strip(),
        "stok": str(stok),
        "harga_beli": str(harga_beli),
        "harga_jual": str(harga_jual)
    })
    write_csv(FILENAME, data, FIELDS)
    return True, "Barang baru berhasil ditambahkan!"

def ubah_barang_data(kode, nama, kategori, stok, harga_beli, harga_jual):
    kode = kode.strip().upper()
    data = read_csv(FILENAME)
    found = False

    for b in data:
        if b.get("kode", "").strip().upper() == kode:
            b["nama"] = nama.strip()
            b["kategori"] = kategori.strip()
            b["stok"] = str(stok)
            b["harga_beli"] = str(harga_beli)
            b["harga_jual"] = str(harga_jual)
            found = True
            break

    if not found:
        return False, "Data barang tidak ditemukan!"

    write_csv(FILENAME, data, FIELDS)
    return True, "Data barang berhasil diperbarui!"

def hapus_barang_data(kode):
    kode = kode.strip().upper()
    data = read_csv(FILENAME)
    data_baru = [b for b in data if b.get("kode", "").strip().upper() != kode]

    if len(data_baru) == len(data):
        return False, "Barang tidak ditemukan!"

    write_csv(FILENAME, data_baru, FIELDS)
    return True, "Barang berhasil dihapus!"
