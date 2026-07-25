import streamlit as st
import base64
import pandas as pd
from pdf_generator import PDFGenerator

def tampilkan_pdf(buffer):
    base64_pdf = base64.b64encode(buffer.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="600" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

def render(db):
    st.header("🖨️ Pratinjau & Cetak Raport")
    
    # ⛔ BLOKIR KEPALA MADRASAH
    if getattr(db, 'role', '') == 'kepala_madrasah':
        st.error("⛔ AKSES DITOLAK: Halaman ini khusus untuk Wali Kelas.")
        st.info("💡 Sesuai SOP, Kepala Madrasah tidak mencetak fisik raport. Pencetakan fisik dilakukan oleh Wali Kelas.")
        return
    
    if not db.data_master:
        st.warning("⚠️ Belum ada data santri di kelas ini. Silakan tambahkan santri terlebih dahulu di menu **Input Biodata**.")
        return

    daftar_nama = [s['nama'] for s in db.data_master]
    pilih_nama = st.selectbox("Pilih Nama Santri untuk dipratinjau:", daftar_nama)

    st.markdown("---")
    
    sub_cover, sub_ganjil, sub_genap = st.tabs([
        "📔 Cover Raport", "📘 Semester 1 (Ganjil)", "📗 Semester 2 (Genap)"
    ])

    gen = PDFGenerator(db)
    santri = next((s for s in db.data_master if s['nama'] == pilih_nama), None)

    with sub_cover:
        if st.button("⚙️ Buat Preview Cover", key="btn_cover"):
            with st.spinner("Membuat Cover..."):
                st.session_state.pdf_cover = gen.cetak_cover(pilih_nama)
                
        if 'pdf_cover' in st.session_state and st.session_state.pdf_cover:
            st.download_button("⬇️ Download Cover (PDF)", data=st.session_state.pdf_cover, file_name=f"Cover_{pilih_nama}.pdf", mime="application/pdf")
            st.session_state.pdf_cover.seek(0)
            tampilkan_pdf(st.session_state.pdf_cover)

    with sub_ganjil:
        nilai_g = db.get_nilai(santri['id'], 1) if santri else None
        if st.button("⚙️ Buat Preview Ganjil", key="btn_ganjil"):
            if not nilai_g:
                st.error(f"❌ {pilih_nama} belum memiliki data nilai untuk Semester Ganjil.")
                st.session_state.pdf_ganjil = None
            else:
                with st.spinner("Membuat Raport Ganjil..."):
                    st.session_state.pdf_ganjil = gen.cetak_raport(pilih_nama, 1)
                    
        if 'pdf_ganjil' in st.session_state and st.session_state.pdf_ganjil:
            st.download_button("⬇️ Download Raport Ganjil (PDF)", data=st.session_state.pdf_ganjil, file_name=f"Raport_Ganjil_{pilih_nama}.pdf", mime="application/pdf")
            st.session_state.pdf_ganjil.seek(0)
            tampilkan_pdf(st.session_state.pdf_ganjil)

    with sub_genap:
        nilai_e = db.get_nilai(santri['id'], 2) if santri else None
        if st.button("⚙️ Buat Preview Genap", key="btn_genap"):
            if not nilai_e:
                st.error(f"❌ {pilih_nama} belum memiliki data nilai untuk Semester Genap.")
                st.session_state.pdf_genap = None
            else:
                with st.spinner("Membuat Raport Genap..."):
                    st.session_state.pdf_genap = gen.cetak_raport(pilih_nama, 2)
                    
        if 'pdf_genap' in st.session_state and st.session_state.pdf_genap:
            st.download_button("⬇️ Download Raport Genap (PDF)", data=st.session_state.pdf_genap, file_name=f"Raport_Genap_{pilih_nama}.pdf", mime="application/pdf")
            st.session_state.pdf_genap.seek(0)
            tampilkan_pdf(st.session_state.pdf_genap)