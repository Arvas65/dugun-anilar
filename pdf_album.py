from fpdf import FPDF
from PIL import Image
import os, json
from datetime import datetime

def create_pdf_album():
    DATA_FILE = 'data.json'
    UPLOAD_DIR = 'static/uploads'
    OUTPUT_DIR = 'static/exports'
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    class AlbumPDF(FPDF):
        def header(self):
            self.set_font("Arial", 'B', 14)
            self.cell(0, 10, "Düğün Anı Albümü", 0, 1, "C")
            self.ln(10)

        def add_entry(self, name, message, filename, date):
            self.set_font("Arial", 'B', 12)
            self.cell(0, 10, f"{name} - {date}", 0, 1)
            self.set_font("Arial", '', 11)
            self.multi_cell(0, 10, message)
            self.ln(5)
            if filename:
                filepath = os.path.join(UPLOAD_DIR, filename)
                if os.path.exists(filepath) and filepath.lower().endswith(('.jpg', '.jpeg', '.png')):
                    try:
                        self.image(filepath, w=100)
                    except:
                        pass
            self.ln(10)

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        entries = json.load(f)

    pdf = AlbumPDF()
    pdf.add_page()

    for entry in entries[::-1]:
        name = entry["name"]
        message = entry["message"]
        filename = entry.get("filename")
        date = entry["timestamp"].split("T")[0]
        pdf.add_entry(name, message, filename, date)

    filename = f"dugun_albumu_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
    pdf.output(os.path.join(OUTPUT_DIR, filename))
    return filename
