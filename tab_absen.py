import streamlit as st
import datetime

def render(db):
    st.header("📅 Buku Absen Harian")
    
    if not db.lembaga_id: 
        return st.warning("⚠️ Anda belum login.")
    
    if not db.data_master:
        return st.info("Belum ada data santri untuk diabsen. Silakan isi biodata terlebih dahulu.")

    # 1. Pilih Tanggal
    col_tgl, _ = st.columns([1, 2])
    with col_tgl:
        tanggal_absen = st.date_input("Pilih Tanggal Absensi", datetime.date.today())

    st.markdown("---")

    # 2. Tarik data absen jika sebelumnya sudah pernah diabsen di tanggal ini
    data_absen_lama = db.get_absensi_harian(tanggal_absen)

    # 3. Tampilkan Form Absensi
    st.write(f"**Daftar Kehadiran Santri (Tanggal: {tanggal_absen.strftime('%d-%m-%Y')})**")
    
    with st.form("form_absen_harian"):
        pilihan_baru = {}
        
        # Header Tabel
        c_no, c_nama, c_status = st.columns([1, 4, 3])
        c_no.markdown("**No.**")
        c_nama.markdown("**Nama Santri**")
        c_status.markdown("**Status Kehadiran**")
        st.markdown("---")
        
        opsi_status = ["Hadir", "Sakit", "Izin", "Alpa"]
        
        for idx, santri in enumerate(db.data_master):
            c_no, c_nama, c_status = st.columns([1, 4, 3])
            c_no.write(idx + 1)
            
            # Tampilkan Nama dan Kelas (Karena sudah ada filter guru di database, ini aman)
            kelas = santri.get("data_lengkap", {}).get("kelas_santri", "-")
            c_nama.write(f"{santri['nama']} (Kelas {kelas})")
            
            status_lama = data_absen_lama.get(santri['id'], "Hadir")
            idx_opsi = opsi_status.index(status_lama) if status_lama in opsi_status else 0
                
            with c_status:
                pilihan_baru[santri['id']] = st.selectbox(
                    "Status", 
                    opsi_status, 
                    index=idx_opsi, 
                    key=f"absen_{santri['id']}", 
                    label_visibility="collapsed"
                )
                
        st.markdown("---")
        submit_absen = st.form_submit_button("💾 Simpan Absensi Harian", type="primary", use_container_width=True)
        
        if submit_absen:
            sukses, pesan = db.simpan_absensi_harian(tanggal_absen, pilihan_baru)
            if sukses:
                st.success(pesan)
                st.rerun()
            else:
                st.error(pesan)