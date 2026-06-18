#!/usr/bin/env bash
set -euo pipefail

MODELS_DRIVE_URL="${MODELS_DRIVE_URL:-https://drive.google.com/drive/folders/1XIOsn-erryTL9f5AB7jxJTJ5kEhGC1cL?usp=drive_link}"

if [ -d ".venv" ]; then
  source .venv/bin/activate
fi

python -m pip install --upgrade gdown

echo "Downloading models from Google Drive..."
gdown --folder "$MODELS_DRIVE_URL" -O .

if [ ! -d "models" ]; then
  echo "ERROR: models folder was not created. Check the Google Drive link permissions."
  exit 1
fi

echo "Models downloaded."
echo "Run: VISION_RPI_MODE=1 python tools/rpi_preflight.py"
