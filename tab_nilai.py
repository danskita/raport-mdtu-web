import streamlit as st

def render(db):
    st.header("📝 Input & Edit Nilai Santri")
    
    if not db.lembaga_id:
        st.warning("⚠️ Anda belum memilih madrasah yang aktif. Silakan kembali ke Profil.")
        return
        
    if not db.data_master:
        return st.warning("Belum ada data santri yang terdaftar di kelas/lembaga ini.")

    st.markdown("---")
    
    map_santri = {s['nama']: s for s in db.data_master}
    
    col_atas1, col_atas2 = st.columns(2)
    with col_atas1: 
        pilih_nama = st.selectbox("Pilih Nama Santri:", list(map_santri.keys()))
    with col_atas2: 
        semester = st.radio("Pilih Semester:", [1, 2], horizontal=True, format_func=lambda x: "Ganjil" if x==1 else "Genap")
    
    st.markdown("---")
    
    if pilih_nama:
        santri_aktif = map_santri[pilih_nama]
        santri_id = santri_aktif["id"]
        kelas_santri = santri_aktif.get("data_lengkap", {}).get("kelas_santri", "").strip()
        
        st.info(f"👤 **Santri:** {pilih_nama} | **Kelas:** {kelas_santri}")
        
        # Tarik pengaturan Master Data untuk Kelas & Mapel
        pengaturan = db.data_lembaga.get("pengaturan_master") or {}
        kelas_mapel = pengaturan.get("kelas_mapel", {})
        mapel_list = kelas_mapel.get(kelas_santri, [])
        
        if not mapel_list:
            st.error(f"❌ Mata pelajaran untuk kelas **{kelas_santri}** belum diatur!")
            st.warning("💡 **Solusi:** Minta Admin Lembaga untuk menambahkan mata pelajaran untuk kelas ini di menu **Master Data & Pengaturan**.")
            return

        # Ambil data nilai yang sudah ada (jika pernah diinput)
        nilai_lama = db.get_nilai(santri_id, semester)
        
        if nilai_lama: 
            st.success("ℹ️ Mode Edit: Data nilai santri ini sudah pernah disimpan. Anda bisa mengubahnya di bawah ini.")
            
        komp_lama = nilai_lama.get('komponen_nilai', {}) if nilai_lama else {}
        
        # Pembacaan struktur lama agar kompatibel
        def_akademik = komp_lama.get('akademik', {})
        def_pribadi = komp_lama.get('kepribadian', {})
        def_absen = komp_lama.get('absen', {})
        stat_lama = komp_lama.get('status', '-')
        catatan_lama = komp_lama.get('catatan', '')
        
        # ==========================================
        # FORM INPUT NILAI LENGKAP
        # ==========================================
        with st.form("form_nilai"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("📊 Nilai Akademik")
                nilai_akademik_input = {}
                
                # Render mapel otomatis sesuai kelasnya
                for mapel in mapel_list:
                    val_awal = int(def_akademik.get(mapel, 0))
                    nilai_akademik_input[mapel] = st.number_input(mapel, min_value=0, max_value=100, value=val_awal, step=1)
            
            with col2:
                st.subheader("🌱 Kepribadian")
                c_p1, c_p2, c_p3 = st.columns(3)
                opsi_pribadi = ["A", "B", "C", "D"]
                def get_idx(val): return opsi_pribadi.index(val) if val in opsi_pribadi else 1
                
                with c_p1: kelakuan = st.selectbox("Kelakuan", opsi_pribadi, index=get_idx(def_pribadi.get("Kelakuan", "B")))
                with c_p2: kerajinan = st.selectbox("Kerajinan", opsi_pribadi, index=get_idx(def_pribadi.get("Kerajinan", "B")))
                with c_p3: kebersihan = st.selectbox("Kebersihan", opsi_pribadi, index=get_idx(def_pribadi.get("Kebersihan", "B")))
                
                st.subheader("📅 Ketidakhadiran (Hari)")
                c_a1, c_a2, c_a3 = st.columns(3)
                with c_a1: sakit = st.number_input("Sakit", min_value=0, value=int(def_absen.get("Sakit", 0)), step=1)
                with c_a2: izin = st.number_input("Izin", min_value=0, value=int(def_absen.get("Izin", 0)), step=1)
                with c_a3: alpa = st.number_input("Alpa", min_value=0, value=int(def_absen.get("Alpa", 0)), step=1)
                
                st.subheader("📜 Keputusan & Catatan")
                
                # Memecah status lama (misal: "Naik Kelas 2A" menjadi "Naik Kelas" dan "2A")
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
                        # Mengambil daftar semua kelas dari Master Data
                        list_kelas = list(kelas_mapel.keys()) if kelas_mapel else [kelas_santri]
                        
                        # Pengunci Dropdown Kelas untuk Wali Kelas
                        if db.role == "wali_kelas" and db.kelas_binaan:
                            kelas_tujuan = st.selectbox("Ke/Di Kelas", [db.kelas_binaan], disabled=True)
                        else:
                            idx_kelas = list_kelas.index(kelas_lama) if kelas_lama in list_kelas else 0
                            kelas_tujuan = st.selectbox("Ke/Di Kelas", list_kelas, index=idx_kelas)
                    else: 
                        kelas_tujuan = ""
                        
                catatan = st.text_area("Catatan Wali Kelas", value=catatan_lama)

            # Tombol Eksekusi
            if st.form_submit_button("🔄 Update Nilai" if nilai_lama else "🧮 Simpan Nilai Baru"):
                
                # Merangkai kembali status akhir
                status_final = f"{status_pilihan} {kelas_tujuan}".strip() if status_pilihan in ["Naik Kelas", "Tinggal di Kelas"] else status_pilihan
                
                # Kalkulasi otomatis
                jumlah = sum(nilai_akademik_input.values())
                rata_rata = jumlah / len(nilai_akademik_input) if len(nilai_akademik_input) > 0 else 0
                
                # Memasukkan ke dalam satu wadah JSONB yang rapi
                wadah_komponen = {
                    "akademik": nilai_akademik_input,
                    "kepribadian": {"Kelakuan": kelakuan, "Kerajinan": kerajinan, "Kebersihan": kebersihan},
                    "absen": {"Sakit": sakit, "Izin": izin, "Alpa": alpa},
                    "catatan": catatan, 
                    "status": status_final
                }

                data_simpan = {
                    "santri_id": santri_id, 
                    "semester": semester, 
                    "jumlah": jumlah, 
                    "rata_rata": rata_rata,
                    "komponen_nilai": wadah_komponen
                }
                
                id_nilai = nilai_lama['id'] if nilai_lama else None
                sukses, pesan = db.simpan_nilai(data_simpan, id_nilai)
                
                if sukses: 
                    st.success(f"✅ {pesan}")
                    st.rerun()
                else: 
                    st.error(f"❌ {pesan}")