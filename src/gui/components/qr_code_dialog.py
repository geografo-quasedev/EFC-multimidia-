from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import qrcode
from io import BytesIO

class QRCodeDialog(QDialog):
    def __init__(self, data, title="Share Playlist", parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setModal(True)
        self.setup_ui(data)
    
    def setup_ui(self, data):
        layout = QVBoxLayout(self)
        
        # Create QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        # Convert QR code to QPixmap
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        qr_pixmap = QPixmap()
        qr_pixmap.loadFromData(buffer.getvalue())
        
        # Add QR code to dialog
        qr_label = QLabel()
        qr_label.setPixmap(qr_pixmap)
        qr_label.setAlignment(Qt.AlignCenter)
        qr_label.setStyleSheet("""
            QLabel {
                padding: 24px;
                background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
                border: 1px solid #e9ecef;
                border-radius: 16px;
                box-shadow: 0 6px 12px rgba(0,0,0,0.08);
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }
            QLabel:hover {
                transform: translateY(-4px);
                box-shadow: 0 12px 24px rgba(0,0,0,0.12);
            }
        """)
        layout.addWidget(qr_label)
        
        # Add close button with modern styling
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        close_button.setStyleSheet("""
            QPushButton {
                padding: 14px 28px;
                background: linear-gradient(135deg, #4a90e2 0%, #357abd 100%);
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 16px;
                font-weight: bold;
                transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            }
            QPushButton:hover {
                background: linear-gradient(135deg, #357abd 0%, #2c5aa0 100%);
                transform: translateY(-2px);
                box-shadow: 0 8px 16px rgba(0,0,0,0.15);
            }
            QPushButton:pressed {
                transform: translateY(0);
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            }
        """)
        layout.addWidget(close_button)
        
        self.setMinimumSize(300, 350)