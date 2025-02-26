from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QComboBox
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
import qrcode
import json
import os

class MediaExporter:
    @staticmethod
    def export_playlist(playlist_items, format_type='json'):
        """Export playlist in various formats"""
        if format_type == 'json':
            return MediaExporter._export_as_json(playlist_items)
        elif format_type == 'm3u':
            return MediaExporter._export_as_m3u(playlist_items)
        else:
            raise ValueError(f"Unsupported format: {format_type}")
    
    @staticmethod
    def _export_as_json(playlist_items):
        """Export playlist as JSON"""
        playlist_data = [{
            'title': item.get('title', ''),
            'artist': item.get('artist', ''),
            'album': item.get('album', ''),
            'file_path': item.get('file_path', '')
        } for item in playlist_items]
        return json.dumps(playlist_data, indent=2)
    
    @staticmethod
    def _export_as_m3u(playlist_items):
        """Export playlist as M3U format"""
        m3u_content = ['#EXTM3U']
        for item in playlist_items:
            title = item.get('title', os.path.basename(item['file_path']))
            duration = item.get('duration', 0)
            m3u_content.append(f'#EXTINF:{duration},{title}')
            m3u_content.append(item['file_path'])
        return '\n'.join(m3u_content)

class ShareDialog(QDialog):
    share_requested = pyqtSignal(str, str)  # format_type, content
    
    def __init__(self, playlist_items, parent=None):
        super().__init__(parent)
        self.playlist_items = playlist_items
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("Share Playlist")
        self.setMinimumWidth(400)
        
        layout = QVBoxLayout(self)
        
        # Format selection
        self.format_combo = QComboBox()
        self.format_combo.addItems(['JSON', 'M3U'])
        layout.addWidget(QLabel("Export Format:"))
        layout.addWidget(self.format_combo)
        
        # QR Code display
        self.qr_label = QLabel()
        self.qr_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.qr_label)
        
        # Share button
        share_button = QPushButton("Generate Share Link")
        share_button.clicked.connect(self.handle_share)
        layout.addWidget(share_button)
        
        self.update_qr_code()
        
    def update_qr_code(self):
        try:
            format_type = self.format_combo.currentText().lower()
            content = MediaExporter.export_playlist(self.playlist_items, format_type)
            
            # Generate QR code
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(content)
            qr.make(fit=True)
            
            qr_image = qr.make_image(fill_color="black", back_color="white")
            qr_pixmap = QPixmap.fromImage(qr_image.toqimage())
            
            # Scale QR code to fit
            scaled_pixmap = qr_pixmap.scaled(
                300, 300,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            
            self.qr_label.setPixmap(scaled_pixmap)
            
        except Exception as e:
            self.qr_label.setText(f"Error generating QR code: {str(e)}")
    
    def handle_share(self):
        format_type = self.format_combo.currentText().lower()
        content = MediaExporter.export_playlist(self.playlist_items, format_type)
        self.share_requested.emit(format_type, content)