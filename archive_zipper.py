import os, zipfile
from datetime import datetime

def zip_all_uploads():
    UPLOAD_DIR = "static/uploads"
    OUTPUT_DIR = "static/exports"
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"dugun_anilari_{now}.zip"
    zip_path = os.path.join(OUTPUT_DIR, zip_filename)

    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for foldername, subfolders, filenames in os.walk(UPLOAD_DIR):
            for filename in filenames:
                filepath = os.path.join(foldername, filename)
                arcname = os.path.relpath(filepath, UPLOAD_DIR)
                zipf.write(filepath, arcname)
    return zip_filename
