#!/bin/bash
set -e # Exit immediately if a command fails

# 1. Fetch latest changes
echo "Fetching latest tags..."
git fetch --tags

# 2. Get the latest tag name
LATEST_TAG=$(git describe --tags --abbrev=0)
echo "Checking out $LATEST_TAG..."
git checkout "$LATEST_TAG"

# 3. Pre-flight check: Verify Python syntax
echo "Verifying syntax..."
python3 -m py_compile backend/*.py

# 4. Update dependencies
if command -v uv &> /dev/null; then
    echo "Updating dependencies with uv..."
    uv sync
else
    echo "Updating dependencies with pip..."
    ./.venv/bin/pip install -r requirements.txt
fi

# 5. Restart services (The only destructive part)
echo "Restarting services..."
sudo systemctl restart mediamtx.service
sudo systemctl restart createStream.service

echo "Scheduling API restart..."
(sleep 2 && sudo systemctl restart restapi.service) &

echo "Upgrade to $LATEST_TAG successful!"