import streamlit as st
from pdf_generator import PDFGenerator

def render(db):
    st.header("🖨️ Cetak Raport Santri")
    st.write("Pilih nama santri dan semester untuk menghasilkan file PDF Raport.")

    if not db.data_master:
        st.warning("Data santri masih kosong.")
        return

    # Ambil daftar nama
    daftar_nama = [s['nama'] for s in db.data_master]
    
    col1, col2 = st.columns(2)
    with col1:
        pilih_nama = st.selectbox("Pilih Santri:", daftar_nama)
    with col2:
        pilih_semester = st.radio("Pilih Semester:", [1, 2], horizontal=True)

    # Tombol Generate
    if st.button("⚙️ Buat File PDF"):
        # Cek apakah santri punya nilai di semester tersebut
        santri = next((s for s in db.data_master if s['nama'] == pilih_nama), None)
        nilai_cek = db.get_nilai(santri['id'], pilih_semester)

        if not nilai_cek:
            st.error(f"❌ {pilih_nama} belum memiliki data nilai untuk Semester {pilih_semester}.")
        else:
            with st.spinner("Sedang merakit PDF..."):
                gen = PDFGenerator(db)
                pdf_buffer = gen.cetak_raport(pilih_nama, pilih_semester)
                
                if pdf_buffer:
                    st.success("✅ PDF Berhasil Dibuat!")
                    st.download_button(
                        label="⬇️ Download Raport (PDF)",
                        data=pdf_buffer,
                        file_name=f"Raport_{pilih_nama.replace(' ', '_')}_Smstr{pilih_semester}.pdf",
                        mime="application/pdf"
                    )