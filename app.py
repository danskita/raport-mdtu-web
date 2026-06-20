import streamlit as st
from database import DataEngine

# Impor semua modul tab
import tab_lembaga
import tab_biodata
import tab_output
import tab_nilai
import tab_rekap  # <-- MODUL REKAP DITAMBAHKAN DI SINI
import tab_cetak

# Setup halaman web
st.set_page_config(page_title="Raport MDTU", page_icon="📚", layout="wide")
st.title("📚 Aplikasi Raport MDTU (Cloud Version)")
st.markdown("---")

# Inisialisasi Database ke dalam Session State
if 'db' not in st.session_state:
    st.session_state.db = DataEngine()
db = st.session_state.db

# MEMBUAT MENU TAB (Sekarang ada 6 Tab termasuk Rekap Nilai)
t_lembaga, t_biodata, t_induk, t_nilai, t_rekap, t_cetak = st.tabs([
    "🏛️ LEMBAGA", "👤 INPUT BIODATA", "🗃️ DATA INDUK", "📝 INPUT NILAI", "📊 REKAP NILAI", "🖨️ CETAK RAPORT"
])

# Memanggil isi masing-masing tab
with t_lembaga: tab_lembaga.render(db)
with t_biodata: tab_biodata.render(db)
with t_induk: tab_output.render(db)
with t_nilai: tab_nilai.render(db)
with t_rekap: tab_rekap.render(db) # <-- RENDER TAB REKAP 
with t_cetak: tab_cetak.render(db)