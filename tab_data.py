import streamlit as st
import pandas as pd
from pdf_generator import PDFGenerator

def render(db):
    st.header("📊 Pemantauan & Rekap Data Madrasah")
    
    if not db.data_master:
        st.warning("Belum ada data santri yang terdaftar di sistem.")
        return

    is_kepala = getattr(db, 'role', '') == 'kepala_madrasah'
    gen = PDFGenerator(db)
    
    if is_kepala:
        st.success("👨‍💼 **Mode Kepala Madrasah:** Anda dapat memantau dan mencetak rekap data seluruh kelas.")
    else:
        st.info(f"👨‍🏫 **Mode Wali Kelas:** Menampilkan rekap data khusus untuk kelas {db.kelas_binaan}.")
        
    tab_santri, tab_nilai = st.tabs(["👥 Rekap Biodata Santri", "📈 Rekap Nilai & Status Akhir"])
    
    # ========================================
    # TAB 1: REKAPITULASI DATA SANTRI
    # ========================================
    with tab_santri:
        st.subheader("Daftar Induk Santri")
        
        # Pilihan Kelas untuk Cetak Rekap Santri
        semua_kelas = list(set([s.get("data_lengkap", {}).get("kelas_santri", "Umum") for s in db.data_master]))
        pilih_kelas_rs = st.selectbox("Pilih Kelas untuk Cetak Rekap Biodata:", semua_kelas, key="sel_k_santri")
        
        if st.button("🖨️ Cetak PDF Rekap Data Santri (F4)"):
            with st.spinner("Membuat dokumen PDF..."):
                pdf_buf = gen.cetak_rekap_santri(pilih_kelas_rs)
                st.download_button(
                    label="⬇️ Download PDF Rekap Santri",
                    data=pdf_buf,
                    file_name=f"Rekap_Data_Santri_Kelas_{pilih_kelas_rs}.pdf",
                    mime="application/pdf"
                )
                st.success("✅ Dokumen PDF Rekap Santri berhasil dibuat!")

        st.markdown("---")
        df_list = []
        for row in db.data_master:
            flat_row = {
                "No. Induk": row.get("no_induk", "-"), 
                "Nama Santri": row.get("nama", "-")
            }
            if row.get("data_lengkap"):
                kelas = row["data_lengkap"].get("kelas_santri", row["data_lengkap"].get("kelas", "-"))
                flat_row["Kelas"] = kelas
                flat_row["Tempat Lahir"] = row["data_lengkap"].get("tempat_lahir", "-")
                flat_row["Tgl Lahir"] = row["data_lengkap"].get("tanggal_lahir", "-")
                flat_row["Nama Ayah"] = row["data_lengkap"].get("nama_ayah", "-")
            df_list.append(flat_row)
            
        df_santri = pd.DataFrame(df_list)
        st.dataframe(df_santri, use_container_width=True)

    # ========================================
    # TAB 2: REKAPITULASI NILAI
    # ========================================
    with tab_nilai:
        st.subheader("Pantauan Nilai & Keputusan Akhir")
        
        c_sem, c_kls = st.columns(2)
        with c_sem:
            semester = st.radio("Pilih Semester Pantauan:", [1, 2], horizontal=True, format_func=lambda x: "Ganjil" if x==1 else "Genap")
        with c_kls:
            semua_kelas_n = list(set([s.get("data_lengkap", {}).get("kelas_santri", "Umum") for s in db.data_master]))
            pilih_kelas_rn = st.selectbox("Pilih Kelas untuk Cetak Rekap Nilai:", semua_kelas_n, key="sel_k_nilai")

        if st.button("🖨️ Cetak PDF Rekap Nilai Kelas (F4 Landscape)"):
            with st.spinner("Membuat rekap nilai PDF..."):
                pdf_buf_n = gen.cetak_rekap_nilai(pilih_kelas_rn, semester)
                sem_str = "Ganjil" if semester == 1 else "Genap"
                st.download_button(
                    label="⬇️ Download PDF Rekap Nilai",
                    data=pdf_buf_n,
                    file_name=f"Rekap_Nilai_Semester_{sem_str}_Kelas_{pilih_kelas_rn}.pdf",
                    mime="application/pdf"
                )
                st.success("✅ Dokumen PDF Rekap Nilai berhasil dibuat!")

        st.markdown("---")
        semua_nilai = db.get_semua_nilai(semester)
        
        if not semua_nilai:
            st.warning("Belum ada nilai yang diinput oleh wali kelas pada semester ini.")
        else:
            rekap_nilai = []
            map_santri = {s['id']: {"nama": s['nama'], "kelas": s.get("data_lengkap", {}).get("kelas_santri", "-")} for s in db.data_master}
            
            for n in semua_nilai:
                s_id = n['santri_id']
                if s_id in map_santri:
                    info = map_santri[s_id]
                    
                    if not is_kepala and str(info["kelas"]).upper().replace(" ","") != str(db.kelas_binaan).upper().replace(" ",""):
                        continue
                        
                    komp = n.get('komponen_nilai', {})
                    rekap_nilai.append({
                        "Nama Santri": info["nama"],
                        "Kelas": info["kelas"],
                        "Rata-rata": round(n.get('rata_rata', 0), 2),
                        "Sakit": komp.get("absen", {}).get("Sakit", 0),
                        "Izin": komp.get("absen", {}).get("Izin", 0),
                        "Alpa": komp.get("absen, {}").get("Alpa", 0),
                        "Status Akhir": komp.get("status", "-")
                    })
                    
            if rekap_nilai:
                df_nilai = pd.DataFrame(rekap_nilai)
                st.dataframe(df_nilai, use_container_width=True)
            else:
                st.warning("Belum ada data nilai untuk kelas Anda di semester ini.")