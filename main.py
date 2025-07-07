import sys
from PySide6.QtWidgets import QApplication
from modules.main_window import MainWindow

# Sets a custom AppUserModelID for the process to help Windows
# uniquely identify and manage the app in the taskbar
import ctypes
myappid = u"mycompany.myproduct.subproduct.version" # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

def main():
    app = QApplication(sys.argv)
    window = MainWindow(app)
    window.show()
    app.exec()

if __name__ == "__main__":
    main()
