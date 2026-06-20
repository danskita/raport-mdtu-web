import streamlit as st

def render(db):
    st.header("⚙️ Master Data & Pengaturan Madrasah")
    
    # 1. Mengintip tingkatan dari Profil Lembaga
    profil = db.data_lembaga.get("profil_lengkap", {})
    tingkatan = profil.get("tingkatan", "MDTU")
    
    st.info(f"💡 Sistem mendeteksi madrasah Anda berada di tingkatan **{tingkatan}**. Daftar Mata Pelajaran dan Kelas di bawah ini telah disesuaikan secara otomatis.")

    # 2. Tarik pengaturan master saat ini
    pengaturan = db.data_lembaga.get("pengaturan_master", {})
    tingkatan_saved = pengaturan.get("tingkatan_saved", "")

    # 3. Siapkan Template Kurikulum Berdasarkan Tingkatan
    if tingkatan == "TKA":
        tmpl_kelas = ["TKA Kecil", "TKA Besar"]
        tmpl_mapel = ["Hafalan Surat Pendek", "Hafalan Doa Harian", "Membaca Iqro/Al-Quran", "Praktek Sholat", "Menulis Huruf Hijaiyah", "Akhlaq / Adab"]
    elif tingkatan == "TPA":
        tmpl_kelas = ["TPA Level 1", "TPA Level 2", "TPA Level 3"]
        tmpl_mapel = ["Tahsin Al-Quran", "Ilmu Tajwid", "Hafalan Juz Amma", "Dinul Islam", "Praktek Ibadah", "Bahasa Arab Dasar"]
    else: # MDTU atau Lainnya
        tmpl_kelas = ["Kelas 1", "Kelas 2", "Kelas 3", "Kelas 4"]
        tmpl_mapel = ["AL QUR'AN", "AL HADITS", "AQIDAH", "AKHLAQ", "FIQIH", "TARIKH ISLAM", "BAHASA ARAB", "NAHWU", "SHARAF", "PRAKTIK IBADAH", "BTQ", "Ke-NU-an"]

    # 4. Logika Ganti Template Otomatis: Jika user baru saja mengubah tingkatan di profil, reset master datanya ke template baru
    paksa_reset = (tingkatan != tingkatan_saved)

    if paksa_reset or not pengaturan.get("kelas"):
        def_kelas = tmpl_kelas
        def_mapel = tmpl_mapel
    else:
        def_kelas = pengaturan.get("kelas")
        def_mapel = pengaturan.get("mapel")

    def_alamat = pengaturan.get("alamat", ["Desa Sukamaju", "Desa Sukaraja"])
    def_narasi = pengaturan.get("narasi", {"A": "Sangat Baik dan memuaskan", "B": "Baik", "C": "Cukup", "D": "Kurang dan perlu bimbingan"})

    with st.form("form_master_data"):
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("1. Daftar Tingkatan Kelas")
            input_kelas = st.text_area("Daftar Kelas (Dinamis)", value="\n".join(def_kelas), height=150)

            st.subheader("2. Daftar Mata Pelajaran")
            st.caption(f"Ketik semua mapel untuk kurikulum {tingkatan} di sini.")
            input_mapel = st.text_area("Daftar Mapel", value="\n".join(def_mapel), height=230)

        with col2:
            st.subheader("3. Daftar Alamat Santri")
            input_alamat = st.text_area("Daftar Desa/Kecamatan/Jalan", value="\n".join(def_alamat), height=150)

            st.subheader("4. Narasi / Deskripsi Nilai")
            narasi_A = st.text_area("Predikat A (Sangat Baik)", value=def_narasi.get("A", ""), height=68)
            narasi_B = st.text_area("Predikat B (Baik)", value=def_narasi.get("B", ""), height=68)
            narasi_C = st.text_area("Predikat C (Cukup)", value=def_narasi.get("C", ""), height=68)
            narasi_D = st.text_area("Predikat D (Kurang)", value=def_narasi.get("D", ""), height=68)

        submit_master = st.form_submit_button("💾 Simpan Pengaturan Master")

        if submit_master:
            list_kelas = [k.strip() for k in input_kelas.split('\n') if k.strip()]
            list_mapel = [m.strip() for m in input_mapel.split('\n') if m.strip()]
            list_alamat = [a.strip() for a in input_alamat.split('\n') if a.strip()]

            data_pengaturan = {
                "tingkatan_saved": tingkatan, # Kunci pengaman agar tidak me-reset terus menerus
                "kelas": list_kelas,
                "mapel": list_mapel,
                "alamat": list_alamat,
                "narasi": {
                    "A": narasi_A,
                    "B": narasi_B,
                    "C": narasi_C,
                    "D": narasi_D
                }
            }

            sukses, pesan = db.simpan_pengaturan(data_pengaturan)
            if sukses:
                st.success(pesan)
                st.rerun()
            else:
                st.error(pesan)