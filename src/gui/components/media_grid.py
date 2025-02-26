from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
import os

class MediaGrid(QWidget):
    media_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.media_items = []
        self.setup_ui()
    
    def setup_ui(self):
        layout = QGridLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        self.grid_layout = layout
        self.setStyleSheet("""
            QWidget { background-color: white; }
            QLabel { 
                padding: 10px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                cursor: pointer;
            }
            QLabel:hover {
                background-color: #e9ecef;
            }
        """)
        
    def add_media_item(self, file_path):
        item_widget = QWidget()
        item_layout = QVBoxLayout(item_widget)
        
        # Get metadata
        from utils.metadata_extractor import MetadataExtractor
        metadata = MetadataExtractor.extract_metadata(file_path)
        
        # Create labels for metadata
        title_label = QLabel(metadata['title'] or os.path.basename(file_path))
        title_label.setStyleSheet("font-weight: bold;")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setWordWrap(True)
        
        info_label = QLabel()
        info_text = []
        if metadata['artist']:
            info_text.append(f"Artist: {metadata['artist']}")
        if metadata['album']:
            info_text.append(f"Album: {metadata['album']}")
        if metadata['duration']:
            minutes = int(metadata['duration'] // 60)
            seconds = int(metadata['duration'] % 60)
            info_text.append(f"Duration: {minutes}:{seconds:02d}")
        info_label.setText('\n'.join(info_text))
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("color: #666;")
        
        # Make widget clickable
        item_widget.mousePressEvent = lambda e, path=file_path: self.media_selected.emit(path)
        
        item_layout.addWidget(title_label)
        item_layout.addWidget(info_label)
        item_layout.setContentsMargins(10, 10, 10, 10)
        
        # Add to grid
        row = len(self.media_items) // 4
        col = len(self.media_items) % 4
        self.grid_layout.addWidget(item_widget, row, col)
        
        # Store media item info
        self.media_items.append({
            'widget': item_widget,
            'file_path': file_path,
            'label': label
        })
        
    def filter_media(self, search_text, filter_type):
        for item in self.media_items:
            item['widget'].setVisible(False)
            
        visible_items = []
        for item in self.media_items:
            if not search_text:  # Show all items if search is empty
                item['widget'].setVisible(True)
                visible_items.append(item)
                continue
                
            # Get metadata for filtering
            from src.utils.metadata_extractor import MetadataExtractor
            metadata = MetadataExtractor.extract_metadata(item['file_path'])
            
            # Apply filter based on type
            show_item = False
            search_text = search_text.lower()
            
            if filter_type == 'all':
                show_item = any(search_text in str(value).lower() 
                               for value in metadata.values() if value)
            elif filter_type in metadata and metadata[filter_type]:
                show_item = search_text in str(metadata[filter_type]).lower()
                
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