from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSlider, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtMultimedia import QMediaPlayer

class PlayerControls(QWidget):
    def __init__(self, media_player, parent=None):
        super().__init__(parent)
        self.media_player = media_player
        self.is_playing = False
        self.setup_ui()
        
    def setup_ui(self):
        layout = QHBoxLayout(self)
        
        # Play/Pause button
        self.play_button = QPushButton("Play")
        self.play_button.clicked.connect(self.toggle_playback)
        layout.addWidget(self.play_button)
        
        # Stop button
        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_playback)
        layout.addWidget(self.stop_button)
        
        # Volume slider
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(self.media_player.volume())
        self.volume_slider.valueChanged.connect(self.media_player.setVolume)
        layout.addWidget(self.volume_slider)
        
        # Volume label
        self.volume_label = QLabel(f"Volume: {self.media_player.volume()}%")
        layout.addWidget(self.volume_label)
        
        # Progress slider
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setRange(0, 0)
        self.progress_slider.sliderMoved.connect(self.set_position)
        layout.addWidget(self.progress_slider)
        
        # Time labels
        self.current_time = QLabel("0:00")
        layout.addWidget(self.current_time)
        layout.addWidget(QLabel("/"))
        self.total_time = QLabel("0:00")
        layout.addWidget(self.total_time)
        
        # Connect media player signals
        self.media_player.durationChanged.connect(self.duration_changed)
        self.media_player.positionChanged.connect(self.position_changed)
        
        # Initially disable controls
        self.enable_controls(False)
        
        self.setStyleSheet("""
            QPushButton { 
                padding: 8px;
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
            QSlider::groove:horizontal {
                border: 1px solid #999;
                height: 8px;
                background: #f0f0f0;
                margin: 2px 0;
                border-radius: 4px;
            }
            QSlider::handle:horizontal {
                background: #4a90e2;
                border: 1px solid #5c5c5c;
                width: 18px;
                margin: -2px 0;
                border-radius: 9px;
            }
        """)
        
    def toggle_playback(self):
        if self.is_playing:
            self.media_player.pause()
            self.play_button.setText("Play")
        else:
            self.media_player.play()
            self.play_button.setText("Pause")
        self.is_playing = not self.is_playing
    
    def stop_playback(self):
        self.media_player.stop()
        self.is_playing = False
        self.play_button.setText("Play")
    
    def set_position(self, position):
        self.media_player.setPosition(position)
    
    def duration_changed(self, duration):
        self.progress_slider.setRange(0, duration)
        self.update_time_label(self.total_time, duration)
    
    def position_changed(self, position):
        self.progress_slider.setValue(position)
        self.update_time_label(self.current_time, position)
    
    def update_time_label(self, label, ms):
        s = ms // 1000
        m = s // 60
        s = s % 60
        label.setText(f"{m}:{s:02d}")
        
    def enable_controls(self, enabled):
        self.play_button.setEnabled(enabled)
        self.stop_button.setEnabled(enabled)
        self.progress_slider.setEnabled(enabled)
        self.volume_slider.setEnabled(enabled)
    
    def set_current_video(self, file_path):
        self.is_video = file_path is not None and file_path.lower().endswith(('.mp4', '.avi', '.mkv'))