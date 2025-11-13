#!/usr/bin/env python3
"""
LeAudio - ready-to-run demo frontend
Instructions:
1) Start the mock backend: python3 mock_backend.py
2) Run this app: python3 main.py
Replace endpoints in network.py when you have real backend.
"""
import sys, os, uuid, subprocess, time, shutil
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import QApplication, QMainWindow
from ui_inlined import Ui_MainWindow  # UI class inlined to keep single-file import simple
import network

# A small recorder thread using arecord (preferred on Raspberry Pi) or fallback to generating silence.
class RecorderThread(QThread):
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    def __init__(self, out_path, duration=4, parent=None):
        super().__init__(parent)
        self.out_path = out_path
        self.duration = duration

    def run(self):
        # Prefer arecord on Raspberry Pi; fall back to creating a silent wav if not available.
        try:
            if shutil.which("arecord"):
                cmd = ["arecord", "-f", "cd", "-d", str(self.duration), self.out_path]
                subprocess.run(cmd, check=True)
            else:
                # fallback: create a short silent wav file
                import wave, struct
                frate = 16000
                amp = 0
                nchannels = 1
                sampwidth = 2
                nframes = frate * self.duration
                wf = wave.open(self.out_path, "wb")
                wf.setnchannels(nchannels)
                wf.setsampwidth(sampwidth)
                wf.setframerate(frate)
                for i in range(nframes):
                    wf.writeframes(struct.pack('<h', 0))
                wf.close()
            self.finished.emit(self.out_path)
        except Exception as e:
            self.error.emit(str(e))

class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        # wire signals
        self.ui.mic_button.clicked.connect(self.on_mic_clicked)
        # Connect play buttons for all translation cards
        for name, card in self.ui.translation_cards.items():
            card.play_button.clicked.connect(lambda checked, n=name: self.play_translation(n))

    def on_mic_clicked(self):
        is_recording = self.ui.mic_button.isChecked()
        self.ui.mic_button.setRecording(is_recording)
        if is_recording:
            # start a recording thread
            os.makedirs("logs", exist_ok=True)
            wav_path = os.path.join("logs", f"{uuid.uuid4().hex}.wav")
            self.rec_thread = RecorderThread(wav_path, duration=4)
            self.rec_thread.finished.connect(self.on_record_finished)
            self.rec_thread.error.connect(self.on_record_error)
            self.rec_thread.start()
            self.ui.status_label.setText("Recording...")
        else:
            # if user toggled off quickly, just stop
            self.ui.status_label.setText("Recording cancelled.")

    def on_record_error(self, err):
        self.ui.status_label.setText(f"Error recording: {err}")
        self.ui.mic_button.setRecording(False)

    def on_record_finished(self, wav_path):
        self.ui.status_label.setText("Uploading for STT...")
        # call STT endpoint via network.py in a background thread
        def job():
            start = time.time()
            try:
                transcript = network.call_stt(wav_path)
                duration = time.time() - start
                QtCore.QMetaObject.invokeMethod(self, "on_stt_result", QtCore.Qt.QueuedConnection, 
                                                QtCore.Q_ARG(str, transcript), QtCore.Q_ARG(float, duration))
            except Exception as e:
                QtCore.QMetaObject.invokeMethod(self, "on_stt_error", QtCore.Qt.QueuedConnection, 
                                                QtCore.Q_ARG(str, str(e)))
        import threading
        t = threading.Thread(target=job, daemon=True)
        t.start()

    @QtCore.pyqtSlot(str, float)
    def on_stt_result(self, transcript, duration):
        self.ui.recorded_text_field.setPlainText(transcript)
        self.ui.status_label.setText(f"STT done ({duration:.2f}s). Requesting translations...")
        # request translations (blocking here is acceptable because user initiated via thread)
        translations = network.call_translate(transcript)
        # Update UI cards and prefetch TTS
        for lang_name, code in {"English":"en","Japanese":"ja","Chinese":"zh-cn","Vietnamese":"vi"}.items():
            card = self.ui.translation_cards.get(lang_name)
            if card and code in translations:
                card.update_content(translations[code], translations[code])
                card.play_button.setEnabled(True)
                # prefetch tts audio to logs/
                audio_path = os.path.join("logs", f"tts_{code}.wav")
                try:
                    network.call_tts(translations[code], out_path=audio_path)
                    self.ui.audio_files_map[code] = audio_path
                except Exception as e:
                    print("TTS prefetch error", e)
        self.ui.status_label.setText("Translations + TTS ready. Tap ▶ Play to listen.")

    @QtCore.pyqtSlot(str)
    def on_stt_error(self, err):
        self.ui.status_label.setText("STT error: " + str(err))
        self.ui.mic_button.setRecording(False)

    def play_translation(self, lang_name):
        code = {"English":"en","Japanese":"ja","Chinese":"zh-cn","Vietnamese":"vi"}.get(lang_name)
        audio = self.ui.audio_files_map.get(code)
        if not audio or not os.path.exists(audio):
            self.ui.status_label.setText("No audio for " + lang_name)
            return
        self.ui.status_label.setText(f"Playing {lang_name}...")
        try:
            if shutil.which("aplay"):
                subprocess.run(["aplay", audio], check=True)
            else:
                import simpleaudio as sa
                wav = sa.WaveObject.from_wave_file(audio)
                play = wav.play()
                play.wait_done()
        except Exception as e:
            self.ui.status_label.setText("Playback error: " + str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = AppWindow()
    w.showMaximized()
    sys.exit(app.exec_())
