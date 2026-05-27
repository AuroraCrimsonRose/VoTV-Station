#!/usr/bin/env python3
"""
VoTV Station FFmpeg Manager
Manages HLS live stream from playlist of video files
"""

import subprocess
import os
import sys

STREAM_DIR = "/var/www/votv/tv"
PLAYLIST = "/var/www/votv/station/playlist.txt"
HLS_FILE = f"{STREAM_DIR}/stream.m3u8"

process = None

FFMPEG_CMD = [
    "ffmpeg",
    "-re",
    "-stream_loop", "-1",
    "-f", "concat",
    "-safe", "0",
    "-i", PLAYLIST,
    "-c:v", "libx264",
    "-preset", "veryfast",
    "-tune", "zerolatency",
    "-b:v", "1200k",
    "-maxrate", "1500k",
    "-bufsize", "2500k",
    "-g", "48",
    "-keyint_min", "48",
    "-f", "hls",
    "-hls_time", "2",
    "-hls_list_size", "30",
    "-hls_flags", "delete_segments+append_list+independent_segments",
    HLS_FILE
]


def start():
    """Start ffmpeg streaming process"""
    global process

    if process and process.poll() is None:
        print("[ffmpeg] already running")
        return process.pid

    try:
        print("[ffmpeg] starting pipeline...")
        process = subprocess.Popen(FFMPEG_CMD)
        print(f"[ffmpeg] started with PID {process.pid}")
        return process.pid
    except Exception as e:
        print(f"[ffmpeg] ERROR: {e}")
        return None


def stop():
    """Stop ffmpeg streaming process"""
    global process

    if process:
        try:
            process.terminate()
            process.wait(timeout=5)
            print("[ffmpeg] stopped")
        except subprocess.TimeoutExpired:
            process.kill()
            print("[ffmpeg] killed (timeout)")
        except Exception as e:
            print(f"[ffmpeg] ERROR stopping: {e}")
        finally:
            process = None


def restart():
    """Restart ffmpeg streaming process"""
    print("[ffmpeg] restarting...")
    stop()
    start()


def alive():
    """Check if ffmpeg process is running"""
    return process and process.poll() is None
