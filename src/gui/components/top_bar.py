from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QLineEdit, 
                           QPushButton, QComboBox)
from PyQt5.QtCore import Qt, pyqtSignal

class TopBar(QWidget):
    search_changed = pyqtSignal(str, str)  # search text, filter type
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)
        
        # Time display
        self.time_label = QLabel("02:39")
        self.time_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 24px;
                font-weight: bold;
                padding: 0 20px;
            }
        """)
        
        # Control icons
        control_buttons = [
            ("⚙", "Settings"),
            ("↻", "Refresh"),
            ("◈", "Minimize"),
            ("□", "Maximize"),
            ("×", "Close")
        ]
        
        self.control_buttons = []
        for symbol, tooltip in control_buttons:
            btn = QPushButton(symbol)
            btn.setToolTip(tooltip)
            btn.setFixedSize(32, 32)
            self.control_buttons.append(btn)
        
        # Add widgets to layout
        layout.addWidget(self.time_label)
        layout.addStretch()
        
        for btn in self.control_buttons:
            layout.addWidget(btn)
        
        # Update styling
        self.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border: none;
            }
            QPushButton {
                background-color: transparent;
                color: #808080;
                font-size: 16px;
                border-radius: 16px;
            }
            QPushButton:hover {
                background-color: #2d2d2d;
                color: #ffffff;
            }
            QPushButton:pressed {
                background-color: #3d3d3d;
            }
        """)
        
    def on_search_changed(self):
        search_text = self.search_box.text()
        filter_type = self.filter_combo.currentText().lower()
        self.search_changed.emit(search_text, filter_type)