from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QLineEdit, QListWidget, QTabWidget)
from PyQt5.QtCore import pyqtSignal
from src.database.models import Media, Tag, Category

class OrganizationPanel(QWidget):
    media_tagged = pyqtSignal()
    media_categorized = pyqtSignal()
    
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Tags section
        tags_label = QLabel("Tags")
        tags_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(tags_label)
        
        self.tag_input = QLineEdit()
        self.tag_input.setPlaceholderText("Enter new tag...")
        layout.addWidget(self.tag_input)
        
        self.add_tag_button = QPushButton("Add Tag")
        self.add_tag_button.clicked.connect(self.add_tag)
        layout.addWidget(self.add_tag_button)
        
        self.tag_list = QListWidget()
        layout.addWidget(self.tag_list)
        
        # Categories section
        categories_label = QLabel("Categories")
        categories_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(categories_label)
        
        self.category_input = QLineEdit()
        self.category_input.setPlaceholderText("Enter new category...")
        layout.addWidget(self.category_input)
        
        self.add_category_button = QPushButton("Add Category")
        self.add_category_button.clicked.connect(self.add_category)
        layout.addWidget(self.add_category_button)
        
        self.category_list = QListWidget()
        layout.addWidget(self.category_list)
        
        self.setStyleSheet("""
            QWidget { 
                background-color: #1a1a1a;
                color: #ffffff;
            }
            QLabel {
                color: #4a90e2;
                font-size: 18px;
                font-weight: bold;
                margin: 16px 0;
                text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }
            QPushButton { 
                background: linear-gradient(135deg, #4a90e2 0%, #357abd 100%);
                color: white;
                border: none;
                border-radius: 20px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
                margin: 8px 0;
                transition: all 0.3s ease;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            QPushButton:hover {
                background: linear-gradient(135deg, #357abd 0%, #2c5aa0 100%);
                transform: translateY(-2px);
                box-shadow: 0 6px 12px rgba(74, 144, 226, 0.3);
            }
            QPushButton:pressed {
                transform: translateY(1px);
                box-shadow: 0 2px 4px rgba(74, 144, 226, 0.2);
            }
            QLineEdit {
                background-color: #2d2d2d;
                color: #ffffff;
                padding: 12px;
                border: 1px solid #3d3d3d;
                border-radius: 15px;
                margin: 8px 0;
                font-size: 14px;
                transition: all 0.3s ease;
            }
            QLineEdit:focus {
                border: 2px solid #4a90e2;
                background-color: #353535;
            }
            QListWidget {
                background-color: #2d2d2d;
                border: 1px solid #3d3d3d;
                border-radius: 15px;
                padding: 10px;
                margin: 8px 0;
                color: #ffffff;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 8px;
                margin: 2px 0;
            }
            QListWidget::item:hover {
                background-color: #353535;
            }
            QListWidget::item:selected {
                background: linear-gradient(135deg, #4a90e2 0%, #357abd 100%);
                color: white;
            }
        """)
        
        self.load_tags()
        self.load_categories()
    
    def load_tags(self):
        self.tag_list.clear()
        tags = self.db.query(Tag).all()
        for tag in tags:
            self.tag_list.addItem(tag.name)
    
    def load_categories(self):
        self.category_list.clear()
        categories = self.db.query(Category).all()
        for category in categories:
            self.category_list.addItem(category.name)
    
    def add_tag(self):
        tag_name = self.tag_input.text().strip()
        if tag_name:
            tag = Tag(name=tag_name)
            self.db.add(tag)
            self.db.commit()
            self.load_tags()
            self.tag_input.clear()
            self.media_tagged.emit()
    
    def add_category(self):
        category_name = self.category_input.text().strip()
        if category_name:
            category = Category(name=category_name)
            self.db.add(category)
            self.db.commit()
            self.load_categories()
            self.category_input.clear()
            self.media_categorized.emit()