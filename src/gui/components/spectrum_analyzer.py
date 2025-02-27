from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QColor, QLinearGradient, QPainter
import numpy as np

class SpectrumAnalyzer(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.setup_analyzer()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.spectrum_label = QLabel()
        self.spectrum_label.setAlignment(Qt.AlignCenter)
        self.spectrum_label.setMinimumSize(320, 120)
        self.spectrum_label.setStyleSheet("""
            QLabel {
                background-color: #1e1e1e;
                border-radius: 4px;
            }
        """)
        
        layout.addWidget(self.spectrum_label)
        
    def setup_analyzer(self):
        # Configure spectrum analysis parameters
        self.num_bands = 64
        self.min_frequency = 20
        self.max_frequency = 20000
        self.smoothing_factor = 0.3
        
        # Initialize spectrum data
        self.current_spectrum = np.zeros(self.num_bands)
        self.peak_spectrum = np.zeros(self.num_bands)
        
        # Setup colors with enhanced gradient
        self.gradient_colors = [
            QColor(41, 128, 185),    # Blue
            QColor(142, 68, 173),    # Purple
            QColor(26, 188, 156),    # Turquoise
            QColor(46, 204, 113),    # Green
            QColor(241, 196, 15),    # Yellow
            QColor(230, 126, 34),    # Orange
            QColor(231, 76, 60)      # Red
        ]
        
        # Setup animation parameters
        self.decay_rate = 0.92
        self.rise_factor = 1.2
        self.min_db = -60
        self.max_db = 0
        
        # Setup peak falloff timer
        self.peak_timer = QTimer(self)
        self.peak_timer.timeout.connect(self.update_peaks)
        self.peak_timer.start(50)  # Update every 50ms
        
    def update_spectrum(self, fft_data):
        if fft_data is None or len(fft_data) == 0:
            return
            
        try:
            # Calculate frequency bands (logarithmic scale)
            bands = np.logspace(
                np.log10(self.min_frequency),
                np.log10(self.max_frequency),
                self.num_bands
            )
            
            # Calculate spectrum values for each band
            new_spectrum = np.zeros(self.num_bands)
            for i in range(self.num_bands):
                if i < len(fft_data):
                    new_spectrum[i] = np.mean(fft_data[max(0, i-2):i+3])
            
            # Apply smoothing
            self.current_spectrum = self.smoothing_factor * new_spectrum + \
                                  (1 - self.smoothing_factor) * self.current_spectrum
            
            # Update peak values
            self.peak_spectrum = np.maximum(self.peak_spectrum, self.current_spectrum)
            
            # Draw visualization
            self.draw_spectrum()
            
        except Exception as e:
            print(f"Error updating spectrum: {str(e)}")
            
    def update_peaks(self):
        # Decay peak values
        self.peak_spectrum *= 0.95
        self.draw_spectrum()
        
    def draw_spectrum(self):
        width = self.spectrum_label.width()
        height = self.spectrum_label.height()
        
        if width <= 0 or height <= 0:
            return
            
        # Create pixmap with high DPI support
        pixmap = QPixmap(width * 2, height * 2)  # Double resolution for better quality
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.scale(2, 2)  # Scale for high DPI
        
        # Calculate bar properties with improved spacing
        bar_width = int(width / (self.num_bands * 1.2))  # Reduced spacing between bars
        max_height = int(height * 0.85)  # Slightly taller bars
        
        # Enhanced gradient with more vibrant colors
        gradient = QLinearGradient(0, height, 0, 0)
        gradient.setColorAt(0.0, QColor(41, 128, 185))    # Blue
        gradient.setColorAt(0.2, QColor(142, 68, 173))    # Purple
        gradient.setColorAt(0.4, QColor(26, 188, 156))    # Turquoise
        gradient.setColorAt(0.6, QColor(46, 204, 113))    # Green
        gradient.setColorAt(0.8, QColor(241, 196, 15))    # Yellow
        gradient.setColorAt(1.0, QColor(231, 76, 60))     # Red
        
        # Draw spectrum bars with enhanced effects
        painter.setPen(Qt.NoPen)
        
        for i in range(self.num_bands):
            # Calculate smoother bar height with easing
            value = self.current_spectrum[i]
            target_height = int(value * max_height)
            bar_height = target_height
            
            x = int(i * width / self.num_bands)
            y = int(height - bar_height)
            
            # Draw bar with gradient
            painter.setBrush(gradient)
            painter.drawRoundedRect(
                int(x + bar_width/4),
                y,
                bar_width,
                bar_height,
                3, 3  # Slightly rounder corners
            )
            
            # Draw peak marker with glow effect
            peak_value = self.peak_spectrum[i]
            peak_y = int(height - (peak_value * max_height))
            
            # Glow effect for peak marker
            glow_gradient = QLinearGradient(0, peak_y, 0, peak_y + 4)
            glow_gradient.setColorAt(0, QColor(255, 255, 255, 180))
            glow_gradient.setColorAt(1, QColor(255, 255, 255, 0))
            
            painter.fillRect(
                int(x + bar_width/4),
                peak_y - 2,
                bar_width,
                4,  # Slightly thicker peak marker
                glow_gradient
            )
        
        painter.end()
        
        # Update label with high-quality scaling
        scaled_pixmap = pixmap.scaled(
            width,
            height,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        self.spectrum_label.setPixmap(scaled_pixmap)