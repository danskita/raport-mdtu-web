import streamlit as st
import time
from database import DataEngine

import tab_lembaga
import tab_master
import tab_biodata
import tab_output
import tab_nilai
import tab_rekap
import tab_cetak

st.set_page_config(page_title="Raport MDTU", page_icon="📚", layout="wide")

if 'db' not in st.session_state:
    st.session_state.db = DataEngine()
db = st.session_state.db

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# ==========================================
# HALAMAN LOGIN & DAFTAR MADRASAH BARU
# ==========================================
if not st.session_state.logged_in:
    st.title("📚 Platform Raport Keagamaan Nasional")
    st.markdown("Sistem Informasi Penilaian Berbasis Cloud untuk TKA, TPA, dan MDTU.")
    
    tab_login, tab_register = st.tabs(["🔐 Login Sistem", "📝 Daftar Akun Baru"])
    
    with tab_login:
        st.subheader("Masuk ke Dashboard")
        with st.form("form_login"):
            email = st.text_input("Email (Lembaga / Guru)")
            password = st.text_input("Password", type="password")
            submit_login = st.form_submit_button("Masuk Aplikasi")
            
            if submit_login:
                with st.spinner("Mencocokkan kredensial..."):
                    sukses, pesan = db.login(email, password)
                    if sukses:
                        st.success(f"✅ {pesan}")
                        time.sleep(1.5) 
                        st.session_state.logged_in = True
                        st.rerun() 
                    else:
                        st.error(pesan)
                        
    with tab_register:
        st.subheader("Pendaftaran Akun Baru")
        
        tipe_akun = st.radio("Mendaftar Sebagai:", ["Lembaga/Madrasah Baru", "Guru (Gabung ke Lembaga)"], horizontal=True)
        st.markdown("---")
        
        if tipe_akun == "Lembaga/Madrasah Baru":
            st.info("Daftarkan madrasah Anda untuk mendapatkan ID Sistem.")
            with st.form("form_register_lembaga"):
                new_email = st.text_input("Email Lembaga (Bisa dipakai daftar berkali-kali jika punya banyak cabang)")
                new_pass = st.text_input("Buat Password (Minimal 6 Karakter)", type="password")
                
                # --- PENGATURAN TINGKATAN DI AWAL ---
                tingkatan = st.selectbox("Tingkatan Lembaga", ["MDTU", "TKA", "TPA", "Lainnya (Tanpa Gelar)"])
                new_nama = st.text_input("Nama Lembaga (Contoh: Al-Ikhlas)")
                new_nsm = st.text_input("Nomor Statistik Madrasah (NSM)")
                
                submit_register = st.form_submit_button("Daftarkan Madrasah")
                
                if submit_register:
                    if not new_email or not new_nama or len(new_pass) < 6:
                        st.warning("Mohon lengkapi Email, Nama Lembaga, dan Password.")
                    else:
                        with st.spinner("Mendaftarkan ke Cloud Supabase..."):
                            nama_final = f"{tingkatan} {new_nama}" if tingkatan != "Lainnya (Tanpa Gelar)" else new_nama
                            sukses, pesan = db.register_madrasah(new_email, new_pass, nama_final, new_nsm, tingkatan)
                            if sukses:
                                st.success(f"🎉 {pesan}")
                                st.balloons()
                                time.sleep(2)
                            else:
                                st.error(pesan)
                                
        else: # FORM GURU
            st.info("Pilih maksimal 3 lembaga tempat Anda mengajar dari daftar di bawah ini.")
            list_lembaga = db.get_semua_madrasah()
            
            if not list_lembaga:
                st.warning("Belum ada madrasah yang terdaftar di sistem.")
            else:
                with st.form("form_register_guru"):
                    guru_email = st.text_input("Email Pribadi Guru (Wajib)")
                    guru_pass = st.text_input("Buat Password (Minimal 6 Karakter)", type="password")
                    guru_nama = st.text_input("Nama Lengkap Guru")
                    
                    # --- BISA PILIH HINGGA 3 LEMBAGA SEKALIGUS ---
                    opsi_lembaga = {f"{m['nama_madrasah']} ({m.get('profil_lengkap',{}).get('tingkatan','')})": m['id'] for m in list_lembaga}
                    pilihan = st.multiselect("Pilih Madrasah (Maksimal 3)", list(opsi_lembaga.keys()), max_selections=3)
                    
                    submit_guru = st.form_submit_button("Daftarkan Akun Guru")
                    
                    if submit_guru:
                        if not guru_email or not guru_nama or len(pilihan) == 0 or len(guru_pass) < 6:
                            st.warning("Mohon lengkapi data dan pilih minimal 1 Madrasah.")
                        else:
                            with st.spinner("Mendaftarkan Akun Guru..."):
                                id_lembaga_terpilih = [opsi_lembaga[p] for p in pilihan]
                                sukses, pesan = db.register_guru(guru_email, guru_pass, guru_nama, id_lembaga_terpilih)
                                if sukses:
                                    st.success(f"🎉 {pesan}")
                                    st.balloons()
                                    time.sleep(2)
                                else:
                                    st.error(pesan)
    st.stop()

