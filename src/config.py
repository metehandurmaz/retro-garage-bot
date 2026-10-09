import os
import shutil
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent

load_dotenv(ROOT / ".env")


def _path(value: str) -> Path:
    p = Path(value)
    return p if p.is_absolute() else ROOT / p


def _tool(name: str, override: str) -> str:
    if override:
        return override
    bundled = ROOT / "tools" / "ffmpeg" / "bin" / f"{name}.exe"
    if bundled.exists():
        return str(bundled)
    return shutil.which(name) or name


@dataclass(frozen=True)
class Config:
    pixabay_key: str
    pexels_key: str
    client_secrets: Path
    token_file: Path
    channel_id: str
    privacy_status: str
    daily_limit: int
    videos_per_run: int
    music_file: Path
    music_credit: str
    silence_db: float
    max_seconds: int
    min_seconds: int
    ffmpeg: str
    ffprobe: str
    data_dir: Path
    work_dir: Path
    out_dir: Path
    log_dir: Path


def load() -> Config:
    env = os.environ.get
    return Config(
        pixabay_key=env("PIXABAY_API_KEY", "").strip(),
        pexels_key=env("PEXELS_API_KEY", "").strip(),
        client_secrets=_path(env("YOUTUBE_CLIENT_SECRETS", "secrets/client_secret.json")),
        token_file=_path(env("YOUTUBE_TOKEN", "secrets/token.json")),
        channel_id=env("YOUTUBE_CHANNEL_ID", "").strip(),
        privacy_status=env("PRIVACY_STATUS", "public").strip() or "public",
        daily_limit=int(env("DAILY_LIMIT", "3")),
        videos_per_run=int(env("VIDEOS_PER_RUN", "1")),
        music_file=_path(env("MUSIC_FILE", "music/bed.mp3")),
        music_credit=env("MUSIC_CREDIT", "").strip(),
        silence_db=float(env("SILENCE_DB", "-45")),
        max_seconds=int(env("MAX_SECONDS", "59")),
        min_seconds=int(env("MIN_SECONDS", "5")),
        ffmpeg=_tool("ffmpeg", env("FFMPEG", "").strip()),
        ffprobe=_tool("ffprobe", env("FFPROBE", "").strip()),
        data_dir=ROOT / "data",
        work_dir=ROOT / "work",
        out_dir=ROOT / "out",
        log_dir=ROOT / "logs",
    )
