#!/bin/bash
# Optimized for Mac Camera -> MediaMTX

# Check if MediaMTX is running
if ! lsof -i :8554 > /dev/null 2>&1; then
    echo "Error: MediaMTX is not running on port 8554"
    echo "Please start MediaMTX first: mediamtx"
    exit 1
fi

if [ "$API_SYSTEM" == "mac" ]; then
    echo "Streaming from Mac to MediaMTX..."

    # Use yuv422p - supported by libx264 and closer to camera's native uyvy422 format
    # This reduces conversion overhead compared to yuv420p
    # Added flags to fix DTS warnings and improve timestamp handling for live streaming
    ffmpeg -hide_banner -loglevel warning \
        -f avfoundation -framerate 30 -probesize 10M -i "0" \
        -fflags nobuffer+genpts \
        -fps_mode passthrough \
        -c:v libx264 -b:v 2M -maxrate 2M -bufsize 4M \
        -preset ultrafast -tune zerolatency \
        -pix_fmt yuyv422 \
        -g 30 -keyint_min 30 -sc_threshold 0 \
        -vsync 0 \
        -f rtsp rtsp://localhost:8554/mystream
elif [ "$API_SYSTEM" == "raspberry-pi" ]; then
    echo "Streaming from Raspberry Pi to MediaMTX..."
    raspivid -o - -t 0 -w 1280 -h 720 -fps 30 -b 2000000 -g 30 | \
    ffmpeg -re -ar 44100 -ac 2 -acodec pcm_s16le -f s16le -ac 2 -i /dev/zero \
    -f h264 -i - -c:v copy -c:a aac -b:a 128k -f rtsp -rtsp_transport tcp \
    rtsp://localhost:8554/stream
else
    echo "Error: Unknown system: $API_SYSTEM"
    exit 1
fi
