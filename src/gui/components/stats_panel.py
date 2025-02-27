from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from ...utils.media_stats import MediaStats
from datetime import datetime
from ...database import get_db
from ...database.models import Media

class StatsPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.media_stats = MediaStats()
        self.current_media = None
        self.db = next(get_db())
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Title
        title_label = QLabel("Media Statistics")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title_label)
        
        # Stats container
        self.stats_container = QFrame()
        self.stats_container.setFrameShape(QFrame.StyledPanel)
        self.stats_container.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        stats_layout = QVBoxLayout(self.stats_container)
        
        # Play statistics section
        play_stats_label = QLabel("Play Statistics")
        play_stats_label.setFont(QFont("Arial", 10, QFont.Bold))
        stats_layout.addWidget(play_stats_label)
        
        # Play count with icon
        play_count_layout = QHBoxLayout()
        play_count_label = QLabel("▶ Plays:")
        self.play_count_value = QLabel("0")
        play_count_layout.addWidget(play_count_label)
        play_count_layout.addWidget(self.play_count_value)
        play_count_layout.addStretch()
        stats_layout.addLayout(play_count_layout)
        
        # Last played
        last_played_layout = QHBoxLayout()
        last_played_label = QLabel("🕒 Last played:")
        self.last_played_value = QLabel("Never")
        last_played_layout.addWidget(last_played_label)
        last_played_layout.addWidget(self.last_played_value)
        last_played_layout.addStretch()
        stats_layout.addLayout(last_played_layout)
        
        # Total play time
        total_time_layout = QHBoxLayout()
        total_time_label = QLabel("⏱ Total play time:")
        self.total_time_value = QLabel("0:00:00")
        total_time_layout.addWidget(total_time_label)
        total_time_layout.addWidget(self.total_time_value)
        total_time_layout.addStretch()
        stats_layout.addLayout(total_time_layout)
        
        # Rating section
        rating_section_label = QLabel("Rating & Favorites")
        rating_section_label.setFont(QFont("Arial", 10, QFont.Bold))
        stats_layout.addWidget(rating_section_label)
        
        # Rating with stars
        rating_layout = QHBoxLayout()
        rating_label = QLabel("⭐ Rating:")
        self.rating_buttons = []
        rating_stars = QHBoxLayout()
        for i in range(5):
            star_button = QPushButton("☆")
            star_button.setFlat(True)
            star_button.setStyleSheet("""
                QPushButton {
                    color: #FFD700;
                    font-size: 16px;
                    border: none;
                    padding: 0;
                    min-width: 20px;
                }
                QPushButton:hover {
                    color: #FFA500;
                }
            """)
            star_button.clicked.connect(lambda checked, index=i: self.set_rating(index + 1))
            self.rating_buttons.append(star_button)
            rating_stars.addWidget(star_button)
        rating_layout.addWidget(rating_label)
        rating_layout.addLayout(rating_stars)
        rating_layout.addStretch()
        stats_layout.addLayout(rating_layout)
        
        # Add average rating display
        avg_rating_layout = QHBoxLayout()
        avg_rating_label = QLabel("📊 Average Rating:")
        self.avg_rating_value = QLabel("0.0")
        avg_rating_layout.addWidget(avg_rating_label)
        avg_rating_layout.addWidget(self.avg_rating_value)
        avg_rating_layout.addStretch()
        stats_layout.addLayout(avg_rating_layout)
        
        # Add favorite toggle button
        favorite_layout = QHBoxLayout()
        favorite_label = QLabel("❤️ Favorite:")
        self.favorite_button = QPushButton()
        self.favorite_button.setCheckable(True)
        self.favorite_button.setStyleSheet("""
            QPushButton {
                border: none;
                padding: 5px;
                font-size: 16px;
            }
            QPushButton:checked {
                color: red;
            }
        """)
        self.favorite_button.clicked.connect(self.toggle_favorite)
        favorite_layout.addWidget(favorite_label)
        favorite_layout.addWidget(self.favorite_button)
        favorite_layout.addStretch()
        stats_layout.addLayout(favorite_layout)
        
        # Add session statistics
        session_label = QLabel("Session Statistics")
        session_label.setFont(QFont("Arial", 10, QFont.Bold))
        stats_layout.addWidget(session_label)
        
        # Session play count
        session_plays_layout = QHBoxLayout()
        session_plays_label = QLabel("🎵 Session plays:")
        self.session_plays_value = QLabel("0")
        session_plays_layout.addWidget(session_plays_label)
        session_plays_layout.addWidget(self.session_plays_value)
        session_plays_layout.addStretch()
        stats_layout.addLayout(session_plays_layout)
        
        # Session time
        session_time_layout = QHBoxLayout()
        session_time_label = QLabel("⌛ Session time:")
        self.session_time_value = QLabel("0:00:00")
        session_time_layout.addWidget(session_time_label)
        session_time_layout.addWidget(self.session_time_value)
        session_time_layout.addStretch()
        stats_layout.addLayout(session_time_layout)
        
        layout.addWidget(self.stats_container)
        layout.addStretch()
        
        # Initialize session stats
        self.session_play_count = 0
        self.session_start_time = datetime.now()
        
        # Favorite button with improved styling
        favorite_layout = QHBoxLayout()
        self.favorite_button = QPushButton("♡ Add to Favorites")
        self.favorite_button.setCheckable(True)
        self.favorite_button.clicked.connect(self.toggle_favorite)
        self.favorite_button.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                border-radius: 20px;
                font-weight: bold;
                background-color: #f0f0f0;
            }
            QPushButton:checked {
                background-color: #e74c3c;
                color: white;
            }
        """)
        favorite_layout.addWidget(self.favorite_button)
        stats_layout.addLayout(favorite_layout)
        
        layout.addWidget(self.stats_container)
        layout.addStretch()
        
        # Set initial state
        self.enable_controls(False)
    
    def update_stats(self, file_path):
        """Update statistics display for the given media file"""
        try:
            media = self.db.query(Media).filter(Media.file_path == file_path).first()
            if media:
                self.current_media = media
                self.play_count_value.setText(str(media.play_count))
                
                # Format last played time
                if media.last_played:
                    last_played = media.last_played.strftime("%Y-%m-%d %H:%M")
                    self.last_played_value.setText(last_played)
                else:
                    self.last_played_value.setText("Never")
                
                # Format total play time
                hours = int(media.total_play_time // 3600)
                minutes = int((media.total_play_time % 3600) // 60)
                seconds = int(media.total_play_time % 60)
                self.total_time_value.setText(f"{hours}:{minutes:02d}:{seconds:02d}")
                
                # Update rating stars
                self.update_rating_display(media.rating or 0)
                
                # Update favorite button
                self.favorite_button.setChecked(media.is_favorite)
                self.favorite_button.setText("❤ Favorite" if media.is_favorite else "♡ Add to Favorites")
                
                self.enable_controls(True)
            else:
                self.enable_controls(False)
        except Exception as e:
            print(f"Error updating stats: {str(e)}")
            self.enable_controls(False)
    
    def set_rating(self, rating):
        """Set rating for current media"""
        if self.current_media:
            try:
                self.current_media.rating = rating
                self.db.commit()
                self.update_rating_display(rating)
            except Exception as e:
                print(f"Error setting rating: {str(e)}")
    
    def update_rating_display(self, rating):
        """Update the display of rating stars"""
        for i, button in enumerate(self.rating_buttons):
            button.setText("★" if i < rating else "☆")
    
    def toggle_favorite(self):
        """Toggle favorite status for current media"""
        if self.current_media:
            try:
                self.current_media.is_favorite = self.favorite_button.isChecked()
                self.db.commit()
                self.favorite_button.setText(
                    "❤ Favorite" if self.current_media.is_favorite else "♡ Add to Favorites"
                )
            except Exception as e:
                print(f"Error toggling favorite: {str(e)}")
    
    def enable_controls(self, enabled):
        """Enable or disable all controls"""
        self.favorite_button.setEnabled(enabled)
        for button in self.rating_buttons:
            button.setEnabled(enabled)
        
        # Most played section with improved styling
        most_played_frame = QFrame()
        most_played_frame.setFrameShape(QFrame.StyledPanel)
        most_played_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                padding: 10px;
                margin-top: 10px;
            }
        """)
        most_played_layout = QVBoxLayout(most_played_frame)
        
        most_played_label = QLabel("📈 Most Played Tracks")
        most_played_label.setFont(QFont("Arial", 10, QFont.Bold))
        most_played_layout.addWidget(most_played_label)
        
        self.most_played_list = QLabel()
        self.most_played_list.setWordWrap(True)
        self.most_played_list.setStyleSheet("color: #666;")
        most_played_layout.addWidget(self.most_played_list)
        
        self.layout().addWidget(most_played_frame)
        
        # Style
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
            QPushButton:checked {
                background-color: #e74c3c;
            }
        """)
        
        self.current_media = None
    
    def update_stats(self, file_path):
        """Update statistics display for the current media"""
        self.current_media = file_path
        if not file_path:
            self.stats_container.hide()
            return
            
        stats = self.media_stats.get_stats(file_path)
        
        # Update play count with formatting
        play_count = stats['play_count']
        self.play_count_value.setText(f"{play_count:,}")
        
        # Update last played time
        last_played = stats['last_played']
        if last_played:
            last_played_str = datetime.fromtimestamp(last_played).strftime('%Y-%m-%d %H:%M')
            self.last_played_value.setText(last_played_str)
        else:
            self.last_played_value.setText("Never")
        
        # Update rating with colored stars
        rating = stats['rating']
        stars = "★" * rating + "☆" * (5 - rating)
        self.rating_value.setText(stars)
        
        # Update favorite button with icon
        self.favorite_button.setChecked(stats['is_favorite'])
        self.favorite_button.setText("♥ Favorite" if stats['is_favorite'] else "♡ Add to Favorites")
        
        # Update most played list
        most_played = self.media_stats.get_most_played(5)
        most_played_text = ""
        for path, stats in most_played.items():
            most_played_text += f"{path.split('/')[-1]}: {stats['play_count']} plays\n"
        self.most_played_list.setText(most_played_text)
        
        self.stats_container.show()
    
    def toggle_favorite(self):
        """Toggle favorite status for current media"""
        if self.current_media:
            is_favorite = self.favorite_button.isChecked()
            self.media_stats.set_favorite(self.current_media, is_favorite)
            self.favorite_button.setText("♥ Favorite" if is_favorite else "♡ Add to Favorites")