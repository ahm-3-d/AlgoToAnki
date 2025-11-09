import re
import os
import shutil
from pathlib import Path

def detect_blob_type(blobpath):
    with open(blobpath, "rb") as f:
        sig = f.read(10)
    
    if sig.startswith(b"\xff\xd8\xff"):
        return '.jpg'
    elif sig.startswith(b"\x89PNG"):
        return '.png'
    elif sig.startswith(b"GIF8"):
        return '.gif'
    elif sig.startswith(b"RIFF"):
        return '.webp'
    elif sig.startswith(b"ID3"):
            return '.mp3'
    else:
        return '.bin'

def convert_blobs(filepath, media_directory):
    blob_map = {}
    media_files = set()

    # Some cards don't have images so thus do not have blobs
    # If so, break out the function and return empty blob maps and media files
    if Path(filepath).is_dir() == False:
        print('No blob folder found. Returning blob map and media files as {} and []')
        return blob_map, media_files

    for file in os.listdir(filepath):
        if re.match(r"[a-f0-9]{32}$", file) or file.endswith(".bin"):
            blob_old_path = Path(filepath) / file

            blob_id = os.path.splitext(file)[0]
            
            blob_type = detect_blob_type(blob_old_path)

            print(f'Blob ID {blob_id}. Detected as file type {blob_type}. Copying file...')

            new_blob_name = f"{blob_id}{blob_type}"
            new_blob_path = os.path.join(media_directory, new_blob_name);

            shutil.copy(blob_old_path, new_blob_path)
            
            blob_map[blob_id] = new_blob_name
            media_files.add(new_blob_path)
    
    return blob_map, media_files
