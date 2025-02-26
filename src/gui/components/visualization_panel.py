from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QColor, QLinearGradient
import numpy as np
import librosa
import matplotlib.pyplot as plt
from ...utils.media_visualizer import MediaVisualizer

class VisualizationPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.current_media_type = None
        self.spectrum_data = None
        self.spectrum_colors = [
            QColor(41, 128, 185),  # Blue
            QColor(142, 68, 173),  # Purple
            QColor(52, 152, 219)   # Light Blue
        ]
        self.spectrum_colors = [
            QColor(41, 128, 185),  # Blue
            QColor(142, 68, 173),  # Purple
            QColor(52, 152, 219)   # Light Blue
        ]
    
    def setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(10, 10, 10, 10)
        
        # Create visualization area
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
        
        self.layout.addWidget(self.visualization_label)
        
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
            # Generate and display waveform
            waveform = MediaVisualizer.generate_waveform(media_path)
            if waveform:
                self.visualization_label.setPixmap(
                    waveform.scaled(
                        self.visualization_label.width(),
                        self.visualization_label.height(),
                        Qt.KeepAspectRatio,
                        Qt.SmoothTransformation
                    )
                )
        
        elif media_type == 'video':
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
            
        try:
            # Calculate spectrum using FFT
            spectrum = np.abs(np.fft.fft(audio_data))
            frequencies = np.fft.fftfreq(len(spectrum))
            
            # Normalize spectrum data
            spectrum = spectrum[:len(spectrum)//2]
            max_value = np.max(spectrum) if len(spectrum) > 0 else 1
            spectrum = spectrum / max_value
            
            # Create QPixmap for visualization
            pixmap = QPixmap(self.visualization_label.width(), self.visualization_label.height())
            pixmap.fill(Qt.transparent)
            
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Calculate bar properties
            num_bars = min(64, len(spectrum))
            bar_width = pixmap.width() / (num_bars * 1.5)
            max_height = pixmap.height() * 0.8
            
            # Create gradient
            gradient = QLinearGradient(0, pixmap.height(), 0, 0)
            for i, color in enumerate(self.spectrum_colors):
                gradient.setColorAt(i / (len(self.spectrum_colors) - 1), color)
            
            # Draw spectrum bars
            painter.setPen(Qt.NoPen)
            painter.setBrush(gradient)
            
            for i in range(num_bars):
                # Use logarithmic scale for better visualization
                height = int(np.log10(1 + spectrum[i] * 9) * max_height)
                x = i * bar_width * 1.5 + (pixmap.width() - num_bars * bar_width * 1.5) / 2
                y = pixmap.height() - height
                
                painter.drawRoundedRect(
                    int(x), int(y),
                    int(bar_width), height,
                    2, 2
                )
            
            painter.end()
            
            # Display the visualization
            self.visualization_label.setPixmap(pixmap)
            
        except Exception as e:
            print(f"Error updating spectrum: {str(e)}")
    
    def update_spectrum(self, audio_data):
        """Update real-time spectrum visualization for audio playback"""
        if self.current_media_type != 'audio' or not audio_data:
            return
            
        try:
            # Calculate spectrum using FFT
            spectrum = np.abs(np.fft.fft(audio_data))
            frequencies = np.fft.fftfreq(len(spectrum))
            
            # Normalize spectrum data
            spectrum = spectrum[:len(spectrum)//2]
            max_value = np.max(spectrum) if len(spectrum) > 0 else 1
            spectrum = spectrum / max_value
            
            # Create QPixmap for visualization
            pixmap = QPixmap(self.visualization_label.width(), self.visualization_label.height())
            pixmap.fill(Qt.transparent)
            
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Calculate bar properties
            num_bars = min(64, len(spectrum))
            bar_width = pixmap.width() / (num_bars * 1.5)
            max_height = pixmap.height() * 0.8
            
            # Create gradient
            gradient = QLinearGradient(0, pixmap.height(), 0, 0)
            for i, color in enumerate(self.spectrum_colors):
                gradient.setColorAt(i / (len(self.spectrum_colors) - 1), color)
            
            # Draw spectrum bars
            painter.setPen(Qt.NoPen)
            painter.setBrush(gradient)
            
            for i in range(num_bars):
                # Use logarithmic scale for better visualization
                height = int(np.log10(1 + spectrum[i] * 9) * max_height)
                x = i * bar_width * 1.5 + (pixmap.width() - num_bars * bar_width * 1.5) / 2
                y = pixmap.height() - height
                
                painter.drawRoundedRect(
                    int(x), int(y),
                    int(bar_width), height,
                    2, 2
                )
            
            painter.end()
            
            # Display the visualization
            self.visualization_label.setPixmap(pixmap)
            
        except Exception as e:
            print(f"Error updating spectrum: {str(e)}")