import streamlit as st
import pandas as pd
from database import DataEngine
import tab_lembaga
import tab_master
import tab_biodata
import tab_output
import tab_absen
import tab_nilai
import tab_cetak

# Pengaturan dasar halaman Streamlit
st.set_page_config(page_title="Raport MDTU", page_icon="📚", layout="wide")

# --- INISIALISASI SESSION STATE ---
if 'db' not in st.session_state:
    st.session_state.db = DataEngine()
db = st.session_state.db

# --- HALAMAN AWAL (LOGIN & REGISTER LEMBAGA) ---
if not db.lembaga_id:
    st.title("📚 Aplikasi Raport MDTU (Cloud Version)")
    st.markdown("Silakan masuk ke akun Anda atau daftarkan lembaga baru untuk menggunakan sistem.")
    
    # Membuat Tab untuk memisahkan Login dan Pendaftaran Madrasah
    tab_login, tab_daftar = st.tabs(["🔑 Masuk (Login)", "📝 Daftar Lembaga Baru"])
    
    # 1. TAB LOGIN (Untuk Admin dan Guru)
    with tab_login:
        st.subheader("Masuk ke Sistem")
        with st.form("form_login"):
            # Kotak input bisa diisi Email (untuk admin) atau NIP/Username (untuk guru)
            username = st.text_input("Email (Admin) / NIP atau Username (Guru)")
            password = st.text_input("Password / PIN", type="password")
            submit_login = st.form_submit_button("Masuk")
            
            if submit_login:
                sukses, pesan = db.login(username, password)
                if sukses:
                    st.success(pesan)
                    st.rerun()
                else:
                    st.error(pesan)
                    
    # 2. TAB DAFTAR (Hanya untuk Lembaga/Madrasah Baru)
    with tab_daftar:
        st.subheader("Pendaftaran Madrasah Baru")
        st.info("Form ini KHUSUS untuk pendaftaran Lembaga/Madrasah. Akun Guru/Wali Kelas akan dibuatkan oleh Admin Lembaga setelah login.")
        with st.form("form_register_madrasah"):
            nama_madrasah = st.text_input("Nama Madrasah *")
            nsm = st.text_input("Nomor Statistik Madrasah (NSM) *")
            tingkatan = st.selectbox("Tingkatan *", ["MDTU", "MDTA", "MDTw", "MDta"])
            
            st.markdown("**Kredensial Login Admin Lembaga:**")
            email = st.text_input("Email Lembaga *")
            password_reg = st.text_input("Password *", type="password")
            
            submit_register = st.form_submit_button("Daftarkan Madrasah")
            
            if submit_register:
                if not email or not password_reg or not nama_madrasah:
                    st.error("Nama Madrasah, Email, dan Password wajib diisi!")
                else:
                    # Memanggil fungsi register_madrasah dari database.py
                    sukses, pesan = db.register_madrasah(email, password_reg, nama_madrasah, nsm, tingkatan)
                    if sukses:
                        st.success(pesan)
                    else:
                        st.error(pesan)
                        
    st.stop() # Hentikan eksekusi kode di bawah jika belum login

# --- HEADER UTAMA SETELAH LOGIN ---
st.sidebar.title(f"🏫 {db.data_lembaga.get('nama_madrasah', 'Madrasah')}")
st.sidebar.write(f"👤 Login sebagai: **{db.role.upper()}** {f'({db.kelas_binaan})' if getattr(db, 'kelas_binaan', None) else ''}")

# Fitur Switch Akun jika memiliki lebih dari 1 akses lembaga
if hasattr(db, 'list_akses_lembaga') and len(db.list_akses_lembaga) > 1:
    st.sidebar.markdown("---")
    st.sidebar.subheader("🔄 Ganti Madrasah")
    pilihan_lembaga = {l['nama_madrasah']: l for l in db.list_akses_lembaga}
    pilih_aktif = st.sidebar.selectbox("Pilih Lembaga Aktif", list(pilihan_lembaga.keys()))
    if pilihan_lembaga[pilih_aktif]['id'] != db.lembaga_id:
        db.set_active_lembaga(pilihan_lembaga[pilih_aktif])
        st.rerun()

st.sidebar.markdown("---")
if st.sidebar.button("🚪 Keluar (Logout)", use_container_width=True):
    db.logout()
    st.rerun()

st.title("📚 Aplikasi Raport MDTU (Cloud Version)")
st.markdown("---")

# --- NAVIGASI TAB UTAMA ---
t_lembaga, t_master, t_biodata, t_induk, t_absen, t_nilai, t_cetak = st.tabs([
    "🏛️ PROFIL", "⚙️ MASTER", "👤 BIODATA", "🗃️ INDUK", "📅 ABSENSI", "📝 NILAI", "🖨️ CETAK"
])

with t_lembaga: tab_lembaga.render(db)
with t_master: tab_master.render(db)
with t_biodata: tab_biodata.render(db)
with t_induk: tab_output.render(db)
with t_absen: tab_absen.render(db)
with t_nilai: tab_nilai.render(db)
with t_cetak: tab_cetak.render(db)