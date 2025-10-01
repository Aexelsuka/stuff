import os
import io
import sys
import zipfile
from b2sdk.v2 import InMemoryAccountInfo, B2Api

# Config
bucket_name = 'usb-zips'
zip_filename = 'output.zip'
key_id = '003178940199c1b0000000001'
application_key = 'K003nZ4X9ru+00xp1EDOCZ3I2y2uzjQ'

# --- Get drive letter from command line ---
if len(sys.argv) != 2:
    print("Usage: python drive.py <DriveLetter>")
    sys.exit(1)

drive_letter = sys.argv[1].upper()
if len(drive_letter) != 1 or not drive_letter.isalpha():
    print("Error: Drive letter must be a single letter, e.g. C")
    sys.exit(1)

source_folder = f"{drive_letter}:\\"

# --- Init B2 API ---
info = InMemoryAccountInfo()
b2_api = B2Api(info)
b2_api.authorize_account('production', key_id, application_key)

# --- Create zip in memory ---
zip_buffer = io.BytesIO()
zipf = zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED)

excluded_extensions = ['.tmp', '.mp4', '.mp3', '.avi', '.exe', '.mov']
max_size = 10 * 1024 * 1024  # 10 MB in bytes

for root, _, files in os.walk(source_folder):
    for f in files:
        file_path = os.path.join(root, f)

        try:
            # Skip excluded extensions
            if any(f.lower().endswith(ext) for ext in excluded_extensions):
                continue

            # Skip large files
            if os.path.getsize(file_path) >= max_size:
                continue

            # Add file relative to drive root
            zipf.write(file_path, os.path.relpath(file_path, start=source_folder))

        except (PermissionError, FileNotFoundError):
            # Skip files we don't have access to or vanish during scanning
            continue

zipf.close()

# --- Upload to Backblaze B2 ---
bucket = b2_api.get_bucket_by_name(bucket_name)
bucket.upload_bytes(zip_buffer.getvalue(), zip_filename)

print(f'Uploaded {zip_filename} from drive {drive_letter}: to bucket {bucket_name}')