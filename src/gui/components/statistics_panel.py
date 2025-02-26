from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea
from PyQt5.QtCore import Qt
from sqlalchemy import func
from ...database.models import Media

class StatisticsPanel(QWidget):
    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.db = db
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Create a scroll area for statistics
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # Create container widget for statistics
        stats_widget = QWidget()
        self.stats_layout = QVBoxLayout(stats_widget)
        
        # Add title
        title = QLabel("Media Statistics")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        self.stats_layout.addWidget(title)
        
        # Create labels for various statistics
        self.total_tracks_label = QLabel()
        self.most_played_label = QLabel()
        self.favorite_tracks_label = QLabel()
        self.total_play_time_label = QLabel()
        self.recent_plays_label = QLabel()
        
        # Add labels to layout
        self.stats_layout.addWidget(self.total_tracks_label)
        self.stats_layout.addWidget(self.most_played_label)
        self.stats_layout.addWidget(self.favorite_tracks_label)
        self.stats_layout.addWidget(self.total_play_time_label)
        self.stats_layout.addWidget(self.recent_plays_label)
        
        # Add stretch to push everything to the top
        self.stats_layout.addStretch()
        
        # Set the widget for the scroll area
        scroll_area.setWidget(stats_widget)
        layout.addWidget(scroll_area)
        
        # Initial update
        self.update_statistics()
        
    def format_time(self, seconds):
        if seconds is None:
            return "Never"
        minutes = int(seconds // 60)
        hours = int(minutes // 60)
        days = int(hours // 24)
        
        if days > 0:
            return f"{days} days ago"
        elif hours > 0:
            return f"{hours} hours ago"
        elif minutes > 0:
            return f"{minutes} minutes ago"
        else:
            return "Just now"
        
    def update_statistics(self):
        # Get total number of tracks
        total_tracks = self.db.query(Media).count()
        self.total_tracks_label.setText(f"Total Tracks: {total_tracks}")
        
        # Get most played tracks
        most_played = self.db.query(Media).order_by(Media.play_count.desc()).limit(3).all()
        most_played_text = "Most Played Tracks:\n"
        for track in most_played:
            most_played_text += f"  • {track.title or track.file_path} ({track.play_count} plays)\n"
        self.most_played_label.setText(most_played_text)
        
        # Get favorite tracks
        favorites = self.db.query(Media).filter(Media.is_favorite == True).all()
        favorites_text = f"Favorite Tracks ({len(favorites)}):\n"
        for track in favorites:
            favorites_text += f"  • {track.title or track.file_path}\n"
        self.favorite_tracks_label.setText(favorites_text)
        
        # Get total play time
        total_play_time = self.db.query(Media).with_entities(
            func.sum(Media.total_play_time)
        ).scalar() or 0
        hours = int(total_play_time // 3600)
        minutes = int((total_play_time % 3600) // 60)
        self.total_play_time_label.setText(
            f"Total Listening Time: {hours} hours, {minutes} minutes"
        )
        
        # Get recently played tracks
        recent_plays = self.db.query(Media).filter(
            Media.last_played.isnot(None)
        ).order_by(Media.last_played.desc()).limit(3).all()
        recent_plays_text = "Recently Played:\n"
        for track in recent_plays:
            recent_plays_text += f"  • {track.title or track.file_path} ({self.format_time(track.last_played)})\n"
        self.recent_plays_label.setText(recent_plays_text)