# ==========================================
# DASHBOARD APLIKASI UTAMA (Setelah Login)
# ==========================================

# --- FITUR PINDAH MADRASAH (SWITCH ACCOUNT) ---
if len(db.list_akses_lembaga) > 1:
    st.sidebar.markdown("### 🔄 Ganti Madrasah")
    st.sidebar.caption("Akun Anda terhubung ke beberapa madrasah. Pilih di bawah untuk berpindah:")
    
    opsi_akses = {f"{l['nama_madrasah']} - Akses: {l['_role'].upper()}": l for l in db.list_akses_lembaga}
    
    # Cari indeks madrasah yang sedang aktif
    nama_aktif_sekarang = f"{db.data_lembaga['nama_madrasah']} - Akses: {db.role.upper()}"
    idx_aktif = list(opsi_akses.keys()).index(nama_aktif_sekarang) if nama_aktif_sekarang in opsi_akses else 0
    
    madrasah_aktif = st.sidebar.selectbox("Madrasah Saat Ini:", list(opsi_akses.keys()), index=idx_aktif)
    l_terpilih = opsi_akses[madrasah_aktif]
    
    # Jika user memilih madrasah lain dari dropdown, muat ulang halaman dengan data madrasah tersebut
    if db.lembaga_id != l_terpilih['id']:
        db.set_active_lembaga(l_terpilih)
        st.rerun()
    st.sidebar.markdown("---")

col_judul, col_logout = st.columns([8, 2])
with col_judul:
    st.title(f"🏫 Dashboard: {db.data_lembaga.get('nama_madrasah', 'Madrasah Anda')}")
with col_logout:
    st.write(f"Hak Akses: **{db.role.upper()}**")
    if st.button("🚪 Keluar (Logout)", width='stretch'):
        db.logout()
        st.session_state.logged_in = False
        st.rerun()

st.markdown("---")

# Jika guru, sembunyikan pengaturan Lembaga dan Master Data
if db.role == "guru":
    t_biodata, t_induk, t_nilai, t_rekap, t_cetak = st.tabs([
        "👤 TAMBAH SANTRI", "🗃️ DATA SANTRI", "📝 INPUT NILAI", "📊 REKAP NILAI", "🖨️ CETAK RAPORT"
    ])
    with t_biodata: tab_biodata.render(db)
    with t_induk: tab_output.render(db)
    with t_nilai: tab_nilai.render(db)
    with t_rekap: tab_rekap.render(db)
    with t_cetak: tab_cetak.render(db)
else:
    # Jika Admin (Kepala Sekolah), tampilkan semuanya
    t_lembaga, t_master, t_biodata, t_induk, t_nilai, t_rekap, t_cetak = st.tabs([
        "🏛️ PROFIL LEMBAGA", "⚙️ MASTER DATA", "👤 TAMBAH SANTRI", "🗃️ DATA SANTRI", "📝 INPUT NILAI", "📊 REKAP NILAI", "🖨️ CETAK RAPORT"
    ])
    with t_lembaga: tab_lembaga.render(db)
    with t_master: tab_master.render(db)
    with t_biodata: tab_biodata.render(db)
    with t_induk: tab_output.render(db)
    with t_nilai: tab_nilai.render(db)
    with t_rekap: tab_rekap.render(db)
    with t_cetak: tab_cetak.render(db)