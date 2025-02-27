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
        # TODO: Implement QR code sharing functionality in future version
        self.setWindowTitle("Share Media")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Placeholder message
        info_label = QLabel("QR code sharing functionality will be implemented in a future version.")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)
        layout.addWidget(close_button)
        
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
            QLabel {
                margin: 15px;
                font-size: 14px;
                color: #666;
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