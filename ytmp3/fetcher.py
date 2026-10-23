from PyQt6.QtCore import QThread, pyqtSignal
import yt_dlp

from . import deezer
from .models import Track


class FetchThread(QThread):
    tracks_found = pyqtSignal(list)
    error = pyqtSignal(str)
    log = pyqtSignal(str)
    not_found = pyqtSignal(list)

    def __init__(self, urls: list[str], parent=None):
        super().__init__(parent)
        self.urls = urls

    def run(self):
        all_tracks: list[Track] = []
        missing: list[str] = []
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
                    if deezer.is_deezer_url(url):
                        self._fetch_deezer(ydl, url, all_tracks, missing)
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
        if missing:
            self.not_found.emit(missing)

    def _fetch_deezer(self, ydl, url: str, all_tracks: list[Track], missing: list[str]):
        try:
            playlist_title, deezer_tracks = deezer.fetch_playlist(url)
        except Exception as exc:
            self.log.emit(f"Erro ao processar {url}: {exc}")
            return

        origin = f"Deezer: {playlist_title}"
        total = len(deezer_tracks)
        for i, dt in enumerate(deezer_tracks, start=1):
            self.log.emit(f"Buscando no YouTube ({i}/{total}): {dt.display_name}")
            try:
                result = ydl.extract_info(f"ytsearch1:{dt.display_name}", download=False)
            except Exception:
                result = None
            entries = [e for e in (result or {}).get("entries") or [] if e]
            if not entries:
                missing.append(f"{dt.display_name} ({playlist_title})")
                continue
            entry = entries[0]
            track_url = (
                entry.get("webpage_url")
                or entry.get("url")
                or f"https://www.youtube.com/watch?v={entry.get('id')}"
            )
            all_tracks.append(
                Track(
                    url=track_url,
                    title=dt.display_name,
                    duration=entry.get("duration") or dt.duration,
                    origin=origin,
                )
            )
