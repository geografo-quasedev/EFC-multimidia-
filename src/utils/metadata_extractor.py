from mutagen import File
from mutagen.mp3 import MP3
from mutagen.mp4 import MP4
from mutagen.wave import WAVE
from pathlib import Path

class MetadataExtractor:
    @staticmethod
    def extract_metadata(file_path):
        path = Path(file_path)
        file_type = path.suffix.lower()
        metadata = {
            'file_path': str(path),
            'title': path.stem,  # Default to filename without extension
            'artist': None,
            'album': None,
            'duration': None,
            'media_type': 'video' if file_type in ['.mp4', '.avi', '.mkv'] else 'audio'
        }

        try:
            media_file = File(file_path)
            if media_file is None:
                return metadata

            if isinstance(media_file, MP3):
                metadata.update(MetadataExtractor._extract_mp3_metadata(media_file))
            elif isinstance(media_file, MP4):
                metadata.update(MetadataExtractor._extract_mp4_metadata(media_file))
            elif isinstance(media_file, WAVE):
                metadata.update(MetadataExtractor._extract_wave_metadata(media_file))

        except Exception as e:
            print(f"Error extracting metadata from {file_path}: {str(e)}")

        return metadata

    @staticmethod
    def _extract_mp3_metadata(media_file):
        metadata = {}
        if 'TIT2' in media_file:
            metadata['title'] = str(media_file['TIT2'])
        if 'TPE1' in media_file:
            metadata['artist'] = str(media_file['TPE1'])
        if 'TALB' in media_file:
            metadata['album'] = str(media_file['TALB'])
        if media_file.info.length:
            metadata['duration'] = float(media_file.info.length)
        return metadata

    @staticmethod
    def _extract_mp4_metadata(media_file):
        metadata = {}
        if '©nam' in media_file:
            metadata['title'] = str(media_file['©nam'][0])
        if '©ART' in media_file:
            metadata['artist'] = str(media_file['©ART'][0])
        if '©alb' in media_file:
            metadata['album'] = str(media_file['©alb'][0])
        if media_file.info.length:
            metadata['duration'] = float(media_file.info.length)
        return metadata

    @staticmethod
    def _extract_wave_metadata(media_file):
        metadata = {}
        if media_file.info.length:
            metadata['duration'] = float(media_file.info.length)
        return metadata