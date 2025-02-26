from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QLineEdit, QListWidget, QTabWidget)
from PyQt5.QtCore import pyqtSignal
from src.database.models import Tag, Category, Media

class OrganizationPanel(QWidget):
    tag_added = pyqtSignal(str)
    category_added = pyqtSignal(str, str)
    favorite_toggled = pyqtSignal(int, bool)
    
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Tags tab
        tags_widget = QWidget()
        tags_layout = QVBoxLayout(tags_widget)
        
        # Tag input
        tag_input_layout = QHBoxLayout()
        self.tag_input = QLineEdit()
        self.tag_input.setPlaceholderText("Enter new tag...")
        add_tag_btn = QPushButton("Add Tag")
        add_tag_btn.clicked.connect(self.add_tag)
        tag_input_layout.addWidget(self.tag_input)
        tag_input_layout.addWidget(add_tag_btn)
        
        # Tag list
        self.tag_list = QListWidget()
        self.refresh_tags()
        
        tags_layout.addLayout(tag_input_layout)
        tags_layout.addWidget(self.tag_list)
        
        # Categories tab
        categories_widget = QWidget()
        categories_layout = QVBoxLayout(categories_widget)
        
        # Category input
        category_input_layout = QVBoxLayout()
        self.category_name_input = QLineEdit()
        self.category_name_input.setPlaceholderText("Enter category name...")
        self.category_desc_input = QLineEdit()
        self.category_desc_input.setPlaceholderText("Enter category description...")
        add_category_btn = QPushButton("Add Category")
        add_category_btn.clicked.connect(self.add_category)
        
        category_input_layout.addWidget(self.category_name_input)
        category_input_layout.addWidget(self.category_desc_input)
        category_input_layout.addWidget(add_category_btn)
        
        # Category list
        self.category_list = QListWidget()
        self.refresh_categories()
        
        categories_layout.addLayout(category_input_layout)
        categories_layout.addWidget(self.category_list)
        
        # Favorites tab
        favorites_widget = QWidget()
        favorites_layout = QVBoxLayout(favorites_widget)
        
        # Favorites list
        self.favorites_list = QListWidget()
        self.refresh_favorites()
        
        favorites_layout.addWidget(QLabel("Favorite Media"))
        favorites_layout.addWidget(self.favorites_list)
        
        # Add tabs
        tab_widget.addTab(tags_widget, "Tags")
        tab_widget.addTab(categories_widget, "Categories")
        tab_widget.addTab(favorites_widget, "Favorites")
        
        layout.addWidget(tab_widget)
        
    def add_tag(self):
        tag_name = self.tag_input.text().strip()
        if tag_name:
            tag = Tag(name=tag_name)
            self.db.add(tag)
            self.db.commit()
            self.tag_added.emit(tag_name)
            self.tag_input.clear()
            self.refresh_tags()
            
    def add_category(self):
        name = self.category_name_input.text().strip()
        description = self.category_desc_input.text().strip()
        if name:
            category = Category(name=name, description=description)
            self.db.add(category)
            self.db.commit()
            self.category_added.emit(name, description)
            self.category_name_input.clear()
            self.category_desc_input.clear()
            self.refresh_categories()
            
    def refresh_tags(self):
        self.tag_list.clear()
        tags = self.db.query(Tag).all()
        for tag in tags:
            self.tag_list.addItem(tag.name)
            
    def refresh_categories(self):
        self.category_list.clear()
        categories = self.db.query(Category).all()
        for category in categories:
            self.category_list.addItem(f"{category.name} - {category.description}")
            
    def refresh_favorites(self):
        self.favorites_list.clear()
        favorites = self.db.query(Media).filter(Media.is_favorite == True).all()
        for media in favorites:
            self.favorites_list.addItem(media.title or media.file_path)