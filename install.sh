#!/usr/bin/env bash

set -e

INSTALL_DIR="$HOME/.local/bin"
INSTALL_PATH="$INSTALL_DIR/ytascii"

echo "Installing ytascii..."

for command in python3 yt-dlp ffmpeg ffplay; do
    if ! command -v "$command" >/dev/null 2>&1; then
        echo "Error: '$command' is not installed."
        echo "Please install the required dependencies and try again."
        exit 1
    fi
done

mkdir -p "$INSTALL_DIR"

install -m 755 ytascii.py "$INSTALL_PATH"

echo
echo "ytascii installed successfully."
echo "Installed to: $INSTALL_PATH"
echo

if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    echo "Warning: $INSTALL_DIR is not in your PATH."
    echo 'Add this line to your shell configuration:'
    echo
    echo 'export PATH="$HOME/.local/bin:$PATH"'
    echo
fi

echo "Usage:"
echo '  ytascii "YOUTUBE_URL"'
