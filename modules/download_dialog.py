from PySide6.QtWidgets import (QVBoxLayout, QLabel, QProgressBar, QDialog)
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

class DownloadDialog(QDialog):
    def __init__(self, title: str, icon: QIcon):
        super().__init__()
        self.setFixedSize(300, 90)
        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(icon))
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)
        self.setModal(True)

        self.setup_status_layout()
        self.setup_main_layout()

    def setup_status_layout(self):
        self.status_text = QLabel("Preparing Download..")
        self.status_text.setWordWrap(True)
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)

        self.status_layout = QVBoxLayout()
        self.status_layout.addWidget(self.status_text)
        self.status_layout.addWidget(self.progress_bar)

    def setup_main_layout(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.status_layout)

        self.setLayout(self.main_layout)

    def update_progress(self, status: str, progress: float):
        self.status_text.setText(status)
        self.progress_bar.setValue(progress)

    def close_dialog(self):
        self.accept()

    def closeEvent(self, event):
        event.ignore()
