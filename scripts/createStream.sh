#!/bin/bash
# Optimized for Mac Camera -> MediaMTX

# Check if MediaMTX is running
if ! (echo > /dev/tcp/127.0.0.1/8554) >/dev/null 2>&1; then
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
    rpicam-vid -t 0 --inline --width 960 --height 540 --framerate 20 --codec h264 -o - | \
    ffmpeg -hide_banner -loglevel warning \
        -f h264 -i - \
        -c:v copy \
        -f rtsp -rtsp_transport tcp rtsp://localhost:8554/mystream
else
    echo "Error: Unknown system: $API_SYSTEM"
    exit 1
fi
