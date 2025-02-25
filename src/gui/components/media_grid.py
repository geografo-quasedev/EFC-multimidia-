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
        
        # Create label with file name
        file_name = os.path.basename(file_path)
        label = QLabel(file_name)
        label.setAlignment(Qt.AlignCenter)
        label.setWordWrap(True)
        
        # Make label clickable
        label.mousePressEvent = lambda e, path=file_path: self.media_selected.emit(path)
        
        item_layout.addWidget(label)
        item_layout.setContentsMargins(5, 5, 5, 5)
        
        # Add to grid
        row = len(self.media_items) // 4
        col = len(self.media_items) % 4
        self.grid_layout.addWidget(item_widget, row, col)
        
        self.media_items.append({"widget": item_widget, "path": file_path})
        
    def clear_media_items(self):
        for item in self.media_items:
            self.grid_layout.removeWidget(item["widget"])
            item["widget"].deleteLater()
        self.media_items.clear()