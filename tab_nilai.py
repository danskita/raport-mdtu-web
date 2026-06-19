import streamlit as st

def render(db):
    st.header("📝 Input Nilai Santri")
    
    if not db.data_master:
        st.warning("Belum ada data santri. Silakan isi lewat tab Input Biodata terlebih dahulu.")
        return
        
    # Buat kamus (dictionary) untuk mencari ID unik santri berdasarkan namanya
    map_santri = {s['nama']: s['id'] for s in db.data_master}
    
    col_atas1, col_atas2 = st.columns(2)
    with col_atas1:
        pilih_nama = st.selectbox("Pilih Nama Santri:", list(map_santri.keys()))
    with col_atas2:
        semester = st.radio("Pilih Semester:", [1, 2], horizontal=True, format_func=lambda x: "Ganjil" if x==1 else "Genap")

    st.markdown("---")
    
    with st.form("form_nilai"):
        col1, col2 = st.columns(2)
        
        # NILAI AKADEMIK
        with col1:
            st.subheader("1. Keagamaan")
            mapel_agama = ["AL QUR'AN", "AL HADITS", "AQIDAH", "AKHLAQ", "FIQIH", "TARIKH ISLAM", "BAHASA ARAB", "NAHWU", "SHARAF"]
            nilai_agama = {}
            for mapel in mapel_agama:
                nilai_agama[mapel] = st.number_input(mapel, min_value=0, max_value=100, value=0, step=1)
                
            st.subheader("2. Muatan Lokal")
            mapel_mulok = ["PRAKTIK IBADAH", "BTQ", "Ke-NU-an"]
            nilai_mulok = {}
            for mapel in mapel_mulok:
                nilai_mulok[mapel] = st.number_input(mapel, min_value=0, max_value=100, value=0, step=1)
        
        # NON-AKADEMIK & STATUS
        with col2:
            st.subheader("Kepribadian")
            c_p1, c_p2, c_p3 = st.columns(3)
            with c_p1: kelakuan = st.selectbox("Kelakuan", ["A", "B", "C", "D"], index=1)
            with c_p2: kerajinan = st.selectbox("Kerajinan", ["A", "B", "C", "D"], index=1)
            with c_p3: kebersihan = st.selectbox("Kebersihan", ["A", "B", "C", "D"], index=1)
            
            st.subheader("Ketidakhadiran (Hari)")
            c_a1, c_a2, c_a3 = st.columns(3)
            with c_a1: sakit = st.number_input("Sakit", min_value=0, value=0, step=1)
            with c_a2: izin = st.number_input("Izin", min_value=0, value=0, step=1)
            with c_a3: alpa = st.number_input("Alpa", min_value=0, value=0, step=1)
            
            st.subheader("Keputusan & Catatan")
            status = st.selectbox("Status Akhir", ["-", "Naik Kelas", "Tinggal di Kelas", "LULUS"])
            catatan = st.text_area("Catatan Wali Kelas")

        submitted = st.form_submit_button("🧮 Simpan Semua Nilai ke Cloud")
        
        if submitted:
            # Hitung otomatis jumlah dan rata-rata
            akademik = {**nilai_agama, **nilai_mulok}
            jumlah = sum(akademik.values())
            rata_rata = jumlah / len(akademik) if akademik else 0
            
            data_nilai = {
                "santri_id": map_santri[pilih_nama], # UUID Supabase
                "semester": semester,
                "akademik": akademik,
                "kepribadian": {"Kelakuan": kelakuan, "Kerajinan": kerajinan, "Kebersihan": kebersihan},
                "absen": {"Sakit": sakit, "Izin": izin, "Alpa": alpa},
                "jumlah": jumlah,
                "rata_rata": rata_rata,
                "catatan": catatan,
                "status": status
            }
            
            sukses, pesan = db.simpan_nilai(data_nilai)
            if sukses:
                st.success(f"{pesan} (Total: {jumlah}, Rata-rata: {rata_rata:.2f})")
            else:
                st.error(pesan)