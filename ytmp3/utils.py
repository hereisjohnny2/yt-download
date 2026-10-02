import re
import shutil

_INVALID_CHARS = r'[\\/*?:"<>|]'


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
