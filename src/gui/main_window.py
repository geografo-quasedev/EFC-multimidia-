from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QListWidget
from PyQt5.QtCore import Qt, QSettings
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaPlaylist
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl
from .components.sidebar import Sidebar
from .components.media_grid import MediaGrid
from .components.player_controls import PlayerControls
from database import get_db, Base, engine
from database.models import Media, Playlist
from utils.metadata_extractor import MetadataExtractor

# Create database tables
Base.metadata.create_all(bind=engine)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Media Library Manager")
        self.setup_player()
        self.setup_ui()
        self.setup_connections()
        self.db = next(get_db())
        
    def handle_file_selected(self, file_path):
        # Extract metadata from the file
        metadata = MetadataExtractor.extract_metadata(file_path)
        
        # Create new media entry in database
        media = Media(
            file_path=metadata['file_path'],
            title=metadata['title'],
            artist=metadata['artist'],
            album=metadata['album'],
            duration=metadata['duration'],
            media_type=metadata['media_type']
        )
        
        # Add to database if not exists
        existing_media = self.db.query(Media).filter(Media.file_path == file_path).first()
        if not existing_media:
            self.db.add(media)
            self.db.commit()
        
        # Add the media item to the grid
        self.media_grid.add_media_item(file_path)
        
    def setup_player(self):
        # Initialize media player and playlist
        self.media_player = QMediaPlayer()
        self.video_widget = QVideoWidget()
        self.media_player.setVideoOutput(self.video_widget)
        
        # Create playlist
        self.playlist = QMediaPlaylist()
        self.media_player.setPlaylist(self.playlist)
        
        # Load last volume setting
        settings = QSettings()
        last_volume = settings.value('volume', 100, type=int)
        self.media_player.setVolume(last_volume)
        
    def setup_ui(self):
        # Set window properties
        self.setMinimumSize(1200, 800)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create main components
        self.sidebar = Sidebar()
        self.media_grid = MediaGrid()
        self.player_controls = PlayerControls()
        
        # Add components to layout
        layout.addWidget(self.sidebar)
        layout.addWidget(self.video_widget)
        layout.addWidget(self.media_grid)
        layout.addWidget(self.player_controls)
        
        # Set initial states
        self.video_widget.hide()
        self.player_controls.enable_controls(False)
        
    def setup_connections(self):
        # Connect sidebar's file selection signal to handle_file_selected
        self.sidebar.file_selected.connect(self.handle_file_selected)
        
        # Connect player control signals
        self.player_controls.play_clicked.connect(self.handle_play)
        self.player_controls.stop_clicked.connect(self.handle_stop)
        self.player_controls.prev_clicked.connect(self.handle_previous)
        self.player_controls.next_clicked.connect(self.handle_next)
        self.player_controls.volume_changed.connect(self.handle_volume_changed)
        
        # Connect media grid selection to play_media
        self.media_grid.media_selected.connect(self.play_media)
        
    def handle_file_selected(self, file_path):
        # Add the selected file to the media grid
        self.media_grid.add_media_item(file_path)
        
    def handle_play(self):
        if self.media_player.state() == QMediaPlayer.PlayingState:
            self.media_player.pause()
        else:
            self.media_player.play()
            
    def handle_stop(self):
        self.media_player.stop()
        self.player_controls.is_playing = False
        self.player_controls.play_button.setText("Play")
        
    def handle_previous(self):
        self.playlist.previous()
        
    def handle_next(self):
        self.playlist.next()
        
    def handle_volume_changed(self, value):
        self.media_player.setVolume(value)
        # Save volume setting
        settings = QSettings()
        settings.setValue('volume', value)
        
    def play_media(self, file_path):
        # Add to playlist if not already present
        url = QUrl.fromLocalFile(file_path)
        if not any(self.playlist.media(i).canonicalUrl() == url for i in range(self.playlist.mediaCount())):
            self.playlist.addMedia(QMediaContent(url))
        
        # Set current media
        for i in range(self.playlist.mediaCount()):
            if self.playlist.media(i).canonicalUrl() == url:
                self.playlist.setCurrentIndex(i)
                break
        
        # Show/hide video widget based on media type
        if file_path.lower().endswith(('.mp4', '.avi', '.mkv')):
            self.video_widget.show()
        else:
            self.video_widget.hide()
            
        # Enable controls and start playback
        self.player_controls.enable_controls(True)
        self.media_player.play()
        self.player_controls.is_playing = True
        self.player_controls.play_button.setText("Pause")