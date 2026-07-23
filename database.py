import streamlit as st
from supabase import create_client, Client
import hashlib # Modul baru untuk enkripsi password guru

class DataEngine:
    def __init__(self):
        url: str = st.secrets["SUPABASE_URL"]
        key: str = st.secrets["SUPABASE_KEY"]
        self.supabase: Client = create_client(url, key)
        
        self.data_lembaga = {}
        self.data_master = []
        self.lembaga_id = None 
        self.role = None 
        self.kelas_binaan = None # Identitas pengunci kelas
        self.list_akses_lembaga = []
        
    def get_semua_madrasah(self):
        try:
            # Mengambil data lembaga (Hanya yang sudah diverifikasi Super Admin agar bisa dipilih Guru)
            res = self.supabase.table("lembaga").select("id, nama_madrasah, profil_lengkap, pengaturan_master").eq("is_active", True).execute()
            return res.data if res.data else []
        except:
            return []

    def register_madrasah(self, email, password, nama_madrasah, nsm, tingkatan):
        try:
            try: self.supabase.auth.sign_up({"email": email, "password": password})
            except: pass 
            
            profil = {"tingkatan": tingkatan}
            self.supabase.table("lembaga").insert({
                "email": email, 
                "nama_madrasah": nama_madrasah, 
                "nsm": nsm, 
                "profil_lengkap": profil,
                "is_active": False # <--- SINKRONISASI: STATUS AWAL DITAHAN SUPER ADMIN
            }).execute()
            return True, "Pendaftaran berhasil! Akun Anda menunggu verifikasi Super Admin."
        except Exception as e:
            return False, f"Pendaftaran error: {e}"

    # --- FITUR MANAJEMEN AKUN GURU (BARU) ---
    def tambah_akun_guru(self, nama_guru, username, password, role, kelas_binaan):
        """Admin mendaftarkan guru/wali kelas secara manual (Tanpa perlu daftar mandiri)"""
        if not self.lembaga_id: 
            return False
        
        # Enkripsi password untuk keamanan
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        data_baru = {
            "lembaga_id": self.lembaga_id,
            "nama_guru": nama_guru,
            "username": username,
            "password": hashed_password, 
            "role": role,
            "kelas_binaan": kelas_binaan if kelas_binaan and str(kelas_binaan).strip() != "" else None
        }
        
        try:
            res = self.supabase.table("guru").insert(data_baru).execute()
            return True if res.data else False
        except Exception as e:
            print(f"Error pada tambah_akun_guru: {e}")
            return False

    def get_semua_guru_lembaga(self):
        """Mengambil daftar seluruh guru di lembaga yang sedang aktif"""
        if not self.lembaga_id: 
            return []
        try:
            res = self.supabase.table("guru").select("*").eq("lembaga_id", self.lembaga_id).execute()
            return res.data if res.data else []
        except Exception as e:
            print("Error get_semua_guru_lembaga:", e)
            return []

    # --- SISTEM LOGIN TERPUSAT ---
    def login(self, identitas, password):
        """Menangani Login Admin (Email) maupun Guru (Username/NIP)"""
        try:
            # 1. Cek apakah ini login Guru/Wali Kelas (menggunakan tabel 'guru' & enkripsi password)
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            guru_res = self.supabase.table("guru").select("*").eq("username", identitas).eq("password", hashed_password).execute()
            
            if guru_res.data:
                g_data = guru_res.data[0]
                
                # Tarik data lembaga yang menaungi guru tersebut
                l_res = self.supabase.table("lembaga").select("*").eq("id", g_data["lembaga_id"]).execute()
                if not l_res.data:
                    return False, "Data lembaga tidak ditemukan."
                
                l_data = l_res.data[0]
                if not l_data.get("is_active"):
                    return False, "⏳ Akses Ditolak: Madrasah Anda telah ditangguhkan/belum disetujui Super Admin."
                
                # Set sesi untuk guru/wali kelas
                l_data["_role"] = g_data.get("role", "guru")
                l_data["_nama_guru"] = g_data["nama_guru"]
                l_data["_kelas_binaan"] = g_data.get("kelas_binaan")
                
                self.list_akses_lembaga = [l_data]
                self.set_active_lembaga(l_data)
                return True, f"Selamat datang, {g_data['nama_guru']}!"

            # 2. Jika bukan guru, cek apakah ini login Admin Lembaga (via Supabase Auth - Email)
            auth_res = self.supabase.auth.sign_in_with_password({"email": identitas, "password": password})
            if auth_res.user:
                lembaga_res = self.supabase.table("lembaga").select("*").eq("email", identitas).execute()
                if not lembaga_res.data:
                    return False, "Akun Admin tidak memiliki data lembaga terdaftar."
                
                admin_lembagas = lembaga_res.data
                lembagas_aktif = [l for l in admin_lembagas if l.get("is_active") == True]
                
                if not lembagas_aktif:
                    return False, "⏳ Akses Ditolak: Madrasah Anda belum disetujui oleh Super Admin. Harap bersabar."
                
                # Set sesi untuk Admin Lembaga
                for a in lembagas_aktif:
                    a["_role"] = "admin"
                    a["_kelas_binaan"] = None
                    
                self.list_akses_lembaga = lembagas_aktif
                self.set_active_lembaga(lembagas_aktif[0])
                return True, "Login Admin berhasil!"

            return False, "NIP/Username/Email atau Password salah."
            
        except Exception as e:
            # Cegah error crash jika sign_in_with_password gagal (karena format email tidak valid dsb)
            return False, "Login gagal! Periksa kembali kredensial Anda."

    def set_active_lembaga(self, data_lembaga):
        self.lembaga_id = data_lembaga['id']
        self.role = data_lembaga['_role']
        self.kelas_binaan = data_lembaga.get('_kelas_binaan')
        self.data_lembaga = data_lembaga
        self.muat_data_santri()

    def logout(self):
        try:
            self.supabase.auth.sign_out()
        except:
            pass
        self.data_lembaga = {}
        self.data_master = []
        self.lembaga_id = None
        self.role = None
        self.kelas_binaan = None
        self.list_akses_lembaga = []

    def muat_data_santri(self):
        if not self.lembaga_id: return
        try:
            # PENGUNCI DATA: Jika wali kelas, hanya tarik santri yang kelasnya cocok dari kolom JSONB
            query = self.supabase.table("biodata_santri").select("*").eq("lembaga_id", self.lembaga_id)
            if self.role == "wali_kelas" and self.kelas_binaan:
                query = query.eq("data_lengkap->>kelas_santri", self.kelas_binaan)
            
            res = query.execute()
            self.data_master = res.data if res.data else []
        except: pass

    def get_daftar_nama(self):
        return [santri["nama"] for santri in self.data_master]

    def simpan_lembaga(self, data):
        if not self.lembaga_id: return False, "Akses ditolak"
        try:
            res = self.supabase.table("lembaga").update(data).eq("id", self.lembaga_id).execute()
            if res.data:
                self.data_lembaga = res.data[0]
                return True, "Data Identitas Lembaga berhasil diperbarui!"
        except Exception as e: return False, f"Gagal: {e}"

    def simpan_pengaturan(self, data_pengaturan):
        if not self.lembaga_id: return False, "Akses ditolak."
        try:
            res = self.supabase.table("lembaga").update({"pengaturan_master": data_pengaturan}).eq("id", self.lembaga_id).execute()
            if res.data:
                self.data_lembaga = res.data[0]
                return True, "Master Data berhasil disimpan!"
        except Exception as e: return False, f"Gagal: {e}"

    # --- FITUR MANAJEMEN SANTRI LENGKAP (TAMBAH, EDIT, BULK, HAPUS) ---
    def simpan_biodata(self, no_induk, nama, data_lengkap, santri_id=None):
        if not self.lembaga_id: return False, "Akses ditolak"
        try:
            if santri_id:
                # Mode EDIT (Update)
                self.supabase.table("biodata_santri").update({
                    "no_induk": no_induk, "nama": nama, "data_lengkap": data_lengkap
                }).eq("id", santri_id).eq("lembaga_id", self.lembaga_id).execute()
                pesan = "Data santri berhasil diperbarui!"
            else:
                # Mode SIMPAN BARU (Insert)
                self.supabase.table("biodata_santri").insert({
                    "lembaga_id": self.lembaga_id, "no_induk": no_induk, "nama": nama, "data_lengkap": data_lengkap
                }).execute()
                pesan = "Biodata santri berhasil ditambahkan!"
            
            self.muat_data_santri() # Refresh memori
            return True, pesan
        except Exception as e: return False, f"Gagal: {e}"

    def simpan_bulk_biodata(self, list_data):
        """Fungsi khusus untuk menyimpan data banyak sekaligus dari Excel"""
        if not self.lembaga_id: return False, "Akses ditolak"
        try:
            for data in list_data:
                data["lembaga_id"] = self.lembaga_id
            
            self.supabase.table("biodata_santri").insert(list_data).execute()
            self.muat_data_santri()
            return True, f"{len(list_data)} data santri berhasil diimpor!"
        except Exception as e:
            return False, f"Gagal mengimpor data: {e}"

    def hapus_biodata(self, santri_id):
        """Fungsi untuk menghapus data santri"""
        if not self.lembaga_id: return False, "Akses ditolak"
        try:
            # Hapus nilai santri terlebih dahulu agar tidak error (Cascade)
            self.supabase.table("nilai_santri").delete().eq("santri_id", santri_id).execute()
            # Hapus data biodata
            self.supabase.table("biodata_santri").delete().eq("id", santri_id).eq("lembaga_id", self.lembaga_id).execute()
            
            self.muat_data_santri()
            return True, "Data santri beserta nilainya berhasil dihapus secara permanen!"
        except Exception as e:
            return False, f"Gagal menghapus: {e}"
    # ------------------------------------------------------------------

    def simpan_nilai(self, data_nilai, id_nilai=None):
        if not self.lembaga_id: return False, "Akses ditolak"
        data_nilai["lembaga_id"] = self.lembaga_id 
        try:
            if id_nilai: self.supabase.table("nilai_santri").update(data_nilai).eq("id", id_nilai).eq("lembaga_id", self.lembaga_id).execute()
            else: self.supabase.table("nilai_santri").insert(data_nilai).execute()
            return True, "Data nilai tersimpan!"
        except Exception as e: return False, f"Gagal: {e}"

    def get_nilai(self, santri_id, semester):
        if not self.lembaga_id: return None
        try:
            res = self.supabase.table("nilai_santri").select("*").eq("santri_id", santri_id).eq("semester", semester).eq("lembaga_id", self.lembaga_id).execute()
            return res.data[0] if res.data else None
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
            # Ranking juga dikunci hanya untuk satu kelas jika yang login wali kelas
            query = self.supabase.table("nilai_santri").select("santri_id, jumlah").eq("semester", semester).eq("lembaga_id", self.lembaga_id)
            res = query.execute()
            if not res.data: return "-", 0
            
            # Filter santri berdasarkan kelas binaan jika wali kelas
            if self.role == "wali_kelas" and self.kelas_binaan:
                santri_kelas_ini = [s['id'] for s in self.data_master]
                data_valid = [x for x in res.data if x['santri_id'] in santri_kelas_ini]
            else:
                data_valid = res.data
                
            data_urut = sorted(data_valid, key=lambda x: x['jumlah'], reverse=True)
            rank = 1
            for item in data_urut:
                if item['santri_id'] == santri_id: return rank, len(data_urut)
                rank += 1
            return "-", len(data_urut)
        except: return "-", 0
        
    def get_absensi_harian(self, tanggal):
        if not self.lembaga_id: return {}
        try:
            # Mengambil data absensi pada tanggal tertentu
            res = self.supabase.table("absensi_harian").select("*").eq("lembaga_id", self.lembaga_id).eq("tanggal", str(tanggal)).execute()
            # Ubah menjadi kamus {santri_id: status} untuk mempermudah UI
            if res.data:
                return {item['santri_id']: item['status'] for item in res.data}
            return {}
        except: return {}

    def simpan_absensi_harian(self, tanggal, dict_absen):
        if not self.lembaga_id: return False, "Akses ditolak"
        try:
            list_santri_id = list(dict_absen.keys())
            if not list_santri_id: return True, "Tidak ada data disimpan"

            # Hapus data absensi tanggal ini KHUSUS untuk santri-santri yang diabsen
            self.supabase.table("absensi_harian").delete().eq("lembaga_id", self.lembaga_id).eq("tanggal", str(tanggal)).in_("santri_id", list_santri_id).execute()

            # Siapkan data baru
            data_insert = []
            for santri_id, status in dict_absen.items():
                data_insert.append({
                    "lembaga_id": self.lembaga_id,
                    "santri_id": santri_id,
                    "tanggal": str(tanggal),
                    "status": status
                })
            
            # Masukkan ke database
            if data_insert:
                self.supabase.table("absensi_harian").insert(data_insert).execute()
                
            return True, "Absensi harian berhasil disimpan!"
        except Exception as e:
            return False, f"Gagal menyimpan absen: {e}"