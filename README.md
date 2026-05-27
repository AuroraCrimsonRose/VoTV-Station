# VoTV-Station

VoTV Live Stream Station Manager - Automated HLS streaming with playlist rotation, auto-restart, and REST API.

## Overview

VoTV-Station manages a continuous live stream by cycling through categorized video content (commercials, videos, filler). It uses FFmpeg to encode video files into HLS segments and serves them via a web player.

## Features

- 🔄 **Automatic Playlist Rotation** - Cycles through VID_, COM_, and FILL_ categories
- 🛡️ **Auto-Restart** - Monitors FFmpeg health and restarts on failure (throttled)
- 🎬 **HLS Streaming** - Industry-standard HTTP Live Streaming protocol
- 🌐 **REST API** - Control and monitor stream via HTTP endpoints
- 📊 **Media Indexer** - Scans directory and generates manifest.json with thumbnails
- 🧵 **Threaded Monitoring** - Health checks run in background

## Architecture

```
station/
├── manager.py       # Main entry point - boots all components
├── ffmpeg.py        # FFmpeg process management
├── scheduler.py     # Playlist builder (category rotation)
├── controller.py    # Health monitoring & auto-restart
├── state.py         # Shared application state
└── web.py           # Flask REST API

tv/
├── indexer.py       # Media scanner & manifest generator
├── VID_/            # Video files (main content)
├── COM_/            # Commercial files
├── FILL_/           # Filler content (backup)
├── thumbs/          # Generated thumbnails
└── manifest.json    # Generated media catalog
```

## Installation

### Requirements

- Python 3.7+
- FFmpeg with libx264 support
- FFprobe

### Setup

```bash
# Clone repository
git clone https://github.com/AuroraCrimsonRose/VoTV-Station.git
cd VoTV-Station

# Install Python dependencies
pip install -r requirements.txt

# Create directory structure
mkdir -p /var/www/votv/tv/{VID_,COM_,FILL_}/Public
mkdir -p /var/www/votv/station

# Add video files
cp your_videos.mp4 /var/www/votv/tv/VID_/Public/
cp your_commercials.mp4 /var/www/votv/tv/COM_/
cp your_filler.mp4 /var/www/votv/tv/FILL_/
```

### Configuration

Edit paths in each Python file if your media directory differs from `/var/www/votv/tv`:

```python
STREAM_DIR = "/var/www/votv/tv"
PLAYLIST = "/var/www/votv/station/playlist.txt"
```

## Usage

### Start Station

```bash
cd station
python3 manager.py
```

Output:
```
[main] booting VoTV Station...
[scheduler] generated 3 entries
[ffmpeg] starting pipeline...
[ffmpeg] started with PID 12345
[controller] monitor started
[main] station online
```

### Index Media

```bash
python3 tv/indexer.py
```

Generates `manifest.json` and thumbnails for the web archive player.

## REST API

### Status
```bash
curl http://localhost:5000/api/status
```

Response:
```json
{
  "status": "online",
  "alive": true,
  "ffmpeg_pid": 12345,
  "started_at": 1234567890
}
```

### Health Check
```bash
curl http://localhost:5000/api/health
```

### Control Endpoints

```bash
# Restart stream
curl -X POST http://localhost:5000/api/restart

# Start stream
curl -X POST http://localhost:5000/api/start

# Stop stream
curl -X POST http://localhost:5000/api/stop

# Rebuild playlist
curl -X POST http://localhost:5000/api/rebuild
```

## Playlist Format

The playlist file uses FFmpeg's concat format:

```
file '/var/www/votv/tv/VID_/Public/video1.mp4'
file '/var/www/votv/tv/COM_/commercial1.mp4'
file '/var/www/votv/tv/FILL_/filler.mp4'
```

Generated automatically by `scheduler.py` - picks one random file from each category.

## HLS Configuration

### Encoding
- **Codec**: H.264 (libx264)
- **Bitrate**: 1200 kbps (max 1500 kbps)
- **Preset**: veryfast (low latency)
- **Tune**: zerolatency
- **GOP**: 48 frames (2 seconds at 24fps)

### Streaming
- **Segment Duration**: 2 seconds
- **List Size**: 30 segments (60 seconds buffer)
- **Flags**: Delete old segments, append to list, independent segments

## Systemd Service (Optional)

Create `/etc/systemd/system/votv-station.service`:

```ini
[Unit]
Description=VoTV Station Manager
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/root/VoTV-Station/station
ExecStart=/usr/bin/python3 /root/VoTV-Station/station/manager.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then:
```bash
sudo systemctl daemon-reload
sudo systemctl start votv-station
sudo systemctl enable votv-station
```

## Troubleshooting

### FFmpeg won't start
- Check FFmpeg is installed: `ffmpeg -version`
- Verify paths in `ffmpeg.py`
- Check file permissions

### Missing playlist
- Ensure media directories exist
- Run indexer: `python3 tv/indexer.py`
- Check file format (must be .mp4)

### Stream stutters
- Increase buffer: `maxBufferLength` in HLS config
- Lower bitrate in FFmpeg command
- Check system resources (CPU, disk I/O)

## License

Private - VoTV Project

## Support

For issues, check logs or contact maintainer.
