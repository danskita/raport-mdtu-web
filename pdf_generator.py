import io
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import cm

def terbilang(angka):
    angka = int(angka)
    huruf = ["", "satu", "dua", "tiga", "empat", "lima", "enam", "tujuh", "delapan", "sembilan", "sepuluh", "sebelas"]
    if angka < 12: return huruf[angka]
    elif angka < 20: return terbilang(angka - 10) + " belas"
    elif angka < 100: return terbilang(angka // 10) + " puluh " + terbilang(angka % 10)
    elif angka == 100: return "seratus"
    else: return str(angka)

class PDFGenerator:
    def __init__(self, db):
        self.db = db

    def cetak_raport(self, nama_santri, semester):
        # 1. Cari data santri dan nilainya
        santri = next((s for s in self.db.data_master if s['nama'] == nama_santri), None)
        if not santri: return None
        
        nilai = self.db.get_nilai(santri['id'], semester)
        if not nilai: return None

        dl = self.db.data_lembaga

        # 2. Siapkan Canvas di dalam Memori (BytesIO)
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        lebar, tinggi = A4
        
        # 3. Mulai Menggambar PDF
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(lebar/2, tinggi - 2*cm, f"DAFTAR NILAI SEMESTER {semester}")

        c.setFont("Helvetica", 10)
        c.drawString(2*cm, tinggi - 3*cm, f"Nama Santri : {nama_santri}")
        c.drawString(2*cm, tinggi - 3.5*cm, f"No. Induk   : {santri.get('no_induk', '-')}")
        c.drawString(lebar - 8*cm, tinggi - 3*cm, f"Kelas       : {dl.get('kelas', '-')}")
        c.drawString(lebar - 8*cm, tinggi - 3.5*cm, f"Madrasah    : {dl.get('nama_madrasah', '-')}")

        # 4. Tabel Sederhana (Bisa dipercantik dengan TableStyle Anda sebelumnya)
        data_tabel = [['Mata Pelajaran', 'Angka', 'Huruf']]
        for mapel, skor in nilai['akademik'].items():
            data_tabel.append([mapel, str(skor), terbilang(skor).capitalize()])
            
        data_tabel.append(['JUMLAH', str(nilai['jumlah']), terbilang(nilai['jumlah']).capitalize()])

        tabel = Table(data_tabel, colWidths=[8*cm, 3*cm, 5*cm])
        tabel.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ]))
        
        w, h = tabel.wrap(lebar, tinggi)
        tabel.drawOn(c, 2*cm, tinggi - 5*cm - h)

        # 5. Keputusan & TTD
        y_bawah = tinggi - 7*cm - h
        c.drawString(2*cm, y_bawah, f"Keputusan: {nilai.get('status', '-')}")
        c.drawString(lebar - 7*cm, y_bawah - 2*cm, "Kepala Madrasah,")
        c.drawString(lebar - 7*cm, y_bawah - 4*cm, dl.get('kepala_madin', '....................'))

        # 6. Selesai dan Simpan ke Buffer
        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer