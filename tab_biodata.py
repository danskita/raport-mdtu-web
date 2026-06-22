import streamlit as st
import pandas as pd
import io

def render(db):
    st.header("👤 Manajemen Biodata Santri")
    if not db.lembaga_id: 
        return st.warning("⚠️ Anda belum login.")

    pengaturan = db.data_lembaga.get("pengaturan_master", {})
    list_kelas = pengaturan.get("kelas", ["TKA", "TPA", "MDTU"])
    list_alamat = pengaturan.get("alamat", ["- Belum diatur -"])

    tab_input, tab_impor, tab_edit = st.tabs(["📝 Input Manual", "📥 Impor Excel", "⚙️ Edit & Hapus"])

    # ==========================================
    # 1. TAB INPUT MANUAL
    # ==========================================
    with tab_input:
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

            submit_tambah = st.form_submit_button("💾 Simpan Biodata", type="primary")
            
            if submit_tambah:
                if not no_induk or not nama: 
                    st.error("Nomor Induk dan Nama wajib diisi!")
                else:
                    data_lengkap = {
                        "kelas_santri": kelas_santri, "jenis_kelamin": jk, "tempat_lahir": tempat_lahir,
                        "tanggal_lahir": str(tanggal_lahir), "anak_ke": anak_ke, "desa_kelurahan": desa_kelurahan,
                        "nama_ayah": nama_ayah, "pekerjaan_ayah": pekerjaan_ayah, "nama_ibu": nama_ibu,
                        "pekerjaan_ibu": pekerjaan_ibu, "nama_wali": nama_wali, "pekerjaan_wali": pekerjaan_wali
                    }
                    sukses, pesan = db.simpan_biodata(no_induk, nama, data_lengkap)
                    if sukses: 
                        st.success(pesan)
                        st.rerun()
                    else: 
                        st.error(pesan)

    # ==========================================
    # 2. TAB IMPOR EXCEL
    # ==========================================
    with tab_impor:
        st.subheader("Impor Puluhan Data Sekaligus")
        st.info("Unduh template Excel di bawah ini, isi data santri, lalu unggah kembali ke sistem.")
        
        # Buat template Excel di memori (Sesuai dengan kolom lengkap)
        template_df = pd.DataFrame({
            "No Induk": ["12345", "12346"],
            "Nama Lengkap": ["Ahmad Fulan", "Siti Fulanah"],
            "Kelas": [list_kelas[0] if list_kelas else "Kelas 1", list_kelas[0] if list_kelas else "Kelas 1"],
            "Desa/Kelurahan": [list_alamat[0] if list_alamat else "Desa A", list_alamat[0] if list_alamat else "Desa A"],
            "Jenis Kelamin (Laki-laki/Perempuan)": ["Laki-laki", "Perempuan"],
            "Tempat Lahir": ["Jakarta", "Bandung"],
            "Tanggal Lahir (YYYY-MM-DD)": ["2015-05-12", "2016-08-20"],
            "Anak Ke-": ["1", "2"],
            "Nama Ayah": ["Budi", "Joko"],
            "Pekerjaan Ayah": ["Wiraswasta", "PNS"],
            "Nama Ibu": ["Ani", "Wati"],
            "Pekerjaan Ibu": ["Ibu Rumah Tangga", "Guru"],
            "Nama Wali": ["", ""],
            "Pekerjaan Wali": ["", ""]
        })
        
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            template_df.to_excel(writer, index=False, sheet_name='Template_Santri')
        
        st.download_button(
            label="⬇️ Unduh Template Excel",
            data=buffer.getvalue(),
            file_name="Template_Impor_Santri_Lengkap.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
        st.markdown("---")
        file_upload = st.file_uploader("Unggah File Excel yang sudah diisi", type=["xlsx", "xls"])
        
        if file_upload:
            try:
                df_upload = pd.read_excel(file_upload)
                st.write("🔍 Pratinjau Data:")
                st.dataframe(df_upload, height=200)
                
                if st.button("🚀 Proses Impor Data Sekarang", type="primary"):
                    list_bulk = []
                    for idx, row in df_upload.iterrows():
                        no_induk = str(row.get("No Induk", ""))
                        nama = str(row.get("Nama Lengkap", ""))
                        if not nama or nama == "nan" or not no_induk or no_induk == "nan": 
                            continue
                        
                        kelas_import = str(row.get("Kelas", ""))
                        # PENGUNCI GURU PADA IMPOR EXCEL (mencegah guru import kelas lain)
                        if db.role == "guru" and db.kelas_binaan:
                            kelas_import = db.kelas_binaan

                        data_lengkap = {
                            "kelas_santri": kelas_import,
                            "desa_kelurahan": str(row.get("Desa/Kelurahan", "")),
                            "jenis_kelamin": str(row.get("Jenis Kelamin (Laki-laki/Perempuan)", "")),
                            "tempat_lahir": str(row.get("Tempat Lahir", "")),
                            "tanggal_lahir": str(row.get("Tanggal Lahir (YYYY-MM-DD)", "")),
                            "anak_ke": str(row.get("Anak Ke-", "")),
                            "nama_ayah": str(row.get("Nama Ayah", "")),
                            "pekerjaan_ayah": str(row.get("Pekerjaan Ayah", "")),
                            "nama_ibu": str(row.get("Nama Ibu", "")),
                            "pekerjaan_ibu": str(row.get("Pekerjaan Ibu", "")),
                            "nama_wali": str(row.get("Nama Wali", "")),
                            "pekerjaan_wali": str(row.get("Pekerjaan Wali", ""))
                        }
                        # Bersihkan nilai NaN menjadi string kosong
                        for k, v in data_lengkap.items():
                            if v == "nan": data_lengkap[k] = ""

                        list_bulk.append({
                            "no_induk": no_induk,
                            "nama": nama,
                            "data_lengkap": data_lengkap
                        })
                    
                    if list_bulk:
                        sukses, pesan = db.simpan_bulk_biodata(list_bulk)
                        if sukses:
                            st.success(pesan)
                            st.rerun()
                        else:
                            st.error(pesan)
                    else:
                        st.warning("Tidak ada data valid yang ditemukan dalam file Excel.")
                        
            except Exception as e:
                st.error(f"Gagal membaca file Excel: Pastikan formatnya sesuai template. Error: {e}")

    # ==========================================
    # 3. TAB EDIT & HAPUS
    # ==========================================
    with tab_edit:
        st.subheader("Edit atau Hapus Data Santri")
        
        if not db.data_master:
            st.info("Belum ada data santri yang tersimpan.")
        else:
            map_santri = {f"{s['nama']} ({s.get('no_induk', '-')}) - Kelas {s.get('data_lengkap', {}).get('kelas_santri', '-')}": s for s in db.data_master}
            pilih_santri = st.selectbox("Pilih Santri yang ingin dikelola:", list(map_santri.keys()))
            
            if pilih_santri:
                santri = map_santri[pilih_santri]
                dl = santri.get("data_lengkap", {})
                
                with st.form("form_edit_santri"):
                    c1, c2 = st.columns(2)
                    with c1:
                        st.subheader("Identitas Dasar")
                        e_no_induk = st.text_input("Nomor Induk Santri", value=santri.get("no_induk", ""))
                        e_nama = st.text_input("Nama Lengkap Santri", value=santri.get("nama", ""))
                        
                        # --- PENGUNCI DROPDOWN KELAS ---
                        if db.role == "guru" and db.kelas_binaan:
                            e_kelas_santri = st.selectbox("Tingkatan Kelas", [db.kelas_binaan], disabled=True)
                        else:
                            try: idx_kelas = list_kelas.index(dl.get("kelas_santri"))
                            except: idx_kelas = 0
                            e_kelas_santri = st.selectbox("Tingkatan Kelas", list_kelas, index=idx_kelas if list_kelas else 0)
                            
                        try: idx_alamat = list_alamat.index(dl.get("desa_kelurahan"))
                        except: idx_alamat = 0
                        e_desa_kelurahan = st.selectbox("Desa / Kelurahan (Alamat)", list_alamat, index=idx_alamat if list_alamat else 0)
                        
                        idx_jk = 0 if dl.get("jenis_kelamin") == "Laki-laki" else 1 if dl.get("jenis_kelamin") == "Perempuan" else 0
                        e_jk = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"], index=idx_jk)
                        
                        e_tempat_lahir = st.text_input("Tempat Lahir", value=dl.get("tempat_lahir", ""))
                        e_tanggal_lahir = st.text_input("Tanggal Lahir (YYYY-MM-DD)", value=dl.get("tanggal_lahir", ""))
                        e_anak_ke = st.text_input("Anak Ke-", value=dl.get("anak_ke", ""))

                    with c2:
                        st.subheader("Data Orang Tua")
                        e_nama_ayah = st.text_input("Nama Ayah", value=dl.get("nama_ayah", ""))
                        e_pekerjaan_ayah = st.text_input("Pekerjaan Ayah", value=dl.get("pekerjaan_ayah", ""))
                        e_nama_ibu = st.text_input("Nama Ibu", value=dl.get("nama_ibu", ""))
                        e_pekerjaan_ibu = st.text_input("Pekerjaan Ibu", value=dl.get("pekerjaan_ibu", ""))

                        st.subheader("Data Wali (Opsional)")
                        e_nama_wali = st.text_input("Nama Wali", value=dl.get("nama_wali", ""))
                        e_pekerjaan_wali = st.text_input("Pekerjaan Wali", value=dl.get("pekerjaan_wali", ""))

                    st.markdown("---")
                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        submit_edit = st.form_submit_button("💾 Simpan Perubahan", type="primary", use_container_width=True)
                    with col_btn2:
                        submit_hapus = st.form_submit_button("🗑️ Hapus Data Santri", use_container_width=True)
                        
                    if submit_edit:
                        if not e_no_induk or not e_nama:
                            st.error("Nomor Induk dan Nama wajib diisi!")
                        else:
                            data_lengkap_baru = {
                                "kelas_santri": e_kelas_santri, "jenis_kelamin": e_jk, "tempat_lahir": e_tempat_lahir,
                                "tanggal_lahir": str(e_tanggal_lahir), "anak_ke": e_anak_ke, "desa_kelurahan": e_desa_kelurahan,
                                "nama_ayah": e_nama_ayah, "pekerjaan_ayah": e_pekerjaan_ayah, "nama_ibu": e_nama_ibu,
                                "pekerjaan_ibu": e_pekerjaan_ibu, "nama_wali": e_nama_wali, "pekerjaan_wali": e_pekerjaan_wali
                            }
                            # Simpan dengan id santri
                            sukses, pesan = db.simpan_biodata(e_no_induk, e_nama, data_lengkap_baru, santri_id=santri['id'])
                            if sukses:
                                st.success(pesan)
                                st.rerun()
                            else:
                                st.error(pesan)
                            
                    if submit_hapus:
                        sukses, pesan = db.hapus_biodata(santri['id'])
                        if sukses:
                            st.success(pesan)
                            st.rerun()
                        else:
                            st.error(pesan)