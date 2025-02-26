from setuptools import setup, find_packages

setup(
    name="media-library-manager",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'PyQt5>=5.15.0',
        'python-vlc>=3.0.0',
        'watchdog>=2.1.0',
        'pillow>=8.0.0',
        'sqlalchemy>=1.4.0',
        'qrcode>=7.3.1',
        'librosa>=0.9.0',
        'opencv-python>=4.7.0',
        'matplotlib>=3.5.0',
        'numpy>=1.21.0'
    ],
    entry_points={
        'console_scripts': [
            'media-library-manager=src.main:main',
        ],
    },
)