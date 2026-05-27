#!/usr/bin/env python3
"""
VoTV Station Main Manager
Boot and coordinate all components
"""

import threading
import time
import sys
import os

import controller
import scheduler
import ffmpeg


def boot():
    """Boot the station"""
    print("[main] booting VoTV Station...")

    # 1. Build initial playlist
    if not scheduler.build_playlist():
        print("[main] ERROR: Failed to build initial playlist")
        sys.exit(1)

    # 2. Start ffmpeg
    if not ffmpeg.start():
        print("[main] ERROR: Failed to start ffmpeg")
        sys.exit(1)

    # 3. Start health monitor (background thread)
    monitor_thread = threading.Thread(target=controller.monitor, daemon=True)
    monitor_thread.start()
    print("[main] monitor started")

    # 4. Periodic playlist refresh
    print("[main] station online")
    try:
        while True:
            time.sleep(10)
            scheduler.tick()
    except KeyboardInterrupt:
        print("[main] shutting down...")
        ffmpeg.stop()
        sys.exit(0)


if __name__ == "__main__":
    boot()
