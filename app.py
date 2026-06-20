import streamlit as st
import time
from database import DataEngine

# Import semua tab modul
import tab_lembaga
import tab_biodata
import tab_output
import tab_nilai
import tab_rekap
import tab_cetak

st.set_page_config(page_title="Raport MDTU", page_icon="📚", layout="wide")

# 1. Inisialisasi Database
if 'db' not in st.session_state:
    st.session_state.db = DataEngine()
db = st.session_state.db

# 2. Inisialisasi Status Login
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# ==========================================
# HALAMAN LOGIN & DAFTAR MADRASAH BARU
# ==========================================
if not st.session_state.logged_in:
    st.title("📚 Platform Raport MDTU Nasional")
    st.markdown("Sistem Informasi Penilaian Madrasah Diniyah Takmiliyah Ula Berbasis Cloud.")
    
    # Membuat Tab untuk Login dan Register
    tab_login, tab_register = st.tabs(["🔐 Login Madrasah", "📝 Daftar Madrasah Baru"])
    
    with tab_login:
        st.subheader("Masuk ke Dashboard")
        with st.form("form_login"):
            email = st.text_input("Email Resmi Madrasah")
            password = st.text_input("Password", type="password")
            submit_login = st.form_submit_button("Masuk Aplikasi")
            
            if submit_login:
                with st.spinner("Mencocokkan kredensial..."):
                    sukses, pesan = db.login(email, password)
                    if sukses:
                        # Menampilkan pesan sukses
                        st.success("✅ Login Berhasil! Memuat dasbor madrasah Anda...")
                        # Menahan layar selama 1.5 detik agar pesan bisa dibaca
                        time.sleep(1.5) 
                        
                        st.session_state.logged_in = True
                        st.rerun() # Pindah ke Dashboard Utama
                    else:
                        st.error(pesan)
                        
    with tab_register:
        st.subheader("Pendaftaran Akun Lembaga Baru")
        st.info("Satu email digunakan untuk menampung seluruh guru & kelas di satu madrasah.")
        with st.form("form_register"):
            new_email = st.text_input("Email Lembaga (Wajib)")
            new_pass = st.text_input("Buat Password (Minimal 6 Karakter)", type="password")
            new_nama = st.text_input("Nama Madrasah")
            new_nsm = st.text_input("Nomor Statistik Madrasah (NSM)")
            submit_register = st.form_submit_button("Daftarkan Madrasah")
            
            if submit_register:
                if not new_email or not new_nama or len(new_pass) < 6:
                    st.warning("Mohon lengkapi Email, Nama Madrasah, dan Password minimal 6 huruf/angka.")
                else:
                    with st.spinner("Mendaftarkan ke Cloud Supabase..."):
                        sukses, pesan = db.register_madrasah(new_email, new_pass, new_nama, new_nsm)
                        if sukses:
                            # Menampilkan pesan sukses dan animasi
                            st.success(f"🎉 {pesan}")
                            st.balloons()
                            # Menahan layar selama 2 detik agar balon selesai terbang
                            time.sleep(2) 
                        else:
                            st.error(pesan)
    st.stop() # Hentikan kode agar menu utama tidak muncul

# ==========================================
# DASHBOARD APLIKASI UTAMA (Setelah Login)
# ==========================================
col_judul, col_logout = st.columns([8, 2])
with col_judul:
    st.title(f"🏫 Dashboard: {db.data_lembaga.get('nama_madrasah', 'Madrasah Anda')}")
with col_logout:
    st.write(f"📧 **{db.data_lembaga.get('email', '')}**")
    if st.button("🚪 Keluar (Logout)", width='stretch'):
        db.logout()
        st.session_state.logged_in = False
        st.rerun()

st.markdown("---")

t_lembaga, t_biodata, t_induk, t_nilai, t_rekap, t_cetak = st.tabs([
    "🏛️ PROFIL LEMBAGA", "👤 TAMBAH SANTRI", "🗃️ DATA SANTRI", "📝 INPUT NILAI", "📊 REKAP NILAI", "🖨️ CETAK RAPORT"
])

with t_lembaga: tab_lembaga.render(db)
with t_biodata: tab_biodata.render(db)
with t_induk: tab_output.render(db)
with t_nilai: tab_nilai.render(db)
with t_rekap: tab_rekap.render(db)
with t_cetak: tab_cetak.render(db)