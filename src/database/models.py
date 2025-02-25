from sqlalchemy import Column, Integer, String, Float, ForeignKey, Table
from sqlalchemy.orm import relationship
from . import Base

# Association table for playlist-media relationship
playlist_media = Table('playlist_media', Base.metadata,
    Column('playlist_id', Integer, ForeignKey('playlists.id'), primary_key=True),
    Column('media_id', Integer, ForeignKey('media.id'), primary_key=True)
)

class Media(Base):
    __tablename__ = 'media'

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, unique=True, index=True)
    title = Column(String)
    artist = Column(String, nullable=True)
    album = Column(String, nullable=True)
    duration = Column(Float, nullable=True)
    media_type = Column(String)  # 'audio' or 'video'
    playlists = relationship('Playlist', secondary=playlist_media, back_populates='media_items')

class Playlist(Base):
    __tablename__ = 'playlists'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    description = Column(String, nullable=True)
    media_items = relationship('Media', secondary=playlist_media, back_populates='playlists')