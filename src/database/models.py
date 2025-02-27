from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table, Boolean, DateTime
from sqlalchemy.orm import relationship
from . import Base

# Association table for playlist-media relationship
playlist_media = Table('playlist_media', Base.metadata,
    Column('playlist_id', Integer, ForeignKey('playlists.id'), primary_key=True),
    Column('media_id', Integer, ForeignKey('media.id'), primary_key=True)
)

# Association table for media-tag relationship
media_tags = Table('media_tags', Base.metadata,
    Column('media_id', Integer, ForeignKey('media.id'), primary_key=True),
    Column('tag_id', Integer, ForeignKey('tags.id'), primary_key=True)
)

# Association table for media-category relationship
media_categories = Table('media_categories', Base.metadata,
    Column('media_id', Integer, ForeignKey('media.id'), primary_key=True),
    Column('category_id', Integer, ForeignKey('categories.id'), primary_key=True)
)

class Media(Base):
    __tablename__ = 'media'
    
    id = Column(Integer, primary_key=True)
    title = Column(String)
    file_path = Column(String, unique=True)
    media_type = Column(String)  # audio, video, image
    duration = Column(Float, nullable=True)
    created_date = Column(DateTime)
    last_played = Column(DateTime, nullable=True)
    play_count = Column(Integer, default=0)
    rating = Column(Integer, nullable=True)
    artist = Column(String, nullable=True)
    album = Column(String, nullable=True)
    is_favorite = Column(Boolean, default=False)
    total_play_time = Column(Float, default=0)  # Total time spent playing this media in seconds
    comment = Column(String, nullable=True)  # User comments on media
    
    # Relationships
    tags = relationship('Tag', secondary=media_tags, back_populates='media')
    categories = relationship('Category', secondary=media_categories, back_populates='media_items')
    playlists = relationship('Playlist', secondary=playlist_media, back_populates='media_items')

class PlaylistItem(Base):
    __tablename__ = 'playlist_items'
    
    id = Column(Integer, primary_key=True)
    playlist_id = Column(Integer, ForeignKey('playlists.id'))
    media_id = Column(Integer, ForeignKey('media.id'))
    position = Column(Integer)
    
    # Relationships
    media = relationship('Media', backref='playlist_items')
    playlist = relationship('Playlist', backref='items')

class Tag(Base):
    __tablename__ = 'tags'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    
    # Relationships
    media = relationship('Media', secondary=media_tags, back_populates='tags')

class Category(Base):
    __tablename__ = 'categories'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    
    # Relationships
    media_items = relationship('Media', secondary=media_categories, back_populates='categories')

class Playlist(Base):
    __tablename__ = 'playlists'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String, nullable=True)
    media_items = relationship('Media', secondary=playlist_media, back_populates='playlists')