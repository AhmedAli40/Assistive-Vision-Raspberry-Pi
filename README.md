# Assistive Vision System
## Emotion Recognition + Face Recognition

---

## Setup

### 1. Clone the repository
git clone https://github.com/AhmedAli40/Assistive-Vision-System.git
cd Assistive-Vision-System

### 2. Install dependencies
install.bat

### 3. Download models
Download from Google Drive and place in `models/` folder:
https://drive.google.com/drive/folders/1FHg9-D0uk08p9xlptWRWBJ5LGU-Uq7oe

Required files:
- models/emotion_fixed.h5
- models/vosk-model/ (full folder)

### 4. Run
run.bat

---

## Voice Commands
Say "Vision" to activate, then:
- "register" - Register current person
- "block" / "unblock" - Manage blocked persons
- "who" - Identify current person
- "quiet" / "speak" - Control announcements
- "stop" - Stop current speech
- "list" / "delete" - Manage database