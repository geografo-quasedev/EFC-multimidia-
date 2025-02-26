from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
import qrcode
from PIL import Image
from PIL.ImageQt import ImageQt

class QRGenerator:
    @staticmethod
    def generate_qr_pixmap(data, size=200):
        """Generate a QR code as a QPixmap"""
        try:
            # Create QR code instance
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4
            )
            
            # Add data
            qr.add_data(data)
            qr.make(fit=True)
            
            # Create PIL image
            qr_image = qr.make_image(fill_color="black", back_color="white")
            
            # Resize image if needed
            if size:
                qr_image = qr_image.resize((size, size), Image.LANCZOS)
            
            # Convert PIL image to QPixmap
            image_qt = ImageQt(qr_image)
            pixmap = QPixmap.fromImage(image_qt)
            
            return pixmap
        except Exception as e:
            print(f"Error generating QR code: {str(e)}")
            return None
    
    @staticmethod
    def generate_styled_qr_pixmap(data, size=200, fill_color="#4a90e2", back_color="white"):
        """Generate a styled QR code as a QPixmap"""
        try:
            # Create QR code instance with custom styling
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,
                box_size=10,
                border=4
            )
            
            # Add data
            qr.add_data(data)
            qr.make(fit=True)
            
            # Create PIL image with custom colors
            qr_image = qr.make_image(fill_color=fill_color, back_color=back_color)
            
            # Resize image if needed
            if size:
                qr_image = qr_image.resize((size, size), Image.LANCZOS)
            
            # Convert PIL image to QPixmap
            image_qt = ImageQt(qr_image)
            pixmap = QPixmap.fromImage(image_qt)
            
            return pixmap
        except Exception as e:
            print(f"Error generating styled QR code: {str(e)}")
            return None