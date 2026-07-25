import streamlit as st
import pandas as pd
from datetime import date

def render(db):
    st.header("⚙️ Master Data & Pengaturan")
    
    if not db.lembaga_id:
        st.warning("⚠️ Anda belum memilih madrasah yang aktif. Silakan kembali ke Profil.")
        return

    st.markdown("---")
    st.subheader("👥 Manajemen Akun & Biodata Guru")
    st.write("Kelola akses login beserta kelengkapan biodata guru di madrasah Anda.")

    # 1. FORM PENAMBAHAN AKUN & BIODATA
    if getattr(db, 'role', '') == 'admin':
        with st.expander("➕ Tambah Akun Guru & Biodata KTP", expanded=False):
            with st.form("form_tambah_guru"):
                
                st.markdown("#### 🔐 1. Data Hak Akses & Login")
                col1, col2 = st.columns(2)
                with col1:
                    nama_guru = st.text_input("Nama Lengkap Guru *")
                    username = st.text_input("NIP / Username (Untuk Login) *")
                    password = st.text_input("Password Default *", value="123456", type="password")
                with col2:
                    role = st.selectbox("Hak Akses (Role) *", ["guru", "wali_kelas"])
                    kelas_binaan = st.text_input("Kelas Binaan", placeholder="Wajib jika Wali Kelas (misal: 1A)")

                st.markdown("---")
                st.markdown("#### 💳 2. Kelengkapan Biodata (Sesuai KTP)")
                col3, col4 = st.columns(2)
                with col3:
                    nik = st.text_input("NIK (Nomor Induk Kependudukan)")
                    tempat_lahir = st.text_input("Tempat Lahir")
                    tgl_lahir = st.date_input("Tanggal Lahir", value=date(1990, 1, 1))
                    jk = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
                with col4:
                    no_hp = st.text_input("Nomor HP / WhatsApp aktif")
                    alamat = st.text_area("Alamat Lengkap (Sesuai KTP)")
                
                submit_guru = st.form_submit_button("Simpan Data Guru")
                
                if submit_guru:
                    if not nama_guru or not username or not password:
                        st.error("❌ Nama, Username, dan Password pada bagian Data Login wajib diisi!")
                    elif role == "wali_kelas" and not kelas_binaan:
                        st.error("❌ Kelas Binaan wajib diisi untuk seorang Wali Kelas!")
                    else:
                        # Memasukkan semua data termasuk KTP
                        sukses, pesan = db.tambah_akun_guru(
                            nama_guru, username, password, role, kelas_binaan,
                            nik, jk, tempat_lahir, tgl_lahir, no_hp, alamat
                        )
                        if sukses:
                            st.success(pesan)
                            st.rerun()
                        else:
                            st.error(pesan)
    else:
        st.info("🔒 Hanya Admin Lembaga yang berhak menambahkan akun guru baru.")

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. TABEL DAFTAR GURU
    st.markdown("### 📋 Daftar Guru & Wali Kelas")
    daftar_guru = db.get_semua_guru_lembaga()
    
    if daftar_guru:
        df_guru = pd.DataFrame(daftar_guru)
        
        # Menampilkan kolom-kolom penting ke layar (termasuk No HP agar mudah dihubungi)
        kolom_tampil = ['nama_guru', 'username', 'role', 'kelas_binaan', 'jenis_kelamin', 'no_hp']
        kolom_ada = [col for col in kolom_tampil if col in df_guru.columns]
        
        df_display = df_guru[kolom_ada].copy()
        df_display.rename(columns={
            'nama_guru': 'Nama Lengkap',
            'username': 'Username/NIP',
            'role': 'Akses',
            'kelas_binaan': 'Wali Kelas',
            'jenis_kelamin': 'L/P',
            'no_hp': 'No. WhatsApp'
        }, inplace=True)
        
        df_display.index = df_display.index + 1 
        st.dataframe(df_display, use_container_width=True)
    else:
        st.warning("Belum ada data guru yang ditambahkan di lembaga ini.")