import io
import base64
from datetime import date
from reportlab.pdfgen import canvas
from reportlab.platypus import Table, TableStyle, Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader

# =========================================================
# DEFINISI KERTAS F4 STANDAR INDONESIA (21.5 cm x 33.0 cm)
# =========================================================
F4 = (21.5 * cm, 33.0 * cm)

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
        """Membongkar data JSONB agar mudah dibaca oleh PDF"""
        dl_raw = self.db.data_lembaga
        profil = dl_raw.get("profil_lengkap", {})
        pengaturan = dl_raw.get("pengaturan_master", {})
        
        dl_flat = {**dl_raw, **profil}
        dl_flat["nomor_statistik"] = dl_raw.get("nsm", "-")
        dl_flat["pengaturan_master"] = pengaturan
        return dl_flat

    def cetak_cover(self, nama_santri):
        santri = next((s for s in self.db.data_master if s['nama'] == nama_santri), None)
        if not santri: return None
        dl = self._get_dl_flat()

        buffer = io.BytesIO()
        # Menggunakan format F4 yang sudah kita buat
        c = canvas.Canvas(buffer, pagesize=F4)
        lebar, tinggi = F4

        # ================= LOGO =================
        logo_b64 = dl.get("logo", "")
        if logo_b64:
            try:
                logo_data = base64.b64decode(logo_b64)
                logo_img = ImageReader(io.BytesIO(logo_data))
                c.drawImage(logo_img, lebar/2 - 2*cm, tinggi - 8*cm, 4*cm, 4*cm, mask='auto')
            except Exception as e:
                c.rect(lebar/2 - 2*cm, tinggi - 7*cm, 4*cm, 4*cm)
                c.drawCentredString(lebar/2, tinggi - 5*cm, "LOGO ERROR")
        else:
            c.rect(lebar/2 - 2*cm, tinggi - 7*cm, 4*cm, 4*cm)
            c.setFont("Helvetica-Bold", 10)
            c.drawCentredString(lebar/2, tinggi - 5*cm, "LOGO")
            c.drawCentredString(lebar/2, tinggi - 5.5*cm, "MADRASAH")

        # ================= JUDUL =================
        tingkatan_teks = dl.get("tingkatan", "MDTU")
        c.setFont("Helvetica-Bold", 28)
        c.drawCentredString(lebar/2, tinggi - 11*cm, "BUKU RAPORT")
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(lebar/2, tinggi - 12.5*cm, f"LEMBAGA PENDIDIKAN {tingkatan_teks}")

        # ================= IDENTITAS =================
        c.setFont("Helvetica", 12)
        y_lembaga = tinggi - 15*cm
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

        # ================= SANTRI =================
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(lebar/2, 9*cm, "NAMA SANTRI")
        
        c.setFont("Helvetica-Bold", 22)
        c.drawCentredString(lebar/2, 7.5*cm, nama_santri)

        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(lebar/2, 6*cm, f"Nomor Induk : {santri.get('no_induk', '-')}")

        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer

    def cetak_raport(self, nama_santri, semester):
        santri = next((s for s in self.db.data_master if s['nama'] == nama_santri), None)
        if not santri: return None
        
        nilai = self.db.get_nilai(santri['id'], semester)
        if not nilai: return None

        dl = self._get_dl_flat()
        pengaturan = dl.get("pengaturan_master", {})
        
        data_lengkap = santri.get("data_lengkap", {})
        kelas_santri = data_lengkap.get("kelas_santri", data_lengkap.get("kelas", "-"))
        
        # Cari data guru (Wali Kelas) dari database
        daftar_guru = self.db.get_semua_guru_lembaga()
        nama_wali = "........................"
        for g in daftar_guru:
            if g.get('role') == 'wali_kelas' and str(g.get('kelas_binaan')).upper().replace(" ","") == str(kelas_santri).upper().replace(" ",""):
                nama_wali = g.get('nama_guru', "........................")
                break
        
        buffer = io.BytesIO()
        # Menggunakan format F4 yang sudah kita buat
        c = canvas.Canvas(buffer, pagesize=F4)
        lebar, tinggi = F4
        
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(lebar/2, tinggi - 2.5*cm, "DAFTAR CAPAIAN KOMPETENSI")

        c.setFont("Helvetica", 10)
        y_kop = tinggi - 3.5*cm
        tingkatan_teks = dl.get("tingkatan", "MDTU")
        c.drawString(2*cm, y_kop, f"Nama {tingkatan_teks}")
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
        c.drawString(x_kanan + 3*cm, y_kop, f": {kelas_santri}")
        c.drawString(x_kanan, y_kop - 0.5*cm, "Semester")
        c.drawString(x_kanan + 3*cm, y_kop - 0.5*cm, f": {sem_teks}")

        # ================= TABEL DINAMIS (PENILAIAN BARU) =================
        komp_nilai = nilai.get('komponen_nilai', {})
        n_akademik = komp_nilai.get('akademik', {})
        n_narasi = komp_nilai.get('narasi_akademik', {})
        
        data_tabel = [['No.', 'Mata Pelajaran', 'Nilai', 'Predikat', 'Deskripsi Kemampuan']]
        styles = [
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (1,0), (1,-1), 'LEFT'),
            ('ALIGN', (4,0), (4,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ]

        kelas_mapel = pengaturan.get("kelas_mapel", {})
        mapel_list = []
        kelas_santri_bersih = str(kelas_santri).upper().replace(" ", "")
        
        for kls, mapels in kelas_mapel.items():
            if str(kls).upper().replace(" ", "") == kelas_santri_bersih:
                mapel_list = mapels
                break

        # MEMBUAT GAYA PARAGRAPH AGAR TEKS BISA TURUN BARIS (AUTO-WRAP)
        style_teks = ParagraphStyle(
            name='NormalTeks',
            fontName='Helvetica',
            fontSize=9,
            leading=12,
            alignment=0 # Rata kiri
        )

        row_idx = 1
        for i, mapel in enumerate(mapel_list):
            skor = int(n_akademik.get(mapel, 0))
            data_mapel = n_narasi.get(mapel, {})
            predikat = data_mapel.get("predikat", "-")
            deskripsi = data_mapel.get("deskripsi", "-")
            
            mapel_p = Paragraph(mapel, style_teks)
            deskripsi_p = Paragraph(deskripsi, style_teks)
            
            data_tabel.append([str(i+1), mapel_p, str(skor), predikat, deskripsi_p])
            row_idx += 1

        # Gambar Tabel Akademik
        tabel = Table(data_tabel, colWidths=[1*cm, 4.5*cm, 1.5*cm, 1.8*cm, 8.5*cm])
        tabel.setStyle(TableStyle(styles))
        w, h = tabel.wrap(lebar, tinggi)
        y_tabel = y_kop - 2.5*cm - h
        tabel.drawOn(c, 2*cm, y_tabel)

        y_bawah = y_tabel - 0.7*cm

        # ================= KEPUTUSAN SEMESTER 2 =================
        if semester == 2:
            status_akhir = komp_nilai.get('status', 'LULUS / NAIK KELAS')
            c.setFont("Helvetica-Bold", 10)
            c.drawString(2*cm, y_bawah, "KEPUTUSAN:")
            c.setFont("Helvetica", 10)
            c.drawString(2*cm, y_bawah - 0.5*cm, "Berdasarkan hasil capaian di atas, santri yang bersangkutan dinyatakan:")
            c.setFont("Helvetica-Bold", 12)
            c.drawString(2*cm, y_bawah - 1.2*cm, status_akhir.upper())
            y_bawah -= 2.2*cm 

        # ================= KEPRIBADIAN & ABSEN =================
        p = komp_nilai.get("kepribadian", {})
        a = komp_nilai.get("absen", {})
        
        def getTextP(val):
            if val == "A": return "Sangat Baik"
            if val == "B": return "Baik"
            if val == "C": return "Cukup"
            return "Kurang"

        kel_val = p.get('Kelakuan','B')
        ker_val = p.get('Kerajinan','B')
        keb_val = p.get('Kebersihan','B')

        kepribadian_kiri = Paragraph("1. Kelakuan<br/>2. Kerajinan<br/>3. Kebersihan", style_teks)
        kepribadian_kanan = Paragraph(f"{kel_val} ({getTextP(kel_val)})<br/>{ker_val} ({getTextP(ker_val)})<br/>{keb_val} ({getTextP(keb_val)})", style_teks)
        
        absen_kiri = Paragraph("1. Sakit<br/>2. Izin<br/>3. Alpa", style_teks)
        absen_kanan = Paragraph(f"{a.get('Sakit','0')} hari<br/>{a.get('Izin','0')} hari<br/>{a.get('Alpa','0')} hari", style_teks)
        
        catatan_p = Paragraph(f"<b>Catatan Wali Kelas:</b><br/>{komp_nilai.get('catatan', '-')}", style_teks)

        data_bawah = [
            ["Kepribadian & Sikap", kepribadian_kiri, kepribadian_kanan],
            ["Ketidakhadiran", absen_kiri, absen_kanan],
            [catatan_p, "", ""]
        ]
        
        tabel_bawah = Table(data_bawah, colWidths=[4.2*cm, 3.5*cm, 9.6*cm])
        tabel_bawah.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 1, colors.black), 
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (0,0), (0,-2), 'CENTER'),
            ('SPAN', (0,2), (2,2))
        ]))
        wb, hb = tabel_bawah.wrap(lebar, tinggi)
        y_bawah = y_bawah - hb - 0.5*cm
        tabel_bawah.drawOn(c, 2*cm, y_bawah)

        # ================= TANDA TANGAN =================
        c.setFont("Helvetica", 10)
        y_ttd = y_bawah - 1.5*cm
        tgl_raport = date.today().strftime('%d %B %Y')
        c.drawString(2*cm, y_ttd, f"Diberikan di : {dl.get('kabupaten_kota', '-')}")
        c.drawString(2*cm, y_ttd - 0.5*cm, f"Tanggal      : {tgl_raport}")
        
        c.drawCentredString(lebar/2, y_ttd - 1.5*cm, "Mengetahui,")
        c.drawString(2.5*cm, y_ttd - 2*cm, "Kepala Madrasah")
        c.drawCentredString(lebar/2, y_ttd - 2*cm, "Orang Tua/Wali")
        c.drawString(lebar - 5.5*cm, y_ttd - 2*cm, "Wali Kelas")

        c.setFont("Helvetica-Bold", 10)
        nama_kepala = dl.get('nama_kepala', '........................')
        c.drawString(2.5*cm, y_ttd - 4.5*cm, nama_kepala)
        c.drawString(lebar - 5.5*cm, y_ttd - 4.5*cm, nama_wali)
        
        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer
    def cetak_rekap_santri(self, kelas_terpilih):
        """Membuat PDF Rekapitulasi Biodata Santri Per Kelas (F4 Landscape/Portrait)"""
        dl = self._get_dl_flat()
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=F4)
        lebar, tinggi = F4
        
        # Header Kop Surat
        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(lebar/2, tinggi - 1.5*cm, f"REKAPITULASI DATA INDUK SANTRI")
        c.setFont("Helvetica-Bold", 12)
        c.drawCentredString(lebar/2, tinggi - 2.1*cm, f"MADRASAH: {dl.get('nama_madrasah', '-').upper()}")
        c.setFont("Helvetica", 10)
        c.drawCentredString(lebar/2, tinggi - 2.6*cm, f"Kelas: {kelas_terpilih}")
        
        # Ambil data santri khusus kelas ini
        santri_kelas = []
        for s in self.db.data_master:
            dl_santri = s.get("data_lengkap", {})
            kls = dl_santri.get("kelas_santri", dl_santri.get("kelas", ""))
            if str(kls).upper().replace(" ","") == str(kelas_terpilih).upper().replace(" ",""):
                santri_kelas.append(s)

        data_tabel = [['No.', 'No. Induk / NIS', 'Nama Lengkap Santri', 'L/P', 'Tempat, Tgl Lahir', 'Nama Ayah']]
        styles = [
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (2,0), (2,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('FONTSIZE', (0,0), (-1,-1), 9),
        ]

        style_teks = ParagraphStyle(name='RSText', fontName='Helvetica', fontSize=9, leading=11)

        for i, s in enumerate(santri_kelas):
            dl_s = s.get("data_lengkap", {})
            tgl_lhr = f"{dl_s.get('tempat_lahir', '-')}, {dl_s.get('tanggal_lahir', '-')}"
            
            data_tabel.append([
                str(i+1),
                Paragraph(str(s.get('no_induk', '-')), style_teks),
                Paragraph(str(s.get('nama', '-')), style_teks),
                Paragraph(str(dl_s.get('jenis_kelamin', '-'))[:1], style_teks),
                Paragraph(tgl_lhr, style_teks),
                Paragraph(str(dl_s.get('nama_ayah', '-')), style_teks)
            ])

        tabel = Table(data_tabel, colWidths=[1*cm, 3*cm, 5.5*cm, 1*cm, 4.5*cm, 3.5*cm])
        tabel.setStyle(TableStyle(styles))
        w, h = tabel.wrap(lebar, tinggi)
        tabel.drawOn(c, 1.5*cm, tinggi - 3.5*cm - h)

        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer

    def cetak_rekap_nilai(self, kelas_terpilih, semester):
        """Membuat PDF Rekapitulasi Nilai Akademik Seluruh Santri Per Kelas (F4)"""
        dl = self._get_dl_flat()
        pengaturan = dl.get("pengaturan_master", {})
        
        # Ambil daftar mapel kelas ini
        mapel_list = []
        for kls, mapels in pengaturan.get("kelas_mapel", {}).items():
            if str(kls).upper().replace(" ","") == str(kelas_terpilih).upper().replace(" ",""):
                mapel_list = mapels
                break
                
        if not mapel_list: mapel_list = ["Al-Qur'an", "Aqidah", "Fiqih"]

        buffer = io.BytesIO()
        # Untuk rekap nilai yang kolomnya banyak, kita gunakan orientasi Landscape F4 (Lebar dan Tinggi dibalik)
        F4_Landscape = (33.0 * cm, 21.5 * cm)
        c = canvas.Canvas(buffer, pagesize=F4_Landscape)
        lebar, tinggi = F4_Landscape

        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(lebar/2, tinggi - 1.5*cm, f"REKAPITULASI NILAI AKADEMIK SANTRI")
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(lebar/2, tinggi - 2.1*cm, f"MADRASAH: {dl.get('nama_madrasah', '-').upper()} | KELAS: {kelas_terpilih} | SEMESTER: {semester}")

        # Header Tabel Dinamis
        header_row = ['No.', 'Nama Santri'] + mapel_list + ['Jumlah', 'Rata-rata', 'Status']
        data_tabel = [header_row]
        
        styles = [
            ('GRID', (0,0), (-1,-1), 1, colors.black),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('ALIGN', (1,0), (1,-1), 'LEFT'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
            ('FONTSIZE', (0,0), (-1,-1), 8),
        ]

        style_teks = ParagraphStyle(name='RKText', fontName='Helvetica', fontSize=8, leading=10)

        santri_kelas = [s for s in self.db.data_master if str(s.get("data_lengkap", {}).get("kelas_santri", "")).upper().replace(" ","") == str(kelas_terpilih).upper().replace(" ","")]

        for i, s in enumerate(santri_kelas):
            nilai_s = self.db.get_nilai(s['id'], semester)
            komp = nilai_s.get('komponen_nilai', {}) if nilai_s else {}
            n_akademik = komp.get('akademik', {})
            
            baris = [str(i+1), Paragraph(s['nama'], style_teks)]
            for m in mapel_list:
                baris.append(str(int(n_akademik.get(m, 0))))
                
            baris.append(f"{nilai_s.get('jumlah', 0):.0f}" if nilai_s else "0")
            baris.append(f"{nilai_s.get('rata_rata', 0):.1f}" if nilai_s else "0")
            baris.append(str(komp.get('status', '-')))
            
            data_tabel.append(baris)

        # Hitung lebar kolom otomatis agar pas di layar Landscape F4 (~30 cm efektif)
        lebar_mapel = min(2.5*cm, 12*cm / max(len(mapel_list), 1))
        col_widths = [1*cm, 5.5*cm] + [lebar_mapel]*len(mapel_list) + [1.8*cm, 1.8*cm, 3.5*cm]

        tabel = Table(data_tabel, colWidths=col_widths)
        tabel.setStyle(TableStyle(styles))
        w, h = tabel.wrap(lebar, tinggi)
        tabel.drawOn(c, 1.5*cm, tinggi - 3.2*cm - h)

        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer