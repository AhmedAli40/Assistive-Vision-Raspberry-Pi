# Assistive Vision Raspberry Pi

Assistive vision system for blind and visually impaired users.

Features:
- Face recognition for registered people.
- Emotion detection.
- Arabic and English voice commands.
- Text-to-speech feedback.
- Raspberry Pi 4 Model B deployment mode.

Repository:
`https://github.com/AhmedAli40/Assistive-Vision-Raspberry-Pi.git`

## Quick Start On Raspberry Pi

Target device:
- Raspberry Pi 4 Model B
- Raspberry Pi OS 64-bit recommended
- USB camera or Pi camera exposed as a camera device
- USB microphone or headset microphone
- Internet recommended for Google STT and Edge TTS

Clone the project:

```bash
cd ~
git clone https://github.com/AhmedAli40/Assistive-Vision-Raspberry-Pi.git
cd Assistive-Vision-Raspberry-Pi
```

Install system and Python dependencies:

```bash
chmod +x install_pi.sh run_pi.sh download_models.sh
./install_pi.sh
```

Download the model files:

```bash
./download_models.sh
```

Check readiness:

```bash
VISION_RPI_MODE=1 python tools/rpi_preflight.py
```

Run:

```bash
./run_pi.sh
```

## Required Models

Large model files are stored separately on Google Drive:

`https://drive.google.com/drive/folders/1XIOsn-erryTL9f5AB7jxJTJ5kEhGC1cL?usp=drive_link`

After download, the project should look like this:

```text
Assistive-Vision-Raspberry-Pi/
  main.py
  models/
    cnn_v3_final.h5
    cnn_v3_final.tflite
    vosk-model/
    vosk-model-ar-mgb2-0.4/
```

`cnn_v3_final.tflite` is used by default on Raspberry Pi for smoother emotion inference. The `.h5` file is kept as a fallback.

## Raspberry Pi Mode

`run_pi.sh` sets:

```bash
VISION_RPI_MODE=1
VISION_CAMERA_INDEX=0
VISION_USE_TFLITE=1
```

Useful overrides:

```bash
VISION_CAMERA_INDEX=1 ./run_pi.sh
VISION_USE_TFLITE=0 ./run_pi.sh
VISION_SHOW_WINDOW=1 ./run_pi.sh
```

## Voice Commands

Say `vision` or `فيجن` before commands.

Activation:

```text
vision
start vision
فيجن
فيجين
ابدأ فيجن
ابدا فيجن
```

Identify current person:

```text
vision who is this
vision identify
فيجن مين ده
فيجن عرفني
فيجن من هذا
```

Register person:

```text
vision register
vision add person
vision save person
vision new person
vision register new person
فيجن سجل
فيجن ضيف شخص
فيجن احفظ الشخص
فيجن شخص جديد
فيجن سجل شخص جديد
```

Improve an existing registration:

```text
vision improve person
vision improved person
vision update person
vision improve registration
vision update registration
فيجن حسن الشخص
فيجن حسن التسجيل
فيجن حدث التسجيل
```

Delete a person:

```text
vision delete
vision del
vision remove
vision delete person
vision remove person
vision delete number
فيجن احذف
فيجن امسح
فيجن احذف شخص
فيجن امسح شخص
فيجن احذف رقم
```

When the system reads registered names by number:

```text
number 1
number 2
رقم 1
رقم 2
one
two
واحد
اتنين
```

Delete all names:

```text
vision delete all
vision delete all names
فيجن امسح الكل
فيجن احذف كل الاسماء
فيجن احذف كل الأسماء
```

List registered names:

```text
vision list names
vision show names
vision registered names
فيجن اسماء
فيجن أسماء
فيجن مين مسجل
فيجن اعرض الاسماء
فيجن اعرض الأسماء
```

Pause or resume automatic person/emotion announcements:

```text
vision standby
vision pause
vision resume
vision continue
فيجن هدوء
فيجن استنى
فيجن تابع
فيجن كمل
```

Mute or unmute system voice:

```text
vision quiet
vision mute
vision silence
vision unmute
فيجن اسكت
فيجن صمت
فيجن شغل الصوت
```

Language and voice:

```text
vision arabic
vision english
vision arabic male voice
vision arabic female voice
vision english male voice
vision english female voice
فيجن عربي
فيجن انجليزي
فيجن صوت رجالي عربي
فيجن صوت نسائي عربي
فيجن صوت رجالي انجليزي
فيجن صوت نسائي انجليزي
```

Block and unblock:

```text
vision block
vision block person
vision unblock
vision unblock person
فيجن احظر
فيجن احظر الشخص
فيجن فك حظر
فيجن ارفع الحظر
```

Close:

```text
close vision
goodbye
bye vision
اغلق
أغلق
اقفل
أقفل
مع السلامة
```

Confirmation words:

```text
yes
no
yeah
nope
okay
cancel
نعم
لا
أيوه
ايوه
تمام
بلاش
الغاء
إلغاء
```

## Important Runtime Notes

- For best face recognition, register each person in good light.
- Use `vision improve person` if a registered person sometimes appears as unknown.
- Use `vision new person` if an unknown person is mistakenly recognized as someone registered.
- The system filters random Vosk command noise and requires clear yes/no confirmations for risky actions.
- `face_data.pkl`, `blocked.json`, `logs/`, `tts_cache/`, and `models/` are intentionally not committed to GitHub.

## Troubleshooting

If dependencies are missing:

```bash
./install_pi.sh
```

If models are missing:

```bash
./download_models.sh
VISION_RPI_MODE=1 python tools/rpi_preflight.py
```

If the camera does not open:

```bash
VISION_CAMERA_INDEX=1 ./run_pi.sh
```

If TFLite fails on Pi, use the Keras fallback:

```bash
VISION_USE_TFLITE=0 ./run_pi.sh
```

If microphone commands trigger without speaking, recalibrate in a quiet room and keep speakers away from the microphone.

## Development Checks

On the development machine:

```bash
python -m py_compile main.py config.py logic_controller.py shared/stt.py shared/tts.py shared/draw_utils.py face/face_db.py face/face_processor.py face/registration.py emotion/audio_detector.py emotion/display.py emotion/face_detector.py test_speech_and_commands.py
python test_speech_and_commands.py
```
