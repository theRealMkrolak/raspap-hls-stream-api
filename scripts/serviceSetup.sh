#!/bin/bash

# Copy service files to systemd
cp ./services/createStream.service /usr/lib/systemd/system/createStream.service
cp ./services/mediamtx.service /usr/lib/systemd/system/mediamtx.service

# Reload systemd and enable services
systemctl daemon-reload
systemctl enable createStream.service
systemctl enable mediamtx.service
systemctl start createStream.service
systemctl start mediamtx.service
