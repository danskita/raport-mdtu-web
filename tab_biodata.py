import streamlit as st

def render(db):
    st.header("👤 Input Biodata Santri Baru")
    
    with st.form("form_biodata"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Identitas Dasar")
            no_induk = st.text_input("No. Induk")
            nama = st.text_input("Nama Lengkap (*Wajib)")
            tempat_lahir = st.text_input("Tempat Lahir")
            tanggal_lahir = st.text_input("Tanggal Lahir")
            jk = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
            
        with col2:
            st.subheader("Data Orang Tua & Alamat")
            nama_ayah = st.text_input("Nama Ayah")
            nama_ibu = st.text_input("Nama Ibu")
            pekerjaan = st.text_input("Pekerjaan Orang Tua")
            alamat = st.text_area("Alamat Lengkap")
            
        submitted = st.form_submit_button("➕ Tambahkan Santri ke Database")
        
        if submitted:
            if not nama.strip():
                st.error("Nama Lengkap tidak boleh kosong!")
            else:
                # Kolom selain nama dan no_induk kita bungkus ke dalam JSONB
                data_lengkap = {
                    "Tempat Lahir": tempat_lahir,
                    "Tanggal Lahir": tanggal_lahir,
                    "Jenis Kelamin": jk,
                    "Nama Ayah": nama_ayah,
                    "Nama Ibu": nama_ibu,
                    "Pekerjaan": pekerjaan,
                    "Alamat": alamat
                }
                sukses, pesan = db.simpan_biodata(no_induk, nama, data_lengkap)
                if sukses:
                    st.success(pesan)
                    st.rerun() # Refresh agar data masuk ke Tab Data Induk
                else:
                    st.error(pesan)