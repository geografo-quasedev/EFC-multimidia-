from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QLineEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QClipboard
from .qr_generator import QRGenerator

class QRShareDialog(QDialog):
    def __init__(self, share_data, parent=None):
        super().__init__(parent)
        self.share_data = share_data
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("Share Media")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # QR Code display
        self.qr_label = QLabel()
        self.qr_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.qr_label)
        
        # Share link display
        link_label = QLabel("Share Link:")
        layout.addWidget(link_label)
        
        self.link_edit = QLineEdit(self.share_data)
        self.link_edit.setReadOnly(True)
        layout.addWidget(self.link_edit)
        
        # Copy button
        copy_button = QPushButton("Copy Link")
        copy_button.clicked.connect(self.copy_link)
        layout.addWidget(copy_button)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)
        
        # Generate and display QR code
        self.generate_qr_code()
        
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
            }
            QPushButton {
                padding: 8px;
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 4px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
                margin: 5px;
            }
            QLabel {
                margin: 5px;
            }
        """)
    
    def generate_qr_code(self):
        qr_pixmap = QRGenerator.generate_styled_qr_pixmap(
            self.share_data,
            size=200,
            fill_color="#4a90e2",
            back_color="white"
        )
        if qr_pixmap:
            self.qr_label.setPixmap(qr_pixmap)
    
    def copy_link(self):
        clipboard = QClipboard()
        clipboard.setText(self.share_data)