import streamlit as st
import base64
from pdf_generator import PDFGenerator

def tampilkan_pdf(buffer):
    """Fungsi ajaib untuk menampilkan PDF langsung di layar browser"""
    base64_pdf = base64.b64encode(buffer.read()).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="800" type="application/pdf"></iframe>'
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
    
    # MEMBUAT 3 SUB-TAB (Sama persis seperti tab_pratinjau_utama.py Anda)
    sub_cover, sub_ganjil, sub_genap = st.tabs([
        "📔 Cover Raport", "📘 Semester 1 (Ganjil)", "📗 Semester 2 (Genap)"
    ])

    gen = PDFGenerator(db)

    # ========================================
    # 1. TAB COVER RAPORT
    # ========================================
    with sub_cover:
        if st.button("⚙️ Buat Preview Cover", key="btn_cover"):
            with st.spinner("Membuat Cover..."):
                pdf_buffer = gen.cetak_cover(pilih_nama)
                if pdf_buffer:
                    st.download_button("⬇️ Download Cover (PDF)", data=pdf_buffer, file_name=f"Cover_{pilih_nama}.pdf", mime="application/pdf")
                    tampilkan_pdf(pdf_buffer)

    # ========================================
    # 2. TAB SEMESTER 1 (GANJIL)
    # ========================================
    with sub_ganjil:
        if st.button("⚙️ Buat Preview Ganjil", key="btn_ganjil"):
            santri = next((s for s in db.data_master if s['nama'] == pilih_nama), None)
            if not db.get_nilai(santri['id'], 1):
                st.error(f"❌ {pilih_nama} belum memiliki data nilai untuk Semester Ganjil.")
            else:
                with st.spinner("Membuat Raport Ganjil..."):
                    pdf_buffer = gen.cetak_raport(pilih_nama, 1)
                    if pdf_buffer:
                        st.download_button("⬇️ Download Raport Ganjil (PDF)", data=pdf_buffer, file_name=f"Raport_Ganjil_{pilih_nama}.pdf", mime="application/pdf")
                        tampilkan_pdf(pdf_buffer)

    # ========================================
    # 3. TAB SEMESTER 2 (GENAP)
    # ========================================
    with sub_genap:
        if st.button("⚙️ Buat Preview Genap", key="btn_genap"):
            santri = next((s for s in db.data_master if s['nama'] == pilih_nama), None)
            if not db.get_nilai(santri['id'], 2):
                st.error(f"❌ {pilih_nama} belum memiliki data nilai untuk Semester Genap.")
            else:
                with st.spinner("Membuat Raport Genap..."):
                    pdf_buffer = gen.cetak_raport(pilih_nama, 2)
                    if pdf_buffer:
                        st.download_button("⬇️ Download Raport Genap (PDF)", data=pdf_buffer, file_name=f"Raport_Genap_{pilih_nama}.pdf", mime="application/pdf")
                        tampilkan_pdf(pdf_buffer)