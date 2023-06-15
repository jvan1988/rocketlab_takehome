import sys
from PyQt5.QtWidgets import QApplication
from communication_app import CommunicationApp

if __name__ == "__main__":
    app = QApplication(sys.argv)
    test_app = CommunicationApp()
    test_app.show()
    sys.exit(app.exec())
