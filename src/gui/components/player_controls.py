from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSlider
from PyQt5.QtCore import Qt, pyqtSignal

class PlayerControls(QWidget):
    play_clicked = pyqtSignal()
    stop_clicked = pyqtSignal()
    prev_clicked = pyqtSignal()
    next_clicked = pyqtSignal()
    volume_changed = pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.is_playing = False
        self.setup_ui()
        self.setup_connections()
    
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(10)
        
        # Create playback control buttons
        self.play_button = QPushButton("Play")
        self.stop_button = QPushButton("Stop")
        self.prev_button = QPushButton("Previous")
        self.next_button = QPushButton("Next")
        
        # Create volume slider
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setMinimum(0)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(100)
        self.volume_slider.setFixedWidth(100)
        
        # Add buttons to layout
        layout.addWidget(self.prev_button)
        layout.addWidget(self.play_button)
        layout.addWidget(self.stop_button)
        layout.addWidget(self.next_button)
        layout.addWidget(self.volume_slider)
        
        # Center the controls
        layout.addStretch(1)
        layout.insertStretch(0, 1)
        
        self.setFixedHeight(50)
        self.setStyleSheet("""
            QWidget { background-color: #e0e0e0; }
            QPushButton { 
                padding: 8px 16px;
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        
    def setup_connections(self):
        self.play_button.clicked.connect(self.handle_play)
        self.stop_button.clicked.connect(self.stop_clicked.emit)
        self.prev_button.clicked.connect(self.prev_clicked.emit)
        self.next_button.clicked.connect(self.next_clicked.emit)
        self.volume_slider.valueChanged.connect(self.volume_changed.emit)
        
    def handle_play(self):
        self.is_playing = not self.is_playing
        self.play_button.setText("Pause" if self.is_playing else "Play")
        self.play_clicked.emit()
        
    def enable_controls(self, enabled=True):
        self.play_button.setEnabled(enabled)
        self.stop_button.setEnabled(enabled)
        self.prev_button.setEnabled(enabled)
        self.next_button.setEnabled(enabled)