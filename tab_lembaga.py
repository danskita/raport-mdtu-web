import streamlit as st
import base64

def render(db):
    st.header("🏛️ Profil & Identitas Lembaga")

    dl = db.data_lembaga

    with st.form("form_lembaga"):
        st.subheader("Data Madrasah")
        col1, col2 = st.columns(2)
        with col1:
            nama = st.text_input("Nama Madrasah", value=dl.get("nama_madrasah", ""))
            nsm = st.text_input("Nomor Statistik (NSM)", value=dl.get("nomor_statistik", ""))
            alamat = st.text_input("Alamat Jalan", value=dl.get("alamat", ""))
            desa = st.text_input("Desa/Kelurahan", value=dl.get("desa_kelurahan", ""))
            kecamatan = st.text_input("Kecamatan", value=dl.get("kecamatan", ""))
        with col2:
            kabupaten = st.text_input("Kabupaten/Kota", value=dl.get("kabupaten_kota", ""))
            provinsi = st.text_input("Provinsi", value=dl.get("provinsi", ""))
            kelas = st.text_input("Kelas", value=dl.get("kelas", ""))
            tahun = st.text_input("Tahun Pelajaran", value=dl.get("tahun_pelajaran", ""))

        st.subheader("Pejabat & Pengesahan")
        col3, col4 = st.columns(2)
        with col3:
            kepala = st.text_input("Nama Kepala Madrasah", value=dl.get("kepala_madin", ""))
            wali = st.text_input("Nama Wali Kelas", value=dl.get("wali_kelas", ""))
        with col4:
            tempat = st.text_input("Tempat Titimangsa (cth: Jakarta)", value=dl.get("tempat_raport", ""))
            tanggal = st.text_input("Tanggal Raport", value=dl.get("tanggal_raport", ""))

        st.markdown("---")
        st.subheader("🖼️ Logo Madrasah")
        # Tombol Upload
        logo_file = st.file_uploader("Pilih Logo Madrasah (Format: PNG / JPG)", type=["png", "jpg", "jpeg"])
        
        # Mengecek apakah ada logo lama di database
        logo_b64 = dl.get("logo", "")
        
        if logo_file:
            # Jika user mengunggah logo baru
            logo_b64 = base64.b64encode(logo_file.read()).decode("utf-8")
            st.image(logo_file, width=150, caption="Logo yang akan disimpan")
        elif logo_b64:
            # Jika belum upload baru, tampilkan logo lama dari database
            st.image(base64.b64decode(logo_b64), width=150, caption="Logo tersimpan")

        submitted = st.form_submit_button("💾 Simpan Perubahan")

        if submitted:
            data_baru = {
                "nama_madrasah": nama, "nomor_statistik": nsm, "alamat": alamat,
                "desa_kelurahan": desa, "kecamatan": kecamatan, "kabupaten_kota": kabupaten,
                "provinsi": provinsi, "kelas": kelas, "tahun_pelajaran": tahun,
                "kepala_madin": kepala, "wali_kelas": wali, "tempat_raport": tempat,
                "tanggal_raport": tanggal, "logo": logo_b64
            }
            sukses, pesan = db.simpan_lembaga(data_baru)
            if sukses:
                st.success(pesan)
                st.rerun()
            else:
                st.error(pesan)