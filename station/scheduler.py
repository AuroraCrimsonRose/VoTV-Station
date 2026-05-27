#!/usr/bin/env python3
"""
Playlist scheduler for VoTV Station
Rotates through categories and manages media rotation
"""

import os
import random

TV_ROOT = "/var/www/votv/tv"
PLAYLIST = "/var/www/votv/station/playlist.txt"

CATEGORIES = ["VID_", "COM_", "FILL_"]

def scan_folder(folder):
    """Scan folder for .mp4 files"""
    base = os.path.join(TV_ROOT, folder)

    if not os.path.exists(base):
        return []

    files = []

    for root, _, fns in os.walk(base):
        for f in fns:
            if f.lower().endswith(".mp4"):
                path = os.path.join(root, f)
                try:
                    if os.path.getsize(path) > 1024:
                        files.append(path)
                except:
                    pass

    return files


def build_playlist():
    """Build new playlist from categories"""
    entries = []

    for cat in CATEGORIES:
        files = scan_folder(cat)

        if files:
            entries.append(random.choice(files))

    # HARD fallback (never allow empty playlist)
    if not entries:
        fill = scan_folder("FILL_")
        if fill:
            entries = [random.choice(fill)]
        else:
            print("[scheduler] CRITICAL: no media found")
            return False

    with open(PLAYLIST, "w") as f:
        for e in entries:
            f.write(f"file '{e}'\n")

    print(f"[scheduler] generated {len(entries)} entries")
    return True


def tick():
    """Lightweight periodic refresh (30% chance)"""
    if random.random() < 0.3:
        build_playlist()
