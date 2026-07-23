import streamlit as st
import pandas as pd

def render(db):
    st.header("⚙️ Master Data & Pengaturan")
    
    # Memastikan pengguna sudah login dan memiliki akses lembaga
    if not db.lembaga_id:
        st.warning("⚠️ Anda belum memilih madrasah yang aktif. Silakan kembali ke Profil.")
        return

    st.markdown("---")
    st.subheader("👥 Manajemen Akun Guru & Wali Kelas")
    st.write("Kelola akses login untuk guru dan wali kelas di madrasah Anda.")

    # 1. FORM PENAMBAHAN AKUN (Hanya ditampilkan untuk role Admin Lembaga)
    if getattr(db, 'role', '') == 'admin':
        with st.expander("➕ Tambah Akun Guru Baru", expanded=False):
            with st.form("form_tambah_guru"):
                st.info("Akun yang dibuat akan langsung terhubung dengan madrasah ini.")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    nama_guru = st.text_input("Nama Lengkap Guru *")
                    username = st.text_input("NIP / Username (Untuk Login) *")
                    password = st.text_input("Password Default *", value="123456", type="password")
                
                with col2:
                    role = st.selectbox("Hak Akses (Role) *", ["guru", "wali_kelas"])
                    kelas_binaan = st.text_input("Kelas Binaan", placeholder="Wajib diisi jika role Wali Kelas (misal: 1A)")
                
                submit_guru = st.form_submit_button("Simpan Akun")
                
                if submit_guru:
                    if not nama_guru or not username or not password:
                        st.error("❌ Nama, Username, dan Password wajib diisi!")
                    elif role == "wali_kelas" and not kelas_binaan:
                        st.error("❌ Kelas Binaan wajib diisi untuk seorang Wali Kelas!")
                    else:
                        # Memanggil fungsi ke database.py
                        sukses = db.tambah_akun_guru(nama_guru, username, password, role, kelas_binaan)
                        if sukses:
                            st.success(f"✅ Berhasil! Akun untuk {nama_guru} telah ditambahkan.")
                            st.rerun()
                        else:
                            st.error("❌ Gagal menambahkan data. Pastikan Username/NIP belum digunakan oleh orang lain.")
    else:
        st.info("🔒 Hanya Admin Lembaga yang berhak menambahkan akun guru baru.")

    st.markdown("<br>", unsafe_allow_html=True)

    # 2. TABEL DAFTAR GURU DI LEMBAGA
    st.markdown("### 📋 Daftar Guru yang Terdaftar")
    
    # Menarik data guru berdasarkan lembaga_id aktif
    daftar_guru = db.get_semua_guru_lembaga()
    
    if daftar_guru:
        df_guru = pd.DataFrame(daftar_guru)
        
        # Merapikan tampilan tabel agar mudah dibaca
        kolom_tampil = ['nama_guru', 'username', 'role', 'kelas_binaan']
        kolom_ada = [col for col in kolom_tampil if col in df_guru.columns]
        
        df_display = df_guru[kolom_ada].copy()
        
        # Mengubah nama kolom agar lebih user-friendly di layar
        df_display.rename(columns={
            'nama_guru': 'Nama Lengkap',
            'username': 'Username / NIP',
            'role': 'Hak Akses',
            'kelas_binaan': 'Wali Kelas'
        }, inplace=True)
        
        df_display.index = df_display.index + 1 
        st.dataframe(df_display, use_container_width=True)
    else:
        st.warning("Belum ada data guru yang ditambahkan di lembaga ini.")