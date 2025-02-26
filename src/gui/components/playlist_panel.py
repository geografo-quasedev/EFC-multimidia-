from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QListWidget
from PyQt5.QtCore import pyqtSignal
from ...utils.media_export import ShareDialog
from ...utils.qr_share_dialog import QRShareDialog
from ...utils.share_manager import ShareManager

class PlaylistPanel(QWidget):
    playlist_selected = pyqtSignal(str)
    playlist_created = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.playlist_items = []
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("Playlists")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)
        
        # Playlist list
        self.playlist_list = QListWidget()
        self.playlist_list.itemClicked.connect(self.on_playlist_selected)
        layout.addWidget(self.playlist_list)
        
        # New playlist section
        new_playlist_label = QLabel("Create New Playlist")
        layout.addWidget(new_playlist_label)
        
        # Input and button layout
        button_layout = QHBoxLayout()
        
        self.playlist_name_input = QLineEdit()
        button_layout.addWidget(self.playlist_name_input)
        
        create_button = QPushButton("Create")
        create_button.clicked.connect(self.create_playlist)
        button_layout.addWidget(create_button)
        
        layout.addLayout(button_layout)
        
        # Share button
        self.share_button = QPushButton("Share Playlist")
        self.share_button.clicked.connect(self.show_share_dialog)
        self.share_button.setEnabled(False)
        layout.addWidget(self.share_button)
        
        # Refresh playlists
        self.refresh_playlists()
        
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
            QListWidget::item:selected {
                background-color: #e3f2fd;
                color: #1976d2;
            }
        """)
    
    def on_playlist_selected(self, item):
        self.playlist_selected.emit(item.text())
    
    def create_playlist(self):
        name = self.playlist_name_input.text().strip()
        if name:
            self.playlist_created.emit(name)
            self.playlist_name_input.clear()
    
    def refresh_playlists(self):
        self.playlist_list.clear()
        # TODO: Load playlists from database
        
    def show_share_dialog(self):
        if not self.playlist_items:
            return
            
        # Generate share link
        share_link = ShareManager.generate_share_link(self.playlist_items)
        
        # Show QR share dialog
        dialog = QRShareDialog(share_link, self)
        dialog.exec_()
        
    def set_playlist_items(self, items):
        """Set the current playlist items for sharing"""
        self.playlist_items = items
        self.share_button.setEnabled(bool(items))