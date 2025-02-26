from PyQt5.QtWidgets import QPushButton, QMenu, QAction, QMessageBox, QFileDialog
from PyQt5.QtCore import pyqtSignal
import json
import csv
import xml.etree.ElementTree as ET
from PyQt5.QtGui import QClipboard, QGuiApplication

class ShareButton(QPushButton):
    share_completed = pyqtSignal(str)  # Signal emitted when sharing is complete
    
    def __init__(self, parent=None):
        super().__init__("Share", parent)
        self.setup_ui()
        self.setup_menu()
        
    def setup_ui(self):
        """Setup the button's appearance"""
        self.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
            QPushButton:pressed {
                background-color: #2b5d8e;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        
    def setup_menu(self):
        """Setup the dropdown menu for sharing options"""
        self.menu = QMenu(self)
        
        # Export actions
        export_json = QAction("Export as JSON", self)
        export_json.triggered.connect(lambda: self.export_playlist("json"))
        
        export_csv = QAction("Export as CSV", self)
        export_csv.triggered.connect(lambda: self.export_playlist("csv"))
        
        export_xml = QAction("Export as XML", self)
        export_xml.triggered.connect(lambda: self.export_playlist("xml"))
        
        # Clipboard actions
        copy_link = QAction("Copy Playlist Link", self)
        copy_link.triggered.connect(self.copy_to_clipboard)
        
        # Add actions to menu
        self.menu.addAction(export_json)
        self.menu.addAction(export_csv)
        self.menu.addAction(export_xml)
        self.menu.addSeparator()
        self.menu.addAction(copy_link)
        
        self.setMenu(self.menu)
        
    def export_playlist(self, format_type):
        """Export the playlist in the specified format"""
        try:
            file_filter = {
                "json": "JSON Files (*.json)",
                "csv": "CSV Files (*.csv)",
                "xml": "XML Files (*.xml)"
            }[format_type]
            
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Export Playlist",
                "",
                file_filter
            )
            
            if not file_path:
                return
                
            # Get playlist data from parent widget
            if not hasattr(self.parent(), 'get_playlist_data'):
                raise AttributeError("Parent widget must implement get_playlist_data() method")
            playlist_data = self.parent().get_playlist_data()
            
            if not playlist_data or 'tracks' not in playlist_data:
                raise ValueError("Invalid playlist data format")
            
            if format_type == "json":
                with open(file_path, 'w') as f:
                    json.dump(playlist_data, f, indent=4)
            
            elif format_type == "csv":
                with open(file_path, 'w', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=["title", "artist", "album", "path"])
                    writer.writeheader()
                    for track in playlist_data['tracks']:
                        writer.writerow(track)
            
            elif format_type == "xml":
                root = ET.Element("playlist")
                for track in playlist_data['tracks']:
                    track_elem = ET.SubElement(root, "track")
                    for key, value in track.items():
                        elem = ET.SubElement(track_elem, key)
                        elem.text = str(value)
                
                tree = ET.ElementTree(root)
                tree.write(file_path, encoding='utf-8', xml_declaration=True)
            
            self.show_success_message(f"Playlist exported successfully as {format_type.upper()}")
            self.share_completed.emit(file_path)
            
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to export playlist: {str(e)}")
    
    def copy_to_clipboard(self):
        """Copy playlist link to clipboard"""
        try:
            # Get shareable link from parent widget
            if not hasattr(self.parent(), 'get_shareable_link'):
                raise AttributeError("Parent widget must implement get_shareable_link() method")
            link = self.parent().get_shareable_link()
            
            if not link:
                raise ValueError("No shareable link available")
            
            # Copy to clipboard
            clipboard = QGuiApplication.clipboard()
            clipboard.setText(link)
            
            self.show_success_message("Playlist link copied to clipboard")
            self.share_completed.emit("clipboard")
            
        except Exception as e:
            QMessageBox.critical(self, "Copy Error", f"Failed to copy link: {str(e)}")
    
    def show_success_message(self, message):
        """Show a success message with a modern look"""
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setText(message)
        msg.setWindowTitle("Success")
        msg.setStyleSheet("""
            QMessageBox {
                background-color: #f0f0f0;
            }
            QMessageBox QLabel {
                color: #333333;
                font-size: 14px;
            }
            QPushButton {
                padding: 6px 12px;
                background-color: #4a90e2;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #357abd;
            }
        """)
        msg.exec_()