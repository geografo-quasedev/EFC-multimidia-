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
        self.prev_heights = None
        self.spectrum_colors = [
            QColor(41, 128, 185),  # Blue
            QColor(142, 68, 173),  # Purple
            QColor(52, 152, 219),  # Light Blue
            QColor(26, 188, 156),  # Turquoise
            QColor(46, 204, 113)   # Green
        ]
        self.transition_speed = 0.3  # Controls the smoothness of transitions
    
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
            # Calculate spectrum using FFT with improved resolution
            window = np.hanning(len(audio_data))
            windowed_data = audio_data * window
            spectrum = np.abs(np.fft.fft(windowed_data))
            frequencies = np.fft.fftfreq(len(spectrum))
            
            # Apply logarithmic scaling and smoothing
            spectrum = spectrum[:len(spectrum)//2]
            spectrum = np.log10(spectrum + 1)
            
            # Apply frequency weighting for better visualization
            freq_weights = np.linspace(1.0, 2.0, len(spectrum))
            spectrum = spectrum * freq_weights
            
            # Normalize spectrum data with dynamic range compression
            max_value = np.max(spectrum) if len(spectrum) > 0 else 1
            min_value = np.min(spectrum)
            spectrum = (spectrum - min_value) / (max_value - min_value)
            
            # Apply smoothing filter
            kernel_size = 3
            kernel = np.ones(kernel_size) / kernel_size
            spectrum = np.convolve(spectrum, kernel, mode='same')
            
            # Create QPixmap for visualization
            pixmap = QPixmap(self.visualization_label.width(), self.visualization_label.height())
            pixmap.fill(Qt.transparent)
            
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Calculate bar properties with improved spacing
            num_bars = min(128, len(spectrum))
            bar_width = pixmap.width() / (num_bars * 1.2)
            max_height = pixmap.height() * 0.9
            
            # Initialize previous heights if needed
            if self.prev_heights is None or len(self.prev_heights) != num_bars:
                self.prev_heights = np.zeros(num_bars)
            
            # Draw spectrum bars with improved visual effects
            painter.setPen(Qt.NoPen)
            
            for i in range(num_bars):
                # Calculate target height with improved scaling
                target_height = int((0.2 + spectrum[i] * 0.8) * max_height)
                
                # Apply smooth transition with variable speed
                transition_speed = self.transition_speed * (1.0 + 0.5 * spectrum[i])
                current_height = int(self.prev_heights[i] + (target_height - self.prev_heights[i]) * transition_speed)
                self.prev_heights[i] = current_height
                
                x = i * bar_width * 1.2 + (pixmap.width() - num_bars * bar_width * 1.2) / 2
                y = pixmap.height() - current_height
                
                # Create dynamic gradient based on frequency and amplitude
                bar_gradient = QLinearGradient(x, y, x, pixmap.height())
                intensity = spectrum[i]
                freq_factor = i / num_bars
                
                # Interpolate colors based on frequency
                start_color = QColor(41, 128, 185).lighter(100 + int(50 * intensity))
                mid_color = QColor(142, 68, 173).lighter(100 + int(30 * intensity))
                end_color = QColor(52, 152, 219).lighter(100 + int(40 * intensity))
                
                bar_gradient.setColorAt(0.0, start_color)
                bar_gradient.setColorAt(0.5, mid_color)
                bar_gradient.setColorAt(1.0, end_color)
                
                painter.setBrush(bar_gradient)
                painter.drawRoundedRect(
                    int(x), int(y),
                    int(bar_width), current_height,
                    2, 2
                )
            
            painter.end()
            
            # Display the visualization
            self.visualization_label.setPixmap(pixmap)
            
        except Exception as e:
            print(f"Error updating spectrum: {str(e)}")