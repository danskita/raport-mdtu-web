import streamlit as st
from supabase import create_client, Client

class DataEngine:
    def __init__(self):
        # 1. Inisialisasi koneksi Supabase
        url: str = st.secrets["SUPABASE_URL"]
        key: str = st.secrets["SUPABASE_KEY"]
        self.supabase: Client = create_client(url, key)
        
        # 2. Tempat menyimpan data di memori
        self.data_lembaga = {}
        self.data_master = []
        self.lembaga_id = None # Ini adalah "Pagar Gaib" kita
        
    def register_madrasah(self, email, password, nama_madrasah, nsm):
        """Mendaftarkan Madrasah Baru Menggunakan Email"""
        try:
            # 1. Daftarkan email dan password ke Sistem Auth Supabase
            auth_res = self.supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            
            # 2. Jika berhasil, masukkan data awal ke tabel lembaga
            if auth_res.user:
                self.supabase.table("lembaga").insert({
                    "email": email,
                    "nama_madrasah": nama_madrasah,
                    "nsm": nsm
                }).execute()
                return True, "Pendaftaran berhasil! Silakan pindah ke tab Login."
            return False, "Gagal mendaftar. Silakan coba lagi."
        except Exception as e:
            return False, f"Pendaftaran error: {e}"

    def login(self, email, password):
        """Login dan tarik profil lembaga"""
        try:
            # 1. Autentikasi email dan password
            res = self.supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if res.user:
                # 2. Cari lembaga_id berdasarkan email ini
                lembaga_res = self.supabase.table("lembaga").select("*").eq("email", email).execute()
                if lembaga_res.data:
                    self.data_lembaga = lembaga_res.data[0]
                    self.lembaga_id = self.data_lembaga['id'] # Pasang Pagar Gaib
                    self.muat_data_santri() # Tarik santri khusus madrasah ini
                    return True, "Login berhasil!"
                return False, "Data profil lembaga tidak ditemukan di database."
        except Exception as e:
            return False, f"Email atau Password salah!"

    def logout(self):
        """Keluar dari aplikasi dan hapus jejak memori"""
        self.supabase.auth.sign_out()
        self.data_lembaga = {}
        self.data_master = []
        self.lembaga_id = None

    def muat_data_santri(self):
        """Menarik biodata HANYA untuk madrasah yang sedang login"""
        if not self.lembaga_id: return
        try:
            res = self.supabase.table("biodata_santri").select("*").eq("lembaga_id", self.lembaga_id).execute()
            self.data_master = res.data if res.data else []
        except Exception as e:
            st.error(f"Gagal memuat data santri: {e}")

    def get_daftar_nama(self):
        return [santri["nama"] for santri in self.data_master]

    def simpan_lembaga(self, data):
        """Memperbarui profil lembaga"""
        if not self.lembaga_id: return False, "Akses ditolak"
        try:
            # Update hanya baris yang ID-nya cocok dengan lembaga_id login
            res = self.supabase.table("lembaga").update(data).eq("id", self.lembaga_id).execute()
            if res.data:
                self.data_lembaga = res.data[0]
                return True, "Data Identitas Lembaga berhasil diperbarui!"
        except Exception as e:
            return False, f"Gagal menyimpan data: {e}"

    def simpan_biodata(self, no_induk, nama, data_lengkap):
        if not self.lembaga_id: return False, "Akses ditolak"
        try:
            res = self.supabase.table("biodata_santri").insert({
                "lembaga_id": self.lembaga_id, # Kunci santri ini ke madrasah yang login
                "no_induk": no_induk,
                "nama": nama,
                "data_lengkap": data_lengkap
            }).execute()
            if res.data:
                self.muat_data_santri()
                return True, "Biodata santri berhasil ditambahkan!"
        except Exception as e:
            return False, f"Gagal menyimpan biodata: {e}"

    def simpan_nilai(self, data_nilai, id_nilai=None):
        if not self.lembaga_id: return False, "Akses ditolak"
        
        # Selalu sisipkan lembaga_id demi keamanan
        data_nilai["lembaga_id"] = self.lembaga_id 
        try:
            if id_nilai:
                # Update but MUST match lembaga_id to prevent hacking
                self.supabase.table("nilai_santri").update(data_nilai).eq("id", id_nilai).eq("lembaga_id", self.lembaga_id).execute()
                pesan = "Data nilai berhasil diperbarui!"
            else:
                self.supabase.table("nilai_santri").insert(data_nilai).execute()
                pesan = "Data nilai baru berhasil ditambahkan!"
            return True, pesan
        except Exception as e:
            return False, f"Gagal menyimpan nilai: {e}"

    def get_nilai(self, santri_id, semester):
        if not self.lembaga_id: return None
        try:
            res = self.supabase.table("nilai_santri").select("*").eq("santri_id", santri_id).eq("semester", semester).eq("lembaga_id", self.lembaga_id).execute()
            if res.data: return res.data[0]
            return None
        except: return None

    def get_semua_nilai(self, semester):
        if not self.lembaga_id: return []
        try:
            res = self.supabase.table("nilai_santri").select("*").eq("semester", semester).eq("lembaga_id", self.lembaga_id).execute()
            return res.data if res.data else []
        except: return []

    def get_ranking(self, santri_id, semester):
        if not self.lembaga_id: return "-", 0
        try:
            res = self.supabase.table("nilai_santri").select("santri_id, jumlah").eq("semester", semester).eq("lembaga_id", self.lembaga_id).execute()
            if not res.data: return "-", 0
            
            data_urut = sorted(res.data, key=lambda x: x['jumlah'], reverse=True)
            rank = 1
            for item in data_urut:
                if item['santri_id'] == santri_id: return rank, len(data_urut)
                rank += 1
            return "-", len(data_urut)
        except: return "-", 0
    def simpan_pengaturan(self, data_pengaturan):
        """Menyimpan Master Data (Kelas, Mapel, Alamat, Narasi) khusus untuk lembaga yang sedang login"""
        if not self.lembaga_id: return False, "Akses ditolak. Anda belum login."
        try:
            res = self.supabase.table("lembaga").update({
                "pengaturan_master": data_pengaturan
            }).eq("id", self.lembaga_id).execute()

            if res.data:
                self.data_lembaga = res.data[0] # Segarkan memori lokal
                return True, "Master Data berhasil disimpan ke Cloud!"
            return False, "Gagal mengupdate database."
        except Exception as e:
            return False, f"Error saat menyimpan pengaturan: {e}"