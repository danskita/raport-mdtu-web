import io
import base64
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader

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

    def _get_dl_flat(self):
        """Membongkar data profil_lengkap (JSONB) agar mudah dibaca oleh PDF"""
        dl_raw = self.db.data_lembaga
        profil = dl_raw.get("profil_lengkap", {})
        dl_flat = {**dl_raw, **profil}
        dl_flat["nomor_statistik"] = dl_raw.get("nsm", "-")
        return dl_flat

    def cetak_cover(self, nama_santri):
        santri = next((s for s in self.db.data_master if s['nama'] == nama_santri), None)
        if not santri: return None
        dl = self._get_dl_flat()

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        lebar, tinggi = A4

        logo_b64 = dl.get("logo", "")
        if logo_b64:
            try:
                logo_data = base64.b64decode(logo_b64)
                logo_img = ImageReader(io.BytesIO(logo_data))
                c.drawImage(logo_img, lebar/2 - 2*cm, tinggi - 7*cm, 4*cm, 4*cm, mask='auto')
            except Exception as e:
                c.rect(lebar/2 - 2*cm, tinggi - 6*cm, 4*cm, 4*cm)
                c.drawCentredString(lebar/2, tinggi - 4*cm, "LOGO ERROR")
        else:
            c.rect(lebar/2 - 2*cm, tinggi - 6*cm, 4*cm, 4*cm)
            c.setFont("Helvetica-Bold", 10)
            c.drawCentredString(lebar/2, tinggi - 4*cm, "LOGO")
            c.drawCentredString(lebar/2, tinggi - 4.5*cm, "MADRASAH")

        c.setFont("Helvetica-Bold", 28)
        c.drawCentredString(lebar/2, tinggi - 9*cm, "BUKU RAPORT")
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(lebar/2, tinggi - 10.5*cm, "MADRASAH DINIYAH TAKMILIYAH ULA")

        c.setFont("Helvetica", 12)
        y_lembaga = tinggi - 13*cm
        labels = [
            ("NAMA MADRASAH", dl.get("nama_madrasah", "-")),
            ("NOMOR STATISTIK", dl.get("nomor_statistik", "-")),
            ("ALAMAT", dl.get("alamat", "-")),
            ("DESA/KELURAHAN", dl.get("desa_kelurahan", "-")),
            ("KECAMATAN", dl.get("kecamatan", "-")),
            ("KABUPATEN/KOTA", dl.get("kabupaten_kota", "-")),
            ("PROVINSI", dl.get("provinsi", "-"))
        ]
        
        for i, (lbl, val) in enumerate(labels):
            y_pos = y_lembaga - (i * 0.8 * cm)
            c.drawString(4*cm, y_pos, lbl)
            c.drawString(9*cm, y_pos, f": {val}")

        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(lebar/2, 8*cm, "NAMA SANTRI")
        
        c.setFont("Helvetica-Bold", 22)
        c.drawCentredString(lebar/2, 6.5*cm, nama_santri)

        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(lebar/2, 5*cm, f"Nomor Induk : {santri.get('no_induk', '-')}")

        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer

    def cetak_raport(self, nama_santri, semester):
        santri = next((s for s in self.db.data_master if s['nama'] == nama_santri), None)
        if not santri: return None
        
        nilai = self.db.get_nilai(santri['id'], semester)
        if not nilai: return None

        rank, total_siswa = self.db.get_ranking(santri['id'], semester)
        dl = self._get_dl_flat()
        
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        lebar, tinggi = A4
        
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(lebar/2, tinggi - 2*cm, "DAFTAR NILAI")

        c.setFont("Helvetica", 10)
        y_kop = tinggi - 3*cm
        c.drawString(2*cm, y_kop, "Nama MDTU")
        c.drawString(4.5*cm, y_kop, f": {dl.get('nama_madrasah', '-')}")
        c.drawString(2*cm, y_kop - 0.5*cm, "Alamat")
        c.drawString(4.5*cm, y_kop - 0.5*cm, f": {dl.get('desa_kelurahan', '-')}")
        c.drawString(2*cm, y_kop - 1*cm, "Nama Santri")
        c.drawString(4.5*cm, y_kop - 1*cm, f": {nama_santri}")
        c.drawString(2*cm, y_kop - 1.5*cm, "No. Induk")
        c.drawString(4.5*cm, y_kop - 1.5*cm, f": {santri.get('no_induk', '-')}")

        sem_teks = "1 (SATU)" if semester == 1 else "2 (DUA)"
        x_kanan = lebar - 8*cm
        c.drawString(x_kanan, y_kop, "Kelas")
        c.drawString(x_kanan + 3*cm, y_kop, f": {dl.get('kelas', '-')}")
        c.drawString(x_kanan, y_kop - 0.5*cm, "Semester")
        c.drawString(x_kanan + 3*cm, y_kop - 0.5*cm, f": {sem_teks}")
        c.drawString(x_kanan, y_kop - 1*cm, "Tahun Pelajaran")
        c.drawString(x_kanan + 3*cm, y_kop - 1*cm, f": {dl.get('tahun_pelajaran', '-')}")

        data_tabel = [['No.', 'Mata Pelajaran', 'Nilai Prestasi', '', 'Rata-rata\nKelas'], ['', '', 'Angka', 'Huruf', '']]
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
        data_tabel.append([f"Peringkat Kelas ke {rank} dari {total_siswa} santri", '', '', '', ''])

        tabel = Table(data_tabel, colWidths=[1*cm, 6*cm, 2*cm, 6*cm, 2*cm])
        tabel.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-3), 1, colors.black),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (1,2), (1,-3), 'LEFT'), ('FONTNAME', (0,0), (-1,1), 'Helvetica-Bold'),
            ('BACKGROUND', (0,0), (-1,1), colors.lightgrey),
            ('SPAN', (0,0), (0,1)), ('SPAN', (1,0), (1,1)), ('SPAN', (2,0), (3,0)), ('SPAN', (4,0), (4,1)),
            ('SPAN', (2,2), (4,2)), ('FONTNAME', (0,2), (1,2), 'Helvetica-Bold'),
            ('SPAN', (2,12), (4,12)), ('FONTNAME', (0,12), (1,12), 'Helvetica-Bold'),
            ('SPAN', (0,-2), (0,-2)), ('FONTNAME', (1,-2), (-1,-2), 'Helvetica-Bold'), ('BOX', (0,-2), (-1,-2), 1, colors.black),
            ('SPAN', (0,-1), (-1,-1)), ('ALIGN', (0,-1), (-1,-1), 'LEFT'), ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'), ('BOX', (0,-1), (-1,-1), 1, colors.black)
        ]))
        w, h = tabel.wrap(lebar, tinggi)
        y_tabel = y_kop - 2*cm - h
        tabel.drawOn(c, 2*cm, y_tabel)

        y_bawah = y_tabel - 0.5*cm

        if semester == 2:
            status_teks = f"KEPUTUSAN :\nDengan memperhatikan hasil yang dicapai pada Semester 1 dan 2,\nsantri ini ditetapkan : STATUS {nilai.get('status', '-').upper()}"
            c.setFont("Helvetica-Bold", 10)
            t = c.beginText(2*cm, y_bawah)
            for line in status_teks.split('\n'):
                t.textLine(line)
            c.drawText(t)
            y_bawah -= 2*cm 

        p = nilai["kepribadian"]
        a = nilai["absen"]
        data_bawah = [
            ["Kepribadian", "1. Kelakuan\n2. Kerajinan\n3. Kebersihan", f"{p.get('Kelakuan','-')}\n{p.get('Kerajinan','-')}\n{p.get('Kebersihan','-')}"],
            ["Ketidakhadiran", "1. Sakit\n2. Izin\n3. Alpa", f"{a.get('Sakit','0')} hari\n{a.get('Izin','0')} hari\n{a.get('Alpa','0')} hari"],
            [f"Catatan Wali Kelas:\n{nilai.get('catatan', '-')}", "", ""]
        ]
        
        tabel_bawah = Table(data_bawah, colWidths=[4*cm, 9*cm, 4*cm])
        tabel_bawah.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 1, colors.black), ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ALIGN', (0,0), (0,-2), 'CENTER'), ('ALIGN', (2,0), (2,-2), 'CENTER'),
            ('SPAN', (0,2), (2,2))
        ]))
        wb, hb = tabel_bawah.wrap(lebar, tinggi)
        y_bawah = y_bawah - hb
        tabel_bawah.drawOn(c, 2*cm, y_bawah)

        c.setFont("Helvetica", 10)
        y_ttd = y_bawah - 1.5*cm
        c.drawString(2*cm, y_ttd, f"Diberikan di : {dl.get('tempat_raport', '-')}")
        c.drawString(2*cm, y_ttd - 0.5*cm, f"Tanggal      : {dl.get('tanggal_raport', '-')}")
        c.drawCentredString(lebar/2, y_ttd - 1.5*cm, "Mengetahui")
        c.drawString(2.5*cm, y_ttd - 2*cm, "Kepala Madrasah,")
        c.drawCentredString(lebar/2, y_ttd - 2*cm, "Orang Tua,")
        c.drawString(lebar - 5*cm, y_ttd - 2*cm, "Wali Kelas,")

        c.setFont("Helvetica-Bold", 10)
        c.drawString(2.5*cm, y_ttd - 4.5*cm, dl.get('kepala_madin', '........................'))
        c.drawString(lebar - 5*cm, y_ttd - 4.5*cm, dl.get('wali_kelas', '........................'))
        
        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer