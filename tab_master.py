import streamlit as st
import pandas as pd
from datetime import date, datetime

def render(db):
    st.header("⚙️ Master Data & Pengaturan Madrasah")
    st.caption("Akses Pengelolaan Kurikulum dan Akun oleh Kepala Madrasah")
    
    if not db.lembaga_id:
        st.warning("⚠️ Anda belum memilih madrasah yang aktif. Silakan kembali ke Profil.")
        return

    # ==========================================
    # BAGIAN 1: PENGATURAN KELAS & KURIKULUM STANDAR
    # ==========================================
    st.markdown("---")
    st.subheader("📚 Pengaturan Kelas & Mata Pelajaran")
    
    pengaturan_lama = db.data_lembaga.get("pengaturan_master") or {}
    kelas_mapel = pengaturan_lama.get("kelas_mapel", {})
    
    teks_default_nasional = """TKA A : Qira'ati / Iqro / Tilawati, Tahfidz, Doa dan Dzikir Harian, Dinul Islam / Aqidah Akhlak, Fiqih Ibadah, Khat / Imla, Tarikh / Sejarah Islam
TKA B : Qira'ati / Iqro / Tilawati, Tahfidz, Doa dan Dzikir Harian, Dinul Islam / Aqidah Akhlak, Fiqih Ibadah, Khat / Imla, Tarikh / Sejarah Islam
TPA A : Qira'ati / Iqro / Tilawati, Tahfidz, Doa dan Dzikir Harian, Dinul Islam / Aqidah Akhlak, Fiqih Ibadah, Khat / Imla, Tarikh / Sejarah Islam
TPA B : Qira'ati / Iqro / Tilawati, Tahfidz, Doa dan Dzikir Harian, Dinul Islam / Aqidah Akhlak, Fiqih Ibadah, Khat / Imla, Tarikh / Sejarah Islam
MDTU 1 : Al-Qur'an Hadits, Aqidah Akhlak, Fiqih, Sejarah Kebudayaan Islam, Bahasa Arab
MDTU 2 : Al-Qur'an Hadits, Aqidah Akhlak, Fiqih, Sejarah Kebudayaan Islam, Bahasa Arab
MDTU 3 : Al-Qur'an Hadits, Aqidah Akhlak, Fiqih, Sejarah Kebudayaan Islam, Bahasa Arab, Tajwid
MDTU 4 : Al-Qur'an Hadits, Aqidah Akhlak, Fiqih, Sejarah Kebudayaan Islam, Bahasa Arab, Praktik Ibadah"""

    teks_awal = ""
    for kls, mapel_list in kelas_mapel.items():
        teks_awal += f"{kls} : {', '.join(mapel_list)}\n"
        
    is_kepala = getattr(db, 'role', '') in ['kepala_madrasah', 'admin']
    
    if is_kepala:
        if st.button("🔄 Muat Kurikulum Standar Nasional"):
            data_baru = {}
            for line in teks_default_nasional.strip().split('\n'):
                if ":" in line:
                    parts = line.split(":")
                    data_baru[parts[0].strip()] = [m.strip() for m in parts[1].split(",") if m.strip()]
            pengaturan_lama["kelas_mapel"] = data_baru
            db.simpan_pengaturan(pengaturan_lama)
            st.success("✅ Kurikulum Standar Nasional berhasil dimuat!")
            st.rerun()

        if not teks_awal:
            teks_awal = teks_default_nasional

        with st.expander("⚙️ Edit / Atur Daftar Kelas & Mata Pelajaran", expanded=True if not kelas_mapel else False):
            with st.form("form_mapel"):
                st.info("💡 **Format:** Nama Kelas : Mata Pelajaran 1, Mata Pelajaran 2, dst.")
                teks_input = st.text_area("Daftar Kelas & Mata Pelajaran", value=teks_awal.strip(), height=220)
                if st.form_submit_button("💾 Simpan Pengaturan Kurikulum"):
                    data_baru = {}
                    for line in teks_input.strip().split('\n'):
                        if ":" in line:
                            parts = line.split(":")
                            data_baru[parts[0].strip()] = [m.strip() for m in parts[1].split(",") if m.strip()]
                    
                    pengaturan_lama["kelas_mapel"] = data_baru
                    sukses, pesan = db.simpan_pengaturan(pengaturan_lama)
                    if sukses:
                        st.success("✅ Pengaturan kurikulum berhasil disimpan!")
                        st.rerun()
                    else:
                        st.error(pesan)
    else:
        if not kelas_mapel:
            st.warning("Belum ada mata pelajaran yang diatur oleh Kepala Madrasah.")
        else:
            st.info("Berikut adalah daftar mata pelajaran yang ditetapkan oleh madrasah:")
            for kls, mapel_list in kelas_mapel.items():
                st.write(f"**Kelas {kls}**: {', '.join(mapel_list)}")

    # ==========================================
    # BAGIAN 2: MANAJEMEN AKUN OLEH KEPALA MADRASAH
    # ==========================================
    st.markdown("---")
    st.subheader("👥 Manajemen Akun Guru & Wali Kelas")
    daftar_guru = db.get_semua_guru_lembaga()

    if is_kepala:
        t_tambah, t_edit, t_daftar = st.tabs(["➕ Tambah Guru", "✏️ Edit & Hapus", "📋 Daftar Guru"])
        
        with t_tambah:
            with st.form("form_tambah_guru"):
                st.markdown("#### 🔐 1. Data Hak Akses & Login")
                col1, col2 = st.columns(2)
                with col1:
                    nama_guru = st.text_input("Nama Lengkap Guru *")
                    username = st.text_input("NIP / Username (Untuk Login) *")
                    password = st.text_input("Password Default *", value="123456", type="password")
                with col2:
                    role = st.selectbox("Hak Akses (Role) *", ["guru", "wali_kelas"])
                    kelas_binaan = st.text_input("Kelas Binaan", placeholder="Contoh: TKA A, TPA B, MDTU 1")

                st.markdown("---")
                st.markdown("#### 💳 2. Kelengkapan Biodata Dasar")
                st.info("Catatan: Identitas lengkap akan diisi mandiri oleh Guru di tab Profil Guru.")
                col3, col4 = st.columns(2)
                with col3:
                    nik = st.text_input("NIK (Opsional)")
                    tempat_lahir = st.text_input("Tempat Lahir (Opsional)")
                    tgl_lahir = st.date_input("Tanggal Lahir", value=date(1990, 1, 1))
                    jk = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
                with col4:
                    no_hp = st.text_input("Nomor WhatsApp Aktif (Opsional)")
                    alamat = st.text_area("Alamat Lengkap (Opsional)")
                
                if st.form_submit_button("Simpan Akun Guru"):
                    if not nama_guru or not username or not password:
                        st.error("❌ Nama, Username, dan Password wajib diisi!")
                    elif role == "wali_kelas" and not kelas_binaan:
                        st.error("❌ Kelas Binaan wajib diisi untuk seorang Wali Kelas!")
                    else:
                        sukses, pesan = db.tambah_akun_guru(
                            nama_guru, username, password, role, kelas_binaan,
                            nik, jk, tempat_lahir, tgl_lahir, no_hp, alamat
                        )
                        if sukses:
                            st.success(pesan)
                            st.rerun()
                        else:
                            st.error(pesan)
                            
        with t_edit:
            if not daftar_guru:
                st.warning("Belum ada data guru terdaftar.")
            else:
                dict_guru = {f"{g['nama_guru']} (NIP: {g['username']})": g for g in daftar_guru}
                pilih_guru = st.selectbox("🔍 Pilih Guru yang ingin diubah/dihapus:", list(dict_guru.keys()))
                
                if pilih_guru:
                    g_data = dict_guru[pilih_guru]
                    with st.form("form_edit_guru"):
                        c1, c2 = st.columns(2)
                        with c1:
                            e_nama = st.text_input("Nama Lengkap", value=g_data.get('nama_guru', ''))
                            e_username = st.text_input("NIP / Username", value=g_data.get('username', ''))
                            e_password = st.text_input("🔑 Password Baru (Kosongkan jika tidak ganti)", type="password")
                        with c2:
                            roles = ["guru", "wali_kelas"]
                            idx_role = roles.index(g_data.get('role', 'guru')) if g_data.get('role') in roles else 0
                            e_role = st.selectbox("Hak Akses (Role)", roles, index=idx_role)
                            e_kelas = st.text_input("Kelas Binaan", value=g_data.get('kelas_binaan', '') or "")
                        
                        st.markdown("---")
                        c3, c4 = st.columns(2)
                        with c3:
                            e_nik = st.text_input("NIK", value=g_data.get('nik', '') or "")
                            e_tempat = st.text_input("Tempat Lahir", value=g_data.get('tempat_lahir', '') or "")
                            
                            tgl_str = g_data.get('tanggal_lahir')
                            try:
                                tgl_val = datetime.strptime(tgl_str, "%Y-%m-%d").date() if tgl_str else date(1990, 1, 1)
                            except:
                                tgl_val = date(1990, 1, 1)
                                
                            e_tgl = st.date_input("Tanggal Lahir", value=tgl_val)
                            
                            jks = ["Laki-laki", "Perempuan"]
                            jk_val = g_data.get('jenis_kelamin', 'Laki-laki')
                            idx_jk = jks.index(jk_val) if jk_val in jks else 0
                            e_jk = st.selectbox("Jenis Kelamin", jks, index=idx_jk)
                            
                        with c4:
                            e_hp = st.text_input("No WhatsApp", value=g_data.get('no_hp', '') or "")
                            e_alamat = st.text_area("Alamat Lengkap", value=g_data.get('alamat', '') or "")
                            
                        if st.form_submit_button("💾 Simpan Perubahan"):
                            sukses, pesan = db.update_akun_guru(
                                g_data['id'], e_nama, e_username, e_password, e_role, e_kelas,
                                e_nik, e_jk, e_tempat, e_tgl, e_hp, e_alamat
                            )
                            if sukses:
                                st.success(pesan)
                                st.rerun()
                            else:
                                st.error(pesan)
                                    
                    st.markdown("---")
                    konfirmasi = st.checkbox(f"Saya yakin ingin menghapus akun **{g_data['nama_guru']}**")
                    if st.button("🗑️ Hapus Akun Guru Ini"):
                        if konfirmasi:
                            sukses, pesan = db.hapus_akun_guru(g_data['id'])
                            if sukses:
                                st.success(pesan)
                                st.rerun()
                            else:
                                st.error(pesan)
                        else:
                            st.warning("Centang konfirmasi terlebih dahulu!")
                            
        with t_daftar:
            if daftar_guru:
                df_guru = pd.DataFrame(daftar_guru)
                kolom_ada = [c for c in ['nama_guru', 'username', 'role', 'kelas_binaan', 'no_hp'] if c in df_guru.columns]
                df_display = df_guru[kolom_ada].copy()
                df_display.rename(columns={'nama_guru': 'Nama Lengkap', 'username': 'Username/NIP', 'role': 'Akses', 'kelas_binaan': 'Wali Kelas', 'no_hp': 'No. WA'}, inplace=True)
                df_display.index = df_display.index + 1 
                st.dataframe(df_display, use_container_width=True)
            else:
                st.info("Belum ada data guru.")
    else:
        st.info("🔒 Pengelolaan akun guru hanya dapat dilakukan oleh Kepala Madrasah.")