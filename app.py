import streamlit as st
from database import DataEngine

# Import semua modul tab yang sudah kita buat
import tab_master
import tab_profil_guru
import tab_biodata
import tab_absen
import tab_nilai
import tab_data
import tab_cetak

# Konfigurasi Halaman Web
st.set_page_config(page_title="e-Raport Madrasah", page_icon="📚", layout="wide")

def main():
    # 1. Inisialisasi Database di Memori (Session State)
    if 'db' not in st.session_state:
        st.session_state.db = DataEngine()
    
    db = st.session_state.db

    # 2. SISTEM LOGIN
    if not db.lembaga_id:
        st.title("🔐 Login Sistem e-Raport Madrasah")
        st.write("Silakan masuk menggunakan akun yang telah terdaftar.")
        
        with st.form("form_login"):
            identitas = st.text_input("Email (Kepala Madrasah) / Username NIP (Guru)")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                sukses, pesan = db.login(identitas, password)
                if sukses:
                    st.success(pesan)
                    st.rerun()
                else:
                    st.error(pesan)
    
    # 3. JIKA SUDAH LOGIN -> TAMPILKAN MENU SESUAI SOP (HAK AKSES)
    else:
        # Menampilkan Identitas di Sidebar Kiri
        nama_lembaga = db.data_lembaga.get('nama_madrasah', 'Madrasah')
        nama_pengguna = db.data_lembaga.get('_nama_guru') or db.data_lembaga.get('email', 'Admin')
        
        st.sidebar.title(f"🏫 {nama_lembaga}")
        st.sidebar.write(f"👤 **{nama_pengguna}**")
        
        if db.role == 'kepala_madrasah':
            st.sidebar.caption("👔 Role: Kepala Madrasah")
            menu_options = ["Pemantauan & Rekap", "Master Data", "Profil Guru"]
        else:
            kelas = db.kelas_binaan if db.kelas_binaan else "Belum Atur Kelas"
            st.sidebar.caption(f"👨‍🏫 Role: Wali Kelas ({kelas})")
            menu_options = ["Profil Guru", "Input Biodata", "Input Absensi", "Input Nilai", "Cetak Raport", "Pemantauan & Rekap"]
            
        st.sidebar.markdown("---")
        
        # Navigasi Menu
        pilihan = st.sidebar.radio("Navigasi Menu", menu_options)
        
        st.sidebar.markdown("---")
        if st.sidebar.button("🚪 Logout / Keluar"):
            db.logout()
            st.rerun()

        # Routing ke file masing-masing (Sesuai Tab yang diklik)
        if pilihan == "Master Data":
            tab_master.render(db)
        elif pilihan == "Profil Guru":
            tab_profil_guru.render(db)
        elif pilihan == "Pemantauan & Rekap":
            tab_data.render(db)
        elif pilihan == "Input Biodata":
            # Pastikan Anda memiliki file tab_biodata.py
            try: tab_biodata.render(db)
            except Exception as e: st.error(f"File tab_biodata.py bermasalah: {e}")
        elif pilihan == "Input Absensi":
            # Pastikan Anda memiliki file tab_absen.py
            try: tab_absen.render(db)
            except Exception as e: st.error(f"File tab_absen.py bermasalah: {e}")
        elif pilihan == "Input Nilai":
            tab_nilai.render(db)
        elif pilihan == "Cetak Raport":
            tab_cetak.render(db)

if __name__ == "__main__":
    main()