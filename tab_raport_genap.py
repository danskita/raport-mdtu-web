# File: tab_raport_genap.py
import tkinter as tk
from tkinter import ttk, messagebox
from tab_cetak import terbilang # Mengambil fungsi terbilang dari modul ganjil

class TabRaportGenap:
    def __init__(self, parent, db):
        self.parent = parent
        self.db = db
        self.lbl_dinamis = {}
        
        # Palet Warna Estetik (Sama dengan Semester 1)
        self.C_BORDER = "#D1D8E0"    # Abu-abu lembut
        self.C_HEAD = "#F4F6F9"      # Biru-abu pudar untuk header
        self.C_TEKS = "#2C3E50"      # Abu-abu gelap modern
        self.FONT_UTAMA = ("Segoe UI", 10)
        
        self.setup_ui()

    def setup_ui(self):
        # --- KONTROL ATAS ---
        frame_kontrol = ttk.Frame(self.parent)
        frame_kontrol.pack(fill=tk.X, padx=20, pady=10)
        
        ttk.Label(frame_kontrol, text="Pilih Santri (Genap):", font=("Segoe UI", 11, "bold")).pack(side=tk.LEFT)
        self.combo_cetak = ttk.Combobox(frame_kontrol, width=40, state="readonly")
        self.combo_cetak.pack(side=tk.LEFT, padx=10)
        ttk.Button(frame_kontrol, text="🔄 Refresh & Tampilkan", command=self.tampilkan_preview).pack(side=tk.LEFT)
        self.combo_cetak.bind("<<ComboboxSelected>>", lambda e: self.tampilkan_preview())

        # --- CANVAS A4 DENGAN BINDING MARGIN ---
        canvas = tk.Canvas(self.parent, bg="#525659", highlightthickness=0)
        scroll_y = ttk.Scrollbar(self.parent, orient="vertical", command=canvas.yview)
        
        # Frame "Kertas A4"
        # padx=80 memberikan margin kiri lebih lebar untuk JILID
        self.kertas = tk.Frame(canvas, bg="white", padx=80, pady=50)
        
        self.kertas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((50, 20), window=self.kertas, anchor="nw", width=800)
        canvas.configure(yscrollcommand=scroll_y.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scroll_y.pack(side="right", fill="y")

        self.bangun_format_raport()

    def buat_sel(self, parent, baris, kolom, teks, font=("Segoe UI", 10), span=1, anchor="w", bg="white", is_header=False):
        # Frame sebagai garis border lembut
        f = tk.Frame(parent, bg=self.C_BORDER)
        f.grid(row=baris, column=kolom, columnspan=span, sticky="nsew")
        
        warna_bg = self.C_HEAD if is_header else bg
        fnt = (font[0], font[1], "bold") if is_header else font
        
        lbl = tk.Label(f, text=teks, font=fnt, bg=warna_bg, fg=self.C_TEKS, anchor=anchor, justify=tk.LEFT, padx=10, pady=6)
        lbl.pack(fill="both", expand=True, padx=(0, 1), pady=(0, 1))
        return lbl

    def bangun_format_raport(self):
        # 1. JUDUL
        tk.Label(self.kertas, text="DAFTAR NILAI", font=("Segoe UI", 18, "bold"), bg="white", fg=self.C_TEKS).grid(row=0, column=0, columnspan=6, pady=(0, 25))

        # 2. KOP RAPORT
        kop_frame = tk.Frame(self.kertas, bg="white")
        kop_frame.grid(row=1, column=0, columnspan=6, sticky="ew", pady=(0, 20))
        kop_frame.columnconfigure(2, weight=1)

        fnt_kop = ("Segoe UI", 10)
        tk.Label(kop_frame, text="Nama MDTU\nAlamat\nNama Santri\nNo. Induk", bg="white", fg=self.C_TEKS, font=fnt_kop, justify="left", anchor="w").grid(row=0, column=0, sticky="nw")
        tk.Label(kop_frame, text=":\n:\n:\n:", bg="white", fg=self.C_TEKS, font=fnt_kop).grid(row=0, column=1, sticky="nw", padx=10)
        self.lbl_dinamis['kop_kiri'] = tk.Label(kop_frame, text="-\n-\n-\n-", bg="white", fg=self.C_TEKS, font=("Segoe UI", 10, "bold"), justify="left", anchor="w")
        self.lbl_dinamis['kop_kiri'].grid(row=0, column=2, sticky="nw")

        tk.Label(kop_frame, text="Kelas\nSemester\nTahun pelajaran", bg="white", fg=self.C_TEKS, font=fnt_kop, justify="left", anchor="w").grid(row=0, column=3, sticky="nw")
        tk.Label(kop_frame, text=":\n:\n:", bg="white", fg=self.C_TEKS, font=fnt_kop).grid(row=0, column=4, sticky="nw", padx=10)
        self.lbl_dinamis['kop_kanan'] = tk.Label(kop_frame, text="-\n2 (DUA)\n-", bg="white", fg=self.C_TEKS, font=("Segoe UI", 10, "bold"), justify="left", anchor="w")
        self.lbl_dinamis['kop_kanan'].grid(row=0, column=5, sticky="nw")

        # 3. TABEL NILAI
        tb_frame = tk.Frame(self.kertas, bg=self.C_BORDER, bd=1)
        tb_frame.grid(row=2, column=0, columnspan=6, sticky="ew")
        tb_frame.columnconfigure(1, weight=1)

        # Header
        self.buat_sel(tb_frame, 0, 0, "No.", anchor="center", is_header=True)
        self.buat_sel(tb_frame, 0, 1, "Mata Pelajaran", anchor="center", is_header=True)
        self.buat_sel(tb_frame, 0, 2, "Nilai Prestasi", span=2, anchor="center", is_header=True)
        self.buat_sel(tb_frame, 0, 4, "Rata-rata\nKelas", anchor="center", is_header=True)
        self.buat_sel(tb_frame, 1, 2, "Angka", anchor="center", is_header=True)
        self.buat_sel(tb_frame, 1, 3, "Huruf", anchor="center", is_header=True)

        mapels = [
            ("1", "Keagamaan", True),
            ("a", "AL QUR'AN", False), ("b", "AL HADITS", False), ("c", "AQIDAH", False),
            ("d", "AKHLAQ", False), ("e", "FIQIH", False), ("f", "TARIKH ISLAM", False),
            ("g", "BAHASA ARAB", False), ("h", "NAHWU", False), ("i", "SHARAF", False),
            ("2", "Muatan Lokal", True),
            ("a", "PRAKTIK IBADAH", False), ("b", "BTQ", False), ("c", "Ke-NU-an", False)
        ]

        r = 2
        for no, teks, is_judul in mapels:
            fnt = ("Segoe UI", 10, "bold") if is_judul else ("Segoe UI", 10)
            self.buat_sel(tb_frame, r, 0, no if is_judul else "", anchor="center", font=fnt)
            self.buat_sel(tb_frame, r, 1, teks if is_judul else f"   {no}.  {teks}", font=fnt)
            if not is_judul:
                self.lbl_dinamis[f'n_{teks}'] = self.buat_sel(tb_frame, r, 2, "-", anchor="center")
                self.lbl_dinamis[f'h_{teks}'] = self.buat_sel(tb_frame, r, 3, "-")
                self.buat_sel(tb_frame, r, 4, "-", anchor="center")
            else:
                self.buat_sel(tb_frame, r, 2, "", span=3)
            r += 1

        # Baris Jumlah
        self.buat_sel(tb_frame, r, 1, "Jumlah", anchor="center", is_header=True)
        self.lbl_dinamis['jml_a'] = self.buat_sel(tb_frame, r, 2, "-", anchor="center", is_header=True)
        self.lbl_dinamis['jml_h'] = self.buat_sel(tb_frame, r, 3, "-", is_header=True)
        self.buat_sel(tb_frame, r, 4, "-", anchor="center", is_header=True)

        # 4. KEPUTUSAN AKHIR (PENTING DI SEMESTER GENAP)
        r += 1
        # Memberikan latar belakang sedikit berbeda agar mencolok
        self.lbl_dinamis['keputusan'] = self.buat_sel(tb_frame, r, 0, 
            "KEPUTUSAN :\nBerdasarkan hasil yang dicapai pada Semester 1 dan 2, santri ini ditetapkan :\nSTATUS : -", 
            span=5, bg="#F9F9F9", font=("Segoe UI", 10, "bold"))

        # 5. TANDA TANGAN
        ttd_frame = tk.Frame(self.kertas, bg="white")
        ttd_frame.grid(row=3, column=0, columnspan=6, sticky="ew", pady=(30, 0))
        ttd_frame.columnconfigure(1, weight=1)
        ttd_frame.columnconfigure(2, weight=1)

        self.lbl_dinamis['ttd_lokasi'] = tk.Label(ttd_frame, text="Diberikan di  : -\nTanggal         : -", bg="white", fg=self.C_TEKS, font=fnt_kop, justify="left", anchor="w")
        self.lbl_dinamis['ttd_lokasi'].grid(row=0, column=0, columnspan=3, sticky="nw", pady=(0, 20))

        tk.Label(ttd_frame, text="Mengetahui", bg="white", fg=self.C_TEKS, font=fnt_kop).grid(row=1, column=1, pady=(0,10))
        
        tk.Label(ttd_frame, text="Kepala Madrasah,", bg="white", fg=self.C_TEKS, font=fnt_kop).grid(row=2, column=0)
        tk.Label(ttd_frame, text="Orang Tua,", bg="white", fg=self.C_TEKS, font=fnt_kop).grid(row=2, column=1)
        tk.Label(ttd_frame, text="Wali Kelas,", bg="white", fg=self.C_TEKS, font=fnt_kop).grid(row=2, column=2)

        self.lbl_dinamis['ttd_kepala'] = tk.Label(ttd_frame, text="........................", bg="white", fg=self.C_TEKS, font=("Segoe UI", 10, "bold underline"))
        self.lbl_dinamis['ttd_kepala'].grid(row=3, column=0, pady=(60,0))
        
        tk.Label(ttd_frame, text="........................", bg="white", fg=self.C_TEKS, font=fnt_kop).grid(row=3, column=1, pady=(60,0))
        
        self.lbl_dinamis['ttd_wali'] = tk.Label(ttd_frame, text="........................", bg="white", fg=self.C_TEKS, font=("Segoe UI", 10, "bold"))
        self.lbl_dinamis['ttd_wali'].grid(row=3, column=2, pady=(60,0))

    def refresh_dropdown(self):
        self.combo_cetak['values'] = self.db.get_daftar_nama()

    def tampilkan_preview(self):
        nama = self.combo_cetak.get()
        if not nama: return
        
        # Ambil Data Identitas
        idx_nama = self.db.kolom_lengkap.index("NAMA") if "NAMA" in self.db.kolom_lengkap else -1
        idx_induk = self.db.kolom_lengkap.index("NO. INDUK") if "NO. INDUK" in self.db.kolom_lengkap else -1
        data_santri = next((row for row in self.db.data_master if len(row) > idx_nama and row[idx_nama] == nama), None)
        no_induk = data_santri[idx_induk] if data_santri else "-"
        
        dl = self.db.data_lembaga
        self.lbl_dinamis['kop_kiri'].config(text=f"{dl.get('NAMA MADRASAH', '-')}\n{dl.get('DESA/KELURAHAN', '-')}\n{nama}\n{no_induk}")
        self.lbl_dinamis['kop_kanan'].config(text=f"{dl.get('KELAS', '-')}\n2 (DUA)\n{dl.get('TAHUN PELAJARAN', '-')}")

        # Update Nilai & Keputusan
        if nama in self.db.data_nilai:
            dn = self.db.data_nilai[nama]
            self.lbl_dinamis['jml_a'].config(text=f"{dn['jumlah']:.0f}")
            self.lbl_dinamis['jml_h'].config(text=terbilang(dn['jumlah']).capitalize())
            
            # Status Kenaikan Kelas
            status = dn.get('status', '-')
            self.lbl_dinamis['keputusan'].config(text=f"KEPUTUSAN :\nDengan memperhatikan hasil yang dicapai pada Semester 1 dan 2, santri ini ditetapkan :\nSTATUS : {status.upper()}")
            
            for m, s in dn['akademik'].items():
                if f'n_{m}' in self.lbl_dinamis:
                    self.lbl_dinamis[f'n_{m}'].config(text=f"{s:.0f}")
                    self.lbl_dinamis[f'h_{m}'].config(text=terbilang(s).capitalize())
        
        # Update TTD
        self.lbl_dinamis['ttd_lokasi'].config(text=f"Diberikan di  : {dl.get('TEMPAT RAPORT', '-')}\nTanggal         : {dl.get('TANGGAL RAPORT', '-')}")
        self.lbl_dinamis['ttd_kepala'].config(text=dl.get('KEPALA MADIN', '........................'))
        self.lbl_dinamis['ttd_wali'].config(text=dl.get('WALI KELAS', '........................'))