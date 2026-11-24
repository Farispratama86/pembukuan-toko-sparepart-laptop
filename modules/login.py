import tkinter as tk
from tkinter import messagebox
from modules.database import read_csv

def halaman_login(root):
    login_win = tk.Toplevel()
    login_win.transient()
    login_win.title("Login - Toko Sparepart Laptop")
    login_win.geometry("380x320")
    login_win.resizable(False, False)
    login_win.configure(bg="#F8FAFC")

    # Posisikan window di tengah layar
    login_win.update_idletasks()
    width = 380
    height = 320
    x = (login_win.winfo_screenwidth() // 2) - (width // 2)
    y = (login_win.winfo_screenheight() // 2) - (height // 2)
    login_win.geometry(f"{width}x{height}+{x}+{y}")

    # Header Card
    header_frame = tk.Frame(login_win, bg="#1E293B", height=80)
    header_frame.pack(fill="x")
    tk.Label(
        header_frame, 
        text="💻 TOKO SPAREPART", 
        font=("Segoe UI", 14, "bold"), 
        fg="#38BDF8", 
        bg="#1E293B"
    ).pack(pady=(15, 2))
    tk.Label(
        header_frame, 
        text="Silakan login untuk masuk ke sistem", 
        font=("Segoe UI", 9), 
        fg="#94A3B8", 
        bg="#1E293B"
    ).pack(pady=(0, 15))

    # Form Container
    body = tk.Frame(login_win, bg="#F8FAFC", padx=30, pady=20)
    body.pack(fill="both", expand=True)

    tk.Label(body, text="Username", font=("Segoe UI", 9, "bold"), fg="#334155", bg="#F8FAFC").pack(anchor="w")
    e_user = tk.Entry(body, font=("Segoe UI", 10), relief="solid", bd=1)
    e_user.pack(fill="x", pady=(3, 12), ipady=4)
    e_user.focus_set()

    tk.Label(body, text="Password", font=("Segoe UI", 9, "bold"), fg="#334155", bg="#F8FAFC").pack(anchor="w")
    e_pass = tk.Entry(body, show="•", font=("Segoe UI", 10), relief="solid", bd=1)
    e_pass.pack(fill="x", pady=(3, 16), ipady=4)

    # Variabel penampung hasil login
    login_result = {"user": None}

    def proses(event=None):
        username = e_user.get().strip()
        password = e_pass.get().strip()
        if not username or not password:
            messagebox.showwarning("Peringatan", "Username dan Password tidak boleh kosong!", parent=login_win)
            return

        data = read_csv("user.csv")
        for row in data:
            if row.get("username") == username and row.get("password") == password:
                login_result["user"] = {
                    "username": row.get("username"),
                    "role": row.get("role", "karyawan")
                }
                messagebox.showinfo("Sukses", f"Selamat datang, {username.title()}!", parent=login_win)
                login_win.destroy()
                return

        messagebox.showerror("Gagal Login", "Username atau password salah!", parent=login_win)
        e_pass.delete(0, tk.END)
        e_pass.focus_set()

    # Bind tombol Enter pada input password & username
    e_user.bind("<Return>", lambda e: e_pass.focus_set())
    e_pass.bind("<Return>", proses)

    btn_login = tk.Button(
        body, 
        text="MASUK", 
        font=("Segoe UI", 10, "bold"), 
        bg="#2563EB", 
        fg="white", 
        activebackground="#1D4ED8",
        activeforeground="white",
        cursor="hand2", 
        relief="flat",
        command=proses
    )
    btn_login.pack(fill="x", ipady=6)

    login_win.grab_set()
    root.wait_window(login_win)

    return login_result["user"]
