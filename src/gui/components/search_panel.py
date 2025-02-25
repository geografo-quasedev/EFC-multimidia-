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
        
        # Style
        self.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                background-color: white;
            }
            QComboBox {
                padding: 5px;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                background-color: white;
            }
            QLabel {
                color: #495057;
            }
        """)
        
    def _on_search_change(self):
        search_text = self.search_input.text()
        filter_type = self.filter_combo.currentText().lower()
        self.search_changed.emit(search_text, filter_type)