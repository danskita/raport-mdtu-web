import streamlit as st
import pandas as pd    # <--- TAMBAHKAN BARIS INI
from datetime import date, datetime

def render(db):
    st.header("👥 Input & Kelola Biodata Santri")
    st.caption("Khusus Wali Kelas / Guru untuk menginput dan mengedit data santri di kelasnya")
    
# ... (sisa kode di bawahnya biarkan saja, tidak perlu diubah) ...
    
    # ⛔ BLOKIR KEPALA MADRASAH
    if getattr(db, 'role', '') == 'kepala_madrasah':
        st.error("⛔ AKSES DITOLAK: Halaman ini khusus untuk Wali Kelas.")
        st.info("💡 Sesuai SOP, Kepala Madrasah tidak menginput data santri. Silakan pantau rekap data di menu **Pemantauan & Rekap**.")
        return

    if not db.lembaga_id:
        st.warning("⚠️ Anda belum memilih madrasah yang aktif. Silakan kembali ke Profil.")
        return

    kelas_default = getattr(db, 'kelas_binaan', '') or "TKA A"

    t_tambah, t_edit, t_daftar = st.tabs(["➕ Tambah Santri Baru", "✏️ Edit / Hapus Santri", "📋 Daftar Santri Kelas"])

    # ==========================================================
    # TAB 1: TAMBAH SANTRI BARU
    # ==========================================================
    with t_tambah:
        st.subheader("➕ Form Tambah Santri Baru")
        with st.form("form_tambah_santri"):
            c1, c2 = st.columns(2)
            with c1:
                no_induk = st.text_input("No. Induk / NIS *")
                nama = st.text_input("Nama Lengkap Santri *")
                
                # Kelas dikunci otomatis sesuai kelas binaan Wali Kelas
                if getattr(db, 'role', '') == 'wali_kelas' and db.kelas_binaan:
                    kelas_santri = st.text_input("Kelas Santri", value=db.kelas_binaan, disabled=True)
                else:
                    kelas_santri = st.text_input("Kelas Santri *", value=kelas_default)
                    
                jk = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
                
            with c2:
                tempat_lahir = st.text_input("Tempat Lahir")
                tgl_lahir = st.date_input("Tanggal Lahir", value=date(2018, 1, 1))
                nama_ayah = st.text_input("Nama Ayah Kandung")
                nama_ibu = st.text_input("Nama Ibu Kandung")
                
            no_hp = st.text_input("No. HP / WhatsApp Orang Tua")
            alamat = st.text_area("Alamat Lengkap Tempat Tinggal")
            
            submit_santri = st.form_submit_button("💾 Simpan Santri Baru")
            
            if submit_santri:
                if not no_induk or not nama:
                    st.error("❌ No. Induk dan Nama Lengkap wajib diisi!")
                else:
                    data_lengkap = {
                        "kelas_santri": kelas_santri,
                        "tempat_lahir": tempat_lahir,
                        "tanggal_lahir": str(tgl_lahir),
                        "jenis_kelamin": jk,
                        "nama_ayah": nama_ayah,
                        "nama_ibu": nama_ibu,
                        "no_hp": no_hp,
                        "alamat": alamat
                    }
                    sukses, pesan = db.simpan_biodata(no_induk, nama, data_lengkap)
                    if sukses:
                        st.success(f"✅ {pesan}")
                        st.rerun()
                    else:
                        st.error(f"❌ {pesan}")

    # ==========================================================
    # TAB 2: EDIT / HAPUS SANTRI
    # ==========================================================
    with t_edit:
        st.subheader("✏️ Edit atau Hapus Data Santri")
        if not db.data_master:
            st.info("Belum ada santri terdaftar di kelas ini.")
        else:
            map_santri = {f"{s['nama']} (No. Induk: {s.get('no_induk', '-')})": s for s in db.data_master}
            pilih_santri_str = st.selectbox("🔍 Pilih Santri yang ingin diubah/dihapus:", list(map_santri.keys()))
            
            if pilih_santri_str:
                s_data = map_santri[pilih_santri_str]
                d_lengkap = s_data.get("data_lengkap", {})
                
                with st.form("form_edit_santri"):
                    c1, c2 = st.columns(2)
                    with c1:
                        e_no_induk = st.text_input("No. Induk / NIS", value=s_data.get("no_induk", ""))
                        e_nama = st.text_input("Nama Lengkap", value=s_data.get("nama", ""))
                        e_kelas = st.text_input("Kelas Santri", value=d_lengkap.get("kelas_santri", db.kelas_binaan or ""))
                        
                        jks = ["Laki-laki", "Perempuan"]
                        jk_val = d_lengkap.get("jenis_kelamin", "Laki-laki")
                        idx_jk = jks.index(jk_val) if jk_val in jks else 0
                        e_jk = st.selectbox("Jenis Kelamin", jks, index=idx_jk)
                        
                    with c2:
                        e_tempat = st.text_input("Tempat Lahir", value=d_lengkap.get("tempat_lahir", ""))
                        
                        tgl_str = d_lengkap.get("tanggal_lahir")
                        try:
                            tgl_val = datetime.strptime(tgl_str, "%Y-%m-%d").date() if tgl_str else date(2018, 1, 1)
                        except:
                            tgl_val = date(2018, 1, 1)
                            
                        e_tgl = st.date_input("Tanggal Lahir", value=tgl_val)
                        e_ayah = st.text_input("Nama Ayah Kandung", value=d_lengkap.get("nama_ayah", ""))
                        e_ibu = st.text_input("Nama Ibu Kandung", value=d_lengkap.get("nama_ibu", ""))
                        
                    e_hp = st.text_input("No. HP / WhatsApp", value=d_lengkap.get("no_hp", ""))
                    e_alamat = st.text_area("Alamat Lengkap", value=d_lengkap.get("alamat", ""))
                    
                    submit_edit = st.form_submit_button("💾 Simpan Perubahan Santri")
                    
                    if submit_edit:
                        data_update = {
                            "kelas_santri": e_kelas,
                            "tempat_lahir": e_tempat,
                            "tanggal_lahir": str(e_tgl),
                            "jenis_kelamin": e_jk,
                            "nama_ayah": e_ayah,
                            "nama_ibu": e_ibu,
                            "no_hp": e_hp,
                            "alamat": e_alamat
                        }
                        sukses, pesan = db.simpan_biodata(e_no_induk, e_nama, data_update, santri_id=s_data['id'])
                        if sukses:
                            st.success(f"✅ {pesan}")
                            st.rerun()
                        else:
                            st.error(f"❌ {pesan}")
                            
                st.markdown("---")
                st.error("⚠️ Menghapus santri akan menghapus seluruh data nilai dan absensinya secara permanen.")
                konfirmasi = st.checkbox(f"Saya yakin ingin menghapus santri **{s_data['nama']}**")
                if st.button("🗑️ Hapus Santri Ini Permanen"):
                    if konfirmasi:
                        sukses, pesan = db.hapus_biodata(s_data['id'])
                        if sukses:
                            st.success(f"✅ {pesan}")
                            st.rerun()
                        else:
                            st.error(f"❌ {pesan}")
                    else:
                        st.warning("Centang kotak konfirmasi terlebih dahulu!")

    # ==========================================================
    # TAB 3: DAFTAR SANTRI KELAS
    # ==========================================================
    with t_daftar:
        st.subheader(f"📋 Daftar Santri Kelas {db.kelas_binaan if db.kelas_binaan else ''}")
        if not db.data_master:
            st.info("Belum ada santri terdaftar di kelas ini.")
        else:
            list_tampil = []
            for s in db.data_master:
                dl = s.get("data_lengkap", {})
                list_tampil.append({
                    "No. Induk": s.get("no_induk", "-"),
                    "Nama Santri": s.get("nama", "-"),
                    "L/P": dl.get("jenis_kelamin", "-"),
                    "Tempat Lahir": dl.get("tempat_lahir", "-"),
                    "Tgl Lahir": dl.get("tanggal_lahir", "-"),
                    "Nama Ayah": dl.get("nama_ayah", "-"),
                    "No. WA Ortu": dl.get("no_hp", "-")
                })
            df = pd.DataFrame(list_tampil)
            df.index = df.index + 1
            st.dataframe(df, use_container_width=True)