import streamlit as st

def render(db):
    st.header("📝 Input & Edit Nilai Santri")
    
    if not db.lembaga_id:
        st.warning("⚠️ Anda belum login.")
        return

    if not db.data_master:
        st.warning("Belum ada data santri di madrasah ini. Silakan tambah di Tab Biodata.")
        return
        
    map_santri = {s['nama']: s['id'] for s in db.data_master}
    
    col_atas1, col_atas2 = st.columns(2)
    with col_atas1:
        pilih_nama = st.selectbox("Pilih Nama Santri:", list(map_santri.keys()))
    with col_atas2:
        semester = st.radio("Pilih Semester:", [1, 2], horizontal=True, format_func=lambda x: "Ganjil" if x==1 else "Genap")

    st.markdown("---")
    
    santri_id = map_santri[pilih_nama]
    nilai_lama = db.get_nilai(santri_id, semester)
    
    def_akademik = nilai_lama['akademik'] if nilai_lama else {}
    def_pribadi = nilai_lama['kepribadian'] if nilai_lama else {}
    def_absen = nilai_lama['absen'] if nilai_lama else {}
    
    if nilai_lama:
        st.info("ℹ️ Mode Edit: Data nilai santri ini sudah ada. Mengubah data di bawah akan memodifikasi file aslinya.")
    
    pengaturan = db.data_lembaga.get("pengaturan_master", {})
    dict_mapel = pengaturan.get("mapel", {"Keagamaan": ["AL QUR'AN"]})
    
    # Migrasi darurat jika mapel masih list biasa
    if isinstance(dict_mapel, list):
        dict_mapel = {"Mata Pelajaran": dict_mapel}
        
    list_kelas = pengaturan.get("kelas", ["MDTU"])

    with st.form("form_nilai"):
        col1, col2 = st.columns(2)
        
        # --- KIRI: NILAI AKADEMIK DIKELOMPOKKAN BERDASARKAN KATEGORI ---
        with col1:
            nilai_akademik_input = {}
            for kategori, daftar_mapel in dict_mapel.items():
                st.subheader(kategori) # Menampilkan nama kategori sebagai sub-judul
                for mapel in daftar_mapel:
                    val_awal = int(def_akademik.get(mapel, 0))
                    nilai_akademik_input[mapel] = st.number_input(mapel, min_value=0, max_value=100, value=val_awal, step=1)
        
        # --- KANAN: NON-AKADEMIK & STATUS ---
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
            stat_lama = nilai_lama.get("status", "-") if nilai_lama else "-"
            stat_dasar, kelas_lama = "-", ""
            if "Naik" in stat_lama: 
                stat_dasar = "Naik Kelas"
                kelas_lama = stat_lama.replace("Naik Kelas", "").strip()
            elif "Tinggal" in stat_lama: 
                stat_dasar = "Tinggal di Kelas"
                kelas_lama = stat_lama.replace("Tinggal di Kelas", "").strip()
            elif "LULUS" in stat_lama: 
                stat_dasar = "LULUS"

            col_stat1, col_stat2 = st.columns(2)
            with col_stat1:
                opsi_status = ["-", "Naik Kelas", "Tinggal di Kelas", "LULUS"]
                idx_status = opsi_status.index(stat_dasar) if stat_dasar in opsi_status else 0
                status_pilihan = st.selectbox("Status Akhir", opsi_status, index=idx_status)
                
            with col_stat2:
                if status_pilihan in ["Naik Kelas", "Tinggal di Kelas"]:
                    # Menggunakan Dropdown kelas dari master data
                    idx_kelas = list_kelas.index(kelas_lama) if kelas_lama in list_kelas else 0
                    kelas_tujuan = st.selectbox("Ke/Di Kelas", list_kelas, index=idx_kelas)
                else:
                    kelas_tujuan = ""
                    
            catatan = st.text_area("Catatan Wali Kelas", value=nilai_lama.get("catatan", "") if nilai_lama else "")

        teks_tombol = "🔄 Update Perubahan Nilai" if nilai_lama else "🧮 Simpan Nilai Baru"
        submitted = st.form_submit_button(teks_tombol)
        
        if submitted:
            status_final = f"{status_pilihan} {kelas_tujuan}".strip() if status_pilihan in ["Naik Kelas", "Tinggal di Kelas"] else status_pilihan

            jumlah = sum(nilai_akademik_input.values())
            rata_rata = jumlah / len(nilai_akademik_input) if nilai_akademik_input else 0
            
            data_nilai = {
                "santri_id": santri_id,
                "semester": semester,
                "akademik": nilai_akademik_input,
                "kepribadian": {"Kelakuan": kelakuan, "Kerajinan": kerajinan, "Kebersihan": kebersihan},
                "absen": {"Sakit": sakit, "Izin": izin, "Alpa": alpa},
                "jumlah": jumlah,
                "rata_rata": rata_rata,
                "catatan": catatan,
                "status": status_final
            }
            
            id_target = nilai_lama['id'] if nilai_lama else None
            sukses, pesan = db.simpan_nilai(data_nilai, id_nilai=id_target)
            
            if sukses:
                st.success(f"{pesan} (Total: {jumlah}, Rata-rata: {rata_rata:.2f})")
                st.rerun()
            else:
                st.error(pesan)