import librosa
import librosa.display
import numpy as np
import cv2
from pathlib import Path
import matplotlib.pyplot as plt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import Qt

class MediaVisualizer:
    @staticmethod
    def generate_waveform(audio_path, width=800, height=200):
        try:
            # Load audio file
            y, sr = librosa.load(audio_path)
            
            # Create figure with specific size
            plt.figure(figsize=(width/100, height/100), dpi=100)
            plt.axis('off')
            
            # Plot waveform
            librosa.display.waveshow(y, sr=sr, alpha=0.5)
            
            # Save to a temporary buffer
            plt.savefig('temp_waveform.png', bbox_inches='tight', pad_inches=0)
            plt.close()
            
            # Load the image and convert to QPixmap
            image = cv2.imread('temp_waveform.png')
            height, width, channel = image.shape
            bytes_per_line = 3 * width
            
            # Convert BGR to RGB
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Create QImage and QPixmap
            q_img = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)
            
            # Remove temporary file
            Path('temp_waveform.png').unlink()
            
            return pixmap
            
        except Exception as e:
            print(f"Error generating waveform: {str(e)}")
            return None
    
    @staticmethod
    def generate_video_thumbnail(video_path, width=320, height=180):
        try:
            # Open video file
            cap = cv2.VideoCapture(video_path)
            
            # Get total frames
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Read frame from middle of video
            cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames // 2)
            ret, frame = cap.read()
            
            if ret:
                # Resize frame
                frame = cv2.resize(frame, (width, height))
                
                # Convert BGR to RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Create QImage and QPixmap
                height, width, channel = frame.shape
                bytes_per_line = 3 * width
                q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(q_img)
                
                return pixmap
            
        except Exception as e:
            print(f"Error generating thumbnail: {str(e)}")
            return None
        finally:
            if 'cap' in locals():
                cap.release()
    
    @staticmethod
    def generate_video_preview(video_path, position_percent, width=320, height=180):
        """Generate a preview frame from a specific position in the video"""
        try:
            cap = cv2.VideoCapture(video_path)
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Calculate frame position
            frame_pos = int(total_frames * position_percent)
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
            
            ret, frame = cap.read()
            if ret:
                # Apply image enhancement
                frame = cv2.detailEnhance(frame, sigma_s=10, sigma_r=0.15)
                
                # Adjust brightness and contrast
                alpha = 1.1  # Contrast control
                beta = 5    # Brightness control
                frame = cv2.convertScaleAbs(frame, alpha=alpha, beta=beta)
                
                # Resize frame with high-quality interpolation
                frame = cv2.resize(frame, (width, height), interpolation=cv2.INTER_LANCZOS4)
                
                # Apply image enhancement
                # Enhance contrast
                lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
                l, a, b = cv2.split(lab)
                clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
                cl = clahe.apply(l)
                enhanced = cv2.merge((cl,a,b))
                frame = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
                
                # Convert BGR to RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Create QImage and QPixmap
                height, width, channel = frame.shape
                bytes_per_line = 3 * width
                q_img = QImage(frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(q_img)
                
                return pixmap
            
        except Exception as e:
            print(f"Error generating preview: {str(e)}")
            return None
        finally:
            if 'cap' in locals():
                cap.release()
    
    @staticmethod
    def get_media_info(file_path):
        """Get technical information about the media file"""
        try:
            info = {}
            if file_path.lower().endswith(('.mp4', '.avi', '.mkv')):
                cap = cv2.VideoCapture(file_path)
                info['resolution'] = f"{int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}"
                info['fps'] = round(cap.get(cv2.CAP_PROP_FPS), 2)
                info['frame_count'] = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                duration = info['frame_count'] / info['fps']
                info['duration'] = f"{int(duration // 60)}:{int(duration % 60):02d}"
                cap.release()
            elif file_path.lower().endswith(('.mp3', '.wav')):
                y, sr = librosa.load(file_path)
                duration = librosa.get_duration(y=y, sr=sr)
                info['duration'] = f"{int(duration // 60)}:{int(duration % 60):02d}"
                info['sample_rate'] = f"{sr} Hz"
                
            return info
            
        except Exception as e:
            print(f"Error getting media info: {str(e)}")
            return None
            # Convert to LAB color space for better enhancement
            lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)
            
            # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            cl = clahe.apply(l)
            
            # Merge channels
            enhanced = cv2.merge((cl,a,b))
            
            # Convert back to BGR then RGB
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_BGR2RGB)
            
            # Create QImage and QPixmap
            height, width, channel = enhanced.shape
            bytes_per_line = 3 * width
            q_img = QImage(enhanced.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)
            
            return pixmap
            
        except Exception as e:
            print(f"Error generating preview: {str(e)}")
            return None
        finally:
            if 'cap' in locals():
                cap.release()

    @staticmethod
    def get_media_info(file_path):
        """Get technical information about the media file"""
        try:
            info = {}
            if file_path.lower().endswith(('.mp4', '.avi', '.mkv')):
                cap = cv2.VideoCapture(file_path)
                info['resolution'] = f"{int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}"
                info['fps'] = round(cap.get(cv2.CAP_PROP_FPS), 2)
                info['duration'] = round(cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS), 2)
                cap.release()
            elif file_path.lower().endswith(('.mp3', '.wav')):
                y, sr = librosa.load(file_path, sr=None)
                info['sample_rate'] = sr
                info['duration'] = round(len(y) / sr, 2)
                info['channels'] = 'Stereo' if len(y.shape) > 1 else 'Mono'
            return info
        except Exception as e:
            print(f"Error getting media info: {str(e)}")
            return None

        return {}