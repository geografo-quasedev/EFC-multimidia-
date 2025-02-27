from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel,
                             QListWidget, QListWidgetItem)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon
from .playlist_panel import PlaylistPanel
from ...database import get_db
from ...database.models import Media

class Sidebar(QWidget):
    file_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.recent_media = []
        self.favorite_media = []
        self.db = next(get_db())
        self.setup_ui()
        self.load_favorites()
        self.load_recent_media()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)  # Increased padding for better spacing
        layout.setSpacing(12)  # Consistent spacing between elements
        
        # Media section with modern styling
        media_label = QLabel("📚 Media Library")
        media_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 20px;
                color: #1a237e;
                margin-bottom: 16px;
                padding: 12px;
                border-radius: 16px;
                background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
                box-shadow: 0 6px 12px rgba(0,0,0,0.1);
            }
        """)
        layout.addWidget(media_label)
        self.browse_button = QPushButton("📁 Browse Media")
        self.browse_button.clicked.connect(self.browse_media)
        layout.addWidget(self.browse_button)
        
        # Favorites section with enhanced visuals
        layout.addSpacing(25)
        favorites_label = QLabel("⭐ Favorites")
        favorites_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 18px;
                color: #1a237e;
                margin-bottom: 12px;
                padding: 12px;
                border-radius: 16px;
                background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
                box-shadow: 0 6px 12px rgba(0,0,0,0.1);
            }
        """)
        layout.addWidget(favorites_label)
        
        self.favorites_list = QListWidget()
        self.favorites_list.itemClicked.connect(self.on_favorite_selected)
        layout.addWidget(self.favorites_list)
        
        # Recent Media section with modern design
        layout.addSpacing(25)
        recent_label = QLabel("🕒 Recent Media")
        recent_label.setStyleSheet("""
            QLabel {
                font-weight: bold;
                font-size: 18px;
                color: #1a237e;
                margin-bottom: 12px;
                padding: 12px;
                border-radius: 16px;
                background: linear-gradient(135deg, #e8eaf6 0%, #c5cae9 100%);
                box-shadow: 0 6px 12px rgba(0,0,0,0.1);
            }
        """)
        layout.addWidget(recent_label)
        
        self.recent_list = QListWidget()
        self.recent_list.itemClicked.connect(self.on_recent_selected)
        layout.addWidget(self.recent_list)
        
        # Add playlist panel with enhanced spacing
        layout.addSpacing(30)
        self.playlist_panel = PlaylistPanel()
        layout.addWidget(self.playlist_panel)
        
        self.setMaximumWidth(300)  # Slightly wider for better content display
        self.setStyleSheet("""
            QWidget { 
                background-color: #ffffff;
                border-right: 2px solid #e3e3e3;
            }
            QPushButton { 
                padding: 12px;
                background: linear-gradient(135deg, #4a90e2 0%, #357abd 100%);
                color: white;
                border: none;
                border-radius: 16px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background: linear-gradient(135deg, #357abd 0%, #2c5aa0 100%);
                transform: translateY(-2px);
                box-shadow: 0 8px 16px rgba(0,0,0,0.15);
            }
            QPushButton:pressed {
                background: linear-gradient(135deg, #2c5aa0 0%, #1a4884 100%);
                transform: translateY(0);
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
            QListWidget {
                background-color: white;
                border: 1px solid #e3e3e3;
                border-radius: 16px;
                padding: 12px;
                margin: 8px 0;
            }
            QListWidget:hover {
                border-color: #4a90e2;
                box-shadow: 0 6px 12px rgba(0,0,0,0.08);
            }
            QListWidget::item {
                padding: 14px;
                border-radius: 12px;
                margin-bottom: 8px;
                background-color: #f8f9fa;
                border-left: 3px solid transparent;
            }
            QListWidget::item:hover {
                background-color: #e3f2fd;
                padding-left: 20px;
                color: #1a237e;
                border-left: 3px solid #4a90e2;
            }
            QListWidget::item:selected {
                background: linear-gradient(135deg, #4a90e2 0%, #357abd 100%);
                color: white;
                padding-left: 20px;
                font-weight: bold;
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
            self.add_to_recent(file_path)
            self.file_selected.emit(file_path)
    
    def load_favorites(self):
        """Load favorite media from database"""
        self.favorites_list.clear()
        favorites = self.db.query(Media).filter(Media.is_favorite == True).all()
        for media in favorites:
            item = QListWidgetItem(media.title or media.file_path)
            item.setData(Qt.UserRole, media.file_path)
            self.favorites_list.addItem(item)
    
    def load_recent_media(self):
        """Load recent media from database"""
        self.recent_list.clear()
        recent = self.db.query(Media).order_by(Media.last_played.desc()).limit(10).all()
        for media in recent:
            item = QListWidgetItem(media.title or media.file_path)
            item.setData(Qt.UserRole, media.file_path)
            self.recent_list.addItem(item)
    
    def add_to_recent(self, file_path):
        """Add media to recent list"""
        media = self.db.query(Media).filter(Media.file_path == file_path).first()
        if media:
            media.last_played = time.time()
            self.db.commit()
            self.load_recent_media()
    
    def on_favorite_selected(self, item):
        """Handle favorite media selection"""
        file_path = item.data(Qt.UserRole)
        if file_path:
            self.file_selected.emit(file_path)
    
    def on_recent_selected(self, item):
        """Handle recent media selection"""
        file_path = item.data(Qt.UserRole)
        if file_path:
            self.file_selected.emit(file_path)