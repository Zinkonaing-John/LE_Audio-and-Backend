# ui_inlined.py
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect, QTimer, QPoint, pyqtProperty
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QPushButton, QLabel, QTextEdit, QFrame, QComboBox
from PyQt5.QtGui import QFont, QColor, QPainter
class LanguageButton(QPushButton):
    def __init__(self, text, flag_emoji="", parent=None):
        super().__init__(parent)
        self.text = text; self.flag_emoji = flag_emoji; self.is_selected = False
        self.setText(self.text); self.setCheckable(True); self.setMinimumHeight(32)
        self.setStyleSheet("QPushButton{border-radius:16px;padding:6px 12px;}")
    def setSelected(self, selected):
        self.is_selected = selected; self.setChecked(selected); self.setProperty("selected", selected)
        self.style().unpolish(self); self.style().polish(self)

class MicrophoneButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent); self.setText("REC"); self.setFixedSize(100,100); self.setCheckable(True)
        self.is_recording = False; self._ring_radius = 0
        self.ring_animation = QPropertyAnimation(self, b"ring_radius"); self.ring_animation.setDuration(1500)
        self.ring_animation.setStartValue(0); self.ring_animation.setEndValue(40); self.ring_animation.setLoopCount(-1)
        self.setStyleSheet("QPushButton{background:#87CEEB;border:none;border-radius:50px;color:white;font-size:36px;} QPushButton:checked{background:#FF6B6B;}")
    @pyqtProperty(int)
    def ring_radius(self): return self._ring_radius
    @ring_radius.setter
    def ring_radius(self, r): self._ring_radius = r; self.update()
    def paintEvent(self, event):
        if self.is_recording:
            painter = QPainter(self); painter.setRenderHint(QPainter.Antialiasing)
            center = self.rect().center(); opacity = 1.0 - (self._ring_radius / 40.0)
            ring_color = QColor(255, 107, 107, int(200 * opacity)); painter.setBrush(ring_color); painter.setPen(Qt.NoPen)
            painter.drawEllipse(center, self._ring_radius, self._ring_radius)
        super().paintEvent(event)
    def setRecording(self, recording):
        self.is_recording = recording; self.setChecked(recording)
        if recording: self.ring_animation.start()
        else: self.ring_animation.stop(); self._ring_radius = 0; self.update()

class DeviceSelector(QComboBox):
    def __init__(self, language, parent=None):
        super().__init__(parent); self.language = language; self.setMinimumWidth(200); self.addItem("default","default")

class TranslationCard(QFrame):
    def __init__(self, language, flag_emoji="", parent=None):
        super().__init__(parent)
        self.language = language; self.flag_emoji = flag_emoji; self.full_text = ""
        layout = QVBoxLayout(); layout.setContentsMargins(15,15,15,15); layout.setSpacing(10)
        header = QHBoxLayout(); self.language_label = QLabel(language); self.language_label.setFont(QFont("Arial",14))
        header.addWidget(self.language_label); header.addStretch()
        self.device_selector = DeviceSelector(language); header.addWidget(self.device_selector)
        layout.addLayout(header)
        self.text_area = QTextEdit(); self.text_area.setReadOnly(True); self.text_area.setMinimumHeight(100)
        layout.addWidget(self.text_area)
        bottom = QHBoxLayout(); bottom.addStretch(); self.play_button = QPushButton("▶ Play"); self.play_button.setFixedSize(90,32); self.play_button.setEnabled(False); bottom.addWidget(self.play_button)
        layout.addLayout(bottom); self.setLayout(layout)
    def update_content(self, summary_text, full_text=None):
        if full_text is None: full_text = summary_text or ""
        self.full_text = full_text; self.text_area.setPlainText(summary_text or ""); self.text_area.setToolTip(full_text)

TARGET_LANGS = {"English":"en","Japanese":"ja","Chinese":"zh-cn","Vietnamese":"vi"}

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow"); MainWindow.resize(1200,800)
        self.centralwidget = QWidget(MainWindow); MainWindow.setCentralWidget(self.centralwidget)
        main_layout = QVBoxLayout(self.centralwidget)
        header = QHBoxLayout(); header.addStretch(); self.mic_button = MicrophoneButton(); header.addWidget(self.mic_button); header.addStretch()
        main_layout.addLayout(header)
        content = QHBoxLayout()
        left = QVBoxLayout(); self.recorded_text_field = QTextEdit(); self.recorded_text_field.setPlaceholderText("Recorded text will appear here..."); left.addWidget(self.recorded_text_field)
        self.chat_response_field = QTextEdit(); self.chat_response_field.setVisible(False); left.addWidget(self.chat_response_field)
        main_layout.addLayout(content)
        content.addLayout(left)
        right = QVBoxLayout()
        lang_layout = QHBoxLayout(); self.to_buttons = []; 
        for lang in ["English","Japanese","Chinese","Vietnamese"]: 
            b = LanguageButton(lang); b.clicked.connect(lambda checked, btn=b: self.select_btn(btn)); self.to_buttons.append(b); lang_layout.addWidget(b)
        right.addLayout(lang_layout)
        self.translation_cards = {name: TranslationCard(name) for name in TARGET_LANGS.keys()}
        for card in self.translation_cards.values(): right.addWidget(card)
        content.addLayout(right,1)
        self.status_label = QLabel("Ready"); main_layout.addWidget(self.status_label)
        self.audio_files_map = {}
    def select_btn(self, btn):
        btn.setSelected(not btn.is_selected)
