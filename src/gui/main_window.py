from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QSplitter, QMessageBox, QPushButton
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent, QMediaPlaylist, QAudioProbe
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl, QSettings, Qt
import time
import numpy as np
from ..utils.media_export import ShareDialog
from ..database import get_db, Base, engine
from ..database.models import Media
from ..utils.metadata_extractor import MetadataExtractor
from .components.sidebar import Sidebar
from .components.search_panel import SearchPanel
from .components.media_grid import MediaGrid
from .components.player_controls import PlayerControls
from .components.now_playing_panel import NowPlayingPanel
from .components.visualization_panel import VisualizationPanel
from .components.organization_panel import OrganizationPanel
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                           QSplitter, QFrame)
from PyQt5.QtCore import Qt
from .components.sidebar import Sidebar
from .components.media_grid import MediaGrid
from .components.player_controls import PlayerControls
from .components.stats_panel import StatsPanel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Media Library Manager")
        # Initialize database connection
        from src.database.manager import DatabaseManager
        self.db = DatabaseManager().get_session()
        self.setup_player()
        self.setup_ui()
        self.setup_connections()
        
    def setup_player(self):
        # Initialize media player and playlist
        self.media_player = QMediaPlayer()
        self.video_widget = QVideoWidget()
        self.media_player.setVideoOutput(self.video_widget)
        
        # Setup audio probe for visualization
        self.audio_probe = QAudioProbe()
        self.audio_probe.setSource(self.media_player)
        self.audio_probe.audioBufferProbed.connect(self.process_audio_buffer)
        
        # Connect error signal
        self.media_player.error.connect(self.handle_media_error)
        
        # Create playlist
        self.playlist = QMediaPlaylist()
        self.media_player.setPlaylist(self.playlist)
        
        # Load last volume setting
        settings = QSettings()
        last_volume = settings.value('volume', 100, type=int)
        self.media_player.setVolume(last_volume)
        
        # Set initial playback mode
        self.playlist.setPlaybackMode(QMediaPlaylist.Sequential)
        
    def play_media(self, file_path):
        try:
            # Add to playlist if not already present
            url = QUrl.fromLocalFile(file_path)
            if not any(self.playlist.media(i).canonicalUrl() == url for i in range(self.playlist.mediaCount())):
                self.playlist.addMedia(QMediaContent(url))
            
            # Update visualization panel
            media_type = 'video' if file_path.lower().endswith(('.mp4', '.avi', '.mkv')) else 'audio'
            self.visualization_panel.update_visualization(file_path, media_type)
            
            # Set current media
            for i in range(self.playlist.mediaCount()):
                if self.playlist.media(i).canonicalUrl() == url:
                    self.playlist.setCurrentIndex(i)
                    break
            
            # Show/hide video widget based on media type
            if file_path.lower().endswith(('.mp4', '.avi', '.mkv')):
                self.video_widget.show()
                self.player_controls.set_current_video(file_path)
            else:
                self.video_widget.hide()
                self.player_controls.set_current_video(None)
                
            # Update now playing panel and media statistics
            self.stats_panel.update_stats(file_path)
            media = self.db.query(Media).filter(Media.file_path == file_path).first()
            if media:
                # Update play statistics
                media.play_count += 1
                media.last_played = time.time()
                self.db.commit()
                
                self.now_playing_panel.update_current_track(
                    title=media.title,
                    artist=media.artist,
                    album=media.album
                )
                
            # Enable controls and start playback
            self.player_controls.enable_controls(True)
            self.media_player.play()
            self.player_controls.is_playing = True
            self.player_controls.play_button.setText("Pause")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to play media: {str(e)}")
            self.player_controls.enable_controls(False)
            
    def process_audio_buffer(self, buffer):
        """Process audio buffer for visualization"""
        if buffer.format().channelCount() > 0:
            data = buffer.data()
            # Convert audio buffer to numpy array for visualization
            try:
                # Convert QByteArray to bytes before using frombuffer
                byte_data = bytes(data)
                audio_data = np.frombuffer(byte_data, dtype=np.int16)
                self.visualization_panel.update_spectrum(audio_data)
            except Exception as e:
                print(f"Error processing audio buffer: {str(e)}")
                return
    
    def handle_media_error(self, error):
        """Handle media player errors"""
        error_messages = {
            QMediaPlayer.NoError: "No error occurred",
            QMediaPlayer.ResourceError: "Error accessing the media resource",
            QMediaPlayer.FormatError: "Unsupported media format",
            QMediaPlayer.NetworkError: "Network error occurred",
            QMediaPlayer.AccessDeniedError: "Access to media was denied",
            QMediaPlayer.ServiceMissingError: "Required media service is missing"
        }
        error_message = error_messages.get(error, "An unknown error occurred")
        QMessageBox.critical(self, "Media Error", error_message)
        self.player_controls.enable_controls(False)
    
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        
        # Create sidebar
        self.sidebar = Sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Create content area
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        
        # Add search panel
        self.search_panel = SearchPanel()
        content_layout.addWidget(self.search_panel)
        
        # Create media display area
        display_layout = QHBoxLayout(display_widget)
        
        content_splitter.setSizes([150, 600, 200, 200])
        self.media_grid = MediaGrid()
        display_layout.addWidget(self.media_grid)
        
        # Add video widget and visualization panel
        media_view = QWidget()
        media_view_layout = QVBoxLayout(media_view)
        media_view_layout.addWidget(self.video_widget)
        
        self.visualization_panel = VisualizationPanel()
        media_view_layout.addWidget(self.visualization_panel)
        display_layout.addWidget(media_view)
        
        content_layout.addWidget(display_widget)
        
        # Add player controls
        self.player_controls = PlayerControls(self.media_player)
        content_layout.addWidget(self.player_controls)
        
        # Add now playing panel
        self.now_playing_panel = NowPlayingPanel()
        content_layout.addWidget(self.now_playing_panel)
        
        main_layout.addWidget(content_widget)
        
        # Add organization panel with database connection
        self.organization_panel = OrganizationPanel(self.db)
        main_layout.addWidget(self.organization_panel)
        
        # Add statistics panel
        self.stats_panel = StatsPanel()
        main_layout.addWidget(self.stats_panel)
        
        # Setup connections
        self.setup_connections()
        
    def setup_connections(self):
        """Setup signal/slot connections between components"""
        # Connect sidebar signals
        self.sidebar.file_selected.connect(self.play_media)
        
        # Connect media grid signals
        self.media_grid.media_selected.connect(self.play_media)
        
        # Connect search panel signals
        self.search_panel.search_changed.connect(self.media_grid.filter_media)
        
        # Connect playlist signals from sidebar
        if hasattr(self.sidebar, 'playlist_panel'):
            self.sidebar.playlist_panel.playlist_selected.connect(self.load_playlist)
            self.sidebar.playlist_panel.playlist_created.connect(self.create_playlist)
        
        # Connect organization panel signals
        self.organization_panel.media_tagged.connect(self.refresh_media_display)
        self.organization_panel.media_categorized.connect(self.refresh_media_display)
        
        # Connect media player signals
        self.media_player.mediaStatusChanged.connect(self.handle_media_status_change)
        self.media_player.stateChanged.connect(self.handle_player_state_change)
    
        # Set window properties
        self.setMinimumSize(1200, 800)
        self.setWindowTitle("Media Library Manager")
    
    def load_playlist(self, playlist_name):
        """Load a playlist and update the media grid"""
        try:
            # Get playlist from database
            playlist = self.db.query(Playlist).filter(Playlist.name == playlist_name).first()
            if playlist:
                # Clear current media grid
                self.media_grid.clear_media_items()
                
                # Add each media file to the grid
                for media in playlist.media:
                    self.media_grid.add_media_item(media.file_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load playlist: {str(e)}")
    
    def create_playlist(self, playlist_name):
        """Create a new playlist"""
        try:
            # Create new playlist in database
            playlist = Playlist(name=playlist_name)
            self.db.add(playlist)
            self.db.commit()
            
            # Update sidebar playlist panel
            if hasattr(self.sidebar, 'playlist_panel'):
                self.sidebar.playlist_panel.refresh_playlists()
                
            # Show share dialog for the new playlist
            self.show_share_dialog(playlist)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create playlist: {str(e)}")
    
    def show_share_dialog(self, playlist):
        """Show the share dialog for a playlist"""
        # TODO: Implement sharing functionality in future version
        # try:
        #     # Prepare playlist data for sharing
        #     playlist_data = {
        #         'name': playlist.name,
        #         'tracks': [{
        #             'file_path': media.file_path,
        #             'title': media.title,
        #             'artist': media.artist,
        #             'album': media.album
        #         } for media in playlist.media]
        #     }
        #     
        #     # Create and show share dialog
        #     from .components.share_dialog import ShareDialog
        #     share_dialog = ShareDialog(playlist_data, self)
        #     share_dialog.exec_()
        # except Exception as e:
        #     QMessageBox.critical(self, "Error", f"Failed to show share dialog: {str(e)}")
        pass
    
    def handle_media_status_change(self, status):
        """Handle changes in media status"""
        if status == QMediaPlayer.EndOfMedia:
            # Move to next track if available
            if self.playlist.currentIndex() < self.playlist.mediaCount() - 1:
                self.playlist.next()
            else:
                self.player_controls.stop_playback()
    
    def handle_player_state_change(self, state):
        """Handle changes in player state"""
        if state == QMediaPlayer.StoppedState:
            self.player_controls.is_playing = False
            self.player_controls.play_button.setText("Play")
        elif state == QMediaPlayer.PlayingState:
            self.player_controls.is_playing = True
            self.player_controls.play_button.setText("Pause")
    
    def refresh_media_display(self):
        """Refresh the media grid display"""
        # Store current media items
        current_items = [item['file_path'] for item in self.media_grid.media_items]
        
        # Clear and reload media items
        self.media_grid.clear_media_items()
        for file_path in current_items:
            self.media_grid.add_media_item(file_path)

    def process_audio_buffer(self, buffer):
        """Process audio buffer for visualization"""
        if buffer.format().channelCount() > 0:
            data = buffer.data()
            # Convert audio buffer to numpy array for visualization
            try:
                # Convert QByteArray to bytes before using frombuffer
                byte_data = bytes(data)
                audio_data = np.frombuffer(byte_data, dtype=np.int16)
                self.visualization_panel.update_spectrum(audio_data)
            except Exception as e:
                print(f"Error processing audio buffer: {str(e)}")
                return
    
    def handle_media_error(self, error):
        """Handle media player errors"""
        error_messages = {
            QMediaPlayer.NoError: "No error occurred",
            QMediaPlayer.ResourceError: "Error accessing the media resource",
            QMediaPlayer.FormatError: "Unsupported media format",
            QMediaPlayer.NetworkError: "Network error occurred",
            QMediaPlayer.AccessDeniedError: "Access to media was denied",
            QMediaPlayer.ServiceMissingError: "Required media service is missing"
        }
        error_message = error_messages.get(error, "An unknown error occurred")
        QMessageBox.critical(self, "Media Error", error_message)
        self.player_controls.enable_controls(False)
    
    def setup_ui(self):
        # Create central widget with dark theme
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #ffffff;
            }
        """)
        
        # Create main layout with proper spacing
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar with fixed width
        self.sidebar = Sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Create content area with gradient background
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            QWidget {
                background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
                border-radius: 20px;
                margin: 10px;
            }
        """)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
        # Add search panel with modern styling
        self.search_panel = SearchPanel()
        content_layout.addWidget(self.search_panel)
        
        # Create media display area with proper organization
        display_widget = QWidget()
        display_widget.setStyleSheet("""
            QWidget {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 15px;
            }
        """)
        display_layout = QHBoxLayout(display_widget)
        display_layout.setContentsMargins(15, 15, 15, 15)
        display_layout.setSpacing(20)
        
        # Add media grid with enhanced visuals
        self.media_grid = MediaGrid()
        display_layout.addWidget(self.media_grid, 2)
        
        # Add video widget and visualization in a container
        media_view = QWidget()
        media_view.setStyleSheet("""
            QWidget {
                background: rgba(0, 0, 0, 0.2);
                border-radius: 12px;
            }
        """)
        media_view_layout = QVBoxLayout(media_view)
        media_view_layout.setContentsMargins(10, 10, 10, 10)
        media_view_layout.setSpacing(10)
        
        # Configure video widget
        self.video_widget.setMinimumSize(320, 180)
        self.video_widget.setStyleSheet("""
            QVideoWidget {
                background: black;
                border-radius: 8px;
            }
        """)
        media_view_layout.addWidget(self.video_widget)
        
        # Add visualization panel
        self.visualization_panel = VisualizationPanel()
        media_view_layout.addWidget(self.visualization_panel)
        display_layout.addWidget(media_view, 1)
        
        content_layout.addWidget(display_widget)
        
        # Add player controls with modern design
        self.player_controls = PlayerControls(self.media_player)
        content_layout.addWidget(self.player_controls)
        
        # Add now playing panel with enhanced styling
        self.now_playing_panel = NowPlayingPanel()
        content_layout.addWidget(self.now_playing_panel)
        
        main_layout.addWidget(content_widget, 2)
        
        # Add right sidebar with organization and stats
        right_sidebar = QWidget()
        right_sidebar.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                border-radius: 20px;
                margin: 10px 10px 10px 0;
            }
        """)
        right_layout = QVBoxLayout(right_sidebar)
        right_layout.setContentsMargins(15, 15, 15, 15)
        right_layout.setSpacing(15)
        
        # Add organization panel
        self.organization_panel = OrganizationPanel(self.db)
        right_layout.addWidget(self.organization_panel)
        
        # Add statistics panel
        self.stats_panel = StatsPanel()
        right_layout.addWidget(self.stats_panel)
        
        main_layout.addWidget(right_sidebar)
        
        # Set window properties
        self.setMinimumSize(1200, 800)
        self.setWindowTitle("Media Library Manager")
        
        # Apply global stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }
        """)
        
    def setup_connections(self):
        """Setup signal/slot connections between components"""
        # Connect sidebar signals
        self.sidebar.file_selected.connect(self.play_media)
        
        # Connect media grid signals
        self.media_grid.media_selected.connect(self.play_media)
        
        # Connect search panel signals
        self.search_panel.search_changed.connect(self.media_grid.filter_media)
        
        # Connect playlist signals from sidebar
        if hasattr(self.sidebar, 'playlist_panel'):
            self.sidebar.playlist_panel.playlist_selected.connect(self.load_playlist)
            self.sidebar.playlist_panel.playlist_created.connect(self.create_playlist)
        
        # Connect organization panel signals
        self.organization_panel.media_tagged.connect(self.refresh_media_display)
        self.organization_panel.media_categorized.connect(self.refresh_media_display)
        
        # Connect media player signals
        self.media_player.mediaStatusChanged.connect(self.handle_media_status_change)
        self.media_player.stateChanged.connect(self.handle_player_state_change)
    
        # Set window properties
        self.setMinimumSize(1200, 800)
        self.setWindowTitle("Media Library Manager")
    
    def load_playlist(self, playlist_name):
        """Load a playlist and update the media grid"""
        try:
            # Get playlist from database
            playlist = self.db.query(Playlist).filter(Playlist.name == playlist_name).first()
            if playlist:
                # Clear current media grid
                self.media_grid.clear_media_items()
                
                # Add each media file to the grid
                for media in playlist.media:
                    self.media_grid.add_media_item(media.file_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load playlist: {str(e)}")
    
    def create_playlist(self, playlist_name):
        """Create a new playlist"""
        try:
            # Create new playlist in database
            playlist = Playlist(name=playlist_name)
            self.db.add(playlist)
            self.db.commit()
            
            # Update sidebar playlist panel
            if hasattr(self.sidebar, 'playlist_panel'):
                self.sidebar.playlist_panel.refresh_playlists()
                
            # Show share dialog for the new playlist
            self.show_share_dialog(playlist)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create playlist: {str(e)}")
    
    def show_share_dialog(self, playlist):
        """Show the share dialog for a playlist"""
        # TODO: Implement sharing functionality in future version
        # try:
        #     # Prepare playlist data for sharing
        #     playlist_data = {
        #         'name': playlist.name,
        #         'tracks': [{
        #             'file_path': media.file_path,
        #             'title': media.title,
        #             'artist': media.artist,
        #             'album': media.album
        #         } for media in playlist.media]
        #     }
        #     
        #     # Create and show share dialog
        #     from .components.share_dialog import ShareDialog
        #     share_dialog = ShareDialog(playlist_data, self)
        #     share_dialog.exec_()
        # except Exception as e:
        #     QMessageBox.critical(self, "Error", f"Failed to show share dialog: {str(e)}")
        pass
    
    def handle_media_status_change(self, status):
        """Handle changes in media status"""
        if status == QMediaPlayer.EndOfMedia:
            # Move to next track if available
            if self.playlist.currentIndex() < self.playlist.mediaCount() - 1:
                self.playlist.next()
            else:
                self.player_controls.stop_playback()
    
    def handle_player_state_change(self, state):
        """Handle changes in player state"""
        if state == QMediaPlayer.StoppedState:
            self.player_controls.is_playing = False
            self.player_controls.play_button.setText("Play")
        elif state == QMediaPlayer.PlayingState:
            self.player_controls.is_playing = True
            self.player_controls.play_button.setText("Pause")
    
    def refresh_media_display(self):
        """Refresh the media grid display"""
        # Store current media items
        current_items = [item['file_path'] for item in self.media_grid.media_items]
        
        # Clear and reload media items
        self.media_grid.clear_media_items()
        for file_path in current_items:
            self.media_grid.add_media_item(file_path)

    def process_audio_buffer(self, buffer):
        """Process audio buffer for visualization"""
        if buffer.format().channelCount() > 0:
            data = buffer.data()
            # Convert audio buffer to numpy array for visualization
            try:
                # Convert QByteArray to bytes before using frombuffer
                byte_data = bytes(data)
                audio_data = np.frombuffer(byte_data, dtype=np.int16)
                self.visualization_panel.update_spectrum(audio_data)
            except Exception as e:
                print(f"Error processing audio buffer: {str(e)}")
                return
    
    def handle_media_error(self, error):
        """Handle media player errors"""
        error_messages = {
            QMediaPlayer.NoError: "No error occurred",
            QMediaPlayer.ResourceError: "Error accessing the media resource",
            QMediaPlayer.FormatError: "Unsupported media format",
            QMediaPlayer.NetworkError: "Network error occurred",
            QMediaPlayer.AccessDeniedError: "Access to media was denied",
            QMediaPlayer.ServiceMissingError: "Required media service is missing"
        }
        error_message = error_messages.get(error, "An unknown error occurred")
        QMessageBox.critical(self, "Media Error", error_message)
        self.player_controls.enable_controls(False)
    
    def setup_ui(self):
        # Create central widget with dark theme
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #ffffff;
            }
        """)
        
        # Create main layout with proper spacing
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar with fixed width
        self.sidebar = Sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Create content area with gradient background
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            QWidget {
                background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
                border-radius: 20px;
                margin: 10px;
            }
        """)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
        # Add search panel with modern styling
        self.search_panel = SearchPanel()
        content_layout.addWidget(self.search_panel)
        
        # Create media display area with proper organization
        display_widget = QWidget()
        display_widget.setStyleSheet("""
            QWidget {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 15px;
            }
        """)
        display_layout = QHBoxLayout(display_widget)
        display_layout.setContentsMargins(15, 15, 15, 15)
        display_layout.setSpacing(20)
        
        # Add media grid with enhanced visuals
        self.media_grid = MediaGrid()
        display_layout.addWidget(self.media_grid, 2)
        
        # Add video widget and visualization in a container
        media_view = QWidget()
        media_view.setStyleSheet("""
            QWidget {
                background: rgba(0, 0, 0, 0.2);
                border-radius: 12px;
            }
        """)
        media_view_layout = QVBoxLayout(media_view)
        media_view_layout.setContentsMargins(10, 10, 10, 10)
        media_view_layout.setSpacing(10)
        
        # Configure video widget
        self.video_widget.setMinimumSize(320, 180)
        self.video_widget.setStyleSheet("""
            QVideoWidget {
                background: black;
                border-radius: 8px;
            }
        """)
        media_view_layout.addWidget(self.video_widget)
        
        # Add visualization panel
        self.visualization_panel = VisualizationPanel()
        media_view_layout.addWidget(self.visualization_panel)
        display_layout.addWidget(media_view, 1)
        
        content_layout.addWidget(display_widget)
        
        # Add player controls with modern design
        self.player_controls = PlayerControls(self.media_player)
        content_layout.addWidget(self.player_controls)
        
        # Add now playing panel with enhanced styling
        self.now_playing_panel = NowPlayingPanel()
        content_layout.addWidget(self.now_playing_panel)
        
        main_layout.addWidget(content_widget, 2)
        
        # Add right sidebar with organization and stats
        right_sidebar = QWidget()
        right_sidebar.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                border-radius: 20px;
                margin: 10px 10px 10px 0;
            }
        """)
        right_layout = QVBoxLayout(right_sidebar)
        right_layout.setContentsMargins(15, 15, 15, 15)
        right_layout.setSpacing(15)
        
        # Add organization panel
        self.organization_panel = OrganizationPanel(self.db)
        right_layout.addWidget(self.organization_panel)
        
        # Add statistics panel
        self.stats_panel = StatsPanel()
        right_layout.addWidget(self.stats_panel)
        
        main_layout.addWidget(right_sidebar)
        
        # Set window properties
        self.setMinimumSize(1200, 800)
        self.setWindowTitle("Media Library Manager")
        
        # Apply global stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }
        """)
        
    def setup_connections(self):
        """Setup signal/slot connections between components"""
        # Connect sidebar signals
        self.sidebar.file_selected.connect(self.play_media)
        
        # Connect media grid signals
        self.media_grid.media_selected.connect(self.play_media)
        
        # Connect search panel signals
        self.search_panel.search_changed.connect(self.media_grid.filter_media)
        
        # Connect playlist signals from sidebar
        if hasattr(self.sidebar, 'playlist_panel'):
            self.sidebar.playlist_panel.playlist_selected.connect(self.load_playlist)
            self.sidebar.playlist_panel.playlist_created.connect(self.create_playlist)
        
        # Connect organization panel signals
        self.organization_panel.media_tagged.connect(self.refresh_media_display)
        self.organization_panel.media_categorized.connect(self.refresh_media_display)
        
        # Connect media player signals
        self.media_player.mediaStatusChanged.connect(self.handle_media_status_change)
        self.media_player.stateChanged.connect(self.handle_player_state_change)
    
        # Set window properties
        self.setMinimumSize(1200, 800)
        self.setWindowTitle("Media Library Manager")
    
    def load_playlist(self, playlist_name):
        """Load a playlist and update the media grid"""
        try:
            # Get playlist from database
            playlist = self.db.query(Playlist).filter(Playlist.name == playlist_name).first()
            if playlist:
                # Clear current media grid
                self.media_grid.clear_media_items()
                
                # Add each media file to the grid
                for media in playlist.media:
                    self.media_grid.add_media_item(media.file_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load playlist: {str(e)}")
    
    def create_playlist(self, playlist_name):
        """Create a new playlist"""
        try:
            # Create new playlist in database
            playlist = Playlist(name=playlist_name)
            self.db.add(playlist)
            self.db.commit()
            
            # Update sidebar playlist panel
            if hasattr(self.sidebar, 'playlist_panel'):
                self.sidebar.playlist_panel.refresh_playlists()
                
            # Show share dialog for the new playlist
            self.show_share_dialog(playlist)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create playlist: {str(e)}")
    
    def show_share_dialog(self, playlist):
        """Show the share dialog for a playlist"""
        # TODO: Implement sharing functionality in future version
        # try:
        #     # Prepare playlist data for sharing
        #     playlist_data = {
        #         'name': playlist.name,
        #         'tracks': [{
        #             'file_path': media.file_path,
        #             'title': media.title,
        #             'artist': media.artist,
        #             'album': media.album
        #         } for media in playlist.media]
        #     }
        #     
        #     # Create and show share dialog
        #     from .components.share_dialog import ShareDialog
        #     share_dialog = ShareDialog(playlist_data, self)
        #     share_dialog.exec_()
        # except Exception as e:
        #     QMessageBox.critical(self, "Error", f"Failed to show share dialog: {str(e)}")
        pass
    
    def handle_media_status_change(self, status):
        """Handle changes in media status"""
        if status == QMediaPlayer.EndOfMedia:
            # Move to next track if available
            if self.playlist.currentIndex() < self.playlist.mediaCount() - 1:
                self.playlist.next()
            else:
                self.player_controls.stop_playback()
    
    def handle_player_state_change(self, state):
        """Handle changes in player state"""
        if state == QMediaPlayer.StoppedState:
            self.player_controls.is_playing = False
            self.player_controls.play_button.setText("Play")
        elif state == QMediaPlayer.PlayingState:
            self.player_controls.is_playing = True
            self.player_controls.play_button.setText("Pause")
    
    def refresh_media_display(self):
        """Refresh the media grid display"""
        # Store current media items
        current_items = [item['file_path'] for item in self.media_grid.media_items]
        
        # Clear and reload media items
        self.media_grid.clear_media_items()
        for file_path in current_items:
            self.media_grid.add_media_item(file_path)

    def process_audio_buffer(self, buffer):
        """Process audio buffer for visualization"""
        if buffer.format().channelCount() > 0:
            data = buffer.data()
            # Convert audio buffer to numpy array for visualization
            try:
                # Convert QByteArray to bytes before using frombuffer
                byte_data = bytes(data)
                audio_data = np.frombuffer(byte_data, dtype=np.int16)
                self.visualization_panel.update_spectrum(audio_data)
            except Exception as e:
                print(f"Error processing audio buffer: {str(e)}")
                return
    
    def handle_media_error(self, error):
        """Handle media player errors"""
        error_messages = {
            QMediaPlayer.NoError: "No error occurred",
            QMediaPlayer.ResourceError: "Error accessing the media resource",
            QMediaPlayer.FormatError: "Unsupported media format",
            QMediaPlayer.NetworkError: "Network error occurred",
            QMediaPlayer.AccessDeniedError: "Access to media was denied",
            QMediaPlayer.ServiceMissingError: "Required media service is missing"
        }
        error_message = error_messages.get(error, "An unknown error occurred")
        QMessageBox.critical(self, "Media Error", error_message)
        self.player_controls.enable_controls(False)
    
    def setup_ui(self):
        # Create central widget with dark theme
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #ffffff;
            }
        """)
        
        # Create main layout with proper spacing
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar with fixed width
        self.sidebar = Sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Create content area with gradient background
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            QWidget {
                background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
                border-radius: 20px;
                margin: 10px;
            }
        """)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
        # Add search panel with modern styling
        self.search_panel = SearchPanel()
        content_layout.addWidget(self.search_panel)
        
        # Create media display area with proper organization
        display_widget = QWidget()
        display_widget.setStyleSheet("""
            QWidget {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 15px;
            }
        """)
        display_layout = QHBoxLayout(display_widget)
        display_layout.setContentsMargins(15, 15, 15, 15)
        display_layout.setSpacing(20)
        
        # Add media grid with enhanced visuals
        self.media_grid = MediaGrid()
        display_layout.addWidget(self.media_grid, 2)
        
        # Add video widget and visualization in a container
        media_view = QWidget()
        media_view.setStyleSheet("""
            QWidget {
                background: rgba(0, 0, 0, 0.2);
                border-radius: 12px;
            }
        """)
        media_view_layout = QVBoxLayout(media_view)
        media_view_layout.setContentsMargins(10, 10, 10, 10)
        media_view_layout.setSpacing(10)
        
        # Configure video widget
        self.video_widget.setMinimumSize(320, 180)
        self.video_widget.setStyleSheet("""
            QVideoWidget {
                background: black;
                border-radius: 8px;
            }
        """)
        media_view_layout.addWidget(self.video_widget)
        
        # Add visualization panel
        self.visualization_panel = VisualizationPanel()
        media_view_layout.addWidget(self.visualization_panel)
        display_layout.addWidget(media_view, 1)
        
        content_layout.addWidget(display_widget)
        
        # Add player controls with modern design
        self.player_controls = PlayerControls(self.media_player)
        content_layout.addWidget(self.player_controls)
        
        # Add now playing panel with enhanced styling
        self.now_playing_panel = NowPlayingPanel()
        content_layout.addWidget(self.now_playing_panel)
        
        main_layout.addWidget(content_widget, 2)
        
        # Add right sidebar with organization and stats
        right_sidebar = QWidget()
        right_sidebar.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                border-radius: 20px;
                margin: 10px 10px 10px 0;
            }
        """)
        right_layout = QVBoxLayout(right_sidebar)
        right_layout.setContentsMargins(15, 15, 15, 15)
        right_layout.setSpacing(15)
        
        # Add organization panel
        self.organization_panel = OrganizationPanel(self.db)
        right_layout.addWidget(self.organization_panel)
        
        # Add statistics panel
        self.stats_panel = StatsPanel()
        right_layout.addWidget(self.stats_panel)
        
        main_layout.addWidget(right_sidebar)
        
        # Set window properties
        self.setMinimumSize(1200, 800)
        self.setWindowTitle("Media Library Manager")
        
        # Apply global stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }
        """)
        
    def setup_connections(self):
        """Setup signal/slot connections between components"""
        # Connect sidebar signals
        self.sidebar.file_selected.connect(self.play_media)
        
        # Connect media grid signals
        self.media_grid.media_selected.connect(self.play_media)
        
        # Connect search panel signals
        self.search_panel.search_changed.connect(self.media_grid.filter_media)
        
        # Connect playlist signals from sidebar
        if hasattr(self.sidebar, 'playlist_panel'):
            self.sidebar.playlist_panel.playlist_selected.connect(self.load_playlist)
            self.sidebar.playlist_panel.playlist_created.connect(self.create_playlist)
        
        # Connect organization panel signals
        self.organization_panel.media_tagged.connect(self.refresh_media_display)
        self.organization_panel.media_categorized.connect(self.refresh_media_display)
        
        # Connect media player signals
        self.media_player.mediaStatusChanged.connect(self.handle_media_status_change)
        self.media_player.stateChanged.connect(self.handle_player_state_change)
    
        # Set window properties
        self.setMinimumSize(1200, 800)
        self.setWindowTitle("Media Library Manager")
    
    def load_playlist(self, playlist_name):
        """Load a playlist and update the media grid"""
        try:
            # Get playlist from database
            playlist = self.db.query(Playlist).filter(Playlist.name == playlist_name).first()
            if playlist:
                # Clear current media grid
                self.media_grid.clear_media_items()
                
                # Add each media file to the grid
                for media in playlist.media:
                    self.media_grid.add_media_item(media.file_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load playlist: {str(e)}")
    
    def create_playlist(self, playlist_name):
        """Create a new playlist"""
        try:
            # Create new playlist in database
            playlist = Playlist(name=playlist_name)
            self.db.add(playlist)
            self.db.commit()
            
            # Update sidebar playlist panel
            if hasattr(self.sidebar, 'playlist_panel'):
                self.sidebar.playlist_panel.refresh_playlists()
                
            # Show share dialog for the new playlist
            self.show_share_dialog(playlist)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create playlist: {str(e)}")
    
    def show_share_dialog(self, playlist):
        """Show the share dialog for a playlist"""
        # TODO: Implement sharing functionality in future version
        # try:
        #     # Prepare playlist data for sharing
        #     playlist_data = {
        #         'name': playlist.name,
        #         'tracks': [{
        #             'file_path': media.file_path,
        #             'title': media.title,
        #             'artist': media.artist,
        #             'album': media.album
        #         } for media in playlist.media]
        #     }
        #     
        #     # Create and show share dialog
        #     from .components.share_dialog import ShareDialog
        #     share_dialog = ShareDialog(playlist_data, self)
        #     share_dialog.exec_()
        # except Exception as e:
        #     QMessageBox.critical(self, "Error", f"Failed to show share dialog: {str(e)}")
        pass
    
    def handle_media_status_change(self, status):
        """Handle changes in media status"""
        if status == QMediaPlayer.EndOfMedia:
            # Move to next track if available
            if self.playlist.currentIndex() < self.playlist.mediaCount() - 1:
                self.playlist.next()
            else:
                self.player_controls.stop_playback()
    
    def handle_player_state_change(self, state):
        """Handle changes in player state"""
        if state == QMediaPlayer.StoppedState:
            self.player_controls.is_playing = False
            self.player_controls.play_button.setText("Play")
        elif state == QMediaPlayer.PlayingState:
            self.player_controls.is_playing = True
            self.player_controls.play_button.setText("Pause")
    
    def refresh_media_display(self):
        """Refresh the media grid display"""
        # Store current media items
        current_items = [item['file_path'] for item in self.media_grid.media_items]
        
        # Clear and reload media items
        self.media_grid.clear_media_items()
        for file_path in current_items:
            self.media_grid.add_media_item(file_path)

    def process_audio_buffer(self, buffer):
        """Process audio buffer for visualization"""
        if buffer.format().channelCount() > 0:
            data = buffer.data()
            # Convert audio buffer to numpy array for visualization
            try:
                # Convert QByteArray to bytes before using frombuffer
                byte_data = bytes(data)
                audio_data = np.frombuffer(byte_data, dtype=np.int16)
                self.visualization_panel.update_spectrum(audio_data)
            except Exception as e:
                print(f"Error processing audio buffer: {str(e)}")
                return
    
    def handle_media_error(self, error):
        """Handle media player errors"""
        error_messages = {
            QMediaPlayer.NoError: "No error occurred",
            QMediaPlayer.ResourceError: "Error accessing the media resource",
            QMediaPlayer.FormatError: "Unsupported media format",
            QMediaPlayer.NetworkError: "Network error occurred",
            QMediaPlayer.AccessDeniedError: "Access to media was denied",
            QMediaPlayer.ServiceMissingError: "Required media service is missing"
        }
        error_message = error_messages.get(error, "An unknown error occurred")
        QMessageBox.critical(self, "Media Error", error_message)
        self.player_controls.enable_controls(False)
    
    def setup_ui(self):
        # Create central widget with dark theme
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #ffffff;
            }
        """)
        
        # Create main layout with proper spacing
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar with fixed width
        self.sidebar = Sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Create content area with gradient background
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            QWidget {
                background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
                border-radius: 20px;
                margin: 10px;
            }
        """)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
        # Add search panel with modern styling
        self.search_panel = SearchPanel()
        content_layout.addWidget(self.search_panel)
        
        # Create media display area with proper organization
        display_widget = QWidget()
        display_widget.setStyleSheet("""
            QWidget {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 15px;
            }
        """)
        display_layout = QHBoxLayout(display_widget)
        display_layout.setContentsMargins(15, 15, 15, 15)
        display_layout.setSpacing(20)
        
        # Add media grid with enhanced visuals
        self.media_grid = MediaGrid()
        display_layout.addWidget(self.media_grid, 2)
        
        # Add video widget and visualization in a container
        media_view = QWidget()
        media_view.setStyleSheet("""
            QWidget {
                background: rgba(0, 0, 0, 0.2);
                border-radius: 12px;
            }
        """)
        media_view_layout = QVBoxLayout(media_view)
        media_view_layout.setContentsMargins(10, 10, 10, 10)
        media_view_layout.setSpacing(10)
        
        # Configure video widget
        self.video_widget.setMinimumSize(320, 180)
        self.video_widget.setStyleSheet("""
            QVideoWidget {
                background: black;
                border-radius: 8px;
            }
        """)
        media_view_layout.addWidget(self.video_widget)
        
        # Add visualization panel
        self.visualization_panel = VisualizationPanel()
        media_view_layout.addWidget(self.visualization_panel)
        display_layout.addWidget(media_view, 1)
        
        content_layout.addWidget(display_widget)
        
        # Add player controls with modern design
        self.player_controls = PlayerControls(self.media_player)
        content_layout.addWidget(self.player_controls)
        
        # Add now playing panel with enhanced styling
        self.now_playing_panel = NowPlayingPanel()
        content_layout.addWidget(self.now_playing_panel)
        
        main_layout.addWidget(content_widget, 2)
        
        # Add right sidebar with organization and stats
        right_sidebar = QWidget()
        right_sidebar.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                border-radius: 20px;
                margin: 10px 10px 10px 0;
            }
        """)
        right_layout = QVBoxLayout(right_sidebar)
        right_layout.setContentsMargins(15, 15, 15, 15)
        right_layout.setSpacing(15)
        
        # Add organization panel
        self.organization_panel = OrganizationPanel(self.db)
        right_layout.addWidget(self.organization_panel)
        
        # Add statistics panel
        self.stats_panel = StatsPanel()
        right_layout.addWidget(self.stats_panel)
        
        main_layout.addWidget(right_sidebar)
        
        # Set window properties
        self.setMinimumSize(1200, 800)
        self.setWindowTitle("Media Library Manager")
        
        # Apply global stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }
        """)
        
    def setup_connections(self):
        """Setup signal/slot connections between components"""
        # Connect sidebar signals
        self.sidebar.file_selected.connect(self.play_media)
        
        # Connect media grid signals
        self.media_grid.media_selected.connect(self.play_media)
        
        # Connect search panel signals
        self.search_panel.search_changed.connect(self.media_grid.filter_media)
        
        # Connect playlist signals from sidebar
        if hasattr(self.sidebar, 'playlist_panel'):
            self.sidebar.playlist_panel.playlist_selected.connect(self.load_playlist)
            self.sidebar.playlist_panel.playlist_created.connect(self.create_playlist)
        
        # Connect organization panel signals
        self.organization_panel.media_tagged.connect(self.refresh_media_display)
        self.organization_panel.media_categorized.connect(self.refresh_media_display)
        
        # Connect media player signals
        self.media_player.mediaStatusChanged.connect(self.handle_media_status_change)
        self.media_player.stateChanged.connect(self.handle_player_state_change)
    
        # Set window properties
        self.setMinimumSize(1200, 800)
        self.setWindowTitle("Media Library Manager")
    
    def load_playlist(self, playlist_name):
        """Load a playlist and update the media grid"""
        try:
            # Get playlist from database
            playlist = self.db.query(Playlist).filter(Playlist.name == playlist_name).first()
            if playlist:
                # Clear current media grid
                self.media_grid.clear_media_items()
                
                # Add each media file to the grid
                for media in playlist.media:
                    self.media_grid.add_media_item(media.file_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load playlist: {str(e)}")
    
    def create_playlist(self, playlist_name):
        """Create a new playlist"""
        try:
            # Create new playlist in database
            playlist = Playlist(name=playlist_name)
            self.db.add(playlist)
            self.db.commit()
            
            # Update sidebar playlist panel
            if hasattr(self.sidebar, 'playlist_panel'):
                self.sidebar.playlist_panel.refresh_playlists()
                
            # Show share dialog for the new playlist
            self.show_share_dialog(playlist)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create playlist: {str(e)}")
    
    def show_share_dialog(self, playlist):
        """Show the share dialog for a playlist"""
        # TODO: Implement sharing functionality in future version
        # try:
        #     # Prepare playlist data for sharing
        #     playlist_data = {
        #         'name': playlist.name,
        #         'tracks': [{
        #             'file_path': media.file_path,
        #             'title': media.title,
        #             'artist': media.artist,
        #             'album': media.album
        #         } for media in playlist.media]
        #     }
        #     
        #     # Create and show share dialog
        #     from .components.share_dialog import ShareDialog
        #     share_dialog = ShareDialog(playlist_data, self)
        #     share_dialog.exec_()
        # except Exception as e:
        #     QMessageBox.critical(self, "Error", f"Failed to show share dialog: {str(e)}")
        pass
    
    def handle_media_status_change(self, status):
        """Handle changes in media status"""
        if status == QMediaPlayer.EndOfMedia:
            # Move to next track if available
            if self.playlist.currentIndex() < self.playlist.mediaCount() - 1:
                self.playlist.next()
            else:
                self.player_controls.stop_playback()
    
    def handle_player_state_change(self, state):
        """Handle changes in player state"""
        if state == QMediaPlayer.StoppedState:
            self.player_controls.is_playing = False
            self.player_controls.play_button.setText("Play")
        elif state == QMediaPlayer.PlayingState:
            self.player_controls.is_playing = True
            self.player_controls.play_button.setText("Pause")
    
    def refresh_media_display(self):
        """Refresh the media grid display"""
        # Store current media items
        current_items = [item['file_path'] for item in self.media_grid.media_items]
        
        # Clear and reload media items
        self.media_grid.clear_media_items()
        for file_path in current_items:
            self.media_grid.add_media_item(file_path)

    def process_audio_buffer(self, buffer):
        """Process audio buffer for visualization"""
        if buffer.format().channelCount() > 0:
            data = buffer.data()
            # Convert audio buffer to numpy array for visualization
            try:
                # Convert QByteArray to bytes before using frombuffer
                byte_data = bytes(data)
                audio_data = np.frombuffer(byte_data, dtype=np.int16)
                self.visualization_panel.update_spectrum(audio_data)
            except Exception as e:
                print(f"Error processing audio buffer: {str(e)}")
                return
    
    def handle_media_error(self, error):
        """Handle media player errors"""
        error_messages = {
            QMediaPlayer.NoError: "No error occurred",
            QMediaPlayer.ResourceError: "Error accessing the media resource",
            QMediaPlayer.FormatError: "Unsupported media format",
            QMediaPlayer.NetworkError: "Network error occurred",
            QMediaPlayer.AccessDeniedError: "Access to media was denied",
            QMediaPlayer.ServiceMissingError: "Required media service is missing"
        }
        error_message = error_messages.get(error, "An unknown error occurred")
        QMessageBox.critical(self, "Media Error", error_message)
        self.player_controls.enable_controls(False)
    
    def setup_ui(self):
        # Create central widget with dark theme
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #ffffff;
            }
        """)
        
        # Create main layout with proper spacing
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar with fixed width
        self.sidebar = Sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Create content area with gradient background
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            QWidget {
                background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
                border-radius: 20px;
                margin: 10px;
            }
        """)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
        # Add search panel with modern styling
        self.search_panel = SearchPanel()
        content_layout.addWidget(self.search_panel)
        
        # Create media display area with proper organization
        display_widget = QWidget()
        display_widget.setStyleSheet("""
            QWidget {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 15px;
            }
        """)
        display_layout = QHBoxLayout(display_widget)
        display_layout.setContentsMargins(15, 15, 15, 15)
        display_layout.setSpacing(20)
        
        # Add media grid with enhanced visuals
        self.media_grid = MediaGrid()
        display_layout.addWidget(self.media_grid, 2)
        
        # Add video widget and visualization in a container
        media_view = QWidget()
        media_view.setStyleSheet("""
            QWidget {
                background: rgba(0, 0, 0, 0.2);
                border-radius: 12px;
            }
        """)
        media_view_layout = QVBoxLayout(media_view)
        media_view_layout.setContentsMargins(10, 10, 10, 10)
        media_view_layout.setSpacing(10)
        
        # Configure video widget
        self.video_widget.setMinimumSize(320, 180)
        self.video_widget.setStyleSheet("""
            QVideoWidget {
                background: black;
                border-radius: 8px;
            }
        """)
        media_view_layout.addWidget(self.video_widget)
        
        # Add visualization panel
        self.visualization_panel = VisualizationPanel()
        media_view_layout.addWidget(self.visualization_panel)
        display_layout.addWidget(media_view, 1)
        
        content_layout.addWidget(display_widget)
        
        # Add player controls with modern design
        self.player_controls = PlayerControls(self.media_player)
        content_layout.addWidget(self.player_controls)
        
        # Add now playing panel with enhanced styling
        self.now_playing_panel = NowPlayingPanel()
        content_layout.addWidget(self.now_playing_panel)
        
        main_layout.addWidget(content_widget, 2)
        
        # Add right sidebar with organization and stats
        right_sidebar = QWidget()
        right_sidebar.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                border-radius: 20px;
                margin: 10px 10px 10px 0;
            }
        """)
        right_layout = QVBoxLayout(right_sidebar)
        right_layout.setContentsMargins(15, 15, 15, 15)
        right_layout.setSpacing(15)
        
        # Add organization panel
        self.organization_panel = OrganizationPanel(self.db)
        right_layout.addWidget(self.organization_panel)
        
        # Add statistics panel
        self.stats_panel = StatsPanel()
        right_layout.addWidget(self.stats_panel)
        
        main_layout.addWidget(right_sidebar)
        
        # Set window properties
        self.setMinimumSize(1200, 800)
        self.setWindowTitle("Media Library Manager")
        
        # Apply global stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }
        """)
        
    def setup_connections(self):
        """Setup signal/slot connections between components"""
        # Connect sidebar signals
        self.sidebar.file_selected.connect(self.play_media)
        
        # Connect media grid signals
        self.media_grid.media_selected.connect(self.play_media)
        
        # Connect search panel signals
        self.search_panel.search_changed.connect(self.media_grid.filter_media)
        
        # Connect playlist signals from sidebar
        if hasattr(self.sidebar, 'playlist_panel'):
            self.sidebar.playlist_panel.playlist_selected.connect(self.load_playlist)
            self.sidebar.playlist_panel.playlist_created.connect(self.create_playlist)
        
        # Connect organization panel signals
        self.organization_panel.media_tagged.connect(self.refresh_media_display)
        self.organization_panel.media_categorized.connect(self.refresh_media_display)
        
        # Connect media player signals
        self.media_player.mediaStatusChanged.connect(self.handle_media_status_change)
        self.media_player.stateChanged.connect(self.handle_player_state_change)
    
        # Set window properties
        self.setMinimumSize(1200, 800)
        self.setWindowTitle("Media Library Manager")
    
    def load_playlist(self, playlist_name):
        """Load a playlist and update the media grid"""
        try:
            # Get playlist from database
            playlist = self.db.query(Playlist).filter(Playlist.name == playlist_name).first()
            if playlist:
                # Clear current media grid
                self.media_grid.clear_media_items()
                
                # Add each media file to the grid
                for media in playlist.media:
                    self.media_grid.add_media_item(media.file_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load playlist: {str(e)}")
    
    def create_playlist(self, playlist_name):
        """Create a new playlist"""
        try:
            # Create new playlist in database
            playlist = Playlist(name=playlist_name)
            self.db.add(playlist)
            self.db.commit()
            
            # Update sidebar playlist panel
            if hasattr(self.sidebar, 'playlist_panel'):
                self.sidebar.playlist_panel.refresh_playlists()
                
            # Show share dialog for the new playlist
            self.show_share_dialog(playlist)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create playlist: {str(e)}")
    
    def show_share_dialog(self, playlist):
        """Show the share dialog for a playlist"""
        # TODO: Implement sharing functionality in future version
        # try:
        #     # Prepare playlist data for sharing
        #     playlist_data = {
        #         'name': playlist.name,
        #         'tracks': [{
        #             'file_path': media.file_path,
        #             'title': media.title,
        #             'artist': media.artist,
        #             'album': media.album
        #         } for media in playlist.media]
        #     }
        #     
        #     # Create and show share dialog
        #     from .components.share_dialog import ShareDialog
        #     share_dialog = ShareDialog(playlist_data, self)
        #     share_dialog.exec_()
        # except Exception as e:
        #     QMessageBox.critical(self, "Error", f"Failed to show share dialog: {str(e)}")
        pass
    
    def handle_media_status_change(self, status):
        """Handle changes in media status"""
        if status == QMediaPlayer.EndOfMedia:
            # Move to next track if available
            if self.playlist.currentIndex() < self.playlist.mediaCount() - 1:
                self.playlist.next()
            else:
                self.player_controls.stop_playback()
    
    def handle_player_state_change(self, state):
        """Handle changes in player state"""
        if state == QMediaPlayer.StoppedState:
            self.player_controls.is_playing = False
            self.player_controls.play_button.setText("Play")
        elif state == QMediaPlayer.PlayingState:
            self.player_controls.is_playing = True
            self.player_controls.play_button.setText("Pause")
    
    def refresh_media_display(self):
        """Refresh the media grid display"""
        # Store current media items
        current_items = [item['file_path'] for item in self.media_grid.media_items]
        
        # Clear and reload media items
        self.media_grid.clear_media_items()
        for file_path in current_items:
            self.media_grid.add_media_item(file_path)

    def process_audio_buffer(self, buffer):
        """Process audio buffer for visualization"""
        if buffer.format().channelCount() > 0:
            data = buffer.data()
            # Convert audio buffer to numpy array for visualization
            try:
                # Convert QByteArray to bytes before using frombuffer
                byte_data = bytes(data)
                audio_data = np.frombuffer(byte_data, dtype=np.int16)
                self.visualization_panel.update_spectrum(audio_data)
            except Exception as e:
                print(f"Error processing audio buffer: {str(e)}")
                return
    
    def handle_media_error(self, error):
        """Handle media player errors"""
        error_messages = {
            QMediaPlayer.NoError: "No error occurred",
            QMediaPlayer.ResourceError: "Error accessing the media resource",
            QMediaPlayer.FormatError: "Unsupported media format",
            QMediaPlayer.NetworkError: "Network error occurred",
            QMediaPlayer.AccessDeniedError: "Access to media was denied",
            QMediaPlayer.ServiceMissingError: "Required media service is missing"
        }
        error_message = error_messages.get(error, "An unknown error occurred")
        QMessageBox.critical(self, "Media Error", error_message)
        self.player_controls.enable_controls(False)
    
    def setup_ui(self):
        # Create central widget with dark theme
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #ffffff;
            }
        """)
        
        # Create main layout with proper spacing
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar with fixed width
        self.sidebar = Sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Create content area with gradient background
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            QWidget {
                background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
                border-radius: 20px;
                margin: 10px;
            }
        """)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
        # Add search panel with modern styling
        self.search_panel = SearchPanel()
        content_layout.addWidget(self.search_panel)
        
        # Create media display area with proper organization
        display_widget = QWidget()
        display_widget.setStyleSheet("""
            QWidget {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 15px;
            }
        """)
        display_layout = QHBoxLayout(display_widget)
        display_layout.setContentsMargins(15, 15, 15, 15)
        display_layout.setSpacing(20)
        
        # Add media grid with enhanced visuals
        self.media_grid = MediaGrid()
        display_layout.addWidget(self.media_grid, 2)
        
        # Add video widget and visualization in a container
        media_view = QWidget()
        media_view.setStyleSheet("""
            QWidget {
                background: rgba(0, 0, 0, 0.2);
                border-radius: 12px;
            }
        """)
        media_view_layout = QVBoxLayout(media_view)
        media_view_layout.setContentsMargins(10, 10, 10, 10)
        media_view_layout.setSpacing(10)
        
        # Configure video widget
        self.video_widget.setMinimumSize(320, 180)
        self.video_widget.setStyleSheet("""
            QVideoWidget {
                background: black;
                border-radius: 8px;
            }
        """)
        media_view_layout.addWidget(self.video_widget)
        
        # Add visualization panel
        self.visualization_panel = VisualizationPanel()
        media_view_layout.addWidget(self.visualization_panel)
        display_layout.addWidget(media_view, 1)
        
        content_layout.addWidget(display_widget)
        
        # Add player controls with modern design
        self.player_controls = PlayerControls(self.media_player)
        content_layout.addWidget(self.player_controls)
        
        # Add now playing panel with enhanced styling
        self.now_playing_panel = NowPlayingPanel()
        content_layout.addWidget(self.now_playing_panel)
        
        main_layout.addWidget(content_widget, 2)
        
        # Add right sidebar with organization and stats
        right_sidebar = QWidget()
        right_sidebar.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                border-radius: 20px;
                margin: 10px 10px 10px 0;
            }
        """)
        right_layout = QVBoxLayout(right_sidebar)
        right_layout.setContentsMargins(15, 15, 15, 15)
        right_layout.setSpacing(15)
        
        # Add organization panel
        self.organization_panel = OrganizationPanel(self.db)
        right_layout.addWidget(self.organization_panel)
        
        # Add statistics panel
        self.stats_panel = StatsPanel()
        right_layout.addWidget(self.stats_panel)
        
        main_layout.addWidget(right_sidebar)
        
        # Set window properties
        self.setMinimumSize(1200, 800)
        self.setWindowTitle("Media Library Manager")
        
        # Apply global stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }
        """)
        
    def setup_connections(self):
        """Setup signal/slot connections between components"""
        # Connect sidebar signals
        self.sidebar.file_selected.connect(self.play_media)
        
        # Connect media grid signals
        self.media_grid.media_selected.connect(self.play_media)
        
        # Connect search panel signals
        self.search_panel.search_changed.connect(self.media_grid.filter_media)
        
        # Connect playlist signals from sidebar
        if hasattr(self.sidebar, 'playlist_panel'):
            self.sidebar.playlist_panel.playlist_selected.connect(self.load_playlist)
            self.sidebar.playlist_panel.playlist_created.connect(self.create_playlist)
        
        # Connect organization panel signals
        self.organization_panel.media_tagged.connect(self.refresh_media_display)
        self.organization_panel.media_categorized.connect(self.refresh_media_display)
        
        # Connect media player signals
        self.media_player.mediaStatusChanged.connect(self.handle_media_status_change)
        self.media_player.stateChanged.connect(self.handle_player_state_change)
    
        # Set window properties
        self.setMinimumSize(1200, 800)
        self.setWindowTitle("Media Library Manager")
    
    def load_playlist(self, playlist_name):
        """Load a playlist and update the media grid"""
        try:
            # Get playlist from database
            playlist = self.db.query(Playlist).filter(Playlist.name == playlist_name).first()
            if playlist:
                # Clear current media grid
                self.media_grid.clear_media_items()
                
                # Add each media file to the grid
                for media in playlist.media:
                    self.media_grid.add_media_item(media.file_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load playlist: {str(e)}")
    
    def create_playlist(self, playlist_name):
        """Create a new playlist"""
        try:
            # Create new playlist in database
            playlist = Playlist(name=playlist_name)
            self.db.add(playlist)
            self.db.commit()
            
            # Update sidebar playlist panel
            if hasattr(self.sidebar, 'playlist_panel'):
                self.sidebar.playlist_panel.refresh_playlists()
                
            # Show share dialog for the new playlist
            self.show_share_dialog(playlist)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create playlist: {str(e)}")
    
    def show_share_dialog(self, playlist):
        """Show the share dialog for a playlist"""
        # TODO: Implement sharing functionality in future version
        # try:
        #     # Prepare playlist data for sharing
        #     playlist_data = {
        #         'name': playlist.name,
        #         'tracks': [{
        #             'file_path': media.file_path,
        #             'title': media.title,
        #             'artist': media.artist,
        #             'album': media.album
        #         } for media in playlist.media]
        #     }
        #     
        #     # Create and show share dialog
        #     from .components.share_dialog import ShareDialog
        #     share_dialog = ShareDialog(playlist_data, self)
        #     share_dialog.exec_()
        # except Exception as e:
        #     QMessageBox.critical(self, "Error", f"Failed to show share dialog: {str(e)}")
        pass
    
    def handle_media_status_change(self, status):
        """Handle changes in media status"""
        if status == QMediaPlayer.EndOfMedia:
            # Move to next track if available
            if self.playlist.currentIndex() < self.playlist.mediaCount() - 1:
                self.playlist.next()
            else:
                self.player_controls.stop_playback()
    
    def handle_player_state_change(self, state):
        """Handle changes in player state"""
        if state == QMediaPlayer.StoppedState:
            self.player_controls.is_playing = False
            self.player_controls.play_button.setText("Play")
        elif state == QMediaPlayer.PlayingState:
            self.player_controls.is_playing = True
            self.player_controls.play_button.setText("Pause")
    
    def refresh_media_display(self):
        """Refresh the media grid display"""
        # Store current media items
        current_items = [item['file_path'] for item in self.media_grid.media_items]
        
        # Clear and reload media items
        self.media_grid.clear_media_items()
        for file_path in current_items:
            self.media_grid.add_media_item(file_path)

    def process_audio_buffer(self, buffer):
        """Process audio buffer for visualization"""
        if buffer.format().channelCount() > 0:
            data = buffer.data()
            # Convert audio buffer to numpy array for visualization
            try:
                # Convert QByteArray to bytes before using frombuffer
                byte_data = bytes(data)
                audio_data = np.frombuffer(byte_data, dtype=np.int16)
                self.visualization_panel.update_spectrum(audio_data)
            except Exception as e:
                print(f"Error processing audio buffer: {str(e)}")
                return
    
    def handle_media_error(self, error):
        """Handle media player errors"""
        error_messages = {
            QMediaPlayer.NoError: "No error occurred",
            QMediaPlayer.ResourceError: "Error accessing the media resource",
            QMediaPlayer.FormatError: "Unsupported media format",
            QMediaPlayer.NetworkError: "Network error occurred",
            QMediaPlayer.AccessDeniedError: "Access to media was denied",
            QMediaPlayer.ServiceMissingError: "Required media service is missing"
        }
        error_message = error_messages.get(error, "An unknown error occurred")
        QMessageBox.critical(self, "Media Error", error_message)
        self.player_controls.enable_controls(False)
    
    def setup_ui(self):
        # Create central widget with dark theme
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #ffffff;
            }
        """)
        
        # Create main layout with proper spacing
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar with fixed width
        self.sidebar = Sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Create content area with gradient background
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            QWidget {
                background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
                border-radius: 20px;
                margin: 10px;
            }
        """)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
        # Add search panel with modern styling
        self.search_panel = SearchPanel()
        content_layout.addWidget(self.search_panel)
        
        # Create media display area with proper organization
        display_widget = QWidget()
        display_widget.setStyleSheet("""
            QWidget {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 15px;
            }
        """)
        display_layout = QHBoxLayout(display_widget)
        display_layout.setContentsMargins(15, 15, 15, 15)
        display_layout.setSpacing(20)
        
        # Add media grid with enhanced visuals
        self.media_grid = MediaGrid()
        display_layout.addWidget(self.media_grid, 2)
        
        # Add video widget and visualization in a container
        media_view = QWidget()
        media_view.setStyleSheet("""
            QWidget {
                background: rgba(0, 0, 0, 0.2);
                border-radius: 12px;
            }
        """)
        media_view_layout = QVBoxLayout(media_view)
        media_view_layout.setContentsMargins(10, 10, 10, 10)
        media_view_layout.setSpacing(10)
        
        # Configure video widget
        self.video_widget.setMinimumSize(320, 180)
        self.video_widget.setStyleSheet("""
            QVideoWidget {
                background: black;
                border-radius: 8px;
            }
        """)
        media_view_layout.addWidget(self.video_widget)
        
        # Add visualization panel
        self.visualization_panel = VisualizationPanel()
        media_view_layout.addWidget(self.visualization_panel)
        display_layout.addWidget(media_view, 1)
        
        content_layout.addWidget(display_widget)
        
        # Add player controls with modern design
        self.player_controls = PlayerControls(self.media_player)
        content_layout.addWidget(self.player_controls)
        
        # Add now playing panel with enhanced styling
        self.now_playing_panel = NowPlayingPanel()
        content_layout.addWidget(self.now_playing_panel)
        
        main_layout.addWidget(content_widget, 2)
        
        # Add right sidebar with organization and stats
        right_sidebar = QWidget()
        right_sidebar.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                border-radius: 20px;
                margin: 10px 10px 10px 0;
            }
        """)
        right_layout = QVBoxLayout(right_sidebar)
        right_layout.setContentsMargins(15, 15, 15, 15)
        right_layout.setSpacing(15)
        
        # Add organization panel
        self.organization_panel = OrganizationPanel(self.db)
        right_layout.addWidget(self.organization_panel)
        
        # Add statistics panel
        self.stats_panel = StatsPanel()
        right_layout.addWidget(self.stats_panel)
        
        main_layout.addWidget(right_sidebar)
        
        # Set window properties
        self.setMinimumSize(1200, 800)
        self.setWindowTitle("Media Library Manager")
        
        # Apply global stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }
        """)
        
    def setup_connections(self):
        """Setup signal/slot connections between components"""
        # Connect sidebar signals
        self.sidebar.file_selected.connect(self.play_media)
        
        # Connect media grid signals
        self.media_grid.media_selected.connect(self.play_media)
        
        # Connect search panel signals
        self.search_panel.search_changed.connect(self.media_grid.filter_media)
        
        # Connect playlist signals from sidebar
        if hasattr(self.sidebar, 'playlist_panel'):
            self.sidebar.playlist_panel.playlist_selected.connect(self.load_playlist)
            self.sidebar.playlist_panel.playlist_created.connect(self.create_playlist)
        
        # Connect organization panel signals
        self.organization_panel.media_tagged.connect(self.refresh_media_display)
        self.organization_panel.media_categorized.connect(self.refresh_media_display)
        
        # Connect media player signals
        self.media_player.mediaStatusChanged.connect(self.handle_media_status_change)
        self.media_player.stateChanged.connect(self.handle_player_state_change)
    
        # Set window properties
        self.setMinimumSize(1200, 800)
        self.setWindowTitle("Media Library Manager")
    
    def load_playlist(self, playlist_name):
        """Load a playlist and update the media grid"""
        try:
            # Get playlist from database
            playlist = self.db.query(Playlist).filter(Playlist.name == playlist_name).first()
            if playlist:
                # Clear current media grid
                self.media_grid.clear_media_items()
                
                # Add each media file to the grid
                for media in playlist.media:
                    self.media_grid.add_media_item(media.file_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load playlist: {str(e)}")
    
    def create_playlist(self, playlist_name):
        """Create a new playlist"""
        try:
            # Create new playlist in database
            playlist = Playlist(name=playlist_name)
            self.db.add(playlist)
            self.db.commit()
            
            # Update sidebar playlist panel
            if hasattr(self.sidebar, 'playlist_panel'):
                self.sidebar.playlist_panel.refresh_playlists()
                
            # Show share dialog for the new playlist
            self.show_share_dialog(playlist)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create playlist: {str(e)}")
    
    def show_share_dialog(self, playlist):
        """Show the share dialog for a playlist"""
        # TODO: Implement sharing functionality in future version
        # try:
        #     # Prepare playlist data for sharing
        #     playlist_data = {
        #         'name': playlist.name,
        #         'tracks': [{
        #             'file_path': media.file_path,
        #             'title': media.title,
        #             'artist': media.artist,
        #             'album': media.album
        #         } for media in playlist.media]
        #     }
        #     
        #     # Create and show share dialog
        #     from .components.share_dialog import ShareDialog
        #     share_dialog = ShareDialog(playlist_data, self)
        #     share_dialog.exec_()
        # except Exception as e:
        #     QMessageBox.critical(self, "Error", f"Failed to show share dialog: {str(e)}")
        pass
    
    def handle_media_status_change(self, status):
        """Handle changes in media status"""
        if status == QMediaPlayer.EndOfMedia:
            # Move to next track if available
            if self.playlist.currentIndex() < self.playlist.mediaCount() - 1:
                self.playlist.next()
            else:
                self.player_controls.stop_playback()
    
    def handle_player_state_change(self, state):
        """Handle changes in player state"""
        if state == QMediaPlayer.StoppedState:
            self.player_controls.is_playing = False
            self.player_controls.play_button.setText("Play")
        elif state == QMediaPlayer.PlayingState:
            self.player_controls.is_playing = True
            self.player_controls.play_button.setText("Pause")
    
    def refresh_media_display(self):
        """Refresh the media grid display"""
        # Store current media items
        current_items = [item['file_path'] for item in self.media_grid.media_items]
        
        # Clear and reload media items
        self.media_grid.clear_media_items()
        for file_path in current_items:
            self.media_grid.add_media_item(file_path)

    def process_audio_buffer(self, buffer):
        """Process audio buffer for visualization"""
        if buffer.format().channelCount() > 0:
            data = buffer.data()
            # Convert audio buffer to numpy array for visualization
            try:
                # Convert QByteArray to bytes before using frombuffer
                byte_data = bytes(data)
                audio_data = np.frombuffer(byte_data, dtype=np.int16)
                self.visualization_panel.update_spectrum(audio_data)
            except Exception as e:
                print(f"Error processing audio buffer: {str(e)}")
                return
    
    def handle_media_error(self, error):
        """Handle media player errors"""
        error_messages = {
            QMediaPlayer.NoError: "No error occurred",
            QMediaPlayer.ResourceError: "Error accessing the media resource",
            QMediaPlayer.FormatError: "Unsupported media format",
            QMediaPlayer.NetworkError: "Network error occurred",
            QMediaPlayer.AccessDeniedError: "Access to media was denied",
            QMediaPlayer.ServiceMissingError: "Required media service is missing"
        }
        error_message = error_messages.get(error, "An unknown error occurred")
        QMessageBox.critical(self, "Media Error", error_message)
        self.player_controls.enable_controls(False)
    
    def setup_ui(self):
        # Create central widget with dark theme
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #ffffff;
            }
        """)
        
        # Create main layout with proper spacing
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar with fixed width
        self.sidebar = Sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Create content area with gradient background
        content_widget = QWidget()
        content_widget.setStyleSheet("""
            QWidget {
                background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 100%);
                border-radius: 20px;
                margin: 10px;
            }
        """)
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
        # Add search panel with modern styling
        self.search_panel = SearchPanel()
        content_layout.addWidget(self.search_panel)
        
        # Create media display area with proper organization
        display_widget = QWidget()
        display_widget.setStyleSheet("""
            QWidget {
                background: rgba(255, 255, 255, 0.05);
                border-radius: 15px;
            }
        """)
        display_layout = QHBoxLayout(display_widget)
        display_layout.setContentsMargins(15, 15, 15, 15)
        display_layout.setSpacing(20)
        
        # Add media grid with enhanced visuals
        self.media_grid = MediaGrid()
        display_layout.addWidget(self.media_grid, 2)
        
        # Add video widget and visualization in a container
        media_view = QWidget()
        media_view.setStyleSheet("""
            QWidget {
                background: rgba(0, 0, 0, 0.2);
                border-radius: 12px;
            }
        """)
        media_view_layout = QVBoxLayout(media_view)
        media_view_layout.setContentsMargins(10, 10, 10, 10)
        media_view_layout.setSpacing(10)
        
        # Configure video widget
        self.video_widget.setMinimumSize(320, 180)
        self.video_widget.setStyleSheet("""
            QVideoWidget {
                background: black;
                border-radius: 8px;
            }
        """)
        media_view_layout.addWidget(self.video_widget)
        
        # Add visualization panel
        self.visualization_panel = VisualizationPanel()
        media_view_layout.addWidget(self.visualization_panel)
        display_layout.addWidget(media_view, 1)
        
        content_layout.addWidget(display_widget)
        
        # Add player controls with modern design
        self.player_controls = PlayerControls(self.media_player)
        content_layout.addWidget(self.player_controls)
        
        # Add now playing panel with enhanced styling
        self.now_playing_panel = NowPlayingPanel()
        content_layout.addWidget(self.now_playing_panel)
        
        main_layout.addWidget(content_widget, 2)
        
        # Add right sidebar with organization and stats
        right_sidebar = QWidget()
        right_sidebar.setStyleSheet("""
            QWidget {
                background-color: #1e1e1e;
                border-radius: 20px;
                margin: 10px 10px 10px 0;
            }
        """)
        right_layout = QVBoxLayout(right_sidebar)
        right_layout.setContentsMargins(15, 15, 15, 15)
        right_layout.setSpacing(15)
        
        # Add organization panel
        self.organization_panel = OrganizationPanel(self.db)
        right_layout.addWidget(self.organization_panel)
        
        # Add statistics panel
        self.stats_panel = StatsPanel()
        right_layout.addWidget(self.stats_panel)
        
        main_layout.addWidget(right_sidebar)
        
        # Set window properties
        self.setMinimumSize(1200, 800)
        self.setWindowTitle("Media Library Manager")
        
        # Apply global stylesheet
        self.setStyleSheet("""
            QMainWindow {
                background-color: #121212;
            }
        """)
        
    def setup_connections(self):
        """Setup signal/slot connections between components"""
        # Connect sidebar signals
        self.sidebar.file_selected.connect(self.play_media)
        
        # Connect media grid signals
        self.media_grid.media_selected.connect(self.play_media)
        
        # Connect search panel signals
        self.search_panel.search_changed.connect(self.media_grid.filter_media)
        
        # Connect playlist signals from sidebar
        if hasattr(self.sidebar, 'playlist_panel'):
            self.sidebar.playlist_panel.playlist_selected.connect(self.load_playlist)
            self.sidebar.playlist_panel.playlist_created.connect(self.create_playlist)
        
        # Connect organization panel signals
        self.organization_panel.media_tagged.connect(self.refresh_media_display)
        self.organization_panel.media_categorized.connect(self.refresh_media_display)
        
        # Connect media player signals
        self.media_player.mediaStatusChanged.connect(self.handle_media_status_change)
        self.media_player.stateChanged.connect(self.handle_player_state_change)
    
        # Set window properties
        self.setMinimumSize(1200, 800)
        self.setWindowTitle("Media Library Manager")
    
    def load_playlist(self, playlist_name):
        """Load a playlist and update the media grid"""
        try:
            # Get playlist from database
            playlist = self.db.query(Playlist).filter(Playlist.name == playlist_name).first()
            if playlist:
                # Clear current media grid
                self.media_grid.clear_media_items()
                
                # Add each media file to the grid
                for media in playlist.media:
                    self.media_grid.add_media_item(media.file_path)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load playlist: {str(e)}")
    
    def create_playlist(self, playlist_name):
        """Create a new playlist"""
        try:
            # Create new playlist in database
            playlist = Playlist(name=playlist_name)
            self.db.add(playlist)
            self.db.commit()
            
            # Update sidebar playlist panel
            if hasattr(self.sidebar, 'playlist_panel'):
                self.sidebar.playlist_panel.refresh_playlists()
                
            # Show share dialog for the new playlist
            self.show_share_dialog(playlist)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to create playlist: {str(e)}")
    
    def show_share_dialog(self, playlist):
        """Show the share dialog for a playlist"""
        # TODO: Implement sharing functionality in future version
        # try:
        #     # Prepare playlist data for sharing
        #     playlist_data = {
        #         'name': playlist.name,
        #         'tracks': [{
        #             'file_path': media.file_path,
        #             'title': media.title,
        #             'artist': media.artist,
        #             'album': media.album
        #         } for media in playlist.media]
        #     }
        #     
        #     # Create and show share dialog
        #     from .components.share_dialog import ShareDialog
        #     share_dialog = ShareDialog(playlist_data, self)
        #     share_dialog.exec_()
        # except Exception as e:
        #     QMessageBox.critical(self, "Error", f"Failed to show share dialog: {str(e)}")
        pass
    
    def handle_media_status_change(self, status):
        """Handle changes in media status"""
        if status == QMediaPlayer.EndOfMedia:
            # Move to next track if available
            if self.playlist.currentIndex() < self.playlist.mediaCount() - 1:
                self.playlist.next()
            else:
                self.player_controls.stop_playback()
    
    def handle_player_state_change(self, state):
        """Handle changes in player state"""
        if state == QMediaPlayer.StoppedState:
            self.player_controls.is_playing = False
            self.player_controls.play_button.setText("Play")
        elif state == QMediaPlayer.PlayingState:
            self.player_controls.is_playing = True
            self.player_controls.play_button.setText("Pause")
        elif state == QMediaPlayer.EndOfMedia:
            # Move to next track if available
            if self.playlist.currentIndex() < self.playlist.mediaCount() - 1:
                self.playlist.next()
            else:
                self.player_controls.stop_playback()