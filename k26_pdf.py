import csv, os, io
from PIL import Image, ImageOps
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
OUT = r"C:\Users\sanno\Downloads\K26"
PH = os.path.join(OUT, "photos")
recs = [r for r in csv.DictReader(open(os.path.join(OUT, "K26_index.csv"), encoding="utf-8")) if r["file"]]
recs.sort(key=lambda r: r["full"].lower())
PDF = os.path.join(OUT, "K26 Contacts - Photos.pdf")
W, H = letter
S = 5 * cm
cols, rows = 3, 4
gx = (W - cols * S) / (cols + 1)
top, cap = 2.0 * cm, 1.1 * cm
gy = (H - top - 1.2 * cm - rows * (S + cap)) / (rows - 1)
c = canvas.Canvas(PDF, pagesize=letter)
c.setTitle("K26 Contacts - Photos")
total_pages = (len(recs) + 11) // 12
def fit(txt, font, size, maxw):
    while c.stringWidth(txt, font, size) > maxw and len(txt) > 3:
        txt = txt[:-2]
    return txt
for p in range(total_pages):
    c.setFont("Helvetica-Bold", 13)
    c.drawString(gx, H - 1.3 * cm, "K26 Contacts")
    c.setFont("Helvetica", 9)
    c.drawRightString(W - gx, H - 1.3 * cm, f"Page {p+1} of {total_pages}  |  {len(recs)} contacts with photos")
    for k, r in enumerate(recs[p*12:(p+1)*12]):
        col, row = k % cols, k // cols
        x = gx + col * (S + gx)
        y = H - top - (row + 1) * S - row * (cap + gy)
        im = Image.open(os.path.join(PH, r["file"]))
        im = ImageOps.exif_transpose(im).convert("RGB")
        im = ImageOps.fit(im, (600, 600), Image.LANCZOS)
        buf = io.BytesIO(); im.save(buf, "JPEG", quality=90); buf.seek(0)
        c.drawImage(ImageReader(buf), x, y, S, S)
        c.setLineWidth(0.4); c.rect(x, y, S, S)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(x + S/2, y - 0.42*cm, fit(r["full"], "Helvetica-Bold", 9, S))
        c.setFont("Helvetica", 8)
        c.drawCentredString(x + S/2, y - 0.82*cm, r["phone"])
    c.showPage()
c.save()
print("pdf", PDF, "photos", len(recs), "pages", total_pages, "bytes", os.path.getsize(PDF))
