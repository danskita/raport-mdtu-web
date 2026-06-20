import streamlit as st
from supabase import create_client, Client

class DataEngine:
    def __init__(self):
        # 1. Inisialisasi koneksi Supabase menggunakan secrets
        url: str = st.secrets["SUPABASE_URL"]
        key: str = st.secrets["SUPABASE_KEY"]
        self.supabase: Client = create_client(url, key)
        
        # 2. Tempat menyimpan data sementara di memori Streamlit
        self.data_lembaga = {}
        self.data_master = []
        
        # 3. Muat data saat sistem pertama kali dijalankan
        self.muat_data()

    def muat_data(self):
        """Mengambil data Lembaga dan Biodata Santri dari Supabase."""
        try:
            # Ambil profil Lembaga (ambil 1 baris terakhir/terbaru)
            res_lembaga = self.supabase.table("lembaga").select("*").order("id", desc=True).limit(1).execute()
            if res_lembaga.data:
                self.data_lembaga = res_lembaga.data[0]
            
            # Ambil Biodata Santri
            res_santri = self.supabase.table("biodata_santri").select("*").execute()
            if res_santri.data:
                self.data_master = res_santri.data
                
        except Exception as e:
            st.error(f"Gagal terhubung ke Supabase: {e}")

    def get_daftar_nama(self):
        """Mengembalikan daftar nama santri untuk menu Dropdown."""
        return [santri["nama"] for santri in self.data_master]

    def simpan_lembaga(self, data):
        """Menyimpan atau memperbarui data profil Lembaga ke Supabase"""
        try:
            # Kita gunakan insert, karena di muat_data() kita selalu mengambil data terakhir (desc limit 1)
            res = self.supabase.table("lembaga").insert(data).execute()
            if res.data:
                self.data_lembaga = res.data[0] # Update data di memori
                return True, "Data Identitas Lembaga berhasil disimpan di Cloud!"
        except Exception as e:
            return False, f"Gagal menyimpan data: {e}"

    def simpan_biodata(self, no_induk, nama, data_lengkap):
        """Menyimpan biodata santri baru ke Supabase"""
        try:
            res = self.supabase.table("biodata_santri").insert({
                "no_induk": no_induk,
                "nama": nama,
                "data_lengkap": data_lengkap # Disimpan dalam format JSONB
            }).execute()
            
            if res.data:
                self.muat_data() # Refresh data di memori agar tabel langsung update
                return True, "Biodata santri berhasil ditambahkan ke Cloud!"
        except Exception as e:
            return False, f"Gagal menyimpan biodata: {e}"

    def simpan_nilai(self, data_nilai, id_nilai=None):
        """Menyimpan data baru atau mengupdate data nilai yang sudah ada di Supabase"""
        try:
            if id_nilai:
                # Jika id_nilai diberikan, lakukan UPDATE ke baris yang sudah ada
                res = self.supabase.table("nilai_santri").update(data_nilai).eq("id", id_nilai).execute()
                pesan = "Data nilai berhasil diperbarui di Cloud!"
            else:
                # Jika tidak ada id_nilai, lakukan INSERT sebagai data baru
                res = self.supabase.table("nilai_santri").insert(data_nilai).execute()
                pesan = "Data nilai baru berhasil ditambahkan ke Cloud!"
            return True, pesan
        except Exception as e:
            return False, f"Gagal menyimpan nilai: {e}"

    def get_nilai(self, santri_id, semester):
        """Mengambil data nilai santri berdasarkan ID dan Semester"""
        try:
            res = self.supabase.table("nilai_santri").select("*").eq("santri_id", santri_id).eq("semester", semester).execute()
            if res.data:
                return res.data[0]
            return None
        except Exception as e:
            st.error(f"Gagal mengambil data nilai: {e}")
            return None

    def get_ranking(self, santri_id, semester):
        """Menghitung ranking berdasarkan jumlah nilai terbesar"""
        try:
            res = self.supabase.table("nilai_santri").select("santri_id, jumlah").eq("semester", semester).execute()
            if not res.data: return "-", 0
            
            # Urutkan dari jumlah nilai terbesar ke terkecil
            data_urut = sorted(res.data, key=lambda x: x['jumlah'], reverse=True)
            
            rank = 1
            for item in data_urut:
                if item['santri_id'] == santri_id:
                    return rank, len(data_urut)
                rank += 1
            return "-", len(data_urut)
        except:
            return "-", 0

    def get_semua_nilai(self, semester):
        """Mengambil semua data nilai untuk fitur Tabel Rekap"""
        try:
            res = self.supabase.table("nilai_santri").select("*").eq("semester", semester).execute()
            return res.data if res.data else []
        except:
            return []