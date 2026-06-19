import streamlit as st

def render(db):
    st.header("🏛️ Identitas Lembaga")
    st.write("Silakan lengkapi profil madrasah Anda di bawah ini.")
    
    # Ambil data yang sudah ada di memori (jika ada)
    dl = db.data_lembaga
    
    # Membuat Form
    with st.form("form_lembaga"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Informasi Madrasah")
            nama = st.text_input("Nama Madrasah", value=dl.get("nama_madrasah", ""))
            nsm = st.text_input("Nomor Statistik", value=dl.get("nomor_statistik", ""))
            alamat = st.text_area("Alamat", value=dl.get("alamat", ""))
            desa = st.text_input("Desa/Kelurahan", value=dl.get("desa_kelurahan", ""))
            kecamatan = st.text_input("Kecamatan", value=dl.get("kecamatan", ""))
            kabupaten = st.text_input("Kabupaten/Kota", value=dl.get("kabupaten_kota", ""))
            provinsi = st.text_input("Provinsi", value=dl.get("provinsi", ""))
            
        with col2:
            st.subheader("Tahun Ajaran & Pejabat")
            kelas = st.text_input("Kelas", value=dl.get("kelas", ""))
            tahun_pel = st.text_input("Tahun Pelajaran", value=dl.get("tahun_pelajaran", ""))
            masehi = st.text_input("Masehi", value=dl.get("masehi", ""))
            tempat_raport = st.text_input("Tempat Raport", value=dl.get("tempat_raport", ""))
            tanggal_raport = st.text_input("Tanggal Raport", value=dl.get("tanggal_raport", ""))
            wali_kelas = st.text_input("Wali Kelas", value=dl.get("wali_kelas", ""))
            kepala_madin = st.text_input("Kepala Madin", value=dl.get("kepala_madin", ""))
            
        # Tombol Submit Form
        submitted = st.form_submit_button("💾 Simpan Perubahan Identitas Lembaga")
        
        if submitted:
            data_baru = {
                "nama_madrasah": nama, "nomor_statistik": nsm, "alamat": alamat,
                "desa_kelurahan": desa, "kecamatan": kecamatan, "kabupaten_kota": kabupaten,
                "provinsi": provinsi, "kelas": kelas, "tahun_pelajaran": tahun_pel,
                "masehi": masehi, "tempat_raport": tempat_raport, "tanggal_raport": tanggal_raport,
                "wali_kelas": wali_kelas, "kepala_madin": kepala_madin
            }
            sukses, pesan = db.simpan_lembaga(data_baru)
            if sukses:
                st.success(pesan)
                st.rerun() # Refresh halaman agar data terbaru langsung muncul
            else:
                st.error(pesan)