import os
import streamlit as st
import pandas as pd
from modules import barang, transaksi, laporan
from modules.database import read_csv, write_csv

# =============================================================================
# KONFIGURASI HALAMAN
# =============================================================================
st.set_page_config(
    page_title="Toko Sparepart Laptop - POS & Pembukuan",
    page_icon="💻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk tampilan modern mirip desktop app
st.markdown("""
<style>
    .metric-card {
        background-color: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 10px;
        padding: 16px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .stButton>button {
        border-radius: 6px;
        font-weight: 600;
    }
    .status-aman { color: #16A34A; font-weight: bold; }
    .status-menipis { color: #EA580C; font-weight: bold; }
    .status-habis { color: #DC2626; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Inisialisasi Session State
if "auth_user" not in st.session_state:
    st.session_state.auth_user = None

if "keranjang" not in st.session_state:
    st.session_state.keranjang = []

# =============================================================================
# HALAMAN LOGIN
# =============================================================================
def render_login():
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("<h2 style='text-align: center; color: #1E293B;'>💻 TOKO SPAREPART LAPTOP</h2>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #64748B;'>Sistem Kasir & Pembukuan Penjualan</p>", unsafe_allow_html=True)
            st.divider()

            with st.form("form_login"):
                uname = st.text_input("Username", placeholder="Masukkan username (contoh: faris)")
                pwd = st.text_input("Password", type="password", placeholder="Masukkan password (contoh: 123456)")
                submit = st.form_submit_button("MASUK KE SISTEM", use_container_width=True, type="primary")

                if submit:
                    users = read_csv("user.csv")
                    matched = next((u for u in users if u.get("username") == uname.strip() and u.get("password") == pwd.strip()), None)
                    if matched:
                        st.session_state.auth_user = {
                            "username": matched["username"],
                            "role": matched.get("role", "karyawan")
                        }
                        st.success(f"Login Berhasil! Selamat datang, {matched['username'].title()}.")
                        st.rerun()
                    else:
                        st.error("Username atau password salah! (Default: faris / 123456)")

            st.caption("ℹ️ Akun Demo Default: **faris** | Password: **123456** (Admin)")

# =============================================================================
# 1. HALAMAN DASHBOARD
# =============================================================================
def render_dashboard():
    st.title("📊 Dashboard Ringkasan Toko")
    st.markdown("Statistik inventaris, performa transaksi kasir, dan pembukuan laba secara real-time.")

    daftar_b = barang.ambil_semua_barang()
    kritis = barang.ambil_stok_kritis(threshold=3)
    keuangan = laporan.ringkasan_keuangan()

    # 4 Metric Cards
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📦 Total Sparepart", f"{len(daftar_b)} Jenis")
    c2.metric("⚠️ Stok Kritis (≤ 3)", f"{len(kritis)} Item", delta=f"{len(kritis)} perlu restock", delta_color="inverse")
    c3.metric("💰 Total Omset", f"Rp {keuangan['total_omset']:,}")
    c4.metric("📈 Keuntungan Bersih", f"Rp {keuangan['total_laba']:,}")

    st.markdown("<br>", unsafe_allow_html=True)
    col_left, col_right = st.columns(2)

    with col_left:
        with st.container(border=True):
            st.subheader("⚠️ Peringatan Stok Menipis / Habis")
            if kritis:
                df_kritis = pd.DataFrame([{
                    "Kode": b["kode"],
                    "Nama Sparepart": b["nama"],
                    "Kategori": b.get("kategori", "-"),
                    "Sisa Stok": f"{b['stok_val']} unit"
                } for b in kritis])
                st.dataframe(df_kritis, use_container_width=True, hide_index=True)
            else:
                st.success("Semua stok sparepart berada dalam batas aman!")

    with col_right:
        with st.container(border=True):
            st.subheader("🕒 Aktivitas Transaksi Terbaru")
            all_tr = laporan.ambil_semua_transaksi()
            if all_tr:
                df_recent = pd.DataFrame([{
                    "Nota": t.get("kode_transaksi"),
                    "Waktu": t.get("tanggal"),
                    "Barang": t.get("nama_barang"),
                    "Total": f"Rp {t.get('total_val', 0):,}"
                } for t in reversed(all_tr[-5:])])
                st.dataframe(df_recent, use_container_width=True, hide_index=True)
            else:
                st.info("Belum ada riwayat transaksi penjualan.")

# =============================================================================
# 2. HALAMAN DATA BARANG (INVENTORY)
# =============================================================================
def render_barang():
    st.title("📦 Manajemen Data Sparepart (Inventory)")

    tab_lihat, tab_tambah, tab_ubah = st.tabs(["📋 Katalog Barang", "➕ Tambah Barang Baru", "✏️ Ubah / Hapus Barang"])

    with tab_lihat:
        col_search, col_filter = st.columns([2, 1])
        with col_search:
            kw = st.text_input("🔍 Cari Barang (Kode / Nama / Kategori)", placeholder="Ketik kata kunci pencarian...")
        
        data_b = barang.cari_barang(kw)
        if data_b:
            table_rows = []
            for b in data_b:
                stk = b["stok_val"]
                status = "🔴 HABIS" if stk <= 0 else ("🟠 MENIPIS" if stk <= 3 else "🟢 AMAN")
                table_rows.append({
                    "Kode": b["kode"],
                    "Nama Sparepart": b["nama"],
                    "Kategori": b["kategori"],
                    "Stok": f"{stk} unit",
                    "Harga Modal (Rp)": f"Rp {b['harga_beli_val']:,}",
                    "Harga Jual (Rp)": f"Rp {b['harga_jual_val']:,}",
                    "Status": status
                })
            st.dataframe(pd.DataFrame(table_rows), use_container_width=True, hide_index=True)
        else:
            st.warning("Tidak ditemukan data barang yang sesuai.")

    with tab_tambah:
        st.subheader("Tambah Data Sparepart Baru")
        with st.form("form_tambah_barang"):
            c1, c2 = st.columns(2)
            k_kode = c1.text_input("Kode Barang", placeholder="Misal: BRG007")
            k_nama = c2.text_input("Nama Sparepart", placeholder="Misal: Baterai Asus Vivobook")
            k_kat = c1.text_input("Kategori", placeholder="Misal: Baterai / RAM / LCD")
            k_stok = c2.number_input("Stok Awal", min_value=0, value=5, step=1)
            k_hb = c1.number_input("Harga Beli / Modal (Rp)", min_value=0, value=250000, step=5000)
            k_hj = c2.number_input("Harga Jual (Rp)", min_value=0, value=350000, step=5000)
            
            btn_save = st.form_submit_button("Simpan Barang", type="primary")
            if btn_save:
                if not k_kode or not k_nama:
                    st.error("Kode dan Nama Barang wajib diisi!")
                else:
                    sukses, pesan = barang.simpan_barang_baru(k_kode, k_nama, k_kat, k_stok, k_hb, k_hj)
                    if sukses:
                        st.success(pesan)
                        st.rerun()
                    else:
                        st.error(pesan)

    with tab_ubah:
        st.subheader("Ubah atau Hapus Data Sparepart")
        semua_b = barang.ambil_semua_barang()
        pilihan = [f"{b['kode']} - {b['nama']}" for b in semua_b]
        if pilihan:
            selected = st.selectbox("Pilih Barang yang Ingin Diedit", pilihan)
            kode_target = selected.split(" - ")[0]
            target_data = next((b for b in semua_b if b["kode"] == kode_target), None)

            if target_data:
                with st.form("form_edit_barang"):
                    c1, c2 = st.columns(2)
                    e_nama = c1.text_input("Nama Sparepart", value=target_data["nama"])
                    e_kat = c2.text_input("Kategori", value=target_data["kategori"])
                    e_stok = c1.number_input("Stok", min_value=0, value=int(target_data["stok"]), step=1)
                    e_hb = c2.number_input("Harga Modal (Rp)", min_value=0, value=int(target_data["harga_beli"]), step=5000)
                    e_hj = c1.number_input("Harga Jual (Rp)", min_value=0, value=int(target_data["harga_jual"]), step=5000)

                    col_b1, col_b2 = st.columns([1, 1])
                    with col_b1:
                        btn_update = st.form_submit_button("💾 Simpan Perubahan", type="primary")
                    with col_b2:
                        btn_delete = st.form_submit_button("🗑️ Hapus Barang Ini", type="secondary")

                    if btn_update:
                        sukses, pesan = barang.ubah_barang_data(kode_target, e_nama, e_kat, e_stok, e_hb, e_hj)
                        if sukses:
                            st.success(pesan)
                            st.rerun()
                        else:
                            st.error(pesan)
                    elif btn_delete:
                        sukses, pesan = barang.hapus_barang_data(kode_target)
                        if sukses:
                            st.warning(pesan)
                            st.rerun()
                        else:
                            st.error(pesan)

# =============================================================================
# 3. HALAMAN KASIR / TRANSAKSI
# =============================================================================
def render_transaksi():
    st.title("🛒 Kasir Penjualan & Keranjang Belanja")

    semua_b = barang.ambil_semua_barang()
    map_b = {b["kode"]: b for b in semua_b}

    with st.container(border=True):
        st.subheader("➕ Tambah Item ke Keranjang")
        c1, c2, c3 = st.columns([3, 1, 1.5])
        
        opsi_barang = [f"{b['kode']} - {b['nama']} (Stok: {b['stok_val']} | Rp {b['harga_jual_val']:,})" for b in semua_b]
        if not opsi_barang:
            st.warning("Belum ada data barang di inventaris!")
            return

        pilih_item = c1.selectbox("Pilih Sparepart", opsi_barang)
        qty_beli = c2.number_input("Jumlah", min_value=1, value=1, step=1)

        kode_pilih = pilih_item.split(" - ")[0]
        barang_obj = map_b[kode_pilih]

        with c3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("➕ Tambahkan ke Keranjang", use_container_width=True, type="primary"):
                stok_tersedia = barang_obj["stok_val"]
                existing = next((item for item in st.session_state.keranjang if item["kode"] == kode_pilih), None)
                qty_total = qty_beli + (existing["qty"] if existing else 0)

                if qty_total > stok_tersedia:
                    st.error(f"Stok tidak cukup! Sisa stok hanya {stok_tersedia} unit.")
                else:
                    if existing:
                        existing["qty"] = qty_total
                        existing["subtotal"] = existing["qty"] * existing["harga_jual"]
                        existing["laba"] = (existing["harga_jual"] - existing["harga_beli"]) * existing["qty"]
                    else:
                        subtotal = qty_beli * barang_obj["harga_jual_val"]
                        laba = (barang_obj["harga_jual_val"] - barang_obj["harga_beli_val"]) * qty_beli
                        st.session_state.keranjang.append({
                            "kode": barang_obj["kode"],
                            "nama": barang_obj["nama"],
                            "qty": qty_beli,
                            "harga_beli": barang_obj["harga_beli_val"],
                            "harga_jual": barang_obj["harga_jual_val"],
                            "subtotal": subtotal,
                            "laba": laba
                        })
                    st.success(f"{barang_obj['nama']} berhasil dimasukkan ke keranjang!")
                    st.rerun()

    # Tabel Keranjang
    st.subheader("🛍️ Daftar Belanjaan Saat Ini")
    if st.session_state.keranjang:
        rows = []
        total_belanja = 0
        for idx, itm in enumerate(st.session_state.keranjang, 1):
            rows.append({
                "No": idx,
                "Kode": itm["kode"],
                "Nama Sparepart": itm["nama"],
                "Qty": f"{itm['qty']} unit",
                "Harga Satuan": f"Rp {itm['harga_jual']:,}",
                "Subtotal": f"Rp {itm['subtotal']:,}"
            })
            total_belanja += itm["subtotal"]

        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

        col_left_act, col_right_checkout = st.columns([1, 1.5])
        with col_left_act:
            if st.button("🗑️ Kosongkan Keranjang"):
                st.session_state.keranjang.clear()
                st.rerun()

        with col_right_checkout:
            with st.container(border=True):
                st.markdown(f"<h3 style='color: #059669;'>TOTAL TAGIHAN: Rp {total_belanja:,}</h3>", unsafe_allow_html=True)
                
                uang_bayar = st.number_input("Nominal Uang Pembeli (Rp)", min_value=0, value=total_belanja, step=10000)
                kembalian = uang_bayar - total_belanja

                if kembalian >= 0:
                    st.info(f"💵 Uang Kembalian: **Rp {kembalian:,}**")
                else:
                    st.error(f"⚠️ Uang Kurang: **Rp {abs(kembalian):,}**")

                if st.button("💳 KONFIRMASI BAYAR & CETAK STRUK NOTA", type="primary", use_container_width=True):
                    if uang_bayar < total_belanja:
                        st.error("Uang pembayaran tidak mencukupi!")
                    else:
                        sukses, pesan, path_nota, kembali = transaksi.proses_checkout(
                            items=st.session_state.keranjang,
                            bayar_tunai=uang_bayar,
                            nama_kasir=st.session_state.auth_user["username"].title()
                        )
                        if sukses:
                            st.success(f"{pesan} (Kembalian: Rp {kembali:,})")
                            st.session_state.keranjang.clear()

                            # Berikan tombol download nota PDF
                            if path_nota and os.path.exists(path_nota):
                                with open(path_nota, "rb") as f:
                                    pdf_data = f.read()
                                st.download_button(
                                    label="📄 Download / Cetak Nota Struk (PDF)",
                                    data=pdf_data,
                                    file_name=os.path.basename(path_nota),
                                    mime="application/pdf"
                                )
                        else:
                            st.error(pesan)
    else:
        st.info("Keranjang belanja masih kosong. Silakan pilih sparepart di atas.")

# =============================================================================
# 4. HALAMAN LAPORAN & LABA
# =============================================================================
def render_laporan():
    st.title("📑 Laporan Penjualan & Pembukuan Laba")

    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        periode = st.selectbox("Filter Periode", ["Semua", "Hari Ini", "Bulan Ini"])
    with c2:
        kw = st.text_input("🔍 Cari Transaksi (No. Nota / Nama Barang)", placeholder="Ketik kata kunci...")

    data_tr = laporan.filter_transaksi_berdasarkan_periode(periode)
    if kw:
        k = kw.lower()
        data_tr = [t for t in data_tr if k in t.get("kode_transaksi", "").lower() or k in t.get("nama_barang", "").lower()]

    # Summary
    omset = sum(t.get("total_val", 0) for t in data_tr)
    laba = sum(t.get("laba_val", 0) for t in data_tr)
    trx_count = len(set(t.get("kode_transaksi", "") for t in data_tr if t.get("kode_transaksi")))

    m1, m2, m3 = st.columns(3)
    m1.metric("Total Transaksi", f"{trx_count} Transaksi")
    m2.metric("Total Omset Penjualan", f"Rp {omset:,}")
    m3.metric("Keuntungan Bersih (Laba)", f"Rp {laba:,}")

    # Tabel Laporan
    st.markdown("<br>", unsafe_allow_html=True)
    if data_tr:
        df_laporan = pd.DataFrame([{
            "No. Nota": t.get("kode_transaksi"),
            "Tanggal & Waktu": t.get("tanggal"),
            "Kode": t.get("kode_barang"),
            "Nama Sparepart": t.get("nama_barang"),
            "Qty": f"{t.get('jumlah', 1)} unit",
            "Omset (Rp)": f"Rp {t.get('total_val', 0):,}",
            "Laba Bersih (Rp)": f"Rp {t.get('laba_val', 0):,}"
        } for t in data_tr])
        st.dataframe(df_laporan, use_container_width=True, hide_index=True)

        # Tombol Export Excel
        with c3:
            st.markdown("<br>", unsafe_allow_html=True)
            sukses, path_excel = laporan.export_laporan_excel(data_tr)
            if sukses and os.path.exists(path_excel):
                with open(path_excel, "rb") as f:
                    excel_data = f.read()
                st.download_button(
                    label="📥 Download Excel (.xlsx)",
                    data=excel_data,
                    file_name=os.path.basename(path_excel),
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
    else:
        st.info("Tidak ada data transaksi yang sesuai dengan filter.")

# =============================================================================
# 5. HALAMAN KELOLA USER (ADMIN)
# =============================================================================
def render_user():
    st.title("👥 Manajemen Pengguna & Hak Akses")

    users = read_csv("user.csv")
    col_tambah, col_list = st.columns([1, 1.5])

    with col_tambah:
        with st.container(border=True):
            st.subheader("➕ Tambah Pengguna Baru")
            with st.form("form_tambah_user"):
                u_name = st.text_input("Username")
                u_pass = st.text_input("Password", type="password")
                u_role = st.selectbox("Hak Akses (Role)", ["karyawan", "admin"])
                btn_add_user = st.form_submit_button("Tambah Pengguna", type="primary")

                if btn_add_user:
                    if not u_name or not u_pass:
                        st.error("Username dan password tidak boleh kosong!")
                    elif any(x.get("username") == u_name.strip() for x in users):
                        st.error(f"Username '{u_name}' sudah terdaftar!")
                    else:
                        users.append({"username": u_name.strip(), "password": u_pass.strip(), "role": u_role})
                        write_csv("user.csv", users, ["username", "password", "role"])
                        st.success(f"Pengguna '{u_name}' berhasil ditambahkan!")
                        st.rerun()

    with col_list:
        with st.container(border=True):
            st.subheader("📋 Daftar Pengguna Terdaftar")
            df_users = pd.DataFrame([{
                "Username": u.get("username"),
                "Role / Hak Akses": u.get("role", "karyawan").upper()
            } for u in users])
            st.dataframe(df_users, use_container_width=True, hide_index=True)

            st.markdown("---")
            st.subheader("✏️ Ubah Password / Hapus Pengguna")
            daftar_uname = [u["username"] for u in users]
            target_uname = st.selectbox("Pilih Akun", daftar_uname)
            curr_acc = next((u for u in users if u["username"] == target_uname), None)

            if curr_acc:
                new_pwd = st.text_input("Password Baru", value=curr_acc.get("password", ""), type="password")
                new_role = st.selectbox("Role", ["karyawan", "admin"], index=0 if curr_acc.get("role") == "karyawan" else 1)

                b1, b2 = st.columns(2)
                if b1.button("💾 Simpan Password Baru", type="primary"):
                    if not new_pwd:
                        st.error("Password tidak boleh kosong!")
                    else:
                        curr_acc["password"] = new_pwd
                        curr_acc["role"] = new_role
                        write_csv("user.csv", users, ["username", "password", "role"])
                        st.success("Akun berhasil diperbarui!")
                        st.rerun()

                if b2.button("🗑️ Hapus Akun Ini", type="secondary"):
                    if target_uname.lower() == st.session_state.auth_user["username"].lower():
                        st.error("Anda tidak bisa menghapus akun yang sedang aktif digunakan!")
                    else:
                        users = [x for x in users if x["username"] != target_uname]
                        write_csv("user.csv", users, ["username", "password", "role"])
                        st.warning(f"Akun '{target_uname}' telah dihapus!")
                        st.rerun()

# =============================================================================
# MAIN CONTROLLER & SIDEBAR
# =============================================================================
if st.session_state.auth_user is None:
    render_login()
else:
    user = st.session_state.auth_user
    role = user["role"]

    # Sidebar Header
    st.sidebar.markdown(f"### ⚡ Toko Sparepart")
    st.sidebar.markdown(f"👤 **{user['username'].title()}** ({role.upper()})")
    st.sidebar.divider()

    # Menu Navigasi
    if role == "admin":
        menu = st.sidebar.radio(
            "NAVIGASI UTAMA",
            ["📊 Dashboard", "📦 Data Barang", "🛒 Kasir / Transaksi", "📑 Laporan & Laba", "👥 Kelola User"]
        )
    else:
        menu = st.sidebar.radio(
            "NAVIGASI UTAMA",
            ["🛒 Kasir / Transaksi", "📑 Laporan & Laba"]
        )

    st.sidebar.divider()
    if st.sidebar.button("🚪 Keluar / Logout", use_container_width=True):
        st.session_state.auth_user = None
        st.session_state.keranjang.clear()
        st.rerun()

    # Routing
    if "Dashboard" in menu:
        render_dashboard()
    elif "Data Barang" in menu:
        render_barang()
    elif "Kasir" in menu:
        render_transaksi()
    elif "Laporan" in menu:
        render_laporan()
    elif "Kelola User" in menu:
        render_user()
