# Raspberry Pi Setup

Target device: Raspberry Pi 4 Model B.

## What Goes To GitHub

Commit the source code, tests, setup files, and documentation.

Do not commit:

- `models/`
- `face_data.pkl`
- `blocked.json`
- `logs/`
- `tts_cache/`
- any personal face data or session recordings

## System Packages

Run:

```bash
chmod +x install_pi.sh
./install_pi.sh
```

This installs Python dependencies plus Linux audio/TTS support such as PortAudio and `espeak-ng`.

## Models

Copy the required model files manually after cloning:

```text
models/
  cnn_v3_final.h5
  cnn_v3_final.tflite       recommended for Raspberry Pi emotion inference
  vosk-model/
  vosk-model-ar-mgb2-0.4/   optional but recommended for Arabic offline STT
```

Large model folders are ignored by Git and should be shared separately, for example by Google Drive or a GitHub Release.

To generate the TFLite emotion model on your laptop before copying files to the Pi:

```bash
python tools/convert_emotion_to_tflite.py --input models/cnn_v3_final.h5 --output models/cnn_v3_final.tflite --quantize dynamic
```

## Run

Check readiness first:

```bash
VISION_RPI_MODE=1 python tools/rpi_preflight.py
```

```bash
source .venv/bin/activate
./run_pi.sh
```

If the camera does not open, edit `config.py`:

```python
CAMERA_INDEX = 0
```

Or run:

```bash
VISION_CAMERA_INDEX=1 ./run_pi.sh
```

`run_pi.sh` enables Raspberry Pi mode automatically:

- prefers `models/cnn_v3_final.tflite` for emotion detection
- uses camera index `0` by default
- disables the display window by default for headless assistive use
- keeps all voice commands, registration, recognition, and emotion features active

## Audio Notes

- Edge TTS needs internet.
- Offline TTS on Raspberry Pi uses `espeak-ng`.
- Google STT needs internet.
- Vosk works offline if the model folders exist in `models/`.

## Before Real Use

1. Test the microphone with a simple recording tool.
2. Test camera index `0` and `1`.
3. Register each person in good lighting.
4. Use `vision improve person` if a registered person is sometimes detected as unknown.
5. Use `vision new person` if the system mistakes a new person for someone registered.
