from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QListWidget,
                             QHBoxLayout, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap

class NowPlayingPanel(QWidget):
    track_selected = pyqtSignal(int)  # Emits track index when selected
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header = QLabel("Now Playing")
        header.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(header)
        
        # Current track info panel
        current_track_panel = QFrame()
        current_track_panel.setFrameStyle(QFrame.StyledPanel)
        current_track_layout = QHBoxLayout(current_track_panel)
        
        # Album art placeholder
        self.album_art = QLabel()
        self.album_art.setFixedSize(100, 100)
        self.album_art.setStyleSheet("background-color: #ddd;")
        self.album_art.setAlignment(Qt.AlignCenter)
        current_track_layout.addWidget(self.album_art)
        
        # Track info
        track_info_layout = QVBoxLayout()
        self.title_label = QLabel("No track playing")
        self.title_label.setStyleSheet("font-weight: bold;")
        self.artist_label = QLabel("")
        self.album_label = QLabel("")
        
        track_info_layout.addWidget(self.title_label)
        track_info_layout.addWidget(self.artist_label)
        track_info_layout.addWidget(self.album_label)
        track_info_layout.addStretch()
        
        current_track_layout.addLayout(track_info_layout)
        layout.addWidget(current_track_panel)
        
        # Queue header
        queue_header = QLabel("Up Next")
        queue_header.setStyleSheet("font-weight: bold; margin-top: 10px;")
        layout.addWidget(queue_header)
        
        # Queue list
        self.queue_list = QListWidget()
        self.queue_list.itemClicked.connect(self.handle_track_selected)
        layout.addWidget(self.queue_list)
        
        self.setStyleSheet("""
            QWidget { background-color: #f0f0f0; }
            QFrame {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 4px;
            }
            QListWidget {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 4px;
            }
            QListWidget::item {
                padding: 5px;
            }
            QListWidget::item:hover {
                background-color: #e9ecef;
            }
            QListWidget::item:selected {
                background-color: #4a90e2;
                color: white;
            }
        """)
    
    def update_current_track(self, title, artist, album, album_art=None):
        self.title_label.setText(title)
        self.artist_label.setText(artist)
        self.album_label.setText(album)
        
        if album_art:
            pixmap = QPixmap(album_art)
            self.album_art.setPixmap(pixmap.scaled(100, 100, Qt.KeepAspectRatio))
        else:
            self.album_art.setText("🎵")
    
    def update_queue(self, tracks):
        self.queue_list.clear()
        for track in tracks:
            self.queue_list.addItem(f"{track['title']} - {track['artist']}")
    
    def handle_track_selected(self, item):
        self.track_selected.emit(self.queue_list.row(item))