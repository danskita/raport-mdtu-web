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

st.set_page_config(page_title="Raport MDTU", page_icon="📚", layout="wide")

# --- INISIALISASI SESSION STATE ---
if 'db' not in st.session_state:
    st.session_state.db = DataEngine()

db = st.session_state.db

# --- HALAMAN LOGIN / REGISTER (JIKA BELUM LOGIN) ---
if not db.lembaga_id:
    st.title("📚 Aplikasi Raport MDTU (Cloud Version)")
    st.markdown("Silakan masuk atau daftarkan lembaga/guru Anda untuk mengakses sistem.")
    
    menu_auth = st.radio("Pilih Aksi:", ["Masuk (Login)", "Daftar Madrasah Baru", "Daftar Akun Guru"], horizontal=True)
    st.markdown("---")
    
    if menu_auth == "Masuk (Login)":
        with st.form("form_login"):
            email = st.text_input("Alamat Email")
            password = st.text_input("Password", type="password")
            submit_login = st.form_submit_button("Masuk Sistem", type="primary")
            
            if submit_login:
                sukses, pesan = db.login(email, password)
                if sukses:
                    st.success(pesan)
                    st.rerun()
                else:
                    st.error(pesan)
                    
    elif menu_auth == "Daftar Madrasah Baru":
        with st.form("form_reg_madrasah"):
            st.subheader("Registrasi Madrasah / Lembaga Baru")
            email = st.text_input("Email Admin/Lembaga")
            password = st.text_input("Password", type="password")
            nama_madrasah = st.text_input("Nama Madrasah")
            nsm = st.text_input("NSM / Nomor Statistik")
            tingkatan = st.selectbox("Tingkatan Lembaga", ["TKA", "TPA", "MDTU", "Lainnya"])
            
            submit_reg = st.form_submit_button("Daftarkan Madrasah", type="primary")
            if submit_reg:
                if not email or not password or not nama_madrasah:
                    st.error("Semua kolom wajib diisi!")
                else:
                    sukses, pesan = db.register_madrasah(email, password, nama_madrasah, nsm, tingkatan)
                    if sukses:
                        st.success(pesan)
                    else:
                        st.error(pesan)
                        
    elif menu_auth == "Masuk sebagai Wali Kelas (via PIN)":
        with st.form("form_login_guru"):
            st.subheader("Login Wali Kelas dengan PIN Khusus")
            st.info("Masukkan Email Madrasah tempat Anda mengajar, Kelas Binaan Anda, dan PIN yang diberikan oleh Admin Madrasah.")
            
            email_lembaga = st.text_input("Email Lembaga / Madrasah")
            kelas_binaan = st.text_input("Kelas Binaan Anda (Contoh: Kelas 1)")
            pin_guru = st.text_input("PIN Khusus dari Admin", type="password")
            
            submit_login_g = st.form_submit_button("Masuk ke Kelas", type="primary")
            if submit_login_g:
                if not email_lembaga or not kelas_binaan or not pin_guru:
                    st.error("Semua kolom wajib diisi!")
                else:
                    sukses, pesan = db.login_guru_dengan_pin(email_lembaga, kelas_binaan, pin_guru)
                    if sukses:
                        st.success(pesan)
                        st.rerun()
                    else:
                        st.error(pesan)
    st.stop()

# --- HEADER UTAMA SETELAH LOGIN ---
st.sidebar.title(f"🏫 {db.data_lembaga.get('nama_madrasah', 'Madrasah')}")
st.sidebar.write(f"**Login sebagai:** {db.role.upper()} {f'({db.kelas_binaan})' if db.kelas_binaan else ''}")

# Fitur Switch Akun jika memiliki lebih dari 1 akses lembaga
if len(db.list_akses_lembaga) > 1:
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

with t_lembaga: 
    tab_lembaga.render(db)
with t_master: 
    tab_master.render(db)
with t_biodata: 
    tab_biodata.render(db)
with t_induk: 
    tab_output.render(db)
with t_absen: 
    tab_absen.render(db)
with t_nilai: 
    tab_nilai.render(db)
with t_cetak: 
    tab_cetak.render(db)