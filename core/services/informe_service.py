"""Service to register viewed videos for reporting purposes."""
from pathlib import Path
from typing import Optional

_LOG_FILE = Path(__file__).resolve().parent.parent / "informes_videos.log"


def registrar_video(video: Optional[object]) -> None:
    """Append basic info about a played video to the log file."""
    if not video:
        return
    try:
        with open(_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{video.id},{video.nombre}\n")
    except Exception:
        # Silently ignore logging errors
        pass
