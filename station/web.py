#!/usr/bin/env python3
"""
VoTV Station Web API
REST endpoints for stream control and monitoring
"""

from flask import Flask, jsonify, request
from state import STATE
import ffmpeg
import scheduler
import threading

app = Flask(__name__)


@app.route("/api/status")
def status():
    """Get current station status"""
    STATE["ffmpeg_pid"] = ffmpeg.process.pid if ffmpeg.process else None
    STATE["alive"] = ffmpeg.alive()
    return jsonify(STATE)


@app.route("/api/health")
def health():
    """Get health status"""
    return jsonify({
        "health": "ok" if ffmpeg.alive() else "error",
        "ffmpeg_alive": ffmpeg.alive()
    })


@app.route("/api/restart", methods=["POST"])
def restart():
    """Restart ffmpeg stream"""
    ffmpeg.restart()
    return jsonify({"ok": True, "action": "restart"})


@app.route("/api/start", methods=["POST"])
def start():
    """Start ffmpeg stream"""
    pid = ffmpeg.start()
    return jsonify({"ok": True if pid else False, "pid": pid})


@app.route("/api/stop", methods=["POST"])
def stop():
    """Stop ffmpeg stream"""
    ffmpeg.stop()
    return jsonify({"ok": True, "action": "stop"})


@app.route("/api/rebuild", methods=["POST"])
def rebuild():
    """Rebuild playlist immediately"""
    success = scheduler.build_playlist()
    return jsonify({"ok": success, "action": "rebuild"})


@app.route("/api/logs")
def logs():
    """Get recent logs (stub)"""
    return jsonify({"logs": []})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
