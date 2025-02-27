from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtMultimedia import QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from .spectrum_analyzer import SpectrumAnalyzer
import numpy as np

class MediaViewer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Video widget
        self.video_widget = QVideoWidget()
        self.video_widget.setStyleSheet("""
            QVideoWidget {
                background-color: #1a1a1a;
                border-radius: 12px;
            }
        """)
        layout.addWidget(self.video_widget)
        
        # Audio visualization
        self.spectrum_analyzer = SpectrumAnalyzer()
        layout.addWidget(self.spectrum_analyzer)
        
        self.setStyleSheet("""
            MediaViewer {
                background-color: #1e1e1e;
                border-radius: 16px;
                padding: 10px;
            }
        """)
        
    def update_visualization(self, audio_data):
        if audio_data is None:
            return
            
        try:
            # Forward audio data to spectrum analyzer
            self.spectrum_analyzer.update_spectrum(audio_data)
            
        except Exception as e:
            print(f"Visualization error: {str(e)}")