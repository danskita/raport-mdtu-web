import io
import base64
from datetime import date
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
        c = canvas.Canvas(buffer, pagesize=A4)
        lebar, tinggi = A4

        # ================= LOGO =================
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

        # ================= JUDUL =================
        tingkatan_teks = dl.get("tingkatan", "MDTU")
        c.setFont("Helvetica-Bold", 28)
        c.drawCentredString(lebar/2, tinggi - 9*cm, "BUKU RAPORT")
        c.setFont("Helvetica-Bold", 18)
        c.drawCentredString(lebar/2, tinggi - 10.5*cm, f"LEMBAGA PENDIDIKAN {tingkatan_teks}")

        # ================= IDENTITAS =================
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

        # ================= SANTRI =================
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
        c = canvas.Canvas(buffer, pagesize=A4)
        lebar, tinggi = A4
        
        c.setFont("Helvetica-Bold", 16)
        c.drawCentredString(lebar/2, tinggi - 2*cm, "DAFTAR CAPAIAN KOMPETENSI")

        c.setFont("Helvetica", 10)
        y_kop = tinggi - 3*cm
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
        # Ekstrak data dari JSONB 'komponen_nilai'
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

        row_idx = 1
        for i, mapel in enumerate(mapel_list):
            skor = int(n_akademik.get(mapel, 0))
            data_mapel = n_narasi.get(mapel, {})
            predikat = data_mapel.get("predikat", "-")
            deskripsi = data_mapel.get("deskripsi", "-")
            
            data_tabel.append([str(i+1), mapel, str(skor), predikat, deskripsi])
            row_idx += 1

        # Gambar Tabel Akademik
        tabel = Table(data_tabel, colWidths=[1*cm, 4*cm, 1.5*cm, 1.8*cm, 8.7*cm])
        tabel.setStyle(TableStyle(styles))
        w, h = tabel.wrap(lebar, tinggi)
        y_tabel = y_kop - 2.5*cm - h
        tabel.drawOn(c, 2*cm, y_tabel)

        y_bawah = y_tabel - 0.5*cm

        # ================= KEPUTUSAN SEMESTER 2 =================
        if semester == 2:
            status_akhir = komp_nilai.get('status', 'LULUS / NAIK KELAS')
            c.setFont("Helvetica-Bold", 10)
            c.drawString(2*cm, y_bawah, "KEPUTUSAN:")
            c.setFont("Helvetica", 10)
            c.drawString(2*cm, y_bawah - 0.5*cm, "Berdasarkan hasil capaian di atas, santri yang bersangkutan dinyatakan:")
            c.setFont("Helvetica-Bold", 12)
            c.drawString(2*cm, y_bawah - 1.2*cm, status_akhir.upper())
            y_bawah -= 2*cm 

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

        data_bawah = [
            ["Kepribadian & Sikap", "1. Kelakuan\n2. Kerajinan\n3. Kebersihan", f"{kel_val} ({getTextP(kel_val)})\n{ker_val} ({getTextP(ker_val)})\n{keb_val} ({getTextP(keb_val)})"],
            ["Ketidakhadiran", "1. Sakit\n2. Izin\n3. Alpa", f"{a.get('Sakit','0')} hari\n{a.get('Izin','0')} hari\n{a.get('Alpa','0')} hari"],
            [f"Catatan Wali Kelas:\n{komp_nilai.get('catatan', '-')}", "", ""]
        ]
        
        tabel_bawah = Table(data_bawah, colWidths=[4*cm, 3*cm, 10*cm])
        tabel_bawah.setStyle(TableStyle([
            ('GRID', (0,0), (-1,-1), 1, colors.black), ('VALIGN', (0,0), (-1,-1), 'TOP'),
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
        # Ambil nama Kepala Madrasah dari Auth/Profil (Jika ada), sementara pakai nama_madrasah fallback
        nama_kepala = dl.get('nama_kepala', '........................')
        c.drawString(2.5*cm, y_ttd - 4.5*cm, nama_kepala)
        c.drawString(lebar - 5.5*cm, y_ttd - 4.5*cm, nama_wali)
        
        c.showPage()
        c.save()
        buffer.seek(0)
        return buffer