import streamlit as st
import pandas as pd

def render(db):
    st.header("📊 Pemantauan & Rekap Data Madrasah")
    
    if not db.data_master:
        st.warning("Belum ada data santri yang terdaftar di sistem.")
        return

    is_kepala = getattr(db, 'role', '') == 'kepala_madrasah'
    
    if is_kepala:
        st.success("👨‍💼 **Mode Kepala Madrasah:** Anda memiliki akses penuh untuk memantau seluruh rekapan data santri dan nilai madrasah.")
    else:
        st.info(f"👨‍🏫 **Mode Wali Kelas:** Menampilkan rekapan data khusus untuk kelas {db.kelas_binaan}.")
        
    tab_santri, tab_nilai = st.tabs(["👥 Rekap Biodata Santri", "📈 Rekap Nilai & Status Akhir"])
    
    # ========================================
    # TAB 1: PEMANTAUAN DATA SANTRI
    # ========================================
    with tab_santri:
        st.subheader("Daftar Induk Santri")
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
    # TAB 2: PEMANTAUAN NILAI & KELULUSAN
    # ========================================
    with tab_nilai:
        st.subheader("Pantauan Nilai & Keputusan Akhir")
        semester = st.radio("Pilih Semester Pantauan:", [1, 2], horizontal=True, format_func=lambda x: "Ganjil" if x==1 else "Genap")
        
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
                    
                    # Filter tambahan untuk Wali Kelas (hanya melihat nilai kelasnya sendiri)
                    if not is_kepala and str(info["kelas"]).upper().replace(" ","") != str(db.kelas_binaan).upper().replace(" ",""):
                        continue
                        
                    komp = n.get('komponen_nilai', {})
                    rekap_nilai.append({
                        "Nama Santri": info["nama"],
                        "Kelas": info["kelas"],
                        "Rata-rata": round(n.get('rata_rata', 0), 2),
                        "Sakit": komp.get("absen", {}).get("Sakit", 0),
                        "Izin": komp.get("absen", {}).get("Izin", 0),
                        "Alpa": komp.get("absen", {}).get("Alpa", 0),
                        "Status Akhir": komp.get("status", "-")
                    })
                    
            if rekap_nilai:
                df_nilai = pd.DataFrame(rekap_nilai)
                st.dataframe(df_nilai, use_container_width=True)
            else:
                st.warning("Belum ada data nilai untuk kelas Anda di semester ini.")