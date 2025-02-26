from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QPushButton,
                             QListWidget, QInputDialog, QMessageBox)
from PyQt5.QtCore import pyqtSignal
from database import get_db
from database.models import Playlist

class PlaylistPanel(QWidget):
    playlist_selected = pyqtSignal(int)  # Emits playlist ID when selected
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = next(get_db())
        self.setup_ui()
        self.load_playlists()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header = QLabel("Playlists")
        header.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(header)
        
        # Playlist list
        self.playlist_list = QListWidget()
        self.playlist_list.itemClicked.connect(self.handle_playlist_selected)
        layout.addWidget(self.playlist_list)
        
        # Add playlist button
        self.add_button = QPushButton("New Playlist")
        self.add_button.clicked.connect(self.create_playlist)
        layout.addWidget(self.add_button)
        
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
    
    def load_playlists(self):
        self.playlist_list.clear()
        playlists = self.db.query(Playlist).all()
        for playlist in playlists:
            self.playlist_list.addItem(playlist.name)
    
    def create_playlist(self):
        name, ok = QInputDialog.getText(
            self, 'Create Playlist', 'Enter playlist name:')
        
        if ok and name:
            # Check if playlist already exists
            existing = self.db.query(Playlist).filter(Playlist.name == name).first()
            if existing:
                QMessageBox.warning(
                    self, 'Error', 'A playlist with this name already exists')
                return
            
            # Create new playlist
            playlist = Playlist(name=name)
            self.db.add(playlist)
            self.db.commit()
            
            # Refresh list
            self.load_playlists()
    
    def handle_playlist_selected(self, item):
        playlist = self.db.query(Playlist)\
            .filter(Playlist.name == item.text())\
            .first()
        if playlist:
            self.playlist_selected.emit(playlist.id)