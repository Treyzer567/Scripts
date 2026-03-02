#!/usr/bin/env python3
import os
import re

# Directory to scan (your franchise folder)
scan_dir = "/mnt/Movies/Movies/Tokyo Ghoul Movies"
# Directory where folders will be created
output_base = "./output"

# Define allowed video extensions
VIDEO_EXTENSIONS = ('.mkv', '.avi', '.mp4')

# Create output directory if it doesn't exist
os.makedirs(output_base, exist_ok=True)

# Get only video files in the scan directory
files = [
    f for f in os.listdir(scan_dir) 
    if os.path.isfile(os.path.join(scan_dir, f)) and f.lower().endswith(VIDEO_EXTENSIONS)
]

def get_movie_base(filename):
    # Remove extension first
    base = os.path.splitext(filename)[0]
    
    # Remove trailing metadata often found in movie files
    # This helps if your filenames have things like '1080p', 'Bluray', etc.
    patterns = [
        r'\.eng(\.\d)?$', r'\.sdh$', r'-poster$', r'-backdrop\d?$', 
        r'-landscape$', r'_chapters$', r'-logo$'
    ]
    for pat in patterns:
        base = re.sub(pat, '', base, flags=re.IGNORECASE).strip()
    return base

# Build a set of unique movie base names
movie_names = set(get_movie_base(f) for f in files)

# Create folders
for movie in movie_names:
    # Clean folder name to avoid illegal characters
    folder_name = re.sub(r'[\/:*?"<>|]', '_', movie)
    folder_path = os.path.join(output_base, folder_name)
    os.makedirs(folder_path, exist_ok=True)

print(f"Success! Created {len(movie_names)} movie folders in {output_base}")
