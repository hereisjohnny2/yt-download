from PyQt6.QtCore import QThread, pyqtSignal
import yt_dlp

from .models import Track


class FetchThread(QThread):
    tracks_found = pyqtSignal(list)
    error = pyqtSignal(str)
    log = pyqtSignal(str)

    def __init__(self, urls: list[str], parent=None):
        super().__init__(parent)
        self.urls = urls

    def run(self):
        all_tracks: list[Track] = []
        opts = {
            "quiet": True,
            "no_warnings": True,
            "extract_flat": "in_playlist",
            "skip_download": True,
        }
        try:
            with yt_dlp.YoutubeDL(opts) as ydl:
                for url in self.urls:
                    url = url.strip()
                    if not url:
                        continue
                    try:
                        info = ydl.extract_info(url, download=False)
                    except Exception as exc:
                        self.log.emit(f"Erro ao processar {url}: {exc}")
                        continue

                    if info is None:
                        continue

                    if info.get("_type") == "playlist":
                        playlist_title = info.get("title") or "Playlist"
                        for entry in info.get("entries") or []:
                            if not entry:
                                continue
                            track_url = (
                                entry.get("url")
                                or entry.get("webpage_url")
                                or f"https://www.youtube.com/watch?v={entry.get('id')}"
                            )
                            all_tracks.append(
                                Track(
                                    url=track_url,
                                    title=entry.get("title") or "Sem título",
                                    duration=entry.get("duration"),
                                    origin=playlist_title,
                                )
                            )
                    else:
                        all_tracks.append(
                            Track(
                                url=info.get("webpage_url") or url,
                                title=info.get("title") or "Sem título",
                                duration=info.get("duration"),
                                origin="Vídeo único",
                            )
                        )
        except Exception as exc:
            self.error.emit(str(exc))
            return

        self.tracks_found.emit(all_tracks)
