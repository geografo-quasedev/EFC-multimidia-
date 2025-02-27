from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
import numpy as np
import librosa
import cv2

class MediaVisualizerPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.current_media_type = None
        self.video_capture = None
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Create visualization area with enhanced styling
        self.visual_label = QLabel()
        self.visual_label.setAlignment(Qt.AlignCenter)
        self.visual_label.setMinimumSize(500, 300)  # Increased size for better visibility
        self.visual_label.setStyleSheet("""
            QLabel {
                background-color: #1e1e1e;
                border-radius: 16px;
                padding: 20px;
                border: 1px solid #3a3a3a;
            }
            QLabel:hover {
                background-color: #2d2d2d;
                border: 2px solid #4a90e2;
            }
        """)
        
        layout.addWidget(self.visual_label)
        layout.addStretch()
        
        # Set main widget styling
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                border-radius: 20px;
                border: 1px solid #2a2a2a;
            }
        """)
        
    def update_spectrum(self, audio_data):
        if not audio_data:
            return
            
        try:
            # Compute spectrum using librosa
            D = librosa.stft(audio_data)
            S_db = librosa.amplitude_to_db(np.abs(D), ref=np.max)
            
            # Create visualization
            height, width = 200, 400
            spectrum_img = np.zeros((height, width, 3), dtype=np.uint8)
            
            # Normalize and scale the spectrum
            normalized = (S_db - S_db.min()) / (S_db.max() - S_db.min())
            for i in range(width):
                freq_index = int((i / width) * normalized.shape[1])
                for j in range(height):
                    amp_index = int((1 - j / height) * normalized.shape[0])
                    value = int(normalized[amp_index, freq_index] * 255)
                    spectrum_img[j, i] = [value, value, 255]  # Blue gradient
            
            # Convert to QPixmap and display
            height, width, channel = spectrum_img.shape
            bytes_per_line = 3 * width
            q_img = QImage(spectrum_img.data, width, height, bytes_per_line, QImage.Format_RGB888)
            self.visual_label.setPixmap(QPixmap.fromImage(q_img).scaled(
                self.visual_label.width(),
                self.visual_label.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))
            
        except Exception as e:
            print(f"Error updating spectrum: {str(e)}")
            
    def update_video_frame(self, frame):
        if frame is None:
            return
            
        try:
            # Convert frame to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Create QImage and display
            height, width, channel = frame_rgb.shape
            bytes_per_line = 3 * width
            q_img = QImage(frame_rgb.data, width, height, bytes_per_line, QImage.Format_RGB888)
            self.visual_label.setPixmap(QPixmap.fromImage(q_img).scaled(
                self.visual_label.width(),
                self.visual_label.height(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))
            
        except Exception as e:
            print(f"Error updating video frame: {str(e)}")
            
    def set_media_type(self, media_type):
        """Set the type of media being played (audio/video)"""
        self.current_media_type = media_type
        
    def clear_visualization(self):
        """Clear the visualization area"""
        self.visual_label.clear()
        if self.video_capture:
            self.video_capture.release()
            self.video_capture = None