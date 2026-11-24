import os
import tkinter as tk
from tkinter import ttk, messagebox

from modules import barang, transaksi, laporan, login
from modules.database import read_csv, write_csv
from modules.login import halaman_login

class AplikasiToko:
    def __init__(self, root, current_user):
        self.root = root
        self.current_user = current_user if isinstance(current_user, dict) else {"username": "User", "role": str(current_user)}
        self.user_role = self.current_user.get("role", "karyawan").lower()
        self.username = self.current_user.get("username", "Admin").title()

        self.root.deiconify()
        self.root.title("Sistem Pembukuan & POS - Toko Sparepart Laptop")
        self.root.geometry("1100x650")
        self.root.minsize(1000, 600)
        self.root.configure(bg="#F1F5F9")

        # Posisikan window di tengah layar
        self.center_window(1100, 650)

        # Inisialisasi Style TTK
        self.setup_styles()

        # Inisialisasi UI
        self.setup_layout()

        # Tampilkan default frame (Dashboard untuk admin, Transaksi untuk karyawan)
        if self.user_role == "admin":
            self.show_page("dashboard")
        else:
            self.show_page("transaksi")

    def center_window(self, width, height):
        self.root.update_idletasks()
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        x = (sw // 2) - (width // 2)
        y = (sh // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use("clam")

        # Konfigurasi Treeview
        style.configure(
            "Custom.Treeview",
            background="#FFFFFF",
            foreground="#1E293B",
            rowheight=28,
            fieldbackground="#FFFFFF",
            font=("Segoe UI", 9)
        )
        style.configure(
            "Custom.Treeview.Heading",
            background="#F8FAFC",
            foreground="#334155",
            font=("Segoe UI", 9, "bold"),
            relief="flat"
        )
        style.map("Custom.Treeview", background=[("selected", "#DBEAFE")], foreground=[("selected", "#1E40AF")])

    def setup_layout(self):
        # 1. Header Bar Atas
        self.top_bar = tk.Frame(self.root, bg="#0F172A", height=50)
        self.top_bar.pack(side="top", fill="x")

        lbl_logo = tk.Label(
            self.top_bar, 
            text="⚡ TOKO SPAREPART LAPTOP - POS & PEMBUKUAN", 
            font=("Segoe UI", 11, "bold"), 
            fg="#38BDF8", 
            bg="#0F172A"
        )
        lbl_logo.pack(side="left", padx=15, pady=10)

        # User Badge
        role_tag = f"👑 {self.username} (Admin)" if self.user_role == "admin" else f"👤 {self.username} (Kasir)"
        lbl_user = tk.Label(
            self.top_bar, 
            text=role_tag, 
            font=("Segoe UI", 9, "bold"), 
            fg="#F8FAFC", 
            bg="#1E293B", 
            padx=10, 
            pady=4
        )
        lbl_user.pack(side="right", padx=15, pady=8)

        # 2. Main Content Split (Sidebar + Container)
        main_body = tk.Frame(self.root, bg="#F1F5F9")
        main_body.pack(side="top", fill="both", expand=True)

        self.sidebar = tk.Frame(main_body, bg="#1E293B", width=220)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        self.container = tk.Frame(main_body, bg="#F1F5F9")
        self.container.pack(side="right", fill="both", expand=True)

        # 3. Buat Frame untuk tiap Menu
        self.frames = {}
        self.sidebar_buttons = {}

        self.build_sidebar()
        self.init_all_frames()

    def build_sidebar(self):
        # Menu Definition
        if self.user_role == "admin":
            nav_items = [
                ("dashboard", "📊  Dashboard", lambda: self.show_page("dashboard")),
                ("barang", "📦  Data Barang", lambda: self.show_page("barang")),
                ("transaksi", "🛒  Kasir / Transaksi", lambda: self.show_page("transaksi")),
                ("laporan", "📑  Laporan & Laba", lambda: self.show_page("laporan")),
                ("user", "👥  Kelola User", lambda: self.show_page("user")),
            ]
        else:
            nav_items = [
                ("transaksi", "🛒  Kasir / Transaksi", lambda: self.show_page("transaksi")),
                ("laporan", "📑  Laporan Penjualan", lambda: self.show_page("laporan")),
            ]

        lbl_nav = tk.Label(self.sidebar, text="NAVIGASI UTAMA", font=("Segoe UI", 8, "bold"), fg="#64748B", bg="#1E293B")
        lbl_nav.pack(anchor="w", padx=15, pady=(15, 8))

        for key, text, cmd in nav_items:
            btn = tk.Button(
                self.sidebar,
                text=text,
                font=("Segoe UI", 9, "bold"),
                anchor="w",
                padx=15,
                pady=10,
                bg="#1E293B",
                fg="#CBD5E1",
                activebackground="#2563EB",
                activeforeground="#FFFFFF",
                relief="flat",
                cursor="hand2",
                command=cmd
            )
            btn.pack(fill="x", pady=1)
            self.sidebar_buttons[key] = btn

        # Spacer
        tk.Frame(self.sidebar, bg="#1E293B").pack(fill="both", expand=True)

        # Bottom Utilities (Export & Logout)
        btn_excel = tk.Button(
            self.sidebar,
            text="📥  Export Excel",
            font=("Segoe UI", 9),
            anchor="w",
            padx=15,
            pady=8,
            bg="#0F766E",
            fg="white",
            activebackground="#0D9488",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            command=self.handle_export_excel
        )
        btn_excel.pack(fill="x", padx=10, pady=(0, 6))

        btn_logout = tk.Button(
            self.sidebar,
            text="🚪  Keluar",
            font=("Segoe UI", 9),
            anchor="w",
            padx=15,
            pady=8,
            bg="#DC2626",
            fg="white",
            activebackground="#B91C1C",
            activeforeground="white",
            relief="flat",
            cursor="hand2",
            command=self.root.destroy
        )
        btn_logout.pack(fill="x", padx=10, pady=(0, 15))

    def show_page(self, page_name):
        # Update highlight tombol sidebar
        for key, btn in self.sidebar_buttons.items():
            if key == page_name:
                btn.configure(bg="#2563EB", fg="#FFFFFF")
            else:
                btn.configure(bg="#1E293B", fg="#CBD5E1")

        # Raise frame terpilih
        if page_name in self.frames:
            # Panggil fungsi refresh data spesifik frame jika ada
            if page_name == "dashboard" and hasattr(self, "refresh_dashboard"):
                self.refresh_dashboard()
            elif page_name == "barang" and hasattr(self, "refresh_barang"):
                self.refresh_barang()
            elif page_name == "transaksi" and hasattr(self, "refresh_transaksi_page"):
                self.refresh_transaksi_page()
            elif page_name == "laporan" and hasattr(self, "refresh_laporan"):
                self.refresh_laporan()
            elif page_name == "user" and hasattr(self, "refresh_user"):
                self.refresh_user()

            self.frames[page_name].tkraise()

    def handle_export_excel(self):
        sukses, pesan_atau_path = laporan.export_laporan_excel()
        if sukses:
            ans = messagebox.askyesno(
                "Export Berhasil", 
                f"Laporan berhasil diexport ke:\n{pesan_atau_path}\n\nApakah ingin membuka foldernya sekarang?"
            )
            if ans:
                try:
                    os.startfile(os.path.dirname(os.path.abspath(pesan_atau_path)))
                except Exception:
                    pass
        else:
            messagebox.showerror("Gagal Export", pesan_atau_path)

    def init_all_frames(self):
        # Register semua frame di container
        for name in ("dashboard", "barang", "transaksi", "laporan", "user"):
            f = tk.Frame(self.container, bg="#F1F5F9", padx=20, pady=15)
            f.place(relx=0, rely=0, relwidth=1, relheight=1)
            self.frames[name] = f

        if self.user_role == "admin":
            self.init_dashboard_frame(self.frames["dashboard"])
            self.init_barang_frame(self.frames["barang"])
            self.init_user_frame(self.frames["user"])

        self.init_transaksi_frame(self.frames["transaksi"])
        self.init_laporan_frame(self.frames["laporan"])

    # =========================================================================
    # 1. FRAME DASHBOARD (Overview & Statistik)
    # =========================================================================
    def init_dashboard_frame(self, frame):
        # Title
        tk.Label(frame, text="📊 Dashboard Ringkasan Toko", font=("Segoe UI", 16, "bold"), fg="#0F172A", bg="#F1F5F9").pack(anchor="w", pady=(0, 15))

        # 4 Metric Cards Container
        cards_frame = tk.Frame(frame, bg="#F1F5F9")
        cards_frame.pack(fill="x", pady=(0, 20))

        self.metric_labels = {}

        def create_card(parent, title, default_val, icon, bg_color):
            card = tk.Frame(parent, bg="white", relief="solid", bd=1)
            card.pack(side="left", fill="both", expand=True, padx=5, ipady=8)

            tk.Label(card, text=f"{icon} {title}", font=("Segoe UI", 9, "bold"), fg="#64748B", bg="white").pack(anchor="w", padx=12, pady=(6, 2))
            lbl_val = tk.Label(card, text=default_val, font=("Segoe UI", 14, "bold"), fg=bg_color, bg="white")
            lbl_val.pack(anchor="w", padx=12, pady=(0, 6))
            return lbl_val

        self.metric_labels["total_barang"] = create_card(cards_frame, "Total Sparepart", "0 Jenis", "📦", "#2563EB")
        self.metric_labels["stok_kritis"] = create_card(cards_frame, "Stok Menipis (≤3)", "0 Item", "⚠️", "#DC2626")
        self.metric_labels["total_omset"] = create_card(cards_frame, "Total Omset", "Rp 0", "💰", "#059669")
        self.metric_labels["total_laba"] = create_card(cards_frame, "Keuntungan Bersih", "Rp 0", "📈", "#7C3AED")

        # Bottom Split (Peringatan Stok & Transaksi Terbaru)
        bottom_split = tk.Frame(frame, bg="#F1F5F9")
        bottom_split.pack(fill="both", expand=True)

        # Kiri: Stok Menipis
        left_box = tk.Frame(bottom_split, bg="white", relief="solid", bd=1, padx=12, pady=10)
        left_box.pack(side="left", fill="both", expand=True, padx=(0, 8))

        tk.Label(left_box, text="⚠️ Peringatan Stok Menipis / Habis", font=("Segoe UI", 11, "bold"), fg="#DC2626", bg="white").pack(anchor="w", pady=(0, 8))
        self.tree_kritis = ttk.Treeview(left_box, columns=("kode", "nama", "stok"), show="headings", style="Custom.Treeview")
        self.tree_kritis.heading("kode", text="Kode")
        self.tree_kritis.heading("nama", text="Nama Sparepart")
        self.tree_kritis.heading("stok", text="Sisa Stok")
        self.tree_kritis.column("kode", width=80, anchor="center")
        self.tree_kritis.column("nama", width=180)
        self.tree_kritis.column("stok", width=80, anchor="center")
        self.tree_kritis.pack(fill="both", expand=True)

        # Kanan: Transaksi Terbaru
        right_box = tk.Frame(bottom_split, bg="white", relief="solid", bd=1, padx=12, pady=10)
        right_box.pack(side="right", fill="both", expand=True, padx=(8, 0))

        tk.Label(right_box, text="🕒 Aktivitas Transaksi Terbaru", font=("Segoe UI", 11, "bold"), fg="#0F172A", bg="white").pack(anchor="w", pady=(0, 8))
        self.tree_recent = ttk.Treeview(right_box, columns=("kode", "nama", "total"), show="headings", style="Custom.Treeview")
        self.tree_recent.heading("kode", text="No. Nota")
        self.tree_recent.heading("nama", text="Sparepart")
        self.tree_recent.heading("total", text="Total")
        self.tree_recent.column("kode", width=90, anchor="center")
        self.tree_recent.column("nama", width=170)
        self.tree_recent.column("total", width=100, anchor="e")
        self.tree_recent.pack(fill="both", expand=True)

    def refresh_dashboard(self):
        daftar_b = barang.ambil_semua_barang()
        kritis = barang.ambil_stok_kritis(threshold=3)
        keuangan = laporan.ringkasan_keuangan()

        self.metric_labels["total_barang"].config(text=f"{len(daftar_b)} Jenis")
        self.metric_labels["stok_kritis"].config(text=f"{len(kritis)} Item")
        self.metric_labels["total_omset"].config(text=f"Rp {keuangan['total_omset']:,}")
        self.metric_labels["total_laba"].config(text=f"Rp {keuangan['total_laba']:,}")

        # Update Tabel Kritis
        self.tree_kritis.delete(*self.tree_kritis.get_children())
        for b in kritis:
            self.tree_kritis.insert("", tk.END, values=(b["kode"], b["nama"], f"{b['stok_val']} unit"))

        # Update Tabel Transaksi Terbaru (5 teratas)
        all_tr = laporan.ambil_semua_transaksi()
        self.tree_recent.delete(*self.tree_recent.get_children())
        for tr in reversed(all_tr[-5:]):
            self.tree_recent.insert("", tk.END, values=(tr.get("kode_transaksi"), tr.get("nama_barang"), f"Rp {tr.get('total_val', 0):,}"))

    # =========================================================================
    # 2. FRAME DATA BARANG (Inventory & Stok)
    # =========================================================================
    def init_barang_frame(self, frame):
        # Header + Tombol Tambah
        top_bar = tk.Frame(frame, bg="#F1F5F9")
        top_bar.pack(fill="x", pady=(0, 10))

        tk.Label(top_bar, text="📦 Manajemen Data Sparepart (Inventory)", font=("Segoe UI", 16, "bold"), fg="#0F172A", bg="#F1F5F9").pack(side="left")

        # Action Buttons
        btn_tambah = tk.Button(top_bar, text="➕ Tambah Barang", font=("Segoe UI", 9, "bold"), bg="#2563EB", fg="white", relief="flat", cursor="hand2", padx=10, pady=5, command=self.popup_tambah_barang)
        btn_tambah.pack(side="right", padx=4)

        btn_ubah = tk.Button(top_bar, text="✏️ Ubah", font=("Segoe UI", 9), bg="#F59E0B", fg="white", relief="flat", cursor="hand2", padx=10, pady=5, command=self.popup_ubah_barang)
        btn_ubah.pack(side="right", padx=4)

        btn_hapus = tk.Button(top_bar, text="🗑️ Hapus", font=("Segoe UI", 9), bg="#DC2626", fg="white", relief="flat", cursor="hand2", padx=10, pady=5, command=self.action_hapus_barang)
        btn_hapus.pack(side="right", padx=4)

        # Search Bar
        search_frame = tk.Frame(frame, bg="white", relief="solid", bd=1, padx=10, pady=6)
        search_frame.pack(fill="x", pady=(0, 10))

        tk.Label(search_frame, text="🔍 Cari Barang:", font=("Segoe UI", 9, "bold"), fg="#475569", bg="white").pack(side="left", padx=(0, 8))
        self.ent_search_barang = tk.Entry(search_frame, font=("Segoe UI", 10), relief="solid", bd=1)
        self.ent_search_barang.pack(side="left", fill="x", expand=True, padx=(0, 10), ipady=3)
        self.ent_search_barang.bind("<KeyRelease>", lambda e: self.refresh_barang())

        btn_reset = tk.Button(search_frame, text="Reset", font=("Segoe UI", 9), relief="flat", bg="#E2E8F0", cursor="hand2", command=self.reset_search_barang)
        btn_reset.pack(side="left")

        # Table Container
        tabel_card = tk.Frame(frame, bg="white", relief="solid", bd=1)
        tabel_card.pack(fill="both", expand=True)

        cols = ("kode", "nama", "kategori", "stok", "harga_beli", "harga_jual", "status")
        self.tree_barang = ttk.Treeview(tabel_card, columns=cols, show="headings", style="Custom.Treeview")
        self.tree_barang.pack(fill="both", expand=True, side="left")

        scroll = ttk.Scrollbar(tabel_card, orient="vertical", command=self.tree_barang.yview)
        scroll.pack(side="right", fill="y")
        self.tree_barang.configure(yscrollcommand=scroll.set)

        headings = {
            "kode": ("Kode", 90, "center"),
            "nama": ("Nama Sparepart", 250, "w"),
            "kategori": ("Kategori", 130, "center"),
            "stok": ("Stok", 90, "center"),
            "harga_beli": ("Harga Beli / Modal", 140, "e"),
            "harga_jual": ("Harga Jual", 140, "e"),
            "status": ("Status Stok", 110, "center")
        }

        for col, (text, w, a) in headings.items():
            self.tree_barang.heading(col, text=text)
            self.tree_barang.column(col, width=w, anchor=a)

    def reset_search_barang(self):
        self.ent_search_barang.delete(0, tk.END)
        self.refresh_barang()

    def refresh_barang(self):
        if not hasattr(self, "tree_barang"):
            return
        self.tree_barang.delete(*self.tree_barang.get_children())
        kw = self.ent_search_barang.get().strip() if hasattr(self, "ent_search_barang") else ""
        data = barang.cari_barang(kw)

        for b in data:
            stok = b["stok_val"]
            if stok <= 0:
                status = "🔴 HABIS"
            elif stok <= 3:
                status = "🟠 MENIPIS"
            else:
                status = "🟢 AMAN"

            self.tree_barang.insert(
                "", tk.END,
                values=(
                    b["kode"],
                    b["nama"],
                    b["kategori"],
                    f"{stok} unit",
                    f"Rp {b['harga_beli_val']:,}",
                    f"Rp {b['harga_jual_val']:,}",
                    status
                )
            )

    def popup_tambah_barang(self):
        win = tk.Toplevel(self.root)
        win.title("Tambah Sparepart Baru")
        win.geometry("400x420")
        win.configure(bg="#F8FAFC")
        win.transient(self.root)
        win.grab_set()

        tk.Label(win, text="Tambah Data Sparepart", font=("Segoe UI", 12, "bold"), bg="#F8FAFC", fg="#0F172A").pack(pady=12)

        form = tk.Frame(win, bg="#F8FAFC", padx=25)
        form.pack(fill="both", expand=True)

        fields = [
            ("Kode Barang (misal: BRG006)", "kode"),
            ("Nama Sparepart", "nama"),
            ("Kategori (LCD / RAM / SSD / dll)", "kategori"),
            ("Stok Awal", "stok"),
            ("Harga Beli / Modal (Rp)", "harga_beli"),
            ("Harga Jual (Rp)", "harga_jual")
        ]
        entries = {}

        for lbl_text, key in fields:
            tk.Label(form, text=lbl_text, font=("Segoe UI", 8, "bold"), fg="#475569", bg="#F8FAFC").pack(anchor="w")
            e = tk.Entry(form, font=("Segoe UI", 9), relief="solid", bd=1)
            e.pack(fill="x", pady=(2, 6), ipady=3)
            entries[key] = e

        def simpan():
            try:
                kode = entries["kode"].get().strip()
                nama = entries["nama"].get().strip()
                kat = entries["kategori"].get().strip()
                stok = int(entries["stok"].get().strip())
                hb = int(entries["harga_beli"].get().strip())
                hj = int(entries["harga_jual"].get().strip())

                if not kode or not nama:
                    return messagebox.showwarning("Peringatan", "Kode dan Nama Barang wajib diisi!", parent=win)

                sukses, pesan = barang.simpan_barang_baru(kode, nama, kat, stok, hb, hj)
                if sukses:
                    messagebox.showinfo("Sukses", pesan, parent=win)
                    win.destroy()
                    self.refresh_barang()
                else:
                    messagebox.showerror("Gagal", pesan, parent=win)
            except ValueError:
                messagebox.showerror("Input Salah", "Stok, Harga Beli, dan Harga Jual harus berupa angka bulat!", parent=win)

        tk.Button(win, text="Simpan Barang", font=("Segoe UI", 10, "bold"), bg="#2563EB", fg="white", relief="flat", cursor="hand2", command=simpan).pack(fill="x", padx=25, pady=15, ipady=5)

    def popup_ubah_barang(self):
        sel = self.tree_barang.focus()
        if not sel:
            return messagebox.showwarning("Peringatan", "Pilih data barang yang ingin diubah terlebih dahulu!")

        vals = self.tree_barang.item(sel, "values")
        kode = vals[0]

        # Ambil detail asli
        semua = barang.ambil_semua_barang()
        target = next((b for b in semua if b["kode"] == kode), None)
        if not target:
            return messagebox.showerror("Error", "Data barang tidak ditemukan!")

        win = tk.Toplevel(self.root)
        win.title(f"Ubah Sparepart - {kode}")
        win.geometry("400x420")
        win.configure(bg="#F8FAFC")
        win.transient(self.root)
        win.grab_set()

        tk.Label(win, text=f"Ubah Data: {kode}", font=("Segoe UI", 12, "bold"), bg="#F8FAFC", fg="#0F172A").pack(pady=12)

        form = tk.Frame(win, bg="#F8FAFC", padx=25)
        form.pack(fill="both", expand=True)

        fields = [
            ("Nama Sparepart", "nama", target.get("nama", "")),
            ("Kategori", "kategori", target.get("kategori", "")),
            ("Stok", "stok", str(target.get("stok", 0))),
            ("Harga Beli / Modal (Rp)", "harga_beli", str(target.get("harga_beli", 0))),
            ("Harga Jual (Rp)", "harga_jual", str(target.get("harga_jual", 0)))
        ]
        entries = {}

        for lbl_text, key, def_val in fields:
            tk.Label(form, text=lbl_text, font=("Segoe UI", 8, "bold"), fg="#475569", bg="#F8FAFC").pack(anchor="w")
            e = tk.Entry(form, font=("Segoe UI", 9), relief="solid", bd=1)
            e.pack(fill="x", pady=(2, 6), ipady=3)
            e.insert(0, def_val)
            entries[key] = e

        def simpan():
            try:
                nama = entries["nama"].get().strip()
                kat = entries["kategori"].get().strip()
                stok = int(entries["stok"].get().strip())
                hb = int(entries["harga_beli"].get().strip())
                hj = int(entries["harga_jual"].get().strip())

                sukses, pesan = barang.ubah_barang_data(kode, nama, kat, stok, hb, hj)
                if sukses:
                    messagebox.showinfo("Sukses", pesan, parent=win)
                    win.destroy()
                    self.refresh_barang()
                else:
                    messagebox.showerror("Gagal", pesan, parent=win)
            except ValueError:
                messagebox.showerror("Input Salah", "Stok, Harga Beli, dan Harga Jual harus angka bulat!", parent=win)

        tk.Button(win, text="Simpan Perubahan", font=("Segoe UI", 10, "bold"), bg="#F59E0B", fg="white", relief="flat", cursor="hand2", command=simpan).pack(fill="x", padx=25, pady=15, ipady=5)

    def action_hapus_barang(self):
        sel = self.tree_barang.focus()
        if not sel:
            return messagebox.showwarning("Peringatan", "Pilih barang yang ingin dihapus terlebih dahulu!")

        vals = self.tree_barang.item(sel, "values")
        kode = vals[0]
        nama = vals[1]

        if messagebox.askyesno("Konfirmasi Hapus", f"Apakah Anda yakin ingin menghapus barang '{nama}' ({kode})?"):
            sukses, pesan = barang.hapus_barang_data(kode)
            if sukses:
                messagebox.showinfo("Sukses", pesan)
                self.refresh_barang()
            else:
                messagebox.showerror("Gagal", pesan)

    # =========================================================================
    # 3. FRAME TRANSAKSI / KASIR (Point of Sale Multi-Item)
    # =========================================================================
    def init_transaksi_frame(self, frame):
        tk.Label(frame, text="🛒 Kasir Penjualan & Keranjang Belanja", font=("Segoe UI", 16, "bold"), fg="#0F172A", bg="#F1F5F9").pack(anchor="w", pady=(0, 10))

        # Top Control: Form Tambah ke Keranjang
        form_card = tk.Frame(frame, bg="white", relief="solid", bd=1, padx=15, pady=12)
        form_card.pack(fill="x", pady=(0, 10))

        # Grid form
        tk.Label(form_card, text="Pilih Sparepart", font=("Segoe UI", 9, "bold"), fg="#475569", bg="white").grid(row=0, column=0, sticky="w", padx=5)
        self.cb_barang = ttk.Combobox(form_card, width=40, font=("Segoe UI", 9), state="readonly")
        self.cb_barang.grid(row=1, column=0, padx=5, pady=3, sticky="w")
        self.cb_barang.bind("<<ComboboxSelected>>", self.on_transaksi_barang_selected)

        tk.Label(form_card, text="Jumlah Beli", font=("Segoe UI", 9, "bold"), fg="#475569", bg="white").grid(row=0, column=1, sticky="w", padx=10)
        self.ent_qty = tk.Entry(form_card, width=10, font=("Segoe UI", 10), relief="solid", bd=1)
        self.ent_qty.grid(row=1, column=1, padx=10, pady=3, sticky="w", ipady=2)
        self.ent_qty.insert(0, "1")

        # Tombol Tambah ke Keranjang
        btn_tambah_keranjang = tk.Button(
            form_card, 
            text="➕ Tambah ke Keranjang", 
            font=("Segoe UI", 9, "bold"), 
            bg="#2563EB", 
            fg="white", 
            relief="flat", 
            cursor="hand2", 
            padx=12, 
            pady=4,
            command=self.action_tambah_ke_keranjang
        )
        btn_tambah_keranjang.grid(row=1, column=2, padx=10, pady=3)

        # Info harga & stok aktif
        self.lbl_info_barang = tk.Label(form_card, text="Pilih barang untuk melihat harga & ketersediaan stok.", font=("Segoe UI", 9, "italic"), fg="#64748B", bg="white")
        self.lbl_info_barang.grid(row=2, column=0, columnspan=3, sticky="w", padx=5, pady=(5, 0))

        # Tabel Keranjang Belanja
        tabel_card = tk.Frame(frame, bg="white", relief="solid", bd=1)
        tabel_card.pack(fill="both", expand=True, pady=(0, 10))

        cols = ("no", "kode", "nama", "qty", "harga", "subtotal")
        self.tree_keranjang = ttk.Treeview(tabel_card, columns=cols, show="headings", style="Custom.Treeview")
        self.tree_keranjang.pack(fill="both", expand=True, side="left")

        scroll = ttk.Scrollbar(tabel_card, orient="vertical", command=self.tree_keranjang.yview)
        scroll.pack(side="right", fill="y")
        self.tree_keranjang.configure(yscrollcommand=scroll.set)

        self.tree_keranjang.heading("no", text="No")
        self.tree_keranjang.heading("kode", text="Kode")
        self.tree_keranjang.heading("nama", text="Nama Sparepart")
        self.tree_keranjang.heading("qty", text="Qty")
        self.tree_keranjang.heading("harga", text="Harga Satuan")
        self.tree_keranjang.heading("subtotal", text="Subtotal")

        self.tree_keranjang.column("no", width=40, anchor="center")
        self.tree_keranjang.column("kode", width=90, anchor="center")
        self.tree_keranjang.column("nama", width=280)
        self.tree_keranjang.column("qty", width=80, anchor="center")
        self.tree_keranjang.column("harga", width=120, anchor="e")
        self.tree_keranjang.column("subtotal", width=140, anchor="e")

        # Keranjang state
        self.keranjang_items = []

        # Bottom Bar: Total Belanja & Tombol Checkout
        bottom_bar = tk.Frame(frame, bg="#1E293B", padx=15, pady=10)
        bottom_bar.pack(fill="x")

        # Tombol aksi keranjang (hapus item)
        btn_hapus_item = tk.Button(bottom_bar, text="❌ Hapus Item", font=("Segoe UI", 9), bg="#475569", fg="white", relief="flat", cursor="hand2", command=self.action_hapus_item_keranjang)
        btn_hapus_item.pack(side="left", padx=(0, 5))

        btn_clear = tk.Button(bottom_bar, text="🗑️ Kosongkan Keranjang", font=("Segoe UI", 9), bg="#475569", fg="white", relief="flat", cursor="hand2", command=self.action_clear_keranjang)
        btn_clear.pack(side="left")

        # Tombol Bayar
        btn_bayar = tk.Button(
            bottom_bar, 
            text="💳 PROSES PEMBAYARAN & NOTA", 
            font=("Segoe UI", 10, "bold"), 
            bg="#059669", 
            fg="white", 
            activebackground="#047857",
            activeforeground="white",
            relief="flat", 
            cursor="hand2", 
            padx=15, 
            pady=6,
            command=self.popup_pembayaran
        )
        btn_bayar.pack(side="right")

        # Label Total
        self.lbl_total_keranjang = tk.Label(bottom_bar, text="TOTAL : Rp 0", font=("Segoe UI", 13, "bold"), fg="#38BDF8", bg="#1E293B")
        self.lbl_total_keranjang.pack(side="right", padx=20)

    def refresh_transaksi_page(self):
        """Memperbarui combobox barang dengan data inventaris paling mutakhir"""
        daftar_b = barang.ambil_semua_barang()
        self.map_barang_transaksi = {b["kode"]: b for b in daftar_b}

        pilihan = [f"{b['kode']} - {b['nama']} (Stok: {b['stok_val']})" for b in daftar_b]
        self.cb_barang["values"] = pilihan
        if pilihan and not self.cb_barang.get():
            self.cb_barang.current(0)
            self.on_transaksi_barang_selected(None)

    def on_transaksi_barang_selected(self, event):
        val = self.cb_barang.get()
        if not val:
            return
        kode = val.split(" - ")[0].strip()
        b = self.map_barang_transaksi.get(kode)
        if b:
            self.lbl_info_barang.config(
                text=f"Harga: Rp {b['harga_jual_val']:,} | Kategori: {b.get('kategori', '-')} | Sisa Stok Tersedia: {b['stok_val']} unit",
                fg="#059669" if b['stok_val'] > 0 else "#DC2626"
            )

    def action_tambah_ke_keranjang(self):
        val = self.cb_barang.get()
        if not val:
            return messagebox.showwarning("Peringatan", "Pilih barang terlebih dahulu!")

        kode = val.split(" - ")[0].strip()
        b = self.map_barang_transaksi.get(kode)
        if not b:
            return messagebox.showerror("Error", "Data barang tidak ditemukan!")

        try:
            qty = int(self.ent_qty.get().strip())
            if qty <= 0:
                return messagebox.showwarning("Input Salah", "Jumlah beli minimal 1!")
        except ValueError:
            return messagebox.showwarning("Input Salah", "Jumlah beli harus berupa angka bulat!")

        stok_tersedia = b["stok_val"]

        # Cek apakah item sudah ada di keranjang
        existing = next((item for item in self.keranjang_items if item["kode"] == kode), None)
        qty_total = qty + (existing["qty"] if existing else 0)

        if qty_total > stok_tersedia:
            return messagebox.showerror(
                "Stok Tidak Cukup", 
                f"Stok '{b['nama']}' tidak mencukupi!\nSisa stok: {stok_tersedia} unit.\nPermintaan (termasuk di keranjang): {qty_total} unit."
            )

        if existing:
            existing["qty"] = qty_total
            existing["subtotal"] = existing["qty"] * existing["harga_jual"]
            existing["laba"] = (existing["harga_jual"] - existing["harga_beli"]) * existing["qty"]
        else:
            subtotal = qty * b["harga_jual_val"]
            laba = (b["harga_jual_val"] - b["harga_beli_val"]) * qty
            self.keranjang_items.append({
                "kode": b["kode"],
                "nama": b["nama"],
                "qty": qty,
                "harga_beli": b["harga_beli_val"],
                "harga_jual": b["harga_jual_val"],
                "subtotal": subtotal,
                "laba": laba
            })

        self.refresh_tabel_keranjang()
        self.ent_qty.delete(0, tk.END)
        self.ent_qty.insert(0, "1")

    def refresh_tabel_keranjang(self):
        self.tree_keranjang.delete(*self.tree_keranjang.get_children())
        total = 0
        for idx, itm in enumerate(self.keranjang_items, 1):
            self.tree_keranjang.insert(
                "", tk.END,
                values=(
                    idx,
                    itm["kode"],
                    itm["nama"],
                    f"{itm['qty']} unit",
                    f"Rp {itm['harga_jual']:,}",
                    f"Rp {itm['subtotal']:,}"
                )
            )
            total += itm["subtotal"]

        self.lbl_total_keranjang.config(text=f"TOTAL : Rp {total:,}")

    def action_hapus_item_keranjang(self):
        sel = self.tree_keranjang.focus()
        if not sel:
            return messagebox.showwarning("Pilih", "Pilih item di keranjang yang ingin dihapus.")
        idx = int(self.tree_keranjang.item(sel, "values")[0]) - 1
        if 0 <= idx < len(self.keranjang_items):
            self.keranjang_items.pop(idx)
            self.refresh_tabel_keranjang()

    def action_clear_keranjang(self):
        if not self.keranjang_items:
            return
        if messagebox.askyesno("Kosongkan Keranjang", "Apakah Anda yakin ingin menghapus semua item di keranjang?"):
            self.keranjang_items.clear()
            self.refresh_tabel_keranjang()

    def popup_pembayaran(self):
        if not self.keranjang_items:
            return messagebox.showwarning("Keranjang Kosong", "Tambahkan barang ke keranjang terlebih dahulu sebelum melakukan pembayaran!")

        total_belanja = sum(itm["subtotal"] for itm in self.keranjang_items)

        win = tk.Toplevel(self.root)
        win.title("Pembayaran Kasir")
        win.geometry("420x400")
        win.configure(bg="#F8FAFC")
        win.transient(self.root)
        win.grab_set()

        # Header Total
        header = tk.Frame(win, bg="#1E293B", pady=15)
        header.pack(fill="x")
        tk.Label(header, text="TOTAL TAGIHAN", font=("Segoe UI", 9, "bold"), fg="#94A3B8", bg="#1E293B").pack()
        tk.Label(header, text=f"Rp {total_belanja:,}", font=("Segoe UI", 18, "bold"), fg="#38BDF8", bg="#1E293B").pack()

        body = tk.Frame(win, bg="#F8FAFC", padx=30, pady=15)
        body.pack(fill="both", expand=True)

        tk.Label(body, text="Nominal Uang Pembeli (Rp):", font=("Segoe UI", 9, "bold"), fg="#334155", bg="#F8FAFC").pack(anchor="w")
        ent_tunai = tk.Entry(body, font=("Segoe UI", 12, "bold"), relief="solid", bd=1, justify="right")
        ent_tunai.pack(fill="x", pady=(3, 8), ipady=4)
        ent_tunai.insert(0, str(total_belanja))
        ent_tunai.focus_set()

        # Shortcut Tombol Uang Cepat
        fast_buttons = tk.Frame(body, bg="#F8FAFC")
        fast_buttons.pack(fill="x", pady=(0, 10))

        def set_uang(nominal):
            ent_tunai.delete(0, tk.END)
            ent_tunai.insert(0, str(nominal))
            update_kembalian()

        tk.Button(fast_buttons, text="Uang Pas", font=("Segoe UI", 8), bg="#E2E8F0", relief="flat", cursor="hand2", command=lambda: set_uang(total_belanja)).pack(side="left", padx=2)
        for nominal in (50000, 100000, 200000, 500000):
            if nominal >= total_belanja:
                tk.Button(fast_buttons, text=f"{nominal//1000}k", font=("Segoe UI", 8), bg="#E2E8F0", relief="flat", cursor="hand2", command=lambda n=nominal: set_uang(n)).pack(side="left", padx=2)

        # Label Kembalian
        card_kembali = tk.Frame(body, bg="white", relief="solid", bd=1, padx=10, pady=8)
        card_kembali.pack(fill="x", pady=(5, 15))

        tk.Label(card_kembali, text="UANG KEMBALIAN:", font=("Segoe UI", 8, "bold"), fg="#64748B", bg="white").pack(anchor="w")
        lbl_kembalian = tk.Label(card_kembali, text="Rp 0", font=("Segoe UI", 13, "bold"), fg="#059669", bg="white")
        lbl_kembalian.pack(anchor="w")

        def update_kembalian(event=None):
            try:
                tunai = int(ent_tunai.get().replace(".", "").replace(",", "").strip() or 0)
                kembali = tunai - total_belanja
                if kembali >= 0:
                    lbl_kembalian.config(text=f"Rp {kembali:,}", fg="#059669")
                else:
                    lbl_kembalian.config(text=f"Kurang Rp {abs(kembali):,}", fg="#DC2626")
            except ValueError:
                lbl_kembalian.config(text="Nominal salah!", fg="#DC2626")

        ent_tunai.bind("<KeyRelease>", update_kembalian)

        def konfirmasi_bayar():
            try:
                tunai = int(ent_tunai.get().replace(".", "").replace(",", "").strip())
            except ValueError:
                return messagebox.showerror("Input Salah", "Nominal uang pembeli tidak valid!", parent=win)

            if tunai < total_belanja:
                return messagebox.showerror("Uang Kurang", f"Uang pembeli masih kurang Rp {total_belanja - tunai:,}!", parent=win)

            # Eksekusi proses transaksi multi-item terpadu
            sukses, pesan, path_nota, kembali = transaksi.proses_checkout(
                items=self.keranjang_items,
                bayar_tunai=tunai,
                nama_kasir=self.username
            )

            if sukses:
                win.destroy()
                self.keranjang_items.clear()
                self.refresh_tabel_keranjang()
                self.refresh_transaksi_page()

                msg = f"{pesan}\n\nKembalian: Rp {kembali:,}\nNota PDF tersimpan: {path_nota or 'Tidak ada'}"
                if path_nota and os.path.exists(path_nota):
                    tanya_buka = messagebox.askyesno(
                        "Transaksi Selesai", 
                        f"{msg}\n\nApakah ingin langsung membuka Nota PDF sekarang?"
                    )
                    if tanya_buka:
                        try:
                            os.startfile(os.path.abspath(path_nota))
                        except Exception:
                            pass
                else:
                    messagebox.showinfo("Transaksi Selesai", msg)
            else:
                messagebox.showerror("Gagal Transaksi", pesan, parent=win)

        btn_confirm = tk.Button(
            win, 
            text="✅ KONFIRMASI BAYAR & CETAK NOTA", 
            font=("Segoe UI", 10, "bold"), 
            bg="#059669", 
            fg="white", 
            relief="flat", 
            cursor="hand2", 
            command=konfirmasi_bayar
        )
        btn_confirm.pack(fill="x", padx=30, pady=(0, 20), ipady=8)

    # =========================================================================
    # 4. FRAME LAPORAN PENJUALAN & PEMBUKUAN LABA
    # =========================================================================
    def init_laporan_frame(self, frame):
        top_bar = tk.Frame(frame, bg="#F1F5F9")
        top_bar.pack(fill="x", pady=(0, 10))

        tk.Label(top_bar, text="📑 Laporan Penjualan & Pembukuan Laba", font=("Segoe UI", 16, "bold"), fg="#0F172A", bg="#F1F5F9").pack(side="left")

        # Tombol Export Excel
        btn_exp = tk.Button(top_bar, text="📥 Export ke Excel", font=("Segoe UI", 9, "bold"), bg="#0F766E", fg="white", relief="flat", cursor="hand2", padx=10, pady=5, command=self.handle_export_excel)
        btn_exp.pack(side="right")

        # Filter Strip (Periode & Pencarian)
        filter_bar = tk.Frame(frame, bg="white", relief="solid", bd=1, padx=10, pady=8)
        filter_bar.pack(fill="x", pady=(0, 10))

        tk.Label(filter_bar, text="Filter Periode:", font=("Segoe UI", 9, "bold"), fg="#475569", bg="white").pack(side="left", padx=(0, 5))
        self.cb_periode = ttk.Combobox(filter_bar, values=["Semua", "Hari Ini", "Bulan Ini"], state="readonly", width=12, font=("Segoe UI", 9))
        self.cb_periode.current(0)
        self.cb_periode.pack(side="left", padx=(0, 15))
        self.cb_periode.bind("<<ComboboxSelected>>", lambda e: self.refresh_laporan())

        tk.Label(filter_bar, text="🔍 Cari Transaksi:", font=("Segoe UI", 9, "bold"), fg="#475569", bg="white").pack(side="left", padx=(0, 5))
        self.ent_search_laporan = tk.Entry(filter_bar, font=("Segoe UI", 9), relief="solid", bd=1)
        self.ent_search_laporan.pack(side="left", fill="x", expand=True, padx=(0, 10), ipady=2)
        self.ent_search_laporan.bind("<KeyRelease>", lambda e: self.refresh_laporan())

        # Metric Banner di Laporan
        summary_card = tk.Frame(frame, bg="#1E293B", padx=15, pady=8)
        summary_card.pack(fill="x", pady=(0, 10))

        self.lbl_lap_trx = tk.Label(summary_card, text="Transaksi: 0", font=("Segoe UI", 9, "bold"), fg="#F8FAFC", bg="#1E293B")
        self.lbl_lap_trx.pack(side="left", padx=(0, 20))

        self.lbl_lap_omset = tk.Label(summary_card, text="Total Omset: Rp 0", font=("Segoe UI", 10, "bold"), fg="#38BDF8", bg="#1E293B")
        self.lbl_lap_omset.pack(side="left", padx=(0, 20))

        self.lbl_lap_laba = tk.Label(summary_card, text="Keuntungan Bersih: Rp 0", font=("Segoe UI", 10, "bold"), fg="#4ADE80", bg="#1E293B")
        self.lbl_lap_laba.pack(side="left")

        # Tabel Laporan
        tabel_card = tk.Frame(frame, bg="white", relief="solid", bd=1)
        tabel_card.pack(fill="both", expand=True)

        cols = ("kode", "tanggal", "kode_brg", "nama_brg", "qty", "omset", "laba")
        self.tree_laporan = ttk.Treeview(tabel_card, columns=cols, show="headings", style="Custom.Treeview")
        self.tree_laporan.pack(fill="both", expand=True, side="left")

        scroll = ttk.Scrollbar(tabel_card, orient="vertical", command=self.tree_laporan.yview)
        scroll.pack(side="right", fill="y")
        self.tree_laporan.configure(yscrollcommand=scroll.set)

        self.tree_laporan.heading("kode", text="No. Nota")
        self.tree_laporan.heading("tanggal", text="Tanggal & Waktu")
        self.tree_laporan.heading("kode_brg", text="Kode")
        self.tree_laporan.heading("nama_brg", text="Nama Sparepart")
        self.tree_laporan.heading("qty", text="Qty")
        self.tree_laporan.heading("omset", text="Omset (Rp)")
        self.tree_laporan.heading("laba", text="Laba Bersih (Rp)")

        self.tree_laporan.column("kode", width=90, anchor="center")
        self.tree_laporan.column("tanggal", width=140, anchor="center")
        self.tree_laporan.column("kode_brg", width=80, anchor="center")
        self.tree_laporan.column("nama_brg", width=220)
        self.tree_laporan.column("qty", width=60, anchor="center")
        self.tree_laporan.column("omset", width=120, anchor="e")
        self.tree_laporan.column("laba", width=120, anchor="e")

    def refresh_laporan(self):
        if not hasattr(self, "tree_laporan"):
            return

        periode = self.cb_periode.get() if hasattr(self, "cb_periode") else "Semua"
        data = laporan.filter_transaksi_berdasarkan_periode(periode)

        # Filter keyword
        kw = self.ent_search_laporan.get().strip().lower() if hasattr(self, "ent_search_laporan") else ""
        if kw:
            data = [
                t for t in data
                if kw in t.get("kode_transaksi", "").lower()
                or kw in t.get("nama_barang", "").lower()
                or kw in t.get("kode_barang", "").lower()
            ]

        self.tree_laporan.delete(*self.tree_laporan.get_children())
        total_omset = 0
        total_laba = 0
        trx_set = set()

        for tr in data:
            omset = tr.get("total_val", 0)
            laba = tr.get("laba_val", 0)
            total_omset += omset
            total_laba += laba
            if tr.get("kode_transaksi"):
                trx_set.add(tr["kode_transaksi"])

            self.tree_laporan.insert(
                "", tk.END,
                values=(
                    tr.get("kode_transaksi"),
                    tr.get("tanggal"),
                    tr.get("kode_barang"),
                    tr.get("nama_barang"),
                    f"{tr.get('jumlah', 1)} unit",
                    f"Rp {omset:,}",
                    f"Rp {laba:,}"
                )
            )

        self.lbl_lap_trx.config(text=f"Total Transaksi: {len(trx_set)}")
        self.lbl_lap_omset.config(text=f"Total Omset: Rp {total_omset:,}")
        self.lbl_lap_laba.config(text=f"Keuntungan Bersih: Rp {total_laba:,}")

    # =========================================================================
    # 5. FRAME KELOLA USER (Admin Only)
    # =========================================================================
    def init_user_frame(self, frame):
        tk.Label(frame, text="👥 Manajemen Pengguna & Hak Akses", font=("Segoe UI", 16, "bold"), fg="#0F172A", bg="#F1F5F9").pack(anchor="w", pady=(0, 10))

        container = tk.Frame(frame, bg="#F1F5F9")
        container.pack(fill="both", expand=True)

        # Form Kiri
        left_card = tk.Frame(container, bg="white", relief="solid", bd=1, padx=20, pady=15, width=320)
        left_card.pack(side="left", fill="y", padx=(0, 10))
        left_card.pack_propagate(False)

        tk.Label(left_card, text="Tambah Pengguna Baru", font=("Segoe UI", 11, "bold"), fg="#0F172A", bg="white").pack(anchor="w", pady=(0, 12))

        tk.Label(left_card, text="Username", font=("Segoe UI", 8, "bold"), fg="#475569", bg="white").pack(anchor="w")
        ent_uname = tk.Entry(left_card, font=("Segoe UI", 9), relief="solid", bd=1)
        ent_uname.pack(fill="x", pady=(2, 8), ipady=3)

        tk.Label(left_card, text="Password", font=("Segoe UI", 8, "bold"), fg="#475569", bg="white").pack(anchor="w")
        ent_pass = tk.Entry(left_card, font=("Segoe UI", 9), show="•", relief="solid", bd=1)
        ent_pass.pack(fill="x", pady=(2, 8), ipady=3)

        tk.Label(left_card, text="Hak Akses (Role)", font=("Segoe UI", 8, "bold"), fg="#475569", bg="white").pack(anchor="w")
        cb_role = ttk.Combobox(left_card, values=["karyawan", "admin"], state="readonly", font=("Segoe UI", 9))
        cb_role.current(0)
        cb_role.pack(fill="x", pady=(2, 15))

        def simpan_user():
            u = ent_uname.get().strip()
            p = ent_pass.get().strip()
            r = cb_role.get().strip().lower()

            if not u or not p:
                return messagebox.showwarning("Peringatan", "Username dan Password tidak boleh kosong!", parent=self.root)

            users = read_csv("user.csv")
            if any(x.get("username") == u for x in users):
                return messagebox.showerror("Duplikat", f"Username '{u}' sudah terdaftar!", parent=self.root)

            users.append({"username": u, "password": p, "role": r})
            write_csv("user.csv", users, ["username", "password", "role"])

            ent_uname.delete(0, tk.END)
            ent_pass.delete(0, tk.END)
            self.refresh_user()
            messagebox.showinfo("Sukses", f"Pengguna '{u}' berhasil ditambahkan!")

        tk.Button(left_card, text="Tambah Pengguna", font=("Segoe UI", 9, "bold"), bg="#2563EB", fg="white", relief="flat", cursor="hand2", command=simpan_user).pack(fill="x", ipady=6)

        # Tabel Kanan
        right_card = tk.Frame(container, bg="white", relief="solid", bd=1, padx=15, pady=12)
        right_card.pack(side="right", fill="both", expand=True)

        tk.Label(right_card, text="Daftar Akun Pengguna Terdaftar", font=("Segoe UI", 11, "bold"), fg="#0F172A", bg="white").pack(anchor="w", pady=(0, 8))

        self.tree_user = ttk.Treeview(right_card, columns=("username", "role"), show="headings", style="Custom.Treeview")
        self.tree_user.heading("username", text="Username")
        self.tree_user.heading("role", text="Hak Akses / Role")
        self.tree_user.column("username", width=180)
        self.tree_user.column("role", width=120, anchor="center")
        self.tree_user.pack(fill="both", expand=True, pady=(0, 10))

        def hapus_user():
            sel = self.tree_user.focus()
            if not sel:
                return messagebox.showwarning("Pilih", "Pilih user yang ingin dihapus.")
            uname = self.tree_user.item(sel, "values")[0]

            if uname.lower() == self.username.lower():
                return messagebox.showerror("Dilarang", "Anda tidak dapat menghapus akun yang sedang aktif digunakan saat ini!")

            if messagebox.askyesno("Konfirmasi", f"Apakah Anda yakin ingin menghapus user '{uname}'?"):
                users = read_csv("user.csv")
                users = [x for x in users if x.get("username") != uname]
                write_csv("user.csv", users, ["username", "password", "role"])
                self.refresh_user()
                messagebox.showinfo("Sukses", f"Pengguna '{uname}' berhasil dihapus.")

        btn_box = tk.Frame(right_card, bg="white")
        btn_box.pack(anchor="e")

        def ubah_user():
            sel = self.tree_user.focus()
            if not sel:
                return messagebox.showwarning("Pilih", "Pilih user yang ingin diubah terlebih dahulu.")
            uname = self.tree_user.item(sel, "values")[0]
            users = read_csv("user.csv")
            target = next((x for x in users if x.get("username") == uname), None)
            if not target:
                return messagebox.showerror("Error", "Data user tidak ditemukan!")

            win_edit = tk.Toplevel(self.root)
            win_edit.title(f"Ubah Password - {uname}")
            win_edit.geometry("340x280")
            win_edit.configure(bg="#F8FAFC")
            win_edit.transient(self.root)
            win_edit.grab_set()

            tk.Label(win_edit, text=f"Ubah Akun: {uname}", font=("Segoe UI", 11, "bold"), bg="#F8FAFC", fg="#0F172A").pack(pady=12)

            f_body = tk.Frame(win_edit, bg="#F8FAFC", padx=25)
            f_body.pack(fill="both", expand=True)

            tk.Label(f_body, text="Password Baru", font=("Segoe UI", 8, "bold"), fg="#475569", bg="#F8FAFC").pack(anchor="w")
            e_new_pass = tk.Entry(f_body, font=("Segoe UI", 9), relief="solid", bd=1)
            e_new_pass.pack(fill="x", pady=(2, 8), ipady=3)
            e_new_pass.insert(0, target.get("password", ""))

            tk.Label(f_body, text="Hak Akses (Role)", font=("Segoe UI", 8, "bold"), fg="#475569", bg="#F8FAFC").pack(anchor="w")
            cb_new_role = ttk.Combobox(f_body, values=["karyawan", "admin"], state="readonly", font=("Segoe UI", 9))
            cb_new_role.set(target.get("role", "karyawan"))
            cb_new_role.pack(fill="x", pady=(2, 15))

            def simpan_perubahan():
                p = e_new_pass.get().strip()
                r = cb_new_role.get().strip().lower()
                if not p:
                    return messagebox.showwarning("Peringatan", "Password tidak boleh kosong!", parent=win_edit)

                for x in users:
                    if x.get("username") == uname:
                        x["password"] = p
                        x["role"] = r
                        break

                write_csv("user.csv", users, ["username", "password", "role"])
                self.refresh_user()
                win_edit.destroy()
                messagebox.showinfo("Sukses", f"Akun '{uname}' berhasil diperbarui!")

            tk.Button(win_edit, text="Simpan Perubahan", font=("Segoe UI", 9, "bold"), bg="#F59E0B", fg="white", relief="flat", cursor="hand2", command=simpan_perubahan).pack(fill="x", padx=25, pady=15, ipady=5)

        tk.Button(btn_box, text="✏️ Ubah Password", font=("Segoe UI", 9), bg="#F59E0B", fg="white", relief="flat", cursor="hand2", padx=10, pady=5, command=ubah_user).pack(side="left", padx=4)
        tk.Button(btn_box, text="🗑️ Hapus User", font=("Segoe UI", 9), bg="#DC2626", fg="white", relief="flat", cursor="hand2", padx=10, pady=5, command=hapus_user).pack(side="left")

    def refresh_user(self):
        if not hasattr(self, "tree_user"):
            return
        self.tree_user.delete(*self.tree_user.get_children())
        users = read_csv("user.csv")
        for u in users:
            self.tree_user.insert("", tk.END, values=(u.get("username"), u.get("role", "karyawan").upper()))


# =========================================================================
# ENTRY POINT
# =========================================================================
if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Sembunyikan window utama selama proses login

    user_info = halaman_login(root)

    if user_info:
        app = AplikasiToko(root, user_info)
        root.mainloop()
    else:
        root.destroy()
