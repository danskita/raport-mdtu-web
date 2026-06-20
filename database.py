import streamlit as st
from supabase import create_client, Client

class DataEngine:
    def __init__(self):
        url: str = st.secrets["SUPABASE_URL"]
        key: str = st.secrets["SUPABASE_KEY"]
        self.supabase: Client = create_client(url, key)
        
        self.data_lembaga = {}
        self.data_master = []
        self.lembaga_id = None 
        self.role = None 
        self.list_akses_lembaga = [] # Menyimpan daftar SEMUA madrasah milik 1 email
        
    def get_semua_madrasah(self):
        try:
            res = self.supabase.table("lembaga").select("id, nama_madrasah, profil_lengkap").execute()
            return res.data if res.data else []
        except:
            return []

    def register_madrasah(self, email, password, nama_madrasah, nsm, tingkatan):
        try:
            # Daftar ke sistem auth (jika email sudah ada, abaikan error auth-nya dan lanjut simpan data)
            try: self.supabase.auth.sign_up({"email": email, "password": password})
            except: pass 
            
            # Kunci pengaturan tingkatan sejak awal mendaftar
            profil = {"tingkatan": tingkatan}
            
            self.supabase.table("lembaga").insert({
                "email": email,
                "nama_madrasah": nama_madrasah,
                "nsm": nsm,
                "profil_lengkap": profil
            }).execute()
            return True, "Pendaftaran Lembaga berhasil! Silakan pindah ke tab Login."
        except Exception as e:
            return False, f"Pendaftaran error: {e}"

    def register_guru(self, email, password, nama_guru, list_lembaga_id):
        """Mendaftarkan akun Guru dan menautkannya ke MAKSIMAL 3 Lembaga yang dipilih"""
        try:
            try: self.supabase.auth.sign_up({"email": email, "password": password})
            except: pass
            
            for l_id in list_lembaga_id:
                self.supabase.table("guru").insert({
                    "email": email, "nama_guru": nama_guru, "lembaga_id": l_id, "role": "guru"
                }).execute()
            return True, "Akun Guru berhasil didaftarkan di madrasah terpilih! Silakan Login."
        except Exception as e:
            return False, f"Pendaftaran error: {e}"

    def login(self, email, password):
        try:
            res = self.supabase.auth.sign_in_with_password({"email": email, "password": password})
            if res.user:
                # 1. Cari SEMUA madrasah di mana email ini menjadi Admin
                lembaga_res = self.supabase.table("lembaga").select("*").eq("email", email).execute()
                admin_lembagas = lembaga_res.data if lembaga_res.data else []

                # 2. Cari SEMUA madrasah di mana email ini menjadi Guru
                guru_res = self.supabase.table("guru").select("*").eq("email", email).execute()
                guru_lembagas = []
                if guru_res.data:
                    for g in guru_res.data:
                        l_res = self.supabase.table("lembaga").select("*").eq("id", g["lembaga_id"]).execute()
                        if l_res.data:
                            l_data = l_res.data[0]
                            l_data["_role"] = "guru"
                            l_data["_nama_guru"] = g["nama_guru"]
                            guru_lembagas.append(l_data)

                # Gabungkan semua akses
                for a in admin_lembagas:
                    a["_role"] = "admin"

                all_lembagas = admin_lembagas + guru_lembagas

                if not all_lembagas:
                    return False, "Akun tidak terdaftar di lembaga manapun."

                # Simpan list akses dan set lembaga pertama sebagai default awal
                self.list_akses_lembaga = all_lembagas
                self.set_active_lembaga(all_lembagas[0])
                
                return True, "Login berhasil!"
            return False, "Email atau Password salah."
        except Exception as e:
            return False, "Email atau Password salah!"

    def set_active_lembaga(self, data_lembaga):
        """Fungsi untuk berpindah antar madrasah di dalam aplikasi"""
        self.lembaga_id = data_lembaga['id']
        self.role = data_lembaga['_role']
        self.data_lembaga = data_lembaga
        self.muat_data_santri()

    def logout(self):
        self.supabase.auth.sign_out()
        self.data_lembaga = {}
        self.data_master = []
        self.lembaga_id = None
        self.role = None
        self.list_akses_lembaga = []

    def muat_data_santri(self):
        if not self.lembaga_id: return
        try:
            res = self.supabase.table("biodata_santri").select("*").eq("lembaga_id", self.lembaga_id).execute()
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

    def simpan_biodata(self, no_induk, nama, data_lengkap):
        if not self.lembaga_id: return False, "Akses ditolak"
        try:
            self.supabase.table("biodata_santri").insert({"lembaga_id": self.lembaga_id, "no_induk": no_induk, "nama": nama, "data_lengkap": data_lengkap}).execute()
            self.muat_data_santri()
            return True, "Biodata santri berhasil ditambahkan!"
        except Exception as e: return False, f"Gagal: {e}"

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
            res = self.supabase.table("nilai_santri").select("santri_id, jumlah").eq("semester", semester).eq("lembaga_id", self.lembaga_id).execute()
            if not res.data: return "-", 0
            data_urut = sorted(res.data, key=lambda x: x['jumlah'], reverse=True)
            rank = 1
            for item in data_urut:
                if item['santri_id'] == santri_id: return rank, len(data_urut)
                rank += 1
            return "-", len(data_urut)
        except: return "-", 0