from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog
from PyQt5.QtCore import pyqtSignal

class Sidebar(QWidget):
    file_selected = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Add buttons for media management
        self.browse_button = QPushButton("Browse Media")
        self.browse_button.clicked.connect(self.browse_media)
        layout.addWidget(self.browse_button)
        
        # Add spacer to push content to the top
        layout.addStretch()
        
        self.setMaximumWidth(250)
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
        """)
    
    def browse_media(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Media File",
            "",
            "Media Files (*.mp3 *.mp4 *.wav *.avi *.mkv);;All Files (*.*)"
        )
        if file_path:
            self.file_selected.emit(file_path)