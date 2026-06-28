import streamlit as st

def render(db):
    st.header("📝 Input & Edit Nilai Santri")
    if not db.data_master: return st.warning("Belum ada data santri di kelas/madrasah ini.")
        
    map_santri = {s['nama']: s['id'] for s in db.data_master}
    
    col_atas1, col_atas2 = st.columns(2)
    with col_atas1: pilih_nama = st.selectbox("Pilih Nama Santri:", list(map_santri.keys()))
    with col_atas2: semester = st.radio("Pilih Semester:", [1, 2], horizontal=True, format_func=lambda x: "Ganjil" if x==1 else "Genap")
    st.markdown("---")
    
    santri_id = map_santri[pilih_nama]
    nilai_lama = db.get_nilai(santri_id, semester)
    
    # =================================================================
    # PERBAIKAN 1: MEMBACA DATA DARI KOLOM JSONB "KOMPONEN_NILAI"
    # =================================================================
    komp_lama = nilai_lama.get('komponen_nilai', {}) if nilai_lama else {}
    
    # Fallback (Sistem Cadangan): Jika komponen_nilai kosong, coba baca dari struktur lama
    # Ini berguna agar nilai yang diinput sebelum kolom JSONB dibuat tidak hilang
    def_akademik = komp_lama.get('akademik') or (nilai_lama.get('akademik', {}) if nilai_lama else {})
    def_pribadi = komp_lama.get('kepribadian') or (nilai_lama.get('kepribadian', {}) if nilai_lama else {})
    def_absen = komp_lama.get('absen') or (nilai_lama.get('absen', {}) if nilai_lama else {})
    stat_lama = komp_lama.get('status') or (nilai_lama.get('status', '-') if nilai_lama else "-")
    catatan_lama = komp_lama.get('catatan') or (nilai_lama.get('catatan', '') if nilai_lama else "")
    
    if nilai_lama: st.info("ℹ️ Mode Edit: Data nilai santri ini sudah ada.")
    
    pengaturan = db.data_lembaga.get("pengaturan_master", {})
    dict_mapel = pengaturan.get("mapel", {"Keagamaan": ["AL QUR'AN"]})
    if isinstance(dict_mapel, list): dict_mapel = {"Mata Pelajaran": dict_mapel}
    list_kelas = pengaturan.get("kelas", ["MDTU"])

    with st.form("form_nilai"):
        col1, col2 = st.columns(2)
        with col1:
            nilai_akademik_input = {}
            for kategori, daftar_mapel in dict_mapel.items():
                st.subheader(kategori) 
                for mapel in daftar_mapel:
                    val_awal = int(def_akademik.get(mapel, 0))
                    nilai_akademik_input[mapel] = st.number_input(mapel, min_value=0, max_value=100, value=val_awal, step=1)
        
        with col2:
            st.subheader("Kepribadian")
            c_p1, c_p2, c_p3 = st.columns(3)
            opsi_pribadi = ["A", "B", "C", "D"]
            def get_idx(val): return opsi_pribadi.index(val) if val in opsi_pribadi else 1
            
            with c_p1: kelakuan = st.selectbox("Kelakuan", opsi_pribadi, index=get_idx(def_pribadi.get("Kelakuan", "B")))
            with c_p2: kerajinan = st.selectbox("Kerajinan", opsi_pribadi, index=get_idx(def_pribadi.get("Kerajinan", "B")))
            with c_p3: kebersihan = st.selectbox("Kebersihan", opsi_pribadi, index=get_idx(def_pribadi.get("Kebersihan", "B")))
            
            st.subheader("Ketidakhadiran (Hari)")
            c_a1, c_a2, c_a3 = st.columns(3)
            with c_a1: sakit = st.number_input("Sakit", min_value=0, value=int(def_absen.get("Sakit", 0)), step=1)
            with c_a2: izin = st.number_input("Izin", min_value=0, value=int(def_absen.get("Izin", 0)), step=1)
            with c_a3: alpa = st.number_input("Alpa", min_value=0, value=int(def_absen.get("Alpa", 0)), step=1)
            
            st.subheader("Keputusan & Catatan")
            stat_dasar, kelas_lama = "-", ""
            if "Naik" in stat_lama: stat_dasar = "Naik Kelas"; kelas_lama = stat_lama.replace("Naik Kelas", "").strip()
            elif "Tinggal" in stat_lama: stat_dasar = "Tinggal di Kelas"; kelas_lama = stat_lama.replace("Tinggal di Kelas", "").strip()
            elif "LULUS" in stat_lama: stat_dasar = "LULUS"

            col_stat1, col_stat2 = st.columns(2)
            with col_stat1:
                opsi_status = ["-", "Naik Kelas", "Tinggal di Kelas", "LULUS"]
                idx_status = opsi_status.index(stat_dasar) if stat_dasar in opsi_status else 0
                status_pilihan = st.selectbox("Status Akhir", opsi_status, index=idx_status)
                
            with col_stat2:
                if status_pilihan in ["Naik Kelas", "Tinggal di Kelas"]:
                    # --- PENGUNCI DROPDOWN KELAS ---
                    if db.role == "guru" and db.kelas_binaan:
                        kelas_tujuan = st.selectbox("Ke/Di Kelas", [db.kelas_binaan], disabled=True)
                    else:
                        idx_kelas = list_kelas.index(kelas_lama) if kelas_lama in list_kelas else 0
                        kelas_tujuan = st.selectbox("Ke/Di Kelas", list_kelas, index=idx_kelas)
                else: kelas_tujuan = ""
                    
            catatan = st.text_area("Catatan Wali Kelas", value=catatan_lama)

        if st.form_submit_button("🔄 Update" if nilai_lama else "🧮 Simpan Nilai"):
            status_final = f"{status_pilihan} {kelas_tujuan}".strip() if status_pilihan in ["Naik Kelas", "Tinggal di Kelas"] else status_pilihan
            jumlah = sum(nilai_akademik_input.values())
            rata_rata = jumlah / len(nilai_akademik_input) if nilai_akademik_input else 0
            
            # =================================================================
            # PERBAIKAN 2: MEMBUNGKUS DATA KE DALAM WADAH JSONB
            # =================================================================
            wadah_komponen = {
                "akademik": nilai_akademik_input,
                "kepribadian": {"Kelakuan": kelakuan, "Kerajinan": kerajinan, "Kebersihan": kebersihan},
                "absen": {"Sakit": sakit, "Izin": izin, "Alpa": alpa},
                "catatan": catatan, 
                "status": status_final
            }

            data_nilai = {
                "santri_id": santri_id, 
                "semester": semester, 
                "jumlah": jumlah, 
                "rata_rata": rata_rata,
                "komponen_nilai": wadah_komponen  # <--- Disimpan secara rapi ke kolom JSONB
            }
            
            sukses, pesan = db.simpan_nilai(data_nilai, id_nilai=nilai_lama['id'] if nilai_lama else None)
            if sukses: 
                st.success(pesan)
                st.rerun()
            else: 
                st.error(pesan)