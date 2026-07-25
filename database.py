import streamlit as st
from supabase import create_client, Client
import hashlib

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
            # Mengambil data lembaga yang sudah diverifikasi Super Admin
            res = self.supabase.table("lembaga").select("id, nama_madrasah, profil_lengkap, pengaturan_master").eq("is_active", True).execute()
            return res.data if res.data else []
        except:
            return []

    def register_madrasah(self, email, password, nama_madrasah, nsm, tingkatan):
        try:
            try: 
                self.supabase.auth.sign_up({"email": email, "password": password})
            except: 
                pass 
            
            profil = {"tingkatan": tingkatan}
            self.supabase.table("lembaga").insert({
                "email": email, 
                "nama_madrasah": nama_madrasah, 
                "nsm": nsm, 
                "profil_lengkap": profil,
                "is_active": False # Status awal ditahan Super Admin
            }).execute()
            return True, "Pendaftaran berhasil! Akun Anda menunggu verifikasi Super Admin."
        except Exception as e:
            return False, f"Pendaftaran error: {e}"

    # --- FITUR MANAJEMEN AKUN GURU ---
    def tambah_akun_guru(self, nama_guru, username, password, role, kelas_binaan, nik, jk, tempat_lahir, tgl_lahir, no_hp, alamat):
        """Admin mendaftarkan guru dengan kelengkapan KTP"""
        if not self.lembaga_id: 
            return False, "❌ Akses ditolak: Identitas lembaga tidak ditemukan."
        
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        data_baru = {
            "lembaga_id": self.lembaga_id,
            "nama_guru": nama_guru,
            "username": username.strip(),
            "password": hashed_password, 
            "role": role,
            "kelas_binaan": kelas_binaan if kelas_binaan and str(kelas_binaan).strip() != "" else None,
            # Data tambahan sesuai KTP
            "nik": nik,
            "jenis_kelamin": jk,
            "tempat_lahir": tempat_lahir,
            "tanggal_lahir": str(tgl_lahir),
            "no_hp": no_hp,
            "alamat": alamat
        }
        
        try:
            res = self.supabase.table("guru").insert(data_baru).execute()
            if res.data:
                return True, f"✅ Berhasil! Akun dan Biodata untuk {nama_guru} telah ditambahkan."
            return False, "❌ Gagal menyimpan data ke database."
        except Exception as e:
            return False, f"❌ Error Database: {e}"

    def update_akun_guru(self, guru_id, nama_guru, username, password, role, kelas_binaan, nik, jk, tempat_lahir, tgl_lahir, no_hp, alamat):
        """Memperbarui data atau mereset sandi guru yang sudah ada"""
        if not self.lembaga_id: 
            return False, "❌ Akses ditolak."
        
        data_update = {
            "nama_guru": nama_guru,
            "username": username.strip(),
            "role": role,
            "kelas_binaan": kelas_binaan if kelas_binaan and str(kelas_binaan).strip() != "" else None,
            "nik": nik,
            "jenis_kelamin": jk,
            "tempat_lahir": tempat_lahir,
            "tanggal_lahir": str(tgl_lahir),
            "no_hp": no_hp,
            "alamat": alamat
        }
        
        # Enkripsi ulang password HANYA jika field password baru diisi
        if password and password.strip() != "":
            data_update["password"] = hashlib.sha256(password.encode()).hexdigest()
            
        try:
            res = self.supabase.table("guru").update(data_update).eq("id", guru_id).eq("lembaga_id", self.lembaga_id).execute()
            if res.data:
                return True, f"✅ Data {nama_guru} berhasil diperbarui!"
            return False, "❌ Gagal mengedit data."
        except Exception as e:
            return False, f"❌ Error: {e}"

    def hapus_akun_guru(self, guru_id):
        """Menghapus akun guru secara permanen"""
        if not self.lembaga_id: 
            return False, "❌ Akses ditolak."
        try:
            self.supabase.table("guru").delete().eq("id", guru_id).eq("lembaga_id", self.lembaga_id).execute()
            return True, "🗑️ Akun guru berhasil dihapus permanen!"
        except Exception as e:
            return False, f"❌ Gagal menghapus data: {e}"

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

    # --- SISTEM LOGIN TERPUSAT (DENGAN ISOLASI ERROR) ---
    def login(self, identitas, password):
        """Menangani Login Admin (Email) maupun Guru (Username/NIP)"""
        identitas = str(identitas).strip()
        
        # 1. CEK LOGIN GURU / WALI KELAS (Tabel 'guru')
        try:
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            guru_res = self.supabase.table("guru").select("*").eq("username", identitas).eq("password", hashed_password).execute()
            
            if guru_res and guru_res.data:
                g_data = guru_res.data[0]
                
                # Tarik data lembaga yang menaungi guru tersebut
                l_res = self.supabase.table("lembaga").select("*").eq("id", g_data["lembaga_id"]).execute()
                if not l_res.data:
                    return False, "❌ Data lembaga untuk guru/wali kelas ini tidak ditemukan."
                
                l_data = l_res.data[0]
                if not l_data.get("is_active"):
                    return False, "⏳ Akses Ditolak: Madrasah Anda belum disetujui Super Admin."
                
                # Set sesi aktif untuk guru
                l_data["_role"] = g_data.get("role", "guru")
                l_data["_nama_guru"] = g_data["nama_guru"]
                l_data["_kelas_binaan"] = g_data.get("kelas_binaan")
                
                self.list_akses_lembaga = [l_data]
                self.set_active_lembaga(l_data)
                return True, f"🔑 Selamat datang, {g_data['nama_guru']}!"
        except Exception:
            # Jika pencarian tabel guru bermasalah/tidak ada, dilewati ke cek Admin
            pass

        # 2. CEK LOGIN ADMIN LEMBAGA (Supabase Auth - Email)
        if "@" in identitas:
            try:
                auth_res = self.supabase.auth.sign_in_with_password({"email": identitas, "password": password})
                if auth_res and auth_res.user:
                    lembaga_res = self.supabase.table("lembaga").select("*").eq("email", identitas).execute()
                    if not lembaga_res.data:
                        return False, "❌ Email terdaftar di Auth, tetapi data madrasah tidak ditemukan di database."
                    
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
                    return True, "🔑 Login Admin Berhasil!"
            except Exception:
                return False, "❌ Login Admin Gagal: Email atau Password salah."

        return False, "❌ Login Gagal: Username/Email tidak terdaftar atau Password salah."

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

    # ==========================================================
    # PERBAIKAN: MESIN PENCARI SANTRI CERDAS (SMART FILTER)
    # ==========================================================
    def muat_data_santri(self):
        if not self.lembaga_id: 
            return
        try:
            # 1. Tarik semua data santri di madrasah ini dari database
            res = self.supabase.table("biodata_santri").select("*").eq("lembaga_id", self.lembaga_id).execute()
            semua_santri = res.data if res.data else []
            
            # 2. Jika yang login adalah Admin (atau guru tanpa kelas binaan), tampilkan semua data
            if self.role != "wali_kelas" or not self.kelas_binaan:
                self.data_master = semua_santri
            else:
                # 3. Jika Wali Kelas, lakukan "Smart Filter" agar tidak di-blokir oleh typo/spasi
                kelas_binaan_bersih = str(self.kelas_binaan).upper().replace(" ", "")
                
                santri_kelasku = []
                for s in semua_santri:
                    # Ambil data kelas dari JSONB
                    data_lengkap = s.get("data_lengkap", {})
                    kelas_santri = str(data_lengkap.get("kelas_santri", data_lengkap.get("kelas", "")))
                    kelas_santri_bersih = kelas_santri.upper().replace(" ", "")
                    
                    # Jika kelasnya cocok, masukkan ke daftar pandangan Wali Kelas
                    if kelas_santri_bersih == kelas_binaan_bersih:
                        santri_kelasku.append(s)
                        
                # Update memori aplikasi dengan daftar santri yang sudah difilter
                self.data_master = santri_kelasku
                
        except Exception as e: 
            print(f"Error muat_data_santri: {e}")

    def get_daftar_nama(self):
        return [santri["nama"] for santri in self.data_master]

    def simpan_lembaga(self, data):
        if not self.lembaga_id: 
            return False, "Akses ditolak"
        try:
            res = self.supabase.table("lembaga").update(data).eq("id", self.lembaga_id).execute()
            if res.data:
                self.data_lembaga = res.data[0]
                return True, "Data Identitas Lembaga berhasil diperbarui!"
        except Exception as e: 
            return False, f"Gagal: {e}"

    def simpan_pengaturan(self, data_pengaturan):
        if not self.lembaga_id: 
            return False, "Akses ditolak."
        try:
            res = self.supabase.table("lembaga").update({"pengaturan_master": data_pengaturan}).eq("id", self.lembaga_id).execute()
            if res.data:
                self.data_lembaga = res.data[0]
                return True, "Master Data berhasil disimpan!"
        except Exception as e: 
            return False, f"Gagal: {e}"

    # --- FITUR MANAJEMEN SANTRI LENGKAP ---
    def simpan_biodata(self, no_induk, nama, data_lengkap, santri_id=None):
        if not self.lembaga_id: 
            return False, "Akses ditolak"
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
            
            self.muat_data_santri()
            return True, pesan
        except Exception as e: 
            return False, f"Gagal: {e}"

    def simpan_bulk_biodata(self, list_data):
        """Fungsi khusus untuk menyimpan data banyak sekaligus dari Excel"""
        if not self.lembaga_id: 
            return False, "Akses ditolak"
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
        if not self.lembaga_id: 
            return False, "Akses ditolak"
        try:
            self.supabase.table("nilai_santri").delete().eq("santri_id", santri_id).execute()
            self.supabase.table("biodata_santri").delete().eq("id", santri_id).eq("lembaga_id", self.lembaga_id).execute()
            
            self.muat_data_santri()
            return True, "Data santri beserta nilainya berhasil dihapus secara permanen!"
        except Exception as e:
            return False, f"Gagal menghapus: {e}"

    # --- FITUR PENILAIAN & RANKING ---
    def simpan_nilai(self, data_nilai, id_nilai=None):
        if not self.lembaga_id: 
            return False, "Akses ditolak"
        data_nilai["lembaga_id"] = self.lembaga_id 
        try:
            if id_nilai: 
                self.supabase.table("nilai_santri").update(data_nilai).eq("id", id_nilai).eq("lembaga_id", self.lembaga_id).execute()
            else: 
                self.supabase.table("nilai_santri").insert(data_nilai).execute()
            return True, "Data nilai tersimpan!"
        except Exception as e: 
            return False, f"Gagal: {e}"

    def get_nilai(self, santri_id, semester):
        if not self.lembaga_id: 
            return None
        try:
            res = self.supabase.table("nilai_santri").select("*").eq("santri_id", santri_id).eq("semester", semester).eq("lembaga_id", self.lembaga_id).execute()
            return res.data[0] if res.data else None
        except: 
            return None

    def get_semua_nilai(self, semester):
        if not self.lembaga_id: 
            return []
        try:
            res = self.supabase.table("nilai_santri").select("*").eq("semester", semester).eq("lembaga_id", self.lembaga_id).execute()
            return res.data if res.data else []
        except: 
            return []

    def get_ranking(self, santri_id, semester):
        if not self.lembaga_id: 
            return "-", 0
        try:
            query = self.supabase.table("nilai_santri").select("santri_id, jumlah").eq("semester", semester).eq("lembaga_id", self.lembaga_id)
            res = query.execute()
            if not res.data: 
                return "-", 0
            
            if self.role == "wali_kelas" and self.kelas_binaan:
                santri_kelas_ini = [s['id'] for s in self.data_master]
                data_valid = [x for x in res.data if x['santri_id'] in santri_kelas_ini]
            else:
                data_valid = res.data
                
            data_urut = sorted(data_valid, key=lambda x: x['jumlah'], reverse=True)
            rank = 1
            for item in data_urut:
                if item['santri_id'] == santri_id: 
                    return rank, len(data_urut)
                rank += 1
            return "-", len(data_urut)
        except: 
            return "-", 0

    # --- FITUR ABSENSI ---
    def get_absensi_harian(self, tanggal):
        if not self.lembaga_id: 
            return {}
        try:
            res = self.supabase.table("absensi_harian").select("*").eq("lembaga_id", self.lembaga_id).eq("tanggal", str(tanggal)).execute()
            if res.data:
                return {item['santri_id']: item['status'] for item in res.data}
            return {}
        except: 
            return {}

    def simpan_absensi_harian(self, tanggal, dict_absen):
        if not self.lembaga_id: 
            return False, "Akses ditolak"
        try:
            list_santri_id = list(dict_absen.keys())
            if not list_santri_id: 
                return True, "Tidak ada data disimpan"

            self.supabase.table("absensi_harian").delete().eq("lembaga_id", self.lembaga_id).eq("tanggal", str(tanggal)).in_("santri_id", list_santri_id).execute()

            data_insert = []
            for santri_id, status in dict_absen.items():
                data_insert.append({
                    "lembaga_id": self.lembaga_id,
                    "santri_id": santri_id,
                    "tanggal": str(tanggal),
                    "status": status
                })
            
            if data_insert:
                self.supabase.table("absensi_harian").insert(data_insert).execute()
                
            return True, "Absensi harian berhasil disimpan!"
        except Exception as e:
            return False, f"Gagal menyimpan absen: {e}"