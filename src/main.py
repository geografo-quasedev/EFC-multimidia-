from PyQt5.QtWidgets import QApplication
from src.gui.main_window import MainWindow
from src.config import Config
import sys

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    
    # Set up server configuration
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((Config.SERVER_HOST, Config.SERVER_PORT))
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()