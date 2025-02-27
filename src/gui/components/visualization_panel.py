from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QStackedWidget
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QLinearGradient, QColor
from ...utils.media_visualizer import MediaVisualizer
from .spectrum_analyzer import SpectrumAnalyzer
import numpy as np

class VisualizationPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_media_type = None
        self.setup_ui()
    
    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        # Create stacked widget for different visualizations
        self.stack = QStackedWidget()
        
        # Create visualization label for video thumbnails
        self.visualization_label = QLabel()
        self.visualization_label.setAlignment(Qt.AlignCenter)
        self.visualization_label.setMinimumSize(320, 180)
        self.visualization_label.setStyleSheet("""
            QLabel {
                background-color: #2c2c2c;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        
        # Create spectrum analyzer for audio visualization
        self.spectrum_analyzer = SpectrumAnalyzer()
        
        # Add widgets to stack
        self.stack.addWidget(self.visualization_label)
        self.stack.addWidget(self.spectrum_analyzer)
        
        self.layout.addWidget(self.stack)
        
        # Set panel properties
        self.setMinimumWidth(340)
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                border-radius: 4px;
            }
        """)
    
    def update_visualization(self, media_path, media_type):
        """Update the visualization based on media type"""
        self.current_media_type = media_type
        
        if media_type == 'audio':
            # Switch to spectrum analyzer for audio
            self.stack.setCurrentWidget(self.spectrum_analyzer)
            # Generate and display initial waveform
            waveform = MediaVisualizer.generate_waveform(media_path)
            if waveform:
                self.spectrum_analyzer.spectrum_label.setPixmap(
                    waveform.scaled(
                        self.spectrum_analyzer.spectrum_label.width(),
                        self.spectrum_analyzer.spectrum_label.height(),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                )
        
        elif media_type == 'video':
            # Switch to visualization label for video
            self.stack.setCurrentWidget(self.visualization_label)
            # Generate and display video thumbnail
            thumbnail = MediaVisualizer.generate_video_thumbnail(media_path)
            if thumbnail:
                self.visualization_label.setPixmap(
                    thumbnail.scaled(
                        self.visualization_label.width(),
                        self.visualization_label.height(),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                )
    
    def update_spectrum(self, audio_data):
        """Update real-time spectrum visualization for audio playback"""
        if self.current_media_type != 'audio' or not audio_data:
            return
            
        # Forward the audio data to the spectrum analyzer
        self.spectrum_analyzer.update_spectrum(audio_data)