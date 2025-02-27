from PyQt5.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, 
                           QDial, QPushButton, QSlider, QLabel)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QColor, QLinearGradient

class ControlDeck(QWidget):
    volume_changed = pyqtSignal(int)
    eq_changed = pyqtSignal(list)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Top row - Transport controls
        transport_layout = QHBoxLayout()
        transport_buttons = ['⏮', '⏯', '⏭', '⏹']
        
        for symbol in transport_buttons:
            btn = QPushButton(symbol)
            btn.setFixedSize(50, 50)
            transport_layout.addWidget(btn)
        
        main_layout.addLayout(transport_layout)
        
        # Middle row - Control knobs
        knobs_layout = QHBoxLayout()
        knob_labels = ['Volume', 'Bass', 'Mid', 'Treble']
        
        for label in knob_labels:
            knob_container = QVBoxLayout()
            
            knob = QDial()
            knob.setFixedSize(70, 70)
            knob.setNotchesVisible(True)
            knob.setRange(0, 100)
            knob.setValue(50)
            
            label = QLabel(label)
            label.setAlignment(Qt.AlignCenter)
            
            knob_container.addWidget(knob)
            knob_container.addWidget(label)
            knobs_layout.addLayout(knob_container)
        
        main_layout.addLayout(knobs_layout)
        
        # Bottom row - EQ sliders
        eq_layout = QHBoxLayout()
        
        for i in range(8):
            slider_container = QVBoxLayout()
            
            slider = QSlider(Qt.Vertical)
            slider.setFixedHeight(100)
            slider.setRange(-12, 12)
            slider.setValue(0)
            
            freq = ['31', '62', '125', '250', '500', '1k', '2k', '4k'][i]
            freq_label = QLabel(freq)
            freq_label.setAlignment(Qt.AlignCenter)
            
            slider_container.addWidget(slider)
            slider_container.addWidget(freq_label)
            eq_layout.addLayout(slider_container)
        
        main_layout.addLayout(eq_layout)
        
        self.setStyleSheet("""
            QWidget {
                background-color: #121212;
                color: #808080;
            }
            QPushButton {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,
                    stop:0 #2d2d2d, stop:1 #1a1a1a);
                border: 2px solid #333333;
                border-radius: 25px;
                color: #4a90e2;
                font-size: 20px;
            }
            QPushButton:hover {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,
                    stop:0 #353535, stop:1 #252525);
                border-color: #4a90e2;
            }
            QDial {
                background: qradialgradient(cx:0.5, cy:0.5, radius:0.5, fx:0.5, fy:0.5,
                    stop:0 #2d2d2d, stop:1 #1a1a1a);
                border: 2px solid #333333;
            }
            QDial:hover {
                border-color: #4a90e2;
            }
            QSlider::groove:vertical {
                background: #2d2d2d;
                width: 4px;
                border-radius: 2px;
            }
            QSlider::handle:vertical {
                background: #4a90e2;
                height: 10px;
                width: 18px;
                margin: 0 -7px;
                border-radius: 9px;
            }
            QLabel {
                color: #808080;
                font-size: 12px;
            }
        """)