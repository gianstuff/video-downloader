import os
from yt_dlp import YoutubeDL
from PySide6.QtCore import QObject, Signal, Slot
from strip_ansi import strip_ansi

FFMPEG_LOCATION = "ffmpeg/bin/ffmpeg.exe"

class VideoDownloader(QObject):
    finished = Signal()
    error = Signal(str)
    downloading = Signal(str, float)

    def __init__(self, url: str):
        super().__init__()
        self.url = url
        self.video_info = {}
        self.ytdl_options = {
            "ffmpeg_location": FFMPEG_LOCATION,
            "noplaylist": True,
            "overwrites": True,
            "outtmpl": None,
            "format": None,
            "postprocessors": [{
                "key": "FFmpegVideoConvertor",
                "preferedformat": None
            }],
            "progress_hooks": [self.progress_hook]
        }

    @Slot()
    def run(self):
        try:
            self.download_video()
        except Exception as error_msg:
            self.error.emit(strip_ansi(str(error_msg)))
        finally:
            self.finished.emit()

    def download_video(self):    
        with YoutubeDL(self.ytdl_options) as ydl:
            self.video_info = ydl.extract_info(self.url, download=False)
            ydl.download(self.url)

    def progress_hook(self, dict: dict):
        if dict["status"] == "downloading":
            percent = dict.get("_percent_str", 0)
            percent = strip_ansi(percent.strip().replace('%', ''))
            self.downloading.emit(f"Downloading: {self.video_info.get("title", "Video Title")}", float(percent))

        elif dict["status"] == "finished":
            file_name = dict.get("filename", None)
            creation_time = os.path.getctime(file_name)
            os.utime(file_name, (creation_time, creation_time))

    def set_savepath(self, savepath: str):
        self.ytdl_options["outtmpl"] = f"{savepath}/%(title)s.%(ext)s"

    def set_quality(self, quality: str, format: str):
        match format:
            case "Video + Audio":
                self.ytdl_options["format"] = f"bestvideo[height<={quality}]+bestaudio"
            case "Video":
                self.ytdl_options["format"] = f"bestvideo[height<={quality}]"
            case "Audio":
                self.ytdl_options["format"] = "bestaudio"

    def set_format(self, format: str):
        self.ytdl_options["postprocessors"][0]["preferedformat"] = format
