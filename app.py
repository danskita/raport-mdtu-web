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
        
        # OPSI PENDAFTARAN DINAMIS
        tipe_akun = st.radio("Mendaftar Sebagai:", ["Lembaga/Madrasah Baru", "Guru (Gabung ke Lembaga)"], horizontal=True)
        st.markdown("---")
        
        if tipe_akun == "Lembaga/Madrasah Baru":
            st.info("Daftarkan madrasah Anda untuk mendapatkan ID Sistem.")
            with st.form("form_register_lembaga"):
                new_email = st.text_input("Email Lembaga (Wajib)")
                new_pass = st.text_input("Buat Password (Minimal 6 Karakter)", type="password")
                
                # Dropdown Tingkatan Lembaga
                tingkatan = st.selectbox("Tingkatan Lembaga", ["MDTU", "TKA", "TPA", "Lainnya (Tanpa Gelar)"])
                new_nama = st.text_input("Nama Lembaga (Contoh: Al-Ikhlas)")
                new_nsm = st.text_input("Nomor Statistik Madrasah (NSM)")
                
                submit_register = st.form_submit_button("Daftarkan Madrasah")
                
                if submit_register:
                    if not new_email or not new_nama or len(new_pass) < 6:
                        st.warning("Mohon lengkapi Email, Nama Lembaga, dan Password minimal 6 karakter.")
                    else:
                        with st.spinner("Mendaftarkan ke Cloud Supabase..."):
                            # Menggabungkan tingkatan dengan nama (Contoh: "MDTU Al-Ikhlas")
                            nama_final = f"{tingkatan} {new_nama}" if tingkatan != "Lainnya (Tanpa Gelar)" else new_nama
                            
                            sukses, pesan = db.register_madrasah(new_email, new_pass, nama_final, new_nsm)
                            if sukses:
                                st.success(f"🎉 {pesan}")
                                st.balloons()
                                time.sleep(2)
                            else:
                                st.error(pesan)
                                
        else: # FORM GURU
            st.info("Pilih lembaga tempat Anda mengajar dari daftar di bawah ini.")
            list_lembaga = db.get_semua_madrasah()
            
            if not list_lembaga:
                st.warning("Belum ada madrasah yang terdaftar di sistem. Silakan minta Kepala Madrasah untuk mendaftar lebih dulu.")
            else:
                with st.form("form_register_guru"):
                    guru_email = st.text_input("Email Pribadi Guru (Wajib)")
                    guru_pass = st.text_input("Buat Password (Minimal 6 Karakter)", type="password")
                    guru_nama = st.text_input("Nama Lengkap Guru")
                    
                    # Dropdown Pilih Lembaga (Dinamis dari Database)
                    opsi_lembaga = {m['nama_madrasah']: m['id'] for m in list_lembaga}
                    pilihan = st.selectbox("Pilih Madrasah Anda", list(opsi_lembaga.keys()))
                    id_lembaga_terpilih = opsi_lembaga[pilihan]
                    
                    submit_guru = st.form_submit_button("Daftarkan Akun Guru")
                    
                    if submit_guru:
                        if not guru_email or not guru_nama or len(guru_pass) < 6:
                            st.warning("Mohon lengkapi Email, Nama, dan Password minimal 6 karakter.")
                        else:
                            with st.spinner("Mendaftarkan Akun Guru..."):
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