#!/usr/bin/env bash
set -euo pipefail

export VISION_RPI_MODE=1
export VISION_CAMERA_INDEX="${VISION_CAMERA_INDEX:-0}"
export VISION_USE_TFLITE="${VISION_USE_TFLITE:-1}"

if [ -d ".venv" ]; then
  source .venv/bin/activate
fi

python main.py
