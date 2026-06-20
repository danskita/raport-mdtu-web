import streamlit as st

def render(db):
    st.header("⚙️ Master Data & Pengaturan Madrasah")
    st.info("Kustomisasi daftar dropdown untuk madrasah Anda. Pisahkan setiap item dengan tombol ENTER (1 baris = 1 item).")

    # Tarik data pengaturan saat ini dari Cloud
    pengaturan = db.data_lembaga.get("pengaturan_master", {})
    if not pengaturan:
        pengaturan = {}

    # Siapkan nilai default bawaan (Template)
    def_kelas = pengaturan.get("kelas", ["Taman Kanak-kanak Alquran (TKA)", "Taman Pendidikan Alquran (TPA)", "Madrasah Diniyah Takmiliyah Ula (MDTU)"])
    def_mapel = pengaturan.get("mapel", ["AL QUR'AN", "AL HADITS", "AQIDAH", "AKHLAQ", "FIQIH", "TARIKH ISLAM", "BAHASA ARAB"])
    def_alamat = pengaturan.get("alamat", ["Desa Sukamaju", "Desa Sukaraja", "Kecamatan Harapan"])
    def_narasi = pengaturan.get("narasi", {"A": "Sangat Baik dan memuaskan", "B": "Baik", "C": "Cukup", "D": "Kurang dan perlu bimbingan"})

    with st.form("form_master_data"):
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("1. Daftar Tingkatan Kelas")
            input_kelas = st.text_area("Daftar Kelas (Dinamis)", value="\n".join(def_kelas), height=150)

            st.subheader("2. Daftar Mata Pelajaran")
            st.caption("Ketik semua mapel yang berlaku di madrasah Anda di sini.")
            input_mapel = st.text_area("Daftar Mapel", value="\n".join(def_mapel), height=230)

        with col2:
            st.subheader("3. Daftar Alamat Santri")
            input_alamat = st.text_area("Daftar Desa/Kecamatan/Jalan", value="\n".join(def_alamat), height=150)

            st.subheader("4. Narasi / Deskripsi Nilai")
            st.caption("Teks ini akan otomatis muncul di raport PDF berdasarkan predikat.")
            narasi_A = st.text_area("Predikat A (Sangat Baik)", value=def_narasi.get("A", ""), height=68)
            narasi_B = st.text_area("Predikat B (Baik)", value=def_narasi.get("B", ""), height=68)
            narasi_C = st.text_area("Predikat C (Cukup)", value=def_narasi.get("C", ""), height=68)
            narasi_D = st.text_area("Predikat D (Kurang)", value=def_narasi.get("D", ""), height=68)

        submit_master = st.form_submit_button("💾 Simpan Pengaturan Master")

        if submit_master:
            # Mengolah teks baris baru (ENTER) menjadi struktur daftar (List) Array
            list_kelas = [k.strip() for k in input_kelas.split('\n') if k.strip()]
            list_mapel = [m.strip() for m in input_mapel.split('\n') if m.strip()]
            list_alamat = [a.strip() for a in input_alamat.split('\n') if a.strip()]

            # Susun ke format JSON 
            data_pengaturan = {
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

            # Kirim ke Supabase
            sukses, pesan = db.simpan_pengaturan(data_pengaturan)
            if sukses:
                st.success(pesan)
                st.rerun()
            else:
                st.error(pesan)