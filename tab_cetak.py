import streamlit as st
import base64
import pandas as pd
from pdf_generator import PDFGenerator

def tampilkan_pdf(buffer):
    """Fungsi untuk menampilkan PDF (Lancar di Laptop, beberapa HP mungkin blank)"""
    base64_pdf = base64.b64encode(buffer.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def render(db):
    st.header("🖨️ Pratinjau & Cetak Raport")
    
    if not db.data_master:
        st.warning("Data santri masih kosong.")
        return

    # Ambil daftar nama
    daftar_nama = [s['nama'] for s in db.data_master]
    pilih_nama = st.selectbox("Pilih Nama Santri untuk dipratinjau:", daftar_nama)

    st.markdown("---")
    
    # MEMBUAT 3 SUB-TAB UTAMA
    sub_cover, sub_ganjil, sub_genap = st.tabs([
        "📔 Cover Raport", "📘 Semester 1 (Ganjil)", "📗 Semester 2 (Genap)"
    ])

    gen = PDFGenerator(db)
    santri = next((s for s in db.data_master if s['nama'] == pilih_nama), None)

    # ========================================
    # 1. TAB COVER RAPORT
    # ========================================
    with sub_cover:
        if st.button("⚙️ Buat Preview Cover", key="btn_cover"):
            with st.spinner("Membuat Cover..."):
                st.session_state.pdf_cover = gen.cetak_cover(pilih_nama)
                
        if 'pdf_cover' in st.session_state and st.session_state.pdf_cover:
            st.download_button("⬇️ Download Cover (PDF)", data=st.session_state.pdf_cover, file_name=f"Cover_{pilih_nama}.pdf", mime="application/pdf")
            
            # --- TAMPILAN RINGKAS UNTUK HP ---
            st.subheader("📱 Ringkasan Cover (Tampilan HP)")
            st.write(f"**Nama Santri:** {pilih_nama}")
            st.write(f"**No. Induk:** {santri.get('no_induk', '-')}")
            st.write(f"**Madrasah:** {db.data_lembaga.get('nama_madrasah', '-')}")
            
            st.info("💡 *Catatan HP:* Jika kotak PDF di bawah ini kosong, silakan langsung klik tombol **Download Cover (PDF)** di atas.")
            st.session_state.pdf_cover.seek(0)
            tampilkan_pdf(st.session_state.pdf_cover)

    # ========================================
    # 2. TAB SEMESTER 1 (GANJIL)
    # ========================================
    with sub_ganjil:
        if st.button("⚙️ Buat Preview Ganjil", key="btn_ganjil"):
            if not db.get_nilai(santri['id'], 1):
                st.error(f"❌ {pilih_nama} belum memiliki data nilai untuk Semester Ganjil.")
                st.session_state.pdf_ganjil = None
            else:
                with st.spinner("Membuat Raport Ganjil..."):
                    st.session_state.pdf_ganjil = gen.cetak_raport(pilih_nama, 1)
                    
        if 'pdf_ganjil' in st.session_state and st.session_state.pdf_ganjil:
            st.download_button("⬇️ Download Raport Ganjil (PDF)", data=st.session_state.pdf_ganjil, file_name=f"Raport_Ganjil_{pilih_nama}.pdf", mime="application/pdf")
            
            # --- TAMPILAN RINGKAS UNTUK HP ---
            nilai_g = db.get_nilai(santri['id'], 1)
            if nilai_g:
                st.subheader("📱 Ringkasan Nilai Ganjil (Tampilan HP)")
                df_g = pd.DataFrame(list(nilai_g['akademik'].items()), columns=['Mata Pelajaran', 'Nilai'])
                st.dataframe(df_g, width='stretch', hide_index=True)
                st.write(f"**Jumlah Nilai:** {nilai_g['jumlah']} | **Rata-rata:** {nilai_g['rata_rata']:.2f}")
                st.write(f"**Catatan Wali Kelas:** {nilai_g.get('catatan', '-')}")
            
            st.info("💡 *Catatan HP:* Jika kotak PDF di bawah ini kosong, silakan langsung klik tombol **Download Raport Ganjil (PDF)** di atas.")
            st.session_state.pdf_ganjil.seek(0)
            tampilkan_pdf(st.session_state.pdf_ganjil)

    # ========================================
    # 3. TAB SEMESTER 2 (GENAP)
    # ========================================
    with sub_genap:
        if st.button("⚙️ Buat Preview Genap", key="btn_genap"):
            if not db.get_nilai(santri['id'], 2):
                st.error(f"❌ {pilih_nama} belum memiliki data nilai untuk Semester Genap.")
                st.session_state.pdf_genap = None
            else:
                with st.spinner("Membuat Raport Genap..."):
                    st.session_state.pdf_genap = gen.cetak_raport(pilih_nama, 2)
                    
        if 'pdf_genap' in st.session_state and st.session_state.pdf_genap:
            st.download_button("⬇️ Download Raport Genap (PDF)", data=st.session_state.pdf_genap, file_name=f"Raport_Genap_{pilih_nama}.pdf", mime="application/pdf")
            
            # --- TAMPILAN RINGKAS UNTUK HP ---
            nilai_e = db.get_nilai(santri['id'], 2)
            if nilai_e:
                st.subheader("📱 Ringkasan Nilai Genap (Tampilan HP)")
                df_e = pd.DataFrame(list(nilai_e['akademik'].items()), columns=['Mata Pelajaran', 'Nilai'])
                st.dataframe(df_e, width='stretch', hide_index=True)
                st.write(f"**Jumlah Nilai:** {nilai_e['jumlah']} | **Rata-rata:** {nilai_e['rata_rata']:.2f}")
                st.write(f"**Keputusan Akhir:** {nilai_e.get('status', '-')}")
                st.write(f"**Catatan Wali Kelas:** {nilai_e.get('catatan', '-')}")
                
            st.info("💡 *Catatan HP:* Jika kotak PDF di bawah ini kosong, silakan langsung klik tombol **Download Raport Genap (PDF)** di atas.")
            st.session_state.pdf_genap.seek(0)
            tampilkan_pdf(st.session_state.pdf_genap)