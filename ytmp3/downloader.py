import os

from PyQt6.QtCore import QThread, pyqtSignal
import yt_dlp

from .models import Track
from .utils import sanitize_filename


class DownloadThread(QThread):
    item_status = pyqtSignal(int, str)
    item_progress = pyqtSignal(int, int)
    overall_progress = pyqtSignal(int, int)
    item_error = pyqtSignal(int, str)
    finished_all = pyqtSignal()

    def __init__(self, tracks: list[tuple[int, Track]], dest_folder: str, parent=None):
        super().__init__(parent)
        self.tracks = tracks
        self.dest_folder = dest_folder
        self._stop = False

    def stop(self):
        self._stop = True

    def run(self):
        total = len(self.tracks)
        for done, (row, track) in enumerate(self.tracks):
            if self._stop:
                break

            self.item_status.emit(row, "Baixando...")
            filename = sanitize_filename(track.output_name)
            outtmpl = os.path.join(self.dest_folder, f"{filename}.%(ext)s")

            def hook(d, row=row):
                if d.get("status") == "downloading":
                    total_bytes = d.get("total_bytes") or d.get("estimated_total_bytes")
                    downloaded = d.get("downloaded_bytes", 0)
                    if total_bytes:
                        percent = int(downloaded * 100 / total_bytes)
                        self.item_progress.emit(row, percent)
                elif d.get("status") == "finished":
                    self.item_status.emit(row, "Convertendo...")

            opts = {
                "format": "bestaudio/best",
                "outtmpl": outtmpl,
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    }
                ],
                "quiet": True,
                "no_warnings": True,
                "noplaylist": True,
                "progress_hooks": [hook],
            }

            try:
                with yt_dlp.YoutubeDL(opts) as ydl:
                    ydl.download([track.url])
                self.item_progress.emit(row, 100)
                self.item_status.emit(row, "Concluído")
            except Exception as exc:
                self.item_error.emit(row, str(exc))
                self.item_status.emit(row, "Erro")

            self.overall_progress.emit(done + 1, total)

        self.finished_all.emit()
