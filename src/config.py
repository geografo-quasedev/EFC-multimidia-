# Application configuration settings

class Config:
    # Server configuration
    SERVER_HOST = "0.0.0.0"  # Allow connections from any IP
    SERVER_PORT = 5000       # Custom port number
    
    # Media player settings
    DEFAULT_VOLUME = 100
    SUPPORTED_FORMATS = [".mp3", ".mp4", ".wav", ".avi", ".mkv"]
    
    # Visualization settings
    SPECTRUM_UPDATE_INTERVAL = 50  # milliseconds
    WAVEFORM_RESOLUTION = 1000     # points