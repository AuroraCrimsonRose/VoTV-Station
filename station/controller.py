#!/usr/bin/env python3
"""
Station controller
Monitors ffmpeg health and manages automatic restarts
"""

import time
import ffmpeg
import scheduler
import os

last_restart = 0
RESTART_COOLDOWN = 10


def start_ffmpeg():
    """Start the ffmpeg process"""
    ffmpeg.start()


def monitor():
    """Monitor ffmpeg health and auto-restart on failure"""
    global last_restart

    print("[controller] monitor started")

    while True:
        time.sleep(5)

        # ffmpeg dead check
        if not ffmpeg.alive():
            print("[controller] ffmpeg dead detected")

            if time.time() - last_restart < RESTART_COOLDOWN:
                print("[controller] restart throttled")
                continue

            last_restart = time.time()

            scheduler.build_playlist()
            ffmpeg.restart()

            continue

        # playlist sanity check
        if not os.path.exists(scheduler.PLAYLIST):
            print("[controller] missing playlist, rebuilding")
            scheduler.build_playlist()
            ffmpeg.restart()
            continue
