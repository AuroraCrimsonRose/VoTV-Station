#!/usr/bin/env python3
"""
Shared state for station management
"""

import time

STATE = {
    "status": "booting",
    "health": "unknown",
    "current_program": "idle",
    "ffmpeg_pid": None,
    "last_hls_update": 0,
    "started_at": time.time()
}
