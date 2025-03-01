from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QSlider, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtMultimedia import QMediaPlayer

class PlayerControls(QWidget):
    def __init__(self, media_player, parent=None):
        super().__init__(parent)
        self.media_player = media_player
        self.is_playing = False
        self.is_video = False
        self.preview_label = QLabel()
        self.preview_label.setFixedSize(160, 90)
        self.preview_label.setStyleSheet("background-color: #2c2c2c; border-radius: 4px;")
        self.preview_label.hide()
        self.setup_ui()
        
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setSpacing(15)  # Increased spacing between controls
        
        # Play/Pause button with enhanced styling
        self.play_button = QPushButton("▶ Play")
        self.play_button.clicked.connect(self.toggle_playback)
        self.play_button.setMinimumWidth(120)
        layout.addWidget(self.play_button)
        
        # Stop button with modern icon
        self.stop_button = QPushButton("⏹ Stop")
        self.stop_button.clicked.connect(self.stop_playback)
        self.stop_button.setMinimumWidth(120)
        layout.addWidget(self.stop_button)
        
        # Volume control with improved visuals
        volume_container = QWidget()
        volume_layout = QHBoxLayout(volume_container)
        volume_layout.setContentsMargins(0, 0, 0, 0)
        volume_layout.setSpacing(10)
        
        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(self.media_player.volume())
        self.volume_slider.valueChanged.connect(self.media_player.setVolume)
        self.volume_slider.setMinimumWidth(150)
        volume_layout.addWidget(self.volume_slider)
        
        self.volume_label = QLabel(f"🔊 {self.media_player.volume()}%")
        self.volume_label.setMinimumWidth(60)
        volume_layout.addWidget(self.volume_label)
        layout.addWidget(volume_container)
        
        # Progress slider with modern styling
        progress_container = QWidget()
        progress_layout = QHBoxLayout(progress_container)
        progress_layout.setContentsMargins(0, 0, 0, 0)
        progress_layout.setSpacing(10)
        
        self.progress_slider = QSlider(Qt.Horizontal)
        self.progress_slider.setRange(0, 0)
        self.progress_slider.sliderMoved.connect(self.set_position)
        self.progress_slider.setMouseTracking(True)
        self.progress_slider.mouseMoveEvent = self.show_preview
        self.progress_slider.leaveEvent = self.hide_preview
        progress_layout.addWidget(self.progress_slider)
        
        # Time labels with improved formatting
        time_container = QWidget()
        time_layout = QHBoxLayout(time_container)
        time_layout.setContentsMargins(0, 0, 0, 0)
        time_layout.setSpacing(5)
        
        self.current_time = QLabel("0:00")
        time_layout.addWidget(self.current_time)
        time_layout.addWidget(QLabel("/"))
        self.total_time = QLabel("0:00")
        time_layout.addWidget(self.total_time)
        progress_layout.addWidget(time_container)
        
        layout.addWidget(progress_container)
        
        self.setStyleSheet("""
            QWidget {
                background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
                border-radius: 20px;
                padding: 25px;
            }
            QPushButton { 
                padding: 16px 32px;
                background: linear-gradient(135deg, #4a90e2 0%, #357abd 100%);
                color: white;
                border: none;
                border-radius: 30px;
                font-weight: bold;
                font-size: 16px;
                min-width: 140px;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                box-shadow: 0 6px 12px rgba(0,0,0,0.15);
            }
            QPushButton:hover {
                background: linear-gradient(135deg, #357abd 0%, #2c5aa0 100%);
                transform: translateY(-3px);
                box-shadow: 0 12px 24px rgba(0,0,0,0.2);
            }
            QPushButton:pressed {
                transform: translateY(1px);
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            QSlider::groove:horizontal {
                border: none;
                height: 10px;
                background: linear-gradient(135deg, #2d2d2d 0%, #3d3d3d 100%);
                border-radius: 5px;
                margin: 2px 0;
            }
            QSlider::handle:horizontal {
                background: linear-gradient(135deg, #4a90e2 0%, #357abd 100%);
                border: 2px solid #ffffff;
                width: 22px;
                height: 22px;
                margin: -7px 0;
                border-radius: 11px;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                box-shadow: 0 2px 6px rgba(0,0,0,0.2);
            }
            QSlider::handle:horizontal:hover {
                background: linear-gradient(135deg, #357abd 0%, #2c5aa0 100%);
                transform: scale(1.2);
                box-shadow: 0 4px 12px rgba(74, 144, 226, 0.4);
            }
            QLabel {
                color: #ffffff;
                font-size: 15px;
                font-weight: 600;
                margin: 0 10px;
                text-shadow: 0 1px 2px rgba(0,0,0,0.2);
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
    
    def show_preview(self, event):
        if not self.is_video:
            return
            
        # Calculate position percentage
        width = self.progress_slider.width()
        x = event.pos().x()
        position_percent = max(0, min(1, x / width))
        
        # Get current media source
        media = self.media_player.currentMedia()
        if media.isNull():
            return
            
        # Generate preview
        preview = MediaVisualizer.generate_video_preview(
            media.canonicalUrl().toLocalFile(),
            position_percent,
            160, 90
        )
        
        if preview:
            self.preview_label.setPixmap(preview)
            
            # Position preview above progress bar
            global_pos = self.progress_slider.mapToGlobal(event.pos())
            self.preview_label.move(
                global_pos.x() - self.preview_label.width() // 2,
                global_pos.y() - self.preview_label.height() - 10
            )
            self.preview_label.show()
    
    def hide_preview(self, event):
        self.preview_label.hide()
    
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