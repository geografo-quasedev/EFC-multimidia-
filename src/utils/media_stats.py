class MediaStats:
    def __init__(self):
        # Dictionary to store media statistics
        # Key: file_path, Value: dict with stats
        self._stats = {}
    
    def _init_media_entry(self, file_path):
        """Initialize statistics for a new media file"""
        if file_path not in self._stats:
            self._stats[file_path] = {
                'play_count': 0,
                'is_favorite': False,
                'rating': 0,  # 0-5 stars
                'last_played': None
            }
    
    def increment_play_count(self, file_path):
        """Increment the play count for a media file"""
        self._init_media_entry(file_path)
        self._stats[file_path]['play_count'] += 1
        return self._stats[file_path]['play_count']
    
    def set_favorite(self, file_path, is_favorite):
        """Set or unset favorite status for a media file"""
        self._init_media_entry(file_path)
        self._stats[file_path]['is_favorite'] = bool(is_favorite)
        return self._stats[file_path]['is_favorite']
    
    def set_rating(self, file_path, rating):
        """Set rating (0-5 stars) for a media file"""
        if not (0 <= rating <= 5):
            raise ValueError("Rating must be between 0 and 5")
        self._init_media_entry(file_path)
        self._stats[file_path]['rating'] = rating
        return self._stats[file_path]['rating']
    
    def update_last_played(self, file_path, timestamp):
        """Update the last played timestamp for a media file"""
        self._init_media_entry(file_path)
        self._stats[file_path]['last_played'] = timestamp
    
    def get_stats(self, file_path):
        """Get all statistics for a media file"""
        self._init_media_entry(file_path)
        return self._stats[file_path].copy()
    
    def get_all_stats(self):
        """Get statistics for all media files"""
        return self._stats.copy()
    
    def get_most_played(self, limit=10):
        """Get the most played media files"""
        sorted_items = sorted(
            self._stats.items(),
            key=lambda x: x[1]['play_count'],
            reverse=True
        )
        return dict(sorted_items[:limit])
    
    def get_favorites(self):
        """Get all favorite media files"""
        return {k: v for k, v in self._stats.items() if v['is_favorite']}
    
    def get_rated(self, min_rating=1):
        """Get all media files with rating >= min_rating"""
        return {k: v for k, v in self._stats.items() if v['rating'] >= min_rating}