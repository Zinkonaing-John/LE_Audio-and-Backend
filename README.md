# LeAudio - PyQt5 Demo (Ready-to-run)

This package contains a ready-to-run **PyQt5 frontend** wired against a **mock Flask backend** so you can test STT, translation, chat, and TTS flows locally.
Replace backend endpoints in `network.py` when your real backend is available.

## Contents
- `main.py` - launches the PyQt5 app (uses `ui_inlined.py` for the UI layout)
- `network.py` - network wrappers (change BASE to your backend URL)
- `mock_backend.py` - Flask app providing mock endpoints on port 8001
- `sample.wav` - small WAV file used by the mock TTS
- `requirements.txt` - Python packages to install

## Quick start (on Raspberry Pi)
1. Create a virtualenv and install requirements:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
2. Start the mock backend:
   ```bash
   python3 mock_backend.py
   ```
   This runs on `http://0.0.0.0:8001`

3. In another terminal (with the same venv) run the app:
   ```bash
   python3 main.py
   ```

4. Click the REC button. The demo will record (uses `arecord` if available on your Pi) or create a dummy wav file, upload it to the mock backend for STT/translate, prefetch TTS audio, and enable ▶ Play buttons on cards.

## Replacing with real backend
Edit `network.py` and set `BASE = "https://api.yourbackend.example/v1"` (or use environment variable `LEAUDIO_BACKEND`). Ensure your backend accepts the same payloads as represented in `mock_backend.py` or adapt `network.py` to match the real API shape.
