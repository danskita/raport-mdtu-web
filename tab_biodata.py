import streamlit as st

def render(db):
    st.header("👤 Input Biodata Santri")
    if not db.lembaga_id: return st.warning("⚠️ Anda belum login.")

    pengaturan = db.data_lembaga.get("pengaturan_master", {})
    list_kelas = pengaturan.get("kelas", ["TKA", "TPA", "MDTU"])
    list_alamat = pengaturan.get("alamat", ["- Belum diatur -"])

    with st.form("form_biodata"):
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Identitas Dasar")
            no_induk = st.text_input("Nomor Induk Santri")
            nama = st.text_input("Nama Lengkap Santri")
            
            # --- PENGUNCI DROPDOWN KELAS ---
            if db.role == "guru" and db.kelas_binaan:
                kelas_santri = st.selectbox("Tingkatan Kelas", [db.kelas_binaan], disabled=True)
                st.caption(f"🔒 Terkunci: Anda hanya berwenang menambah santri untuk {db.kelas_binaan}.")
            else:
                kelas_santri = st.selectbox("Tingkatan Kelas", list_kelas)
                
            desa_kelurahan = st.selectbox("Desa / Kelurahan (Alamat)", list_alamat)
            jk = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
            tempat_lahir = st.text_input("Tempat Lahir")
            tanggal_lahir = st.date_input("Tanggal Lahir")
            anak_ke = st.text_input("Anak Ke-")

        with col2:
            st.subheader("Data Orang Tua")
            nama_ayah = st.text_input("Nama Ayah")
            pekerjaan_ayah = st.text_input("Pekerjaan Ayah")
            nama_ibu = st.text_input("Nama Ibu")
            pekerjaan_ibu = st.text_input("Pekerjaan Ibu")

            st.subheader("Data Wali (Opsional)")
            nama_wali = st.text_input("Nama Wali")
            pekerjaan_wali = st.text_input("Pekerjaan Wali")

        if st.form_submit_button("💾 Simpan Biodata"):
            if not no_induk or not nama: st.error("Nomor Induk dan Nama wajib diisi!")
            else:
                data_lengkap = {
                    "kelas_santri": kelas_santri, "jenis_kelamin": jk, "tempat_lahir": tempat_lahir,
                    "tanggal_lahir": str(tanggal_lahir), "anak_ke": anak_ke, "desa_kelurahan": desa_kelurahan,
                    "nama_ayah": nama_ayah, "pekerjaan_ayah": pekerjaan_ayah, "nama_ibu": nama_ibu,
                    "pekerjaan_ibu": pekerjaan_ibu, "nama_wali": nama_wali, "pekerjaan_wali": pekerjaan_wali
                }
                sukses, pesan = db.simpan_biodata(no_induk, nama, data_lengkap)
                if sukses: st.success(pesan)
                else: st.error(pesan)