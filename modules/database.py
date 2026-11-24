import csv
import os
import sys
import shutil

# Dapatkan direktori dasar
if getattr(sys, 'frozen', False):
    # Jika berjalan sebagai file .exe (PyInstaller)
    BASE_DIR = os.path.dirname(sys.executable)
    # Jika folder data tidak ada di folder .exe tapi ada di parent folder (misal di folder dist/ tapi data ada di ../data)
    parent_dir = os.path.dirname(BASE_DIR)
    if not os.path.exists(os.path.join(BASE_DIR, "data", "user.csv")) and os.path.exists(os.path.join(parent_dir, "data", "user.csv")):
        BASE_DIR = parent_dir
else:
    # Jika berjalan sebagai script Python biasa
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "data")

def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    # Auto-seed user default jika user.csv belum ada agar tidak gagal login
    user_file = os.path.join(DATA_DIR, "user.csv")
    if not os.path.exists(user_file) or os.path.getsize(user_file) == 0:
        with open(user_file, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["username", "password", "role"])
            writer.writerow(["faris", "123456", "admin"])

    # Auto-seed header barang.csv jika belum ada
    barang_file = os.path.join(DATA_DIR, "barang.csv")
    if not os.path.exists(barang_file) or os.path.getsize(barang_file) == 0:
        with open(barang_file, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["kode", "nama", "kategori", "stok", "harga_beli", "harga_jual"])

    # Auto-seed header transaksi.csv jika belum ada
    trans_file = os.path.join(DATA_DIR, "transaksi.csv")
    if not os.path.exists(trans_file) or os.path.getsize(trans_file) == 0:
        with open(trans_file, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["kode_transaksi", "tanggal", "kode_barang", "nama_barang", "jumlah", "total", "laba"])

def read_csv(filename):
    ensure_data_dir()
    path = os.path.join(DATA_DIR, filename)
    data = []
    if not os.path.exists(path):
        return data
    with open(path, mode="r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            data.append(row)
    return data

def write_csv(filename, data, fields):
    ensure_data_dir()
    path = os.path.join(DATA_DIR, filename)
    with open(path, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(data)
