import streamlit as st

def render(db):
    st.header("👤 Input Biodata Santri Lengkap")
    
    with st.form("form_biodata"):
        # GRUP 1: IDENTITAS DASAR
        st.subheader("A. Identitas Dasar")
        col1, col2 = st.columns(2)
        with col1:
            no_induk = st.text_input("No. Induk")
            nama = st.text_input("Nama Lengkap (*Wajib)")
            tempat_lahir = st.text_input("Tempat Lahir")
            tanggal_lahir = st.text_input("Tanggal Lahir")
            jk = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
        with col2:
            agama = st.text_input("Agama", value="Islam")
            status_keluarga = st.text_input("Status dalam Keluarga", value="Anak Kandung")
            anak_ke = st.text_input("Anak Ke-")
            alamat_santri = st.text_area("Alamat Lengkap Santri")

        st.markdown("---")
        
        # GRUP 2: DATA ORANG TUA
        st.subheader("B. Data Orang Tua")
        col3, col4 = st.columns(2)
        with col3:
            nama_ayah = st.text_input("Nama Ayah")
            pekerjaan_ayah = st.text_input("Pekerjaan Ayah")
        with col4:
            nama_ibu = st.text_input("Nama Ibu")
            pekerjaan_ibu = st.text_input("Pekerjaan Ibu")
        alamat_ortu = st.text_area("Alamat Orang Tua (Isi jika berbeda dengan alamat santri)")

        st.markdown("---")

        # GRUP 3: DATA WALI SANTRI
        st.subheader("C. Data Wali Santri (Opsional)")
        col5, col6 = st.columns(2)
        with col5:
            nama_wali = st.text_input("Nama Wali")
            pekerjaan_wali = st.text_input("Pekerjaan Wali")
        with col6:
            alamat_wali = st.text_area("Alamat Wali Lengkap")
            
        submitted = st.form_submit_button("➕ Simpan Biodata Lengkap")
        
        if submitted:
            if not nama.strip():
                st.error("Nama Lengkap tidak boleh kosong!")
            else:
                # Semua field tambahan dibungkus ke dalam JSONB
                data_lengkap = {
                    "Tempat Lahir": tempat_lahir, "Tanggal Lahir": tanggal_lahir,
                    "Jenis Kelamin": jk, "Agama": agama, 
                    "Status Keluarga": status_keluarga, "Anak Ke": anak_ke,
                    "Alamat Santri": alamat_santri, "Nama Ayah": nama_ayah, 
                    "Pekerjaan Ayah": pekerjaan_ayah, "Nama Ibu": nama_ibu, 
                    "Pekerjaan Ibu": pekerjaan_ibu, "Alamat Ortu": alamat_ortu,
                    "Nama Wali": nama_wali, "Pekerjaan Wali": pekerjaan_wali, 
                    "Alamat Wali": alamat_wali
                }
                sukses, pesan = db.simpan_biodata(no_induk, nama, data_lengkap)
                if sukses:
                    st.success(pesan)
                    st.rerun()
                else:
                    st.error(pesan)