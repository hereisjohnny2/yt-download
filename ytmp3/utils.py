import os
import re
import shutil
import sys

_INVALID_CHARS = r'[\\/*?:"<>|]'


def resource_path(*parts: str) -> str:
    """Resolve a bundled resource path, both in dev mode and in a PyInstaller build."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    return os.path.join(base, *parts)


def sanitize_filename(name: str) -> str:
    cleaned = re.sub(_INVALID_CHARS, "", name).strip()
    return cleaned or "faixa_sem_titulo"


def format_duration(seconds) -> str:
    if not seconds:
        return "—"
    seconds = int(seconds)
    minutes, secs = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None
