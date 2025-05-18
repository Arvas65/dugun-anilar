from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.utils import secure_filename
from functools import wraps
from datetime import datetime
import os
import json
import zipfile
from fpdf import FPDF
from cloudinary_upload import upload_to_cloudinary


app = Flask(__name__)
app.secret_key = 'gizli_düğün_anahtarı'

BASE_UPLOAD_FOLDER = 'static/uploads'
EXPORT_FOLDER = 'static/exports'
DATA_FILE = 'data.json'
os.makedirs(BASE_UPLOAD_FOLDER, exist_ok=True)
os.makedirs(EXPORT_FOLDER, exist_ok=True)

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "mp4", "mp3", "wav", "ogg"}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Admin girişi kontrolü
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Ana sayfa - Misafir formu
@app.route('/')
def home():
    return render_template('form.html')

# Form verisi gönderme
@app.route('/submit', methods=['POST'])
def submit():
    name = request.form.get('name') or "Anonim"
    message = request.form.get('message')
    file = request.files['file']
    filename = None

    if file and allowed_file(file.filename):
        today = datetime.now().strftime("%Y-%m-%d")
        upload_path = os.path.join(BASE_UPLOAD_FOLDER, today)
        os.makedirs(upload_path, exist_ok=True)

        filename = datetime.now().strftime("%H%M%S_") + secure_filename(file.filename)
        temp_path = os.path.join("temp", filename)
        os.makedirs("temp", exist_ok=True)
        file.save(temp_path)

        file_path = upload_to_cloudinary(temp_path)  # 🔥 Firebase yerine artık burası
        os.remove(temp_path)
    else:
        file_path = None

    entry = {
        "name": name,
        "message": message,
        "filename": file_path,
        "timestamp": datetime.now().isoformat()
    }

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = []

    data.append(entry)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    return redirect(url_for('home'))

# Admin giriş sayfası
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'dugun123':
            session['logged_in'] = True
            return redirect(url_for('admin'))
        else:
            error = 'Hatalı kullanıcı adı veya şifre.'
    return render_template('login.html', error=error)

# Admin paneli
@app.route('/admin')
@login_required
def admin():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            entries = json.load(f)
    else:
        entries = []
    return render_template('admin.html', entries=entries)

# ZIP arşivi oluştur
def zip_all_uploads():
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"dugun_anilari_{now}.zip"
    zip_path = os.path.join(EXPORT_FOLDER, zip_filename)

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for foldername, subfolders, filenames in os.walk(BASE_UPLOAD_FOLDER):
            for filename in filenames:
                filepath = os.path.join(foldername, filename)
                arcname = os.path.relpath(filepath, BASE_UPLOAD_FOLDER)
                zipf.write(filepath, arcname)
    return zip_filename

# PDF albüm oluştur
class AlbumPDF(FPDF):
    def header(self):
        self.add_font('DejaVu', '', 'fonts/DejaVuSans.ttf', uni=True)
        self.set_font("DejaVu", '', 14)
        self.cell(0, 10, "Düğün Anı Albümü", 0, 1, "C")
        self.ln(10)

    def add_entry(self, name, message, filename, date):
        self.set_font("DejaVu", '', 12)
        self.cell(0, 10, f"{name} - {date}", 0, 1)
        self.set_font("DejaVu", '', 11)
        self.multi_cell(0, 10, message)
        self.ln(5)

        if filename:
            filepath = os.path.join(BASE_UPLOAD_FOLDER, filename)
            if os.path.exists(filepath) and filepath.lower().endswith(('.jpg', '.jpeg', '.png')):
                try:
                    self.image(filepath, w=100)
                except:
                    pass
        self.ln(10)

def create_pdf_album():
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
    filepath = os.path.join(EXPORT_FOLDER, filename)
    pdf.output(filepath)
    return filename

# Albüm ve ZIP oluşturma
@app.route('/generate_album')
@login_required
def generate_album():
    pdf_name = create_pdf_album()
    zip_name = zip_all_uploads()
    print(f'Oluşturuldu: {pdf_name}, {zip_name}')
    return redirect(url_for('admin'))

# Oturum kapatma
@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    if __name__ == "__main__":
        from dotenv import load_dotenv

        load_dotenv()
        app.run(host="0.0.0.0", port=5000)

