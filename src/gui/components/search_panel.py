from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit,
                             QComboBox, QLabel)
from PyQt5.QtCore import pyqtSignal

class SearchPanel(QWidget):
    search_changed = pyqtSignal(str, str)  # search text, filter type
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        search_layout = QHBoxLayout()
        
        # Search input
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search media...")
        self.search_input.textChanged.connect(self._on_search_change)
        
        # Filter dropdown
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["All", "Title", "Artist", "Album"])
        self.filter_combo.currentTextChanged.connect(self._on_search_change)
        
        # Add widgets to layout
        search_layout.addWidget(QLabel("Search:"))
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(QLabel("Filter by:"))
        search_layout.addWidget(self.filter_combo)
        
        layout.addLayout(search_layout)
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1a1a1a, stop:1 #2d2d2d);
                border-radius: 24px;
                padding: 20px;
                box-shadow: 0 8px 16px rgba(0, 0, 0, 0.15);
            }
            QLineEdit {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2d2d2d, stop:1 #3d3d3d);
                border: 2px solid rgba(74, 144, 226, 0.1);
                border-radius: 25px;
                padding: 14px 24px;
                color: #ffffff;
                font-size: 15px;
                min-width: 320px;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }
            QLineEdit:focus {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #3d3d3d, stop:1 #4d4d4d);
                border-color: #4a90e2;
                box-shadow: 0 0 16px rgba(74, 144, 226, 0.25);
                transform: translateY(-1px);
            }
            QComboBox {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #2d2d2d, stop:1 #3d3d3d);
                border: 2px solid rgba(74, 144, 226, 0.1);
                border-radius: 25px;
                padding: 14px 24px;
                color: #ffffff;
                min-width: 200px;
                font-weight: 500;
                selection-background-color: #4a90e2;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }
            QComboBox:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #3d3d3d, stop:1 #4d4d4d);
                border-color: #4a90e2;
                box-shadow: 0 4px 12px rgba(74, 144, 226, 0.2);
                transform: translateY(-2px);
            }
            QComboBox::drop-down {
                border: none;
                width: 32px;
                border-left: 2px solid rgba(255, 255, 255, 0.1);
                padding-left: 12px;
                transition: all 0.2s ease;
            }
            QComboBox::down-arrow {
                image: url(resources/icons/arrow-down.png);
                width: 18px;
                height: 18px;
                margin-right: 12px;
                transition: transform 0.2s ease;
            }
            QComboBox QAbstractItemView {
                background: #2d2d2d;
                border: 2px solid #4a90e2;
                selection-background-color: #4a90e2;
                selection-color: white;
                border-radius: 16px;
                padding: 12px;
                box-shadow: 0 8px 16px rgba(0, 0, 0, 0.2);
            }
            QLabel {
                color: #ffffff;
                font-size: 15px;
                font-weight: 500;
                margin-right: 16px;
                opacity: 0.9;
                text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
                transition: all 0.2s ease;
                letter-spacing: 0.3px;
            }
            QLabel:hover {
                opacity: 1;
                transform: translateX(2px);
            }
        """)

    def _on_search_change(self):
        search_text = self.search_input.text()
        filter_type = self.filter_combo.currentText().lower()
        self.search_changed.emit(search_text, filter_type)