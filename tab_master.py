import streamlit as st

def render(db):
    st.header("⚙️ Master Data & Pengaturan")
    
    profil = db.data_lembaga.get("profil_lengkap", {})
    tingkatan = profil.get("tingkatan", "MDTU")
    
    st.info(f"💡 Pengaturan ini khusus untuk Madrasah: **{db.data_lembaga.get('nama_madrasah')}** (Tingkat: **{tingkatan}**)")

    pengaturan = db.data_lembaga.get("pengaturan_master", {})
    tingkatan_saved = pengaturan.get("tingkatan_saved", "")
    
    # Template Kategori Bawaan Berdasarkan Tingkat
    if tingkatan == "TKA":
        tmpl_kelas = ["TKA Kecil", "TKA Besar"]
        tmpl_mapel = {
            "Mata Pelajaran Pokok": ["Hafalan Surat Pendek", "Hafalan Doa Harian", "Membaca Iqro/Al-Quran", "Praktek Sholat", "Menulis Huruf Hijaiyah"],
            "Muatan Lokal": ["Akhlaq / Adab"]
        }
    elif tingkatan == "TPA":
        tmpl_kelas = ["TPA Level 1", "TPA Level 2", "TPA Level 3"]
        tmpl_mapel = {
            "Keagamaan Dasar": ["Tahsin Al-Quran", "Ilmu Tajwid", "Hafalan Juz Amma", "Dinul Islam", "Praktek Ibadah"],
            "Muatan Lokal": ["Bahasa Arab Dasar"]
        }
    else: # MDTU / Lainnya
        tmpl_kelas = ["Kelas 1", "Kelas 2", "Kelas 3", "Kelas 4"]
        tmpl_mapel = {
            "Keagamaan": ["AL QUR'AN", "AL HADITS", "AQIDAH", "AKHLAQ", "FIQIH", "TARIKH ISLAM", "BAHASA ARAB", "NAHWU", "SHARAF"],
            "Muatan Lokal": ["PRAKTIK IBADAH", "BTQ", "Ke-NU-an"]
        }

    # Cek apakah baru ganti tingkat
    paksa_reset = (tingkatan != tingkatan_saved)
    
    if paksa_reset or not pengaturan.get("kelas"):
        def_kelas = tmpl_kelas
        def_mapel = tmpl_mapel
    else:
        def_kelas = pengaturan.get("kelas")
        def_mapel = pengaturan.get("mapel")
        
        # Migrasi: Jika data mapel lama masih berupa list biasa, ubah otomatis jadi Kategori
        if isinstance(def_mapel, list):
            def_mapel = {"Keagamaan": def_mapel, "Muatan Lokal": []}

    def_alamat = pengaturan.get("alamat", ["Desa Sukamaju", "Desa Sukaraja"])
    def_narasi = pengaturan.get("narasi", {"A": "Sangat Baik", "B": "Baik", "C": "Cukup", "D": "Kurang"})

    with st.form("form_master_data"):
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("1. Daftar Kelas (Dinamis)")
            input_kelas = st.text_area("Masukkan tiap kelas di baris baru (ENTER)", value="\n".join(def_kelas), height=100)

            st.subheader("2. Kategori & Mata Pelajaran")
            st.caption("Kelompokkan mapel sesuai kategorinya agar rapi saat dicetak.")
            
            # Form Dinamis Kategori 1
            kat_1_default = list(def_mapel.keys())[0] if len(def_mapel) > 0 else "Keagamaan"
            kat_1 = st.text_input("Nama Kategori 1 (Misal: Keagamaan)", value=kat_1_default)
            mapel_1 = st.text_area(f"Mapel untuk Kategori 1", value="\n".join(def_mapel.get(kat_1_default, [])), height=130)
            
            # Form Dinamis Kategori 2
            kat_2_default = list(def_mapel.keys())[1] if len(def_mapel) > 1 else "Muatan Lokal"
            kat_2 = st.text_input("Nama Kategori 2 (Misal: Muatan Lokal)", value=kat_2_default)
            mapel_2 = st.text_area(f"Mapel untuk Kategori 2", value="\n".join(def_mapel.get(kat_2_default, [])), height=100)

        with col2:
            st.subheader("3. Daftar Alamat Santri")
            input_alamat = st.text_area("Daftar Desa/Kecamatan/Jalan", value="\n".join(def_alamat), height=100)

            st.subheader("4. Narasi Predikat Nilai")
            narasi_A = st.text_area("Predikat A (Sangat Baik)", value=def_narasi.get("A", ""), height=68)
            narasi_B = st.text_area("Predikat B (Baik)", value=def_narasi.get("B", ""), height=68)
            narasi_C = st.text_area("Predikat C (Cukup)", value=def_narasi.get("C", ""), height=68)
            narasi_D = st.text_area("Predikat D (Kurang)", value=def_narasi.get("D", ""), height=68)

        submit_master = st.form_submit_button("💾 Simpan Master Data Lembaga Ini")

        if submit_master:
            list_kelas = [k.strip() for k in input_kelas.split('\n') if k.strip()]
            list_alamat = [a.strip() for a in input_alamat.split('\n') if a.strip()]
            
            # Susun Kategori ke dalam format JSON
            dict_mapel = {}
            if kat_1: dict_mapel[kat_1] = [m.strip() for m in mapel_1.split('\n') if m.strip()]
            if kat_2: dict_mapel[kat_2] = [m.strip() for m in mapel_2.split('\n') if m.strip()]

            data_pengaturan = {
                "tingkatan_saved": tingkatan,
                "kelas": list_kelas,
                "mapel": dict_mapel,
                "alamat": list_alamat,
                "narasi": {"A": narasi_A, "B": narasi_B, "C": narasi_C, "D": narasi_D}
            }

            sukses, pesan = db.simpan_pengaturan(data_pengaturan)
            if sukses:
                st.success(pesan)
                st.rerun()
            else:
                st.error(pesan)