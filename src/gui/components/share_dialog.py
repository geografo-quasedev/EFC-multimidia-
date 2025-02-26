from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel
from .qr_code_dialog import QRCodeDialog
import json

class ShareDialog(QDialog):
    def __init__(self, playlist_data, parent=None):
        super().__init__(parent)
        self.playlist_data = playlist_data
        self.setWindowTitle("Share Playlist")
        self.setModal(True)
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Share Playlist")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 15px;")
        layout.addWidget(title)
        
        # QR Code sharing button
        qr_button = QPushButton("Share via QR Code")
        qr_button.clicked.connect(self.show_qr_code)
        qr_button.setStyleSheet("""
            QPushButton {
                padding: 10px;
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 4px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
        """)
        layout.addWidget(qr_button)
        
        # Export button
        export_button = QPushButton("Export Playlist")
        export_button.clicked.connect(self.export_playlist)
        export_button.setStyleSheet("""
            QPushButton {
                padding: 10px;
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 4px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
        """)
        layout.addWidget(export_button)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        close_button.setStyleSheet("""
            QPushButton {
                padding: 10px;
                background-color: #666;
                color: white;
                border: none;
                border-radius: 4px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #555;
            }
        """)
        layout.addWidget(close_button)
        
        self.setMinimumWidth(300)
    
    def show_qr_code(self):
        # Convert playlist data to JSON string
        playlist_json = json.dumps(self.playlist_data)
        
        # Create and show QR code dialog
        qr_dialog = QRCodeDialog(playlist_json, parent=self)
        qr_dialog.exec_()
    
    def export_playlist(self):
        # Save playlist data to file
        with open('playlist.json', 'w') as f:
            json.dump(self.playlist_data, f, indent=4)