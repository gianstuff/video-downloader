import os
from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit,
                               QGroupBox, QPushButton, QComboBox, QFileDialog, QMessageBox)
from PySide6.QtCore import QThread, QSettings
from PySide6.QtGui import QIcon

from .video_downloader import VideoDownloader
from .download_dialog import DownloadDialog

WINDOW_TITLE = "Video Downloader"
ICON_LOCATION = "images/icon.png"

class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self.app = app
        self.settings = QSettings("MyCompany", "VideoDownloader")

        self.setFixedSize(500, 140)
        self.setWindowTitle(WINDOW_TITLE)
        self.setWindowIcon(QIcon(ICON_LOCATION))

        self.setup_url_layout()
        self.setup_save_layout()
        self.setup_options_groupbox()
        self.setup_main_layout()

    def setup_url_layout(self):
        self.url_text = QLabel("Video URL: ")
        self.url_line_edit = QLineEdit()
        self.url_line_edit.setText(self.settings.value("url", "", type=str))

        self.download_button = QPushButton("Download")
        self.download_button.clicked.connect(self.download_video)

        self.url_layout = QHBoxLayout()
        self.url_layout.addWidget(self.url_text)
        self.url_layout.addWidget(self.url_line_edit)
        self.url_layout.addWidget(self.download_button)

    def setup_save_layout(self):
        self.savepath_text = QLabel("Save Path: ")
        self.savepath_line_edit = QLineEdit()
        self.savepath_line_edit.setText(self.settings.value("savepath", "", type=str))

        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self.open_directory)

        self.savepath_layout = QHBoxLayout()
        self.savepath_layout.addWidget(self.savepath_text)
        self.savepath_layout.addWidget(self.savepath_line_edit)
        self.savepath_layout.addWidget(self.browse_button)

    def setup_options_groupbox(self):
        self.quality_text = QLabel("Quality:")
        self.quality_option = QComboBox()
        self.quality_option.addItem("2160")
        self.quality_option.addItem("1440")
        self.quality_option.addItem("1080")
        self.quality_option.addItem("720")
        self.quality_option.addItem("480")
        self.quality_option.addItem("360")
        self.quality_option.addItem("240")
        self.quality_option.addItem("144")
        self.quality_option.setFixedWidth(80)
        self.quality_option.setCurrentIndex(self.settings.value("quality", 0, type=int))

        self.format_text = QLabel("Format:")
        self.format_option = QComboBox()
        self.format_option.addItem("mp4")
        self.format_option.addItem("mkv")
        self.format_option.addItem("mov")
        self.format_option.addItem("webm")
        self.format_option.setFixedWidth(80)
        self.format_option.setCurrentIndex(self.settings.value("format", 0, type=int))

        self.download_text = QLabel("Download:")
        self.download_option = QComboBox()
        self.download_option.addItem("Video + Audio")
        self.download_option.addItem("Video")
        self.download_option.addItem("Audio")
        self.download_option.setFixedWidth(120)
        self.download_option.setCurrentIndex(self.settings.value("download", 0, type=int))

        self.options_layout = QHBoxLayout()
        self.options_layout.addWidget(self.quality_text)
        self.options_layout.addWidget(self.quality_option)
        self.options_layout.addWidget(self.format_text)
        self.options_layout.addWidget(self.format_option)
        self.options_layout.addWidget(self.download_text)
        self.options_layout.addWidget(self.download_option)
        self.options_layout.addStretch()

        self.group_box = QGroupBox("Options")
        self.group_box.setLayout(self.options_layout)

    def setup_main_layout(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.addLayout(self.url_layout)
        self.main_layout.addLayout(self.savepath_layout)
        self.main_layout.addWidget(self.group_box)
        
        central_widget = QWidget()
        central_widget.setLayout(self.main_layout)

        self.setCentralWidget(central_widget)

    def closeEvent(self, event):
        super().closeEvent(event)
        self.save_settings()

    def save_settings(self):
        self.settings.setValue("url", self.url_line_edit.text())
        self.settings.setValue("savepath", self.savepath_line_edit.text())
        self.settings.setValue("quality", self.quality_option.currentIndex())
        self.settings.setValue("format", self.format_option.currentIndex())
        self.settings.setValue("download", self.download_option.currentIndex())

    def download_video(self):
        try:
            if not self.url_line_edit.text():
                self.display_warning("Please enter a video URL")
                return
            if not self.savepath_line_edit.text():
                self.display_warning("Please enter a save path")
                return
            if not os.path.exists(self.savepath_line_edit.text()):
                self.display_warning("Please enter an existing save path")
                return

            self.download_thread = QThread()
            self.download_worker = VideoDownloader(self.url_line_edit.text().strip())
            self.download_dialog = DownloadDialog(WINDOW_TITLE, QIcon(ICON_LOCATION))
            self.download_dialog.show()

            self.download_worker.set_savepath(self.savepath_line_edit.text().strip())
            self.download_worker.set_quality(self.quality_option.currentText(), self.download_option.currentText())
            self.download_worker.set_format(self.format_option.currentText())

            self.download_worker.moveToThread(self.download_thread)
            self.download_thread.started.connect(self.download_worker.run)
            self.download_thread.finished.connect(self.download_thread.deleteLater)
            self.download_worker.finished.connect(self.download_thread.quit)
            self.download_worker.finished.connect(self.download_worker.deleteLater)
            self.download_worker.finished.connect(self.download_dialog.close_dialog)
            self.download_worker.downloading.connect(self.download_dialog.update_progress)
            self.download_worker.error.connect(self.display_error)
            self.download_thread.start()

        except Exception as error_msg:
            self.display_error(error_msg)

    def open_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Save Path", None, QFileDialog.Option.ShowDirsOnly)
        if directory:
            self.savepath_line_edit.setText(directory)

    def display_error(self, msg: str):
        QMessageBox.critical(self, WINDOW_TITLE, msg, QMessageBox.Ok)

    def display_warning(self, msg: str):
        QMessageBox.warning(self, WINDOW_TITLE, msg, QMessageBox.Ok)
