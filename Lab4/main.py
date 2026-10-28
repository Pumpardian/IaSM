from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from main_window import MainWindow
import sys


def main():
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())    

if __name__ == "__main__":
    main()