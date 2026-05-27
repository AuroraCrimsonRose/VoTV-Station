#!/usr/bin/env python3
"""
VoTV Media Indexer
Scans TV directory and generates manifest.json with thumbnails
Run this periodically to update available media
"""

import os
import json
import time
import hashlib
import subprocess
import sys

TV_ROOT = "/var/www/votv/tv"
THUMB_DIR = os.path.join(TV_ROOT, "thumbs")

os.makedirs(THUMB_DIR, exist_ok=True)

TYPE_MAP = {
    "COM_": "commercial",
    "VID_": "video",
    "FILL_": "fill",
    "NEWS_": "news"
}


def make_id(path):
    """Generate unique ID from file path"""
    return hashlib.sha1(path.encode()).hexdigest()[:12]


def get_duration(file_path):
    """Get video duration using ffprobe"""
    try:
        out = subprocess.check_output([
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            file_path
        ], timeout=10)
        return float(out.strip())
    except:
        return None


def make_thumbnail(file_path, thumb_path):
    """Generate thumbnail from video (only if missing)"""
    if os.path.exists(thumb_path):
        return

    try:
        subprocess.run([
            "ffmpeg",
            "-y",
            "-ss", "00:00:01",
            "-i", file_path,
            "-frames:v", "1",
            "-q:v", "2",
            thumb_path
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        timeout=10)
        print(f"  ✓ {os.path.basename(thumb_path)}")
    except Exception as e:
        print(f"  ✗ thumbnail failed: {e}")


def scan_and_index():
    """Scan TV directory and build manifest"""
    manifest = []
    count = 0

    for root, dirs, files in os.walk(TV_ROOT):
        for f in files:
            if not f.endswith(".mp4"):
                continue

            full_path = os.path.join(root, f)
            rel_path = os.path.relpath(full_path, TV_ROOT).replace("\\", "/")

            # Skip special directories
            if rel_path.startswith("thumbs"):
                continue

            stat = os.stat(full_path)

            # Type detection
            file_type = "unknown"
            category = rel_path.split("/")[0] if "/" in rel_path else "root"
            name = f

            for prefix, t in TYPE_MAP.items():
                if f.startswith(prefix):
                    file_type = t
                    name = f[len(prefix):]
                    break

            file_id = make_id(rel_path)
            thumb_path = os.path.join(THUMB_DIR, f"{file_id}.jpg")

            print(f"Indexing: {rel_path}")
            make_thumbnail(full_path, thumb_path)

            manifest.append({
                "id": file_id,
                "name": name,
                "type": file_type,
                "category": category,
                "path": rel_path,
                "size": stat.st_size,
                "mtime": int(stat.st_mtime),
                "duration": get_duration(full_path),
                "thumbnail": f"thumbs/{file_id}.jpg" if os.path.exists(thumb_path) else None
            })

            count += 1

    # Sort by category then name
    manifest.sort(key=lambda x: (x["category"], x["name"]))

    # Write manifest
    manifest_path = os.path.join(TV_ROOT, "manifest.json")
    with open(manifest_path, "w") as f:
        json.dump({
            "generated": int(time.time()),
            "count": len(manifest),
            "items": manifest
        }, f, indent=2)

    print(f"\n✓ Generated manifest for {count} files")
    return count


if __name__ == "__main__":
    print(f"[indexer] scanning {TV_ROOT}...")
    scan_and_index()
