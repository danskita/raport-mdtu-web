import streamlit as st
import base64

def render(db):
    st.header("🏛️ Profil & Identitas Lembaga")

    dl_raw = db.data_lembaga
    profil = dl_raw.get("profil_lengkap", {})

    with st.form("form_lembaga"):
        st.subheader("Data Madrasah")
        col1, col2 = st.columns(2)
        with col1:
            nama = st.text_input("Nama Madrasah", value=dl_raw.get("nama_madrasah", ""))
            nsm = st.text_input("Nomor Statistik (NSM)", value=dl_raw.get("nsm", ""))
            
            # --- SAKELAR UTAMA TINGKATAN LEMBAGA ---
            opsi_tingkatan = ["MDTU", "TKA", "TPA", "Lainnya"]
            idx_tingkat = opsi_tingkatan.index(profil.get("tingkatan", "MDTU")) if profil.get("tingkatan", "MDTU") in opsi_tingkatan else 0
            tingkatan = st.selectbox("Tingkatan Lembaga (Menentukan Mata Pelajaran)", opsi_tingkatan, index=idx_tingkat)
            
            alamat = st.text_input("Alamat Jalan", value=profil.get("alamat", ""))
            desa = st.text_input("Desa/Kelurahan", value=profil.get("desa_kelurahan", ""))
        with col2:
            kecamatan = st.text_input("Kecamatan", value=profil.get("kecamatan", ""))
            kabupaten = st.text_input("Kabupaten/Kota", value=profil.get("kabupaten_kota", ""))
            provinsi = st.text_input("Provinsi", value=profil.get("provinsi", ""))
            tahun = st.text_input("Tahun Pelajaran", value=profil.get("tahun_pelajaran", ""))

        st.subheader("Pejabat & Pengesahan")
        col3, col4 = st.columns(2)
        with col3:
            kepala = st.text_input("Nama Kepala Madrasah", value=profil.get("kepala_madin", ""))
            wali = st.text_input("Nama Wali Kelas", value=profil.get("wali_kelas", ""))
        with col4:
            tempat = st.text_input("Tempat Titimangsa (cth: Jakarta)", value=profil.get("tempat_raport", ""))
            tanggal = st.text_input("Tanggal Raport", value=profil.get("tanggal_raport", ""))

        st.markdown("---")
        st.subheader("🖼️ Logo Madrasah")
        logo_file = st.file_uploader("Pilih Logo Madrasah (Format: PNG / JPG)", type=["png", "jpg", "jpeg"])
        
        logo_b64 = profil.get("logo", "")
        
        if logo_file:
            logo_b64 = base64.b64encode(logo_file.read()).decode("utf-8")
            st.image(logo_file, width=150, caption="Logo yang akan disimpan")
        elif logo_b64:
            try:
                st.image(base64.b64decode(logo_b64), width=150, caption="Logo tersimpan")
            except:
                st.write("Gagal memuat logo lama.")

        submitted = st.form_submit_button("💾 Simpan Perubahan")

        if submitted:
            data_baru = {
                "nama_madrasah": nama, 
                "nsm": nsm, 
                "profil_lengkap": {
                    "tingkatan": tingkatan, # <-- Menyimpan pilihan Tingkatan
                    "alamat": alamat, 
                    "desa_kelurahan": desa, 
                    "kecamatan": kecamatan, 
                    "kabupaten_kota": kabupaten,
                    "provinsi": provinsi, 
                    "tahun_pelajaran": tahun,
                    "kepala_madin": kepala, 
                    "wali_kelas": wali, 
                    "tempat_raport": tempat,
                    "tanggal_raport": tanggal, 
                    "logo": logo_b64
                }
            }
            sukses, pesan = db.simpan_lembaga(data_baru)
            if sukses:
                st.success(pesan)
                st.rerun()
            else:
                st.error(pesan)