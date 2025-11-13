# network.py - simple wrappers to call local backend endpoints.
# Replace the base URL with your real backend when available.
import requests, os, time
BASE = os.environ.get("LEAUDIO_BACKEND","http://localhost:8001")

HEADERS = {"Authorization": "Bearer test-token"}

def call_stt(wav_path, timeout=60):
    """Upload wav to /stt/stop and return transcript (string)."""
    url = BASE + "/stt/stop"
    with open(wav_path, "rb") as f:
        files = {"file": ("record.wav", f, "audio/wav")}
        r = requests.post(url, headers=HEADERS, files=files, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    return data.get("transcript","")

def call_translate(transcript, timeout=30):
    """Send transcript to /translate and expect {'en': '...', 'ja': '...'}"""
    url = BASE + "/translate"
    body = {"text": transcript}
    r = requests.post(url, headers={**HEADERS, "Content-Type":"application/json"}, json=body, timeout=timeout)
    r.raise_for_status()
    return r.json().get("translations", {})

def call_tts(text, out_path="out.wav", timeout=30):
    """Request TTS audio from /tts/speak and save binary to out_path."""
    url = BASE + "/tts/speak"
    body = {"text": text, "format": "wav"}
    r = requests.post(url, headers={**HEADERS, "Content-Type":"application/json"}, json=body, timeout=timeout)
    r.raise_for_status()
    # if binary content returned, save it
    with open(out_path, "wb") as f:
        f.write(r.content)
    return out_path

def call_llm(message, timeout=30):
    url = BASE + "/llm/chat"
    body = {"message": message}
    r = requests.post(url, headers={**HEADERS, "Content-Type":"application/json"}, json=body, timeout=timeout)
    r.raise_for_status()
    return r.json().get("response","")
