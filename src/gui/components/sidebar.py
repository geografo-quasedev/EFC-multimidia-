from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel
from PyQt5.QtCore import pyqtSignal
from .playlist_panel import PlaylistPanel

class Sidebar(QWidget):
    file_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Media section
        media_label = QLabel("Media")
        media_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(media_label)
        
        self.browse_button = QPushButton("Browse Media")
        self.browse_button.clicked.connect(self.browse_media)
        layout.addWidget(self.browse_button)
        
        # Add playlist panel
        layout.addSpacing(20)
        self.playlist_panel = PlaylistPanel()
        layout.addWidget(self.playlist_panel)
        
        self.setMaximumWidth(250)
        self.setStyleSheet("""
            QWidget { background-color: #f0f0f0; }
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
        """)
    
    def browse_media(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Media File",
            "",
            "Media Files (*.mp3 *.mp4 *.wav *.avi *.mkv);;All Files (*.*)"
        )
        if file_path:
            self.file_selected.emit(file_path)