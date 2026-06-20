import streamlit as st

def render(db):
    st.header("📝 Input & Edit Nilai Santri")
    
    if not db.data_master:
        st.warning("Belum ada data santri. Silakan isi lewat tab Input Biodata terlebih dahulu.")
        return
        
    # Buat kamus (dictionary) untuk mencari ID unik santri berdasarkan namanya
    map_santri = {s['nama']: s['id'] for s in db.data_master}
    
    # 1. NAVIGASI PILIHAN SANTRI
    col_atas1, col_atas2 = st.columns(2)
    with col_atas1:
        pilih_nama = st.selectbox("Pilih Nama Santri:", list(map_santri.keys()))
    with col_atas2:
        semester = st.radio("Pilih Semester:", [1, 2], horizontal=True, format_func=lambda x: "Ganjil" if x==1 else "Genap")

    st.markdown("---")
    
    # 2. TARIK DATA LAMA (FITUR AUTO-FILL)
    # Ini akan memperbaiki error "nilai_lama is not defined"
    santri_id = map_santri[pilih_nama]
    nilai_lama = db.get_nilai(santri_id, semester)
    
    # Siapkan nilai default (jika belum ada nilai, gunakan angka 0 atau kosong)
    def_akademik = nilai_lama['akademik'] if nilai_lama else {}
    def_pribadi = nilai_lama['kepribadian'] if nilai_lama else {}
    def_absen = nilai_lama['absen'] if nilai_lama else {}
    
    if nilai_lama:
        st.info("ℹ️ Data nilai untuk semester ini sudah ada di database. Anda sedang dalam mode Edit.")
    
    # 3. MEMBANGUN FORM INPUT
    with st.form("form_nilai"):
        col1, col2 = st.columns(2)
        
        # --- KIRI: NILAI AKADEMIK ---
        with col1:
            st.subheader("1. Keagamaan")
            mapel_agama = ["AL QUR'AN", "AL HADITS", "AQIDAH", "AKHLAQ", "FIQIH", "TARIKH ISLAM", "BAHASA ARAB", "NAHWU", "SHARAF"]
            nilai_agama = {}
            for mapel in mapel_agama:
                val_awal = int(def_akademik.get(mapel, 0))
                nilai_agama[mapel] = st.number_input(mapel, min_value=0, max_value=100, value=val_awal, step=1)
                
            st.subheader("2. Muatan Lokal")
            mapel_mulok = ["PRAKTIK IBADAH", "BTQ", "Ke-NU-an"]
            nilai_mulok = {}
            for mapel in mapel_mulok:
                val_awal = int(def_akademik.get(mapel, 0))
                nilai_mulok[mapel] = st.number_input(mapel, min_value=0, max_value=100, value=val_awal, step=1)
        
        # --- KANAN: NON-AKADEMIK & KEPUTUSAN ---
        with col2:
            st.subheader("Kepribadian")
            c_p1, c_p2, c_p3 = st.columns(3)
            opsi_pribadi = ["A", "B", "C", "D"]
            
            # Fungsi kecil untuk mencari index combobox
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
            
            # Ekstrak status lama agar bisa di-edit (Auto-fill)
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
                    kelas_tujuan = st.text_input("Ke/Di Kelas (Angka/Teks)", value=kelas_lama)
                else:
                    kelas_tujuan = ""
                    
            catatan = st.text_area("Catatan Wali Kelas", value=nilai_lama.get("catatan", "") if nilai_lama else "")

        # Tombol Submit Dinamis
        teks_tombol = "🔄 Update Perubahan Nilai" if nilai_lama else "🧮 Simpan Nilai Baru"
        submitted = st.form_submit_button(teks_tombol)
        
        # --- PERBAIKAN INDENTASI ERROR PYLANCE ADA DI SINI ---
        if submitted:
            # 1. Tentukan Status Final
            if status_pilihan in ["Naik Kelas", "Tinggal di Kelas"]:
                status_final = f"{status_pilihan} {kelas_tujuan}".strip()
            else:
                status_final = status_pilihan

            # 2. Hitung otomatis jumlah dan rata-rata
            akademik = {**nilai_agama, **nilai_mulok}
            jumlah = sum(akademik.values())
            rata_rata = jumlah / len(akademik) if akademik else 0
            
            # 3. Kumpulkan data untuk dikirim ke Supabase
            data_nilai = {
                "santri_id": santri_id,
                "semester": semester,
                "akademik": akademik,
                "kepribadian": {"Kelakuan": kelakuan, "Kerajinan": kerajinan, "Kebersihan": kebersihan},
                "absen": {"Sakit": sakit, "Izin": izin, "Alpa": alpa},
                "jumlah": jumlah,
                "rata_rata": rata_rata,
                "catatan": catatan,
                "status": status_final
            }
            
            # 4. Eksekusi simpan (Kirim ID nilai lama jika sedang mode edit)
            id_target = nilai_lama['id'] if nilai_lama else None
            sukses, pesan = db.simpan_nilai(data_nilai, id_nilai=id_target)
            
            if sukses:
                st.success(f"{pesan} (Total: {jumlah}, Rata-rata: {rata_rata:.2f})")
                st.rerun() # Refresh form agar data terbaru langsung tersedot
            else:
                st.error(pesan)