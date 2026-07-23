import streamlit as st
import pandas as pd

def render(db):
    st.header("⚙️ Master Data & Pengaturan")
    
    if not db.lembaga_id:
        st.warning("⚠️ Anda belum login atau belum memilih lembaga aktif.")
        return

    st.markdown("---")
    st.subheader("👥 Manajemen Akun Guru & Wali Kelas")
    
    # 1. FORM PENAMBAHAN AKUN (Hanya untuk Admin)
    if getattr(db, 'role', '') == 'admin':
        with st.expander("➕ Tambah Akun Guru Baru", expanded=False):
            with st.form("form_tambah_guru"):
                st.info("Akun ini akan langsung terikat dengan madrasah yang sedang aktif.")
                col1, col2 = st.columns(2)
                
                with col1:
                    nama_guru = st.text_input("Nama Lengkap Guru *")
                    username = st.text_input("NIP / Username (Untuk Login) *")
                    password = st.text_input("Password Default *", value="123456", type="password")
                
                with col2:
                    role = st.selectbox("Hak Akses (Role) *", ["guru", "wali_kelas", "admin"])
                    kelas_binaan = st.text_input("Kelas Binaan", placeholder="Isi jika role Wali Kelas (misal: 1A)")
                
                submit_guru = st.form_submit_button("Simpan Akun")
                
                if submit_guru:
                    if not nama_guru or not username or not password:
                        st.error("Nama, Username, dan Password wajib diisi!")
                    else:
                        # Fungsi tambah akun ke database (ditambahkan di database.py)
                        sukses = db.tambah_akun_guru(nama_guru, username, password, role, kelas_binaan)
                        if sukses:
                            st.success(f"Berhasil! Akun {nama_guru} telah ditambahkan.")
                            st.rerun()
                        else:
                            st.error("Gagal menambahkan data. Pastikan Username/NIP belum digunakan.")
    else:
        st.info("Hanya Admin yang dapat menambahkan akun guru baru.")

    # 2. MENAMPILKAN DAFTAR GURU DI LEMBAGA
    st.markdown("### 📋 Daftar Guru di Madrasah Ini")
    daftar_guru = db.get_semua_guru_lembaga()
    
    if daftar_guru:
        df_guru = pd.DataFrame(daftar_guru)
        
        # Rapikan kolom sebelum ditampilkan
        kolom_tampil = ['nama_guru', 'username', 'role', 'kelas_binaan']
        # Filter hanya kolom yang ada di dataframe untuk mencegah error
        kolom_ada = [col for col in kolom_tampil if col in df_guru.columns]
        
        df_display = df_guru[kolom_ada].copy()
        df_display.index = df_display.index + 1 # Ubah index mulai dari 1
        st.dataframe(df_display, use_container_width=True)
    else:
        st.warning("Belum ada data guru di lembaga ini.")