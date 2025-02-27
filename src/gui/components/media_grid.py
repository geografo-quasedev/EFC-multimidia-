from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from src.database import get_db
from src.database.models import Media
import os
from ...utils.media_visualizer import MediaVisualizer

class MediaGrid(QWidget):
    media_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.media_items = []
        self.setup_ui()
    
    def setup_ui(self):
        layout = QGridLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        layout.setAlignment(Qt.AlignTop)
        
        self.grid_layout = layout
        self.setStyleSheet("""
            QWidget { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1a1a1a, stop:1 #2d2d2d);
                border-radius: 24px;
                padding: 24px;
            }
            QWidget[class="media-item"] {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2d2d2d, stop:1 #3d3d3d);
                border-radius: 24px;
                padding: 24px;
                border: 2px solid rgba(255,255,255,0.1);
                margin: 8px;
                min-width: 320px;
                max-width: 400px;
            }
            QWidget[class="media-item"]:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #3d3d3d, stop:1 #4d4d4d);
                border: 2px solid #4a90e2;
            }
            QLabel { 
                padding: 16px;
                color: #ffffff;
                font-size: 15px;
                opacity: 0.95;
                transition: all 0.2s ease;
                letter-spacing: 0.3px;
            }
            QLabel[class="title-label"] {
                font-size: 22px;
                font-weight: bold;
                color: #4a90e2;
                margin-bottom: 16px;
                text-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
                letter-spacing: 0.5px;
            }
            QLabel[class="info-label"] {
                color: #b0bec5;
                font-size: 15px;
                font-weight: 500;
                line-height: 1.5;
                letter-spacing: 0.3px;
            }
            QLabel[class="visual-label"] {
                background: rgba(0,0,0,0.25);
                border-radius: 16px;
                padding: 12px;
                margin-bottom: 20px;
                box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.15);
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }
            QLabel[class="visual-label"]:hover {
                transform: scale(1.03);
                box-shadow: inset 0 3px 6px rgba(0, 0, 0, 0.2);
            }
            .metadata-container {
                padding: 24px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2d2d2d, stop:1 #3d3d3d);
                border-radius: 20px;
                border: 2px solid rgba(255,255,255,0.1);
                margin-top: 20px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }
            .metadata-container:hover {
                border-color: #4a90e2;
                box-shadow: 0 6px 12px rgba(74, 144, 226, 0.25);
                transform: translateY(-4px);
            }
        """)
        self.grid_layout = layout
        self.setStyleSheet("""
            QWidget { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1a1a1a, stop:1 #2d2d2d);
                border-radius: 24px;
                padding: 24px;
            }
            QWidget[class="media-item"] {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2d2d2d, stop:1 #3d3d3d);
                border-radius: 24px;
                padding: 24px;
                border: 2px solid rgba(255,255,255,0.1);
                margin: 8px;
                min-width: 320px;
                max-width: 400px;
            }
            QWidget[class="media-item"]:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #3d3d3d, stop:1 #4d4d4d);
                border: 2px solid #4a90e2;
            }
            QLabel { 
                padding: 16px;
                color: #ffffff;
                font-size: 15px;
                opacity: 0.95;
                transition: all 0.2s ease;
                letter-spacing: 0.3px;
            }
            QLabel[class="title-label"] {
                font-size: 22px;
                font-weight: bold;
                color: #4a90e2;
                margin-bottom: 16px;
                text-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
                letter-spacing: 0.5px;
            }
            QLabel[class="info-label"] {
                color: #b0bec5;
                font-size: 15px;
                font-weight: 500;
                line-height: 1.5;
                letter-spacing: 0.3px;
            }
            QLabel[class="visual-label"] {
                background: rgba(0,0,0,0.25);
                border-radius: 16px;
                padding: 12px;
                margin-bottom: 20px;
                box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.15);
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }
            QLabel[class="visual-label"]:hover {
                transform: scale(1.03);
                box-shadow: inset 0 3px 6px rgba(0, 0, 0, 0.2);
            }
            .metadata-container {
                padding: 24px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2d2d2d, stop:1 #3d3d3d);
                border-radius: 20px;
                border: 2px solid rgba(255,255,255,0.1);
                margin-top: 20px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }
            .metadata-container:hover {
                border-color: #4a90e2;
                box-shadow: 0 6px 12px rgba(74, 144, 226, 0.25);
                transform: translateY(-4px);
            }
        """)
    def add_media_item(self, file_path):
        item_widget = QWidget()
        item_widget.setProperty("class", "media-item")
        item_layout = QVBoxLayout(item_widget)
        item_layout.setContentsMargins(0, 0, 0, 0)
        item_layout.setSpacing(10)
        
        # Get metadata and media info
        from src.utils.metadata_extractor import MetadataExtractor
        metadata = MetadataExtractor.extract_metadata(file_path)
        media_info = MediaVisualizer.get_media_info(file_path)
        
        # Add visualization with enhanced styling
        if metadata['media_type'] == 'audio':
            waveform = MediaVisualizer.generate_waveform(file_path)
            if waveform:
                visual_label = QLabel()
                visual_label.setProperty("class", "visual-label")
                visual_label.setPixmap(waveform.scaled(320, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                visual_label.setAlignment(Qt.AlignCenter)
                item_layout.addWidget(visual_label)
        else:
            thumbnail = MediaVisualizer.generate_video_thumbnail(file_path)
            if thumbnail:
                visual_label = QLabel()
                visual_label.setProperty("class", "visual-label")
                visual_label.setPixmap(thumbnail.scaled(320, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                visual_label.setAlignment(Qt.AlignCenter)
                item_layout.addWidget(visual_label)
        
        # Create metadata container with modern styling
        metadata_container = QWidget()
        metadata_container.setProperty("class", "metadata-container")
        metadata_layout = QVBoxLayout(metadata_container)
        metadata_layout.setSpacing(8)
        
        # Title with enhanced styling
        title_label = QLabel(metadata['title'] or os.path.basename(file_path))
        title_label.setProperty("class", "title-label")
        title_label.setWordWrap(True)
        metadata_layout.addWidget(title_label)
        
        # Info with improved layout
        info_label = QLabel()
        info_label.setProperty("class", "info-label")
        info_text = []
        
        if metadata['artist']:
            info_text.append(f"🎤 {metadata['artist']}")
        if metadata['album']:
            info_text.append(f"💿 {metadata['album']}")
        
        # Add technical information with icons
        if media_info:
            for key, value in media_info.items():
                icon = {
                    'duration': '⏱',
                    'bitrate': '📊',
                    'resolution': '📐',
                    'codec': '🔧'
                }.get(key.lower(), '•')
                info_text.append(f"{icon} {key.replace('_', ' ').title()}: {value}")
        
        info_label.setText('\n'.join(info_text))
        info_label.setWordWrap(True)
        metadata_layout.addWidget(info_label)
        
        item_layout.addWidget(metadata_container)
        
        # Make widget clickable with ripple effect
        item_widget.mousePressEvent = lambda e, path=file_path: self.media_selected.emit(path)
        
        # Add to grid with improved layout
        row = len(self.media_items) // 3  # Changed to 3 items per row for better layout
        col = len(self.media_items) % 3
        self.grid_layout.addWidget(item_widget, row, col)
        
        self.media_items.append({
            'widget': item_widget,
            'file_path': file_path,
            'metadata': metadata
        })
        
    def filter_media(self, search_text, filter_type):
                # Get database connection
        self.db = next(get_db())
        
        for item in self.media_items:
            item['widget'].setVisible(False)
            
        visible_items = []
        for item in self.media_items:
            if not search_text:  # Show all items if search is empty
                item['widget'].setVisible(True)
                visible_items.append(item)
                continue
                
            # Get media from database for filtering
            media = db.query(Media).filter(Media.file_path == item['file_path']).first()
            show_item = False
            search_text = search_text.lower()
            
            if filter_type == 'all':
                # Search in metadata
                show_item = any(search_text in str(value).lower() 
                               for value in item['metadata'].values() if value)
                               
                # Search in tags
                if media and media.tags:
                    show_item = show_item or any(search_text in tag.name.lower() 
                                                for tag in media.tags)
                                                
                # Search in categories
                if media and media.categories:
                    show_item = show_item or any(search_text in cat.name.lower() 
                                                for cat in media.categories)
                                                
            elif filter_type == 'tag' and media:
                show_item = any(search_text in tag.name.lower() for tag in media.tags)
                
            elif filter_type == 'category' and media:
                show_item = any(search_text in cat.name.lower() for cat in media.categories)
                
            elif filter_type == 'favorite' and media:
                show_item = media.is_favorite
                
            elif filter_type in item['metadata'] and item['metadata'][filter_type]:
                show_item = search_text in str(item['metadata'][filter_type]).lower()
                
            item['widget'].setVisible(show_item)
            if show_item:
                visible_items.append(item)
        
        # Reposition visible items in grid
        for i, item in enumerate(visible_items):
            row = i // 4
            col = i % 4
            self.grid_layout.addWidget(item['widget'], row, col)
        
    def clear_media_items(self):
        for item in self.media_items:
            self.grid_layout.removeWidget(item["widget"])
            item["widget"].deleteLater()
        self.media_items.clear()