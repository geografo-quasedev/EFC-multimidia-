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
            QWidget { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1a1a1a, stop:1 #2d2d2d);
                border-radius: 24px;
                padding: 24px;
                box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
            }
            QPushButton { 
                padding: 14px 28px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4a90e2, stop:1 #357abd);
                color: white;
                border: none;
                border-radius: 25px;
                font-weight: bold;
                font-size: 15px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #357abd, stop:1 #2c5aa0);
                box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
                transform: translateY(-2px);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2c5aa0, stop:1 #1f4677);
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
                transform: translateY(1px);
            }
            QListWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2d2d2d, stop:1 #3d3d3d);
                border: 2px solid rgba(74, 144, 226, 0.1);
                border-radius: 16px;
                padding: 16px;
                box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);
                margin: 12px 0;
            }
            QListWidget:hover {
                border-color: #4a90e2;
                box-shadow: inset 0 2px 4px rgba(74, 144, 226, 0.2);
            }
            QListWidget::item {
                padding: 14px;
                border-radius: 12px;
                margin-bottom: 8px;
                color: #ffffff;
                background: rgba(255, 255, 255, 0.05);
                transition: all 0.2s ease;
            }
            QListWidget::item:hover {
                background: rgba(74, 144, 226, 0.1);
                padding-left: 24px;
                color: #4a90e2;
                border-left: 3px solid #4a90e2;
            }
            QListWidget::item:selected {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4a90e2, stop:1 #357abd);
                color: white;
                padding-left: 24px;
                font-weight: bold;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
            }
            QLineEdit {
                padding: 14px 24px;
                border: 2px solid rgba(74, 144, 226, 0.1);
                border-radius: 25px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2d2d2d, stop:1 #3d3d3d);
                color: #ffffff;
                font-size: 15px;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }
            QLineEdit:focus {
                border-color: #4a90e2;
                box-shadow: 0 0 16px rgba(74, 144, 226, 0.25);
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #3d3d3d, stop:1 #4d4d4d);
            }
            QLabel {
                color: #ffffff;
                font-size: 15px;
                font-weight: 500;
                margin-bottom: 12px;
                text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
                letter-spacing: 0.3px;
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