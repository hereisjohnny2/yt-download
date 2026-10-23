import json
import re
import urllib.request
from dataclasses import dataclass

API_URL = "https://api.deezer.com"
_PLAYLIST_RE = re.compile(r"deezer\.com/(?:[a-z]{2}(?:-[a-z]{2})?/)?playlist/(\d+)", re.I)
_SHORT_HOSTS = ("link.deezer.com", "dzr.page.link", "deezer.page.link")
_PAGE_SIZE = 100
_TIMEOUT = 20


@dataclass
class DeezerTrack:
    title: str
    artist: str
    duration: int | None = None

    @property
    def display_name(self) -> str:
        return f"{self.artist} - {self.title}" if self.artist else self.title


def is_deezer_url(url: str) -> bool:
    lowered = url.lower()
    return "deezer.com" in lowered or any(host in lowered for host in _SHORT_HOSTS)


def _get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "yt-download"})
    with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
        data = json.load(resp)
    if isinstance(data, dict) and "error" in data:
        err = data["error"]
        message = err.get("message") if isinstance(err, dict) else str(err)
        raise ValueError(f"Deezer: {message}")
    return data


def _resolve_playlist_id(url: str) -> str:
    match = _PLAYLIST_RE.search(url)
    if match:
        return match.group(1)
    if any(host in url.lower() for host in _SHORT_HOSTS):
        # Short links redirect to the full playlist URL.
        req = urllib.request.Request(url, headers={"User-Agent": "yt-download"})
        with urllib.request.urlopen(req, timeout=_TIMEOUT) as resp:
            match = _PLAYLIST_RE.search(resp.geturl())
        if match:
            return match.group(1)
    raise ValueError(f"Link do Deezer não é uma playlist: {url}")


def fetch_playlist(url: str) -> tuple[str, list[DeezerTrack]]:
    """Return (playlist title, tracks) for a Deezer playlist URL."""
    playlist_id = _resolve_playlist_id(url)
    info = _get_json(f"{API_URL}/playlist/{playlist_id}")
    title = info.get("title") or "Playlist Deezer"

    tracks: list[DeezerTrack] = []
    index = 0
    while True:
        page = _get_json(
            f"{API_URL}/playlist/{playlist_id}/tracks?index={index}&limit={_PAGE_SIZE}"
        )
        for item in page.get("data") or []:
            name = item.get("title")
            if not name:
                continue
            artist = (item.get("artist") or {}).get("name") or ""
            tracks.append(DeezerTrack(name, artist, item.get("duration")))
        if not page.get("next"):
            break
        index += _PAGE_SIZE
    return title, tracks
