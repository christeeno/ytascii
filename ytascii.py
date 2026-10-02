#!/usr/bin/env python3

import subprocess
import sys
import shutil
import time
import json

if len(sys.argv) != 2:
    print(f"Usage: {sys.argv[0]} <youtube-url>")
    sys.exit(1)

url = sys.argv[1]

# Dark -> bright
CHARS = "@#S%?*+;:,.' "

# Get complete video metadata from yt-dlp
result = subprocess.run(
    ["yt-dlp", "--dump-single-json", "--no-warnings", url],
    capture_output=True,
    text=True
)

if result.returncode != 0:
    print(result.stderr.strip())
    sys.exit(1)

info = json.loads(result.stdout)
formats = info.get("formats", [])

# --------------------------------------------------
# SELECT VIDEO
# --------------------------------------------------

video_formats = [
    f for f in formats
    if f.get("vcodec") not in (None, "none")
    and f.get("url")
]

if not video_formats:
    print("No video stream found.")
    sys.exit(1)


def video_score(f):
    height = f.get("height") or 0
    codec = f.get("vcodec") or ""
    ext = f.get("ext") or ""

    # Prefer H.264 MP4
    codec_score = (
        3 if codec.startswith("avc1")
        else 2 if codec.startswith("vp9")
        else 1
    )

    ext_score = 2 if ext == "mp4" else 0

    # Keep terminal playback at <=720p when possible
    if height <= 720:
        resolution_score = height
    else:
        resolution_score = 720 - (height - 720)

    return (resolution_score, codec_score + ext_score)


video = max(video_formats, key=video_score)

video_url = video["url"]

# Get the video's ACTUAL FPS
fps = float(video.get("fps") or 25)

# --------------------------------------------------
# SELECT AUDIO
# --------------------------------------------------

audio_formats = [
    f for f in formats
    if f.get("acodec") not in (None, "none")
    and f.get("vcodec") in (None, "none")
    and f.get("url")
]


def audio_score(f):
    language = (f.get("language") or "").lower()
    note = (f.get("format_note") or "").lower()
    codec = f.get("acodec") or ""
    bitrate = f.get("abr") or 0

    # Strongly prefer the original track
    original = 100 if "original" in note else 0

    # Prefer English if no original marker exists
    english = 20 if language.startswith("en") else 0

    # Prefer AAC/m4a, then Opus
    codec_score = (
        3 if codec.startswith("mp4a")
        else 2 if codec.startswith("opus")
        else 1
    )

    return (original, english, codec_score, bitrate)


audio = max(audio_formats, key=audio_score) if audio_formats else None

# --------------------------------------------------
# TERMINAL SIZE
# --------------------------------------------------

term_width, term_height = shutil.get_terminal_size()

width = max(40, term_width - 2)

# Terminal characters are taller than they are wide,
# so compensate for that.
height = max(10, int(width * 0.45))

frame_time = 1.0 / fps

# --------------------------------------------------
# START VIDEO
# --------------------------------------------------

video_process = subprocess.Popen(
    [
        "ffmpeg",
        "-loglevel", "error",
        "-i", video_url,
        "-vf", f"scale={width}:{height},format=gray",
        "-f", "rawvideo",
        "-pix_fmt", "gray",
        "-"
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.DEVNULL
)

# --------------------------------------------------
# START AUDIO
# --------------------------------------------------

audio_process = None

if audio:
    audio_process = subprocess.Popen(
        [
            "ffplay",
            "-nodisp",
            "-autoexit",
            "-loglevel", "quiet",
            audio["url"]
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

# --------------------------------------------------
# PLAY ASCII VIDEO
# --------------------------------------------------

frame_size = width * height

print("\033[2J\033[H", end="", flush=True)

next_frame_time = time.monotonic()

try:

    while True:

        frame = video_process.stdout.read(frame_size)

        if len(frame) != frame_size:
            break

        lines = []

        for y in range(height):

            row = frame[y * width:(y + 1) * width]

            line = "".join(
                CHARS[p * len(CHARS) // 256]
                for p in row
            )

            lines.append(line)

        print(
            "\033[H" + "\n".join(lines),
            end="",
            flush=True
        )

        # Maintain the video's actual FPS
        next_frame_time += frame_time

        delay = next_frame_time - time.monotonic()

        if delay > 0:
            time.sleep(delay)
        else:
            next_frame_time = time.monotonic()

except KeyboardInterrupt:
    pass

finally:

    video_process.terminate()

    if audio_process:
        audio_process.terminate()

    print("\033[0m\033[2J\033[H", end="")
