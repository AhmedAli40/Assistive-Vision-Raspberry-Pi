# 🎯 Assistive Vision System v2
### Real-Time Face Recognition + Emotion Detection + Bilingual Voice Interface

> **Emotion Recognition Accuracy: 81.5%** (CNN v3 + Test-Time Augmentation)  
> **Languages:** Arabic 🇪🇬 + English 🇺🇸  
> **Voice:** Microsoft Edge TTS Neural (human-like voice)

---

## 📋 Table of Contents
- [Requirements](#-requirements)
- [Installation](#-installation)
- [Raspberry Pi Setup](RASPBERRY_PI_SETUP.md)
- [Download Models](#-download-models)
- [Run the System](#-run-the-system)
- [Voice Commands](#-voice-commands)
- [Language & Voice Switching](#-language--voice-switching)
- [Troubleshooting](#-troubleshooting)
- [Project Structure](#-project-structure)

---

## 💻 Requirements

### Operating System
- Windows 10 / 11 (64-bit)

### Python
- Python **3.12.x** only — [Download here](https://www.python.org/downloads/release/python-3120/)
- During installation: ✅ Make sure to check **"Add Python to PATH"**

### Hardware
- Webcam (built-in or external USB)
- Microphone

### Internet
- Required for voice output (Edge TTS) and speech recognition (Google STT)
- Works offline in limited mode via Vosk

---

## 🚀 Installation

### Step 1 — Clone the repository
```bash
git clone https://github.com/AhmedAli40/Assistive-Vision-System-v2-Acc-81.5-TTA.git
cd Assistive-Vision-System-v2-Acc-81.5-TTA
```

Or download the ZIP directly from GitHub and extract it.

---

### Step 2 — Install dependencies

Open **Terminal (PowerShell)** inside the project folder and run:

```bash
pip install -r requirements.txt
```

> ⏳ Installation may take 5–10 minutes — wait until it finishes

Then install the audio libraries:
```bash
pip install edge-tts pygame
```

---

### Step 3 — Download Models

Download the required files from Google Drive:

🔗 **[Download Models from Google Drive](https://drive.google.com/drive/folders/1IiyegcJBzjf3WaNF5NjgujU8I55vBiDt?usp=drive_link)**

After downloading, place the files as follows:

```
Assistive-Vision-System-v2/
└── models/
    ├── cnn_v3_final.h5        ← ✅ Required (main emotion model)
    └── vosk-model/            ← ✅ Required (full folder for offline STT)
        ├── am/
        ├── conf/
        ├── graph/
        └── ...
```

> ⚠️ **Important:** The `models/` folder must be in the same directory as `main.py`

---

### Step 4 — Configure Camera

Open `config.py` and set your camera index:
```python
CAMERA_INDEX = 0   # 0 = built-in laptop camera
                   # 1 = external USB camera
```

---

## ▶️ Run the System

```bash
python main.py
```

Or double-click `run.bat`

On startup you should see:
```
[Model] Loaded successfully before DeepFace
[TTS] Using Edge TTS neural voice: en-US-AriaNeural
System Ready! Press Q or ESC to quit.
```

> ⏳ First run may take 30–60 seconds to load Facenet512

---

## 🎤 Voice Commands

### Activation
Say the wake word first, then wait for **"Yes?"**, then say your command.

| Arabic | English |
|--------|---------|
| **فيجن** | **vision** |
| فيجين | hey vision |
| بصر | ok vision |
| مساعد | — |

---

### Person Commands

| Action | Arabic | English |
|--------|--------|---------|
| Register person | سجل، احفظ، اضف | register, save, add, record |
| Who is this? | مين، عرفني | who, identify, tell me |
| Delete person | احذف، امسح، شيل | delete, remove, erase, forget |
| List registered | الأسماء، قائمة | list, show, names |

---

### Block Commands

| Action | Arabic | English |
|--------|--------|---------|
| Block person | احظر، امنع | block, ban, blacklist |
| Unblock person | الغ الحظر | unblock, allow, unlock |

---

### Voice Control Commands

| Action | Arabic | English |
|--------|--------|---------|
| Mute | اسكت، سكوت، كفاية | quiet, silence, mute |
| Resume | اتكلم، كمل | speak, resume, continue |
| Stop immediately | وقف، بس | stop, halt |

---

## 🌐 Language & Voice Switching

### Switch Language
After the wake word, say:

| From → To | Say |
|-----------|-----|
| English → Arabic | `arabic` or `switch to arabic` or `عربي` |
| Arabic → English | `english` or `switch to english` or `انجليزي` |

---

### Switch Voice Gender
After the wake word, say:

| Voice | Arabic Command | English Command |
|-------|---------------|-----------------|
| Arabic male | صوت رجالي | male arabic |
| Arabic female | صوت ستات | female arabic |
| English male | صوت رجالي إنجليزي | male english |
| English female | صوت أنثى إنجليزي | female english |

---

### Available Voices

| Language | Gender | Voice |
|----------|--------|-------|
| Arabic | Female ✅ default | ar-EG-SalmaNeural (Egyptian) |
| Arabic | Male | ar-EG-ShakirNeural (Egyptian) |
| English | Female ✅ default | en-US-AriaNeural |
| English | Male | en-US-GuyNeural |

---

## 😊 Detected Emotions

| Emotion | Arabic |
|---------|--------|
| Happy | سعيد |
| Sad | حزين |
| Angry | غاضب |
| Fear | خائف |
| Surprise | متفاجئ |
| Neutral | طبيعي |
| Disgust | مشمئز |

---

## 🔧 Troubleshooting

### ❌ `ModuleNotFoundError`
```bash
pip install -r requirements.txt
pip install edge-tts pygame
```

### ❌ `Model not found at models/cnn_v3_final.h5`
Download the model from Google Drive and place it inside the `models/` folder.

### ❌ Camera not working
Change `CAMERA_INDEX` in `config.py`:
```python
CAMERA_INDEX = 0  # try 0 or 1
```

### ❌ No voice output
```bash
pip install edge-tts pygame
```
Make sure you have an active internet connection — Edge TTS requires it.

### ❌ Microphone not responding
- Make sure the microphone is not muted in Windows
- Wait for this message on startup: `STT Ready. Threshold = ...`

### ❌ `No module named 'stt'`
Make sure you run `main.py` from the project root folder:
```bash
cd "path\to\Assistive-Vision-System-v2"
python main.py
```

### ❌ Slow emotion detection
This is normal on first run. After 30 seconds the system stabilizes.  
If still slow, increase `INFERENCE_EVERY_N` in `config.py`:
```python
INFERENCE_EVERY_N = 6
```

---

## 📁 Project Structure

```
Assistive-Vision-System-v2/
├── main.py                    # Entry point
├── config.py                  # All settings
├── logic_controller.py        # System logic & voice commands
├── requirements.txt           # Python dependencies
├── install.bat                # Auto installer
├── run.bat                    # Run script
├── shared/
│   ├── tts.py                 # Text-to-Speech engine (Edge TTS)
│   └── stt.py                 # Speech-to-Text engine
├── face/
│   ├── face_db.py             # Face database
│   ├── face_processor.py      # Face detection & recognition
│   └── registration.py        # Person registration flow
├── emotion/
│   ├── face_detector.py       # Emotion detection (CNN)
│   ├── audio_detector.py      # Audio emotion fallback
│   └── display.py             # Visual results overlay
└── models/                    # ⬅️ Download from Google Drive
    ├── cnn_v3_final.h5        # Main emotion model (81.5% accuracy)
    └── vosk-model/            # Offline speech recognition
```

---

## 👨‍💻 Developers

| Name | Role |
|------|------|
| Ahmed Ali | Emotion Recognition + Face Recognition + System Integration |
| Ismail Mohsen | Voice Assistant Integration |

---

## 📄 License
This is an academic project — 2026
