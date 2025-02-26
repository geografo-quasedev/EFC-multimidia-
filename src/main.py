import sys
from PyQt5.QtWidgets import QApplication
from .gui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Set application info
    app.setApplicationName("Media Library Manager")
    app.setOrganizationName("MediaManager")
    
    # Create and show the main window
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()