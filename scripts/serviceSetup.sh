#!/bin/bash

# Check if ssl certificates exist
if [ ! -f ./certs/server.crt ] || [ ! -f ./certs/server.key ]; then
    echo "Error: SSL certificates not found. Creating self-signed certificates..."
    mkdir -p ./certs
    openssl genrsa -out ./certs/server.key 2048
    openssl req -new -key ./certs/server.key -out ./certs/server.csr
    openssl x509 -req -days 365 -in ./certs/server.csr -signkey ./certs/server.key -out ./certs/server.crt
fi

# Copy service files to systemd
cp ./services/createStream.service /usr/lib/systemd/system/createStream.service
cp ./services/mediamtx.service /usr/lib/systemd/system/mediamtx.service
cp ./services/restapi.service /usr/lib/systemd/system/restapi.service

# Reload systemd and enable services
systemctl daemon-reload
systemctl enable createStream.service
systemctl enable mediamtx.service
systemctl enable restapi.service
systemctl start createStream.service
systemctl start mediamtx.service
systemctl start restapi.service
