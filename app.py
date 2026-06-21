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

if 'db' not in st.session_state: st.session_state.db = DataEngine()
db = st.session_state.db
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("📚 Platform Raport Keagamaan Nasional")
    tab_login, tab_register = st.tabs(["🔐 Login Sistem", "📝 Daftar Akun Baru"])
    
    with tab_login:
        with st.form("form_login"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            if st.form_submit_button("Masuk Aplikasi"):
                with st.spinner("Mencocokkan kredensial..."):
                    sukses, pesan = db.login(email, password)
                    if sukses:
                        st.success(f"✅ {pesan}")
                        time.sleep(1) 
                        st.session_state.logged_in = True
                        st.rerun() 
                    else: st.error(pesan)
                        
    with tab_register:
        tipe_akun = st.radio("Mendaftar Sebagai:", ["Lembaga (Kepala Sekolah/Admin)", "Wali Kelas (Guru)"], horizontal=True)
        st.markdown("---")
        
        if tipe_akun == "Lembaga (Kepala Sekolah/Admin)":
            with st.form("form_register_lembaga"):
                new_email = st.text_input("Email Lembaga")
                new_pass = st.text_input("Buat Password", type="password")
                tingkatan = st.selectbox("Tingkatan Lembaga", ["MDTU", "TKA", "TPA", "Lainnya"])
                new_nama = st.text_input("Nama Lembaga (Contoh: Al-Ikhlas)")
                new_nsm = st.text_input("Nomor Statistik (NSM)")
                if st.form_submit_button("Daftarkan Madrasah"):
                    if not new_email or not new_nama or len(new_pass) < 6: st.warning("Mohon lengkapi form!")
                    else:
                        nama_final = f"{tingkatan} {new_nama}" if tingkatan != "Lainnya" else new_nama
                        sukses, pesan = db.register_madrasah(new_email, new_pass, nama_final, new_nsm, tingkatan)
                        if sukses:
                            st.success(pesan); st.balloons(); time.sleep(2)
                        else: st.error(pesan)
        else:
            list_lembaga = db.get_semua_madrasah()
            if not list_lembaga: st.warning("Belum ada madrasah terdaftar.")
            else:
                # Opsi Pilih Lembaga (Di luar form agar dropdown kelas bisa dinamis)
                opsi_lembaga = {f"{m['nama_madrasah']} ({m.get('profil_lengkap',{}).get('tingkatan','')})": m for m in list_lembaga}
                pilihan_nama = st.selectbox("1. Pilih Madrasah Tempat Anda Mengajar", list(opsi_lembaga.keys()))
                lembaga_terpilih = opsi_lembaga[pilihan_nama]
                
                # Baca pengaturan kelas dari lembaga terpilih
                list_kelas = lembaga_terpilih.get("pengaturan_master", {}).get("kelas", ["Kelas belum diatur"])
                kelas_binaan = st.selectbox("2. Pilih Kelas Binaan Anda", list_kelas)
                
                with st.form("form_register_guru"):
                    guru_email = st.text_input("Email Pribadi (Wajib)")
                    guru_pass = st.text_input("Buat Password", type="password")
                    guru_nama = st.text_input("Nama Lengkap")
                    
                    if st.form_submit_button("Daftarkan Akun Wali Kelas"):
                        if not guru_email or not guru_nama or len(guru_pass) < 6: st.warning("Lengkapi data!")
                        else:
                            with st.spinner("Mendaftarkan..."):
                                sukses, pesan = db.register_guru(guru_email, guru_pass, guru_nama, lembaga_terpilih['id'], kelas_binaan)
                                if sukses:
                                    st.success(pesan); st.balloons(); time.sleep(2)
                                else: st.error(pesan)
    st.stop()

# ================= DASHBOARD UTAMA =================
if len(db.list_akses_lembaga) > 1:
    st.sidebar.markdown("### 🔄 Ganti Akses")
    opsi_akses = {f"{l['nama_madrasah']} ({l['_role'].upper()})" : l for l in db.list_akses_lembaga}
    nama_aktif_sekarang = f"{db.data_lembaga['nama_madrasah']} ({db.role.upper()})"
    idx_aktif = list(opsi_akses.keys()).index(nama_aktif_sekarang) if nama_aktif_sekarang in opsi_akses else 0
    madrasah_aktif = st.sidebar.selectbox("Beralih Akun:", list(opsi_akses.keys()), index=idx_aktif)
    if db.lembaga_id != opsi_akses[madrasah_aktif]['id']:
        db.set_active_lembaga(opsi_akses[madrasah_aktif])
        st.rerun()

info_hak_akses = f"**{db.role.upper()}**"
if db.role == "guru": info_hak_akses += f" (Wali {db.kelas_binaan})"

col_judul, col_logout = st.columns([8, 2])
with col_judul: st.title(f"🏫 Dashboard: {db.data_lembaga.get('nama_madrasah', 'Madrasah Anda')}")
with col_logout:
    st.write(f"Akses: {info_hak_akses}")
    if st.button("🚪 Keluar", width='stretch'):
        db.logout(); st.session_state.logged_in = False; st.rerun()
st.markdown("---")

if db.role == "guru":
    t_biodata, t_induk, t_nilai, t_rekap, t_cetak = st.tabs(["👤 TAMBAH SANTRI", "🗃️ DATA SANTRI", "📝 INPUT NILAI", "📊 REKAP NILAI", "🖨️ CETAK RAPORT"])
    with t_biodata: tab_biodata.render(db)
    with t_induk: tab_output.render(db)
    with t_nilai: tab_nilai.render(db)
    with t_rekap: tab_rekap.render(db)
    with t_cetak: tab_cetak.render(db)
else:
    t_lembaga, t_master, t_biodata, t_induk, t_nilai, t_rekap, t_cetak = st.tabs(["🏛️ LEMBAGA", "⚙️ MASTER DATA", "👤 TAMBAH SANTRI", "🗃️ DATA SANTRI", "📝 INPUT NILAI", "📊 REKAP NILAI", "🖨️ CETAK RAPORT"])
    with t_lembaga: tab_lembaga.render(db)
    with t_master: tab_master.render(db)
    with t_biodata: tab_biodata.render(db)
    with t_induk: tab_output.render(db)
    with t_nilai: tab_nilai.render(db)
    with t_rekap: tab_rekap.render(db)
    with t_cetak: tab_cetak.render(db)