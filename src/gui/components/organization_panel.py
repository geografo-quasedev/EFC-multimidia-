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
            QLineEdit {
                padding: 5px;
                border: 1px solid #dee2e6;
                border-radius: 4px;
                background-color: white;
            }
            QListWidget {
                background-color: white;
                border: 1px solid #dee2e6;
                border-radius: 4px;
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