# main.py
import sys
from PySide6.QtWidgets import QApplication
from app import MainWindow

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.resize(1200, 800)
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
