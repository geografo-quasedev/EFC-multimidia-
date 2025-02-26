from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QComboBox, QLineEdit, QMessageBox
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
import qrcode
import json
import os
import uuid
from datetime import datetime, timedelta

class ShareManager:
    _shared_playlists = {}
    
    @staticmethod
    def generate_share_link(playlist_items):
        """Generate a unique share link for a playlist"""
        share_id = str(uuid.uuid4())
        expiry = datetime.now() + timedelta(days=7)  # Link expires in 7 days
        
        ShareManager._shared_playlists[share_id] = {
            'playlist': playlist_items,
            'expiry': expiry
        }
        
        # In a real application, you might want to use a proper URL
        return f"medialib://share/{share_id}"
    
    @staticmethod
    def get_shared_playlist(share_id):
        """Retrieve a shared playlist by its ID"""
        if share_id not in ShareManager._shared_playlists:
            return None
            
        share_data = ShareManager._shared_playlists[share_id]
        if datetime.now() > share_data['expiry']:
            del ShareManager._shared_playlists[share_id]
            return None
            
        return share_data['playlist']

class ShareLinkDialog(QDialog):
    def __init__(self, share_link, parent=None):
        super().__init__(parent)
        self.share_link = share_link
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("Share Link")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Link display
        link_label = QLabel("Share Link:")
        layout.addWidget(link_label)
        
        self.link_edit = QLineEdit(self.share_link)
        self.link_edit.setReadOnly(True)
        layout.addWidget(self.link_edit)
        
        # QR Code
        self.qr_label = QLabel()
        self.qr_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.qr_label)
        
        # Generate QR code
        self.generate_qr_code()
        
        # Copy button
        copy_button = QPushButton("Copy Link")
        copy_button.clicked.connect(self.copy_link)
        layout.addWidget(copy_button)
        
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
            }
            QPushButton:hover {
                background-color: #357abd;
            }
            QLineEdit {
                padding: 8px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
        """)
    
    def generate_qr_code(self):
        try:
            from .qr_generator import QRGenerator
            qr_pixmap = QRGenerator.generate_styled_qr_pixmap(self.share_link)
            if qr_pixmap:
                self.qr_label.setPixmap(qr_pixmap)
                self.qr_label.setScaledContents(True)
                self.qr_label.setFixedSize(200, 200)
        except Exception as e:
            print(f"Error generating QR code: {str(e)}")
            self.qr_label.setText("QR Code generation failed")
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(self.share_link)
            qr.make(fit=True)
            
            qr_image = qr.make_image(fill_color="black", back_color="white")
            qr_pixmap = QPixmap.fromImage(qr_image.toqimage())
            
            scaled_pixmap = qr_pixmap.scaled(
                300, 300,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            self.qr_label.setPixmap(scaled_pixmap)
            
        except Exception as e:
            self.qr_label.setText(f"Error generating QR code: {str(e)}")
    
    def copy_link(self):
        from PyQt5.QtWidgets import QApplication
        QApplication.clipboard().setText(self.share_link)
        QMessageBox.information(self, "Success", "Link copied to clipboard!")