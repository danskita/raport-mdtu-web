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
        lebar_kertas, tinggi_kertas = A4
        
        # 3. MENGGAMBAR JUDUL
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(lebar_kertas/2, tinggi_kertas - 2*cm, "DAFTAR NILAI")

        # 4. MENGGAMBAR KOP LENGKAP
        c.setFont("Helvetica", 10)
        y_kop = tinggi_kertas - 3*cm
        
        # Kop Kiri
        c.drawString(2*cm, y_kop, "Nama MDTU")
        c.drawString(4.5*cm, y_kop, f": {dl.get('nama_madrasah', '-')}")
        c.drawString(2*cm, y_kop - 0.5*cm, "Alamat")
        c.drawString(4.5*cm, y_kop - 0.5*cm, f": {dl.get('desa_kelurahan', '-')}")
        c.drawString(2*cm, y_kop - 1*cm, "Nama Santri")
        c.drawString(4.5*cm, y_kop - 1*cm, f": {nama_santri}")
        c.drawString(2*cm, y_kop - 1.5*cm, "No. Induk")
        c.drawString(4.5*cm, y_kop - 1.5*cm, f": {santri.get('no_induk', '-')}")

        # Kop Kanan
        x_kanan = lebar_kertas - 8*cm
        c.drawString(x_kanan, y_kop, "Kelas")
        c.drawString(x_kanan + 3*cm, y_kop, f": {dl.get('kelas', '-')}")
        c.drawString(x_kanan, y_kop - 0.5*cm, "Semester")
        c.drawString(x_kanan + 3*cm, y_kop - 0.5*cm, f": {semester}")
        c.drawString(x_kanan, y_kop - 1*cm, "Tahun Pelajaran")
        c.drawString(x_kanan + 3*cm, y_kop - 1*cm, f": {dl.get('tahun_pelajaran', '-')}")

        # 5. MENYUSUN TABEL NILAI (Dengan Span dan Desain Asli)
        data_tabel = [
            ['No.', 'Mata Pelajaran', 'Nilai Prestasi', '', 'Rata-rata\nKelas'],
            ['', '', 'Angka', 'Huruf', '']
        ]

        mapels = [
            ("1", "Keagamaan", True),
            ("a", "AL QUR'AN", False), ("b", "AL HADITS", False), ("c", "AQIDAH", False),
            ("d", "AKHLAQ", False), ("e", "FIQIH", False), ("f", "TARIKH ISLAM", False),
            ("g", "BAHASA ARAB", False), ("h", "NAHWU", False), ("i", "SHARAF", False),
            ("2", "Muatan Lokal", True),
            ("a", "PRAKTIK IBADAH", False), ("b", "BTQ", False), ("c", "Ke-NU-an", False)
        ]

        for no, teks, is_judul in mapels:
            if is_judul:
                data_tabel.append([no, teks, '', '', ''])
            else:
                skor = nilai['akademik'].get(teks, 0)
                data_tabel.append([no, f"   {teks}", f"{skor:.0f}", terbilang(skor).capitalize(), '-'])

        data_tabel.append(['', 'JUMLAH', f"{nilai['jumlah']:.0f}", terbilang(nilai['jumlah']).capitalize(), '-'])

        tabel = Table(data_tabel, colWidths=[1*cm, 6*cm, 2*cm, 6*cm, 2*cm])
        
        style_tabel = TableStyle([
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (1,2), (1,-2), 'LEFT'),
            ('FONTNAME', (0,0), (-1,1), 'Helvetica-Bold'),
            ('BACKGROUND', (0,0), (-1,1), colors.lightgrey),
            
            # Penggabungan Header (SPAN)
            ('SPAN', (0,0), (0,1)),
            ('SPAN', (1,0), (1,1)),
            ('SPAN', (2,0), (3,0)),
            ('SPAN', (4,0), (4,1)),
            
            # Penggabungan Judul Keagamaan & Muatan Lokal
            ('SPAN', (2,2), (4,2)), 
            ('FONTNAME', (0,2), (1,2), 'Helvetica-Bold'),
            ('SPAN', (2,12), (4,12)),
            ('FONTNAME', (0,12), (1,12), 'Helvetica-Bold'),
            
            # Baris Bawah (Jumlah)
            ('SPAN', (0,-1), (0,-1)),
            ('FONTNAME', (1,-1), (-1,-1), 'Helvetica-Bold')
        ])
        tabel.setStyle(style_tabel)
        
        w, h = tabel.wrap(lebar_kertas, tinggi_kertas)
        y_tabel = y_kop - 2*cm - h
        tabel.drawOn(c, 2*cm, y_tabel)

        # 6. TABEL KEPRIBADIAN & ABSENSI
        y_bawah = y_tabel - 0.5*cm
        p = nilai["kepribadian"]
        a = nilai["absen"]
        data_bawah = [
            ["Kepribadian", "1. Kelakuan\n2. Kerajinan\n3. Kebersihan", f"{p.get('Kelakuan','-')}\n{p.get('Kerajinan','-')}\n{p.get('Kebersihan','-')}"],
            ["Ketidakhadiran", "1. Sakit\n2. Izin\n3. Alpa", f"{a.get('Sakit','0')} hari\n{a.get('Izin','0')} hari\n{a.get('Alpa','0')} hari"],
            [f"Catatan Wali Kelas:\n{nilai.get('catatan', '-')}", "", ""]
        ]
        
        tabel_bawah = Table(data_bawah, colWidths=[4*cm, 9*cm, 4*cm])
        tabel_bawah.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ALIGN', (0,0), (0,-2), 'CENTER'),
            ('ALIGN', (2,0), (2,-2), 'CENTER'),
            ('SPAN', (0,2), (2,2)) # Span Catatan
        ]))
        wb, hb = tabel_bawah.wrap(lebar_kertas, tinggi_kertas)
        y_bawah = y_bawah - hb
        tabel_bawah.drawOn(c, 2*cm, y_bawah)

        # Keputusan Kenaikan/Kelulusan
        c.setFont("Helvetica-Bold", 10)
        c.drawString(2*cm, y_bawah - 0.5*cm, f"Keputusan: {nilai.get('status', '-')}")

        # 7. TANDA TANGAN POSISI RAPI
        c.setFont("Helvetica", 10)
        y_ttd = y_bawah - 2*cm
        c.drawString(2*cm, y_ttd, f"Diberikan di : {dl.get('tempat_raport', '-')}")
        c.drawString(2*cm, y_ttd - 0.5*cm, f"Tanggal      : {dl.get('tanggal_raport', '-')}")
        
        c.drawCentredString(lebar_kertas/2, y_ttd - 1.5*cm, "Mengetahui")
        c.drawString(2.5*cm, y_ttd - 2*cm, "Kepala Madrasah,")
        c.drawCentredString(lebar_kertas/2, y_ttd - 2*cm, "Orang Tua,")
        c.drawString(lebar_kertas - 5*cm, y_ttd - 2*cm, "Wali Kelas,")

        c.setFont("Helvetica-Bold", 10)
        c.drawString(2.5*cm, y_ttd - 4.5*cm, dl.get('kepala_madin', '........................'))
        c.drawString(lebar_kertas - 5*cm, y_ttd - 4.5*cm, dl.get('wali_kelas', '........................'))
        
        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer