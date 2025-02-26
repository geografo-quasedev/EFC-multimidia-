from PyQt5.QtWidgets import QLabel, QWidget
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from ...utils.media_visualizer import MediaVisualizer

class VideoPreview(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.current_video_path = None
        
    def setup_ui(self):
        self.preview_label = QLabel(self)
        self.preview_label.setMinimumSize(160, 90)  # 16:9 aspect ratio
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("""
            QLabel {
                background-color: #2c2c2c;
                border: 1px solid #444;
                border-radius: 4px;
                padding: 2px;
            }
        """)
        
        # Set widget properties
        self.setWindowFlags(Qt.ToolTip | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.hide()
        
    def update_preview(self, video_path, position_percent):
        """Update the preview frame for the given video position"""
        if video_path != self.current_video_path:
            self.current_video_path = video_path
            
        preview_frame = MediaVisualizer.generate_video_preview(
            video_path,
            position_percent,
            width=160,
            height=90
        )
        
        if preview_frame:
            self.preview_label.setPixmap(preview_frame)
            self.adjustSize()
            
    def show_at_position(self, x, y):
        """Show the preview widget at the specified coordinates"""
        # Position the widget above the progress bar
        self.move(x - self.width()//2, y - self.height() - 10)
        self.show()