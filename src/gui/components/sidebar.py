from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel,
                             QListWidget, QListWidgetItem)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QIcon
from .playlist_panel import PlaylistPanel
from ...database import get_db
from ...database.models import Media
from PyQt5.QtCore import QTimer, QTime
from datetime import datetime

class Sidebar(QWidget):
    file_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.recent_media = []
        self.favorite_media = []
        self.db = next(get_db())
        # Initialize time_label before setup_ui
        self.time_label = QLabel()
        self.time_label.setAlignment(Qt.AlignCenter)
        self.time_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 24px;
                font-weight: bold;
                padding: 10px;
                background: linear-gradient(135deg, #1a237e 0%, #3949ab 100%);
                border-radius: 12px;
                margin-bottom: 20px;
            }
        """)
        
        # Setup timer for updating clock
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # Update every second
        self.update_time()  # Initial update
        
        self.setup_ui()
    
    def update_time(self):
        current_time = datetime.now().strftime("%H:%M:%S")
        self.time_label.setText(current_time)

    def update_clock(self):
        current_time = QTime.currentTime()
        time_text = current_time.toString('HH:mm')
        self.time_label.setText(time_text)

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Add clock at the top
        layout.addWidget(self.time_label)
        
        # Library items with icons
        library_items = [
            ("Browse", "🎵"),
            ("History", "⏱"),
            ("Setup", "⚙"),
            ("Clan Gaming", "🎮"),
            ("Remix", "🎚"),
            ("Saved", "💾"),
            ("Settings", "⚙"),
            ("Social", "👥"),
            ("Source", "📁"),
            ("Playlists", "📑"),
            ("Collections", "📚")
        ]
        
        for text, icon in library_items:
            btn = QPushButton(f"{icon} {text}")
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 12px 20px;
                    color: #808080;
                    background: transparent;
                    border: none;
                    font-size: 14px;
                }
                QPushButton:hover {
                    color: #ffffff;
                    background-color: #2d2d2d;
                }
                QPushButton:checked {
                    color: #ffffff;
                    background-color: #3d3d3d;
                }
            """)
            layout.addWidget(btn)

        layout.addStretch()
        
        self.setStyleSheet("""
            QWidget { 
                background-color: #1e1e1e;
                border: none;
            }
        """)
        
        self.setFixedWidth(250)
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
                background-color: #1a1a1a;
                border: none;
                border-radius: 20px;
            }
            QPushButton { 
                text-align: left;
                padding: 14px 24px;
                background: transparent;
                color: #808080;
                border: none;
                border-radius: 12px;
                font-size: 15px;
                margin: 4px 0;
                transition: all 0.3s ease;
            }
            QPushButton:hover {
                color: #ffffff;
                background-color: rgba(74, 144, 226, 0.1);
                padding-left: 28px;
            }
            QPushButton:checked {
                color: #ffffff;
                background: linear-gradient(135deg, rgba(74, 144, 226, 0.2) 0%, rgba(53, 122, 189, 0.2) 100%);
                border-left: 3px solid #4a90e2;
            }
            QListWidget {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 16px;
                padding: 12px;
                margin: 8px 0;
                color: #ffffff;
            }
            QListWidget:hover {
                border: 2px solid #4a90e2;
                background-color: #353535;
            }
            QListWidget::item {
                padding: 14px;
                border-radius: 12px;
                margin: 4px 0;
                background-color: rgba(255, 255, 255, 0.05);
                border-left: 3px solid transparent;
            }
            QListWidget::item:hover {
                background-color: rgba(74, 144, 226, 0.1);
                padding-left: 20px;
                border-left: 3px solid #4a90e2;
            }
            QListWidget::item:selected {
                background: linear-gradient(135deg, rgba(74, 144, 226, 0.2) 0%, rgba(53, 122, 189, 0.2) 100%);
                color: #ffffff;
                padding-left: 20px;
                font-weight: bold;
                border-left: 3px solid #4a90e2;
            }
            QLabel {
                color: #4a90e2;
                font-size: 16px;
                font-weight: bold;
                padding: 16px;
                margin: 8px 0;
                background: rgba(74, 144, 226, 0.1);
                border-radius: 12px;
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