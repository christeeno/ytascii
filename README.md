ytascii
=======

Watch YouTube videos directly in your terminal using real ASCII characters.

Features
--------
- YouTube URL support
- Real-time ASCII rendering
- Audio playback
- Automatic video/audio stream selection
- Automatic FPS detection
- FFmpeg-based video decoding
- Terminal-based playback

Requirements
------------
- Python 3
- yt-dlp
- FFmpeg
- ffplay

Usage
-----
ytascii "https://www.youtube.com/watch?v=..."

Architecture
------------
YouTube
  ↓
yt-dlp
  ↓
Video + Audio streams
  ↓
FFmpeg ──────→ ffplay
  ↓
Grayscale frames
  ↓
ASCII renderer
  ↓
Terminal

