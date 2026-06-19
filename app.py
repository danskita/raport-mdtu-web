import streamlit as st
from database import DataEngine

import tab_lembaga
import tab_biodata
import tab_output
import tab_nilai
import tab_cetak

st.set_page_config(page_title="Raport MDTU", page_icon="📚", layout="wide")
st.title("📚 Aplikasi Raport MDTU (Cloud Version)")
st.markdown("---")

if 'db' not in st.session_state:
    st.session_state.db = DataEngine()
db = st.session_state.db

t_lembaga, t_biodata, t_induk, t_nilai, t_cetak = st.tabs([
    "🏛️ LEMBAGA", "👤 INPUT BIODATA", "🗃️ DATA INDUK", "📝 INPUT NILAI", "🖨️ CETAK RAPORT"
])

with t_lembaga: tab_lembaga.render(db)
with t_biodata: tab_biodata.render(db)
with t_induk: tab_output.render(db)
with t_nilai: tab_nilai.render(db)
with t_cetak: tab_cetak.render(db)