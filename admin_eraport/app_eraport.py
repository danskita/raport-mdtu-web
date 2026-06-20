import streamlit as st
import pandas as pd
from supabase import create_client, Client

# --- PENGATURAN HALAMAN ---
st.set_page_config(page_title="Super Admin - eRaport", page_icon="👁️", layout="wide")

# --- INISIALISASI SUPABASE ---
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

# --- SISTEM LOGIN SUPER ADMIN ---
if 'admin_logged_in' not in st.session_state:
    st.session_state.admin_logged_in = False

if not st.session_state.admin_logged_in:
    st.title("🔐 Login Super Admin e-Raport")
    st.markdown("Dasbor khusus pemantauan dan persetujuan akun madrasah.")
    
    with st.form("form_login_admin"):
        pin = st.text_input("Masukkan PIN Rahasia", type="password")
        submit = st.form_submit_button("Masuk Dasbor")
        
        if submit:
            # GANTI "123456" DENGAN PIN RAHASIA YANG ANDA INGINKAN!
            if pin == "123456": 
                st.session_state.admin_logged_in = True
                st.rerun()
            else:
                st.error("❌ PIN Salah! Akses ditolak.")
    st.stop() # Hentikan eksekusi kode di bawah jika belum login

# --- HEADER DASBOR UTAMA ---
col_judul, col_logout = st.columns([8, 2])
with col_judul:
    st.title("👁️ Menara Pengawas e-Raport MDTU")
with col_logout:
    if st.button("🚪 Keluar", width='stretch'):
        st.session_state.admin_logged_in = False
        st.rerun()

st.markdown("---")

# --- TARIK DATA DARI SUPABASE ---
# Kita tarik semua data lembaga dari database
try:
    response = supabase.table("lembaga").select("*").execute()
    data_lembaga = response.data if response.data else []
except Exception as e:
    st.error(f"Gagal mengambil data dari Supabase: {e}")
    data_lembaga = []

# --- MEMBUAT TAB MENU ---
tab_verifikasi, tab_statistik, tab_manajemen = st.tabs([
    "🚦 Antrean Verifikasi", "📊 Statistik Global", "🏢 Manajemen Akun"
])

# 1. TAB ANTREAN VERIFIKASI
with tab_verifikasi:
    st.subheader("Madrasah Menunggu Persetujuan")
    st.info("Madrasah di bawah ini sudah mendaftar, tetapi belum bisa login sebelum Anda klik 'Setujui'.")
    
    # Filter hanya madrasah yang is_active-nya masih False atau belum ada (None)
    belum_aktif = [d for d in data_lembaga if not d.get("is_active", False)]
    
    if not belum_aktif:
        st.success("🎉 Tidak ada antrean! Semua madrasah yang terdaftar sudah aktif.")
    else:
        for m in belum_aktif:
            with st.container():
                c1, c2 = st.columns([4, 1])
                with c1:
                    st.markdown(f"**🏫 {m.get('nama_madrasah', 'Tanpa Nama')}** (NSM: {m.get('nsm', '-')})")
                    st.write(f"📧 Email Pendaftar: `{m.get('email', '-')}`")
                with c2:
                    # Tombol Setujui
                    if st.button(f"✅ Setujui Madrasah", key=f"btn_{m['id']}", type="primary"):
                        try:
                            # Update status is_active menjadi True di database
                            supabase.table("lembaga").update({"is_active": True}).eq("id", m['id']).execute()
                            st.success(f"{m['nama_madrasah']} berhasil disetujui!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Gagal menyetujui: {e}")
                st.divider()

# 2. TAB STATISTIK GLOBAL
with tab_verifikasi:
    pass # Pindah scope

with tab_statistik:
    st.subheader("Statistik Nasional Platform")
    
    total_madrasah = len(data_lembaga)
    aktif = len([d for d in data_lembaga if d.get("is_active", False)])
    non_aktif = total_madrasah - aktif
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Pendaftar", total_madrasah)
    c2.metric("Madrasah Aktif", aktif)
    c3.metric("Antrean Verifikasi", non_aktif)

# 3. TAB MANAJEMEN AKUN
with tab_manajemen:
    st.subheader("Semua Akun Madrasah")
    if data_lembaga:
        # Ubah ke dataframe Pandas agar mudah dibaca di tabel
        df = pd.DataFrame(data_lembaga)
        
        # Susun ulang dan ganti nama kolom untuk tampilan
        kolom_tampil = ['nama_madrasah', 'email', 'nsm', 'is_active', 'kabupaten_kota', 'provinsi']
        # Pastikan kolom ada sebelum difilter
        kolom_tersedia = [k for k in kolom_tampil if k in df.columns]
        
        df_tampil = df[kolom_tersedia]
        
        # Tampilkan tabel data
        st.dataframe(df_tampil, width='stretch', hide_index=True)
    else:
        st.write("Belum ada data madrasah di database.")