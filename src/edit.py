import json
import logging
import re
import subprocess
from dataclasses import dataclass
from pathlib import Path

from .config import Config

log = logging.getLogger(__name__)

WIDTH, HEIGHT = 1080, 1920


class Skip(Exception):
    """The clip cannot be used; the reason is stored so it is not retried."""


class Transient(Exception):
    """Network or download problem; the clip may work on a later run."""


@dataclass
class Rendered:
    path: Path
    seconds: float
    music_added: bool


def _run(cmd: list[str], timeout: int = 900) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)


def probe(cfg: Config, path: str) -> dict:
    res = _run([cfg.ffprobe, "-v", "error", "-print_format", "json", "-show_format", "-show_streams", path], 180)
    if res.returncode != 0:
        raise Skip(f"ffprobe failed: {res.stderr.strip()[-200:]}")
    return json.loads(res.stdout)


def _duration(info: dict) -> float:
    try:
        return float(info["format"]["duration"])
    except (KeyError, TypeError, ValueError):
        return 0.0


def mean_volume(cfg: Config, path: Path) -> float | None:
    res = _run([cfg.ffmpeg, "-hide_banner", "-nostats", "-i", str(path), "-vn", "-af", "volumedetect", "-f", "null", "-"])
    m = re.search(r"mean_volume:\s*(-?[\d.]+|-inf) dB", res.stderr)
    if not m:
        return None
    return float("-inf") if m.group(1) == "-inf" else float(m.group(1))


def fetch_segment(cfg: Config, url: str, dest: Path, known_duration: float | None) -> float:
    """Copy at most MAX_SECONDS from the source without downloading the whole file."""
    total = known_duration
    if not total:
        try:
            total = _duration(probe(cfg, url))
        except Skip as err:
            raise Transient(str(err)) from err
    if total and total < cfg.min_seconds:
        raise Skip(f"too short ({total:.1f}s)")
    start = 0.0
    if total > cfg.max_seconds * 2:
        start = round(total * 0.1, 2)

    res = _run([
        cfg.ffmpeg, "-hide_banner", "-y", "-ss", str(start), "-i", url,
        "-t", str(cfg.max_seconds), "-map", "0:v:0", "-map", "0:a:0?", "-c", "copy", str(dest),
    ])
    if res.returncode != 0 or not dest.exists():
        raise Transient(f"download failed: {res.stderr.strip()[-200:]}")
    try:
        seconds = _duration(probe(cfg, str(dest)))
    except Skip as err:
        raise Transient(f"downloaded file unreadable: {err}") from err
    if seconds < cfg.min_seconds:
        raise Skip(f"too short after trim ({seconds:.1f}s)")
    return seconds


def render(cfg: Config, raw: Path, dest: Path, seconds: float) -> Rendered:
    info = probe(cfg, str(raw))
    has_audio = any(s.get("codec_type") == "audio" for s in info.get("streams", []))
    volume = mean_volume(cfg, raw) if has_audio else None
    silent = volume is None or volume < cfg.silence_db
    log.info("audio: stream=%s mean=%s dB -> %s", has_audio, volume, "silent" if silent else "keeps own sound")

    if silent and not cfg.music_file.exists():
        raise Skip(f"silent clip and no music file at {cfg.music_file}")

    video_filter = (
        f"[0:v]split=2[bg][fg];"
        f"[bg]scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,crop={WIDTH}:{HEIGHT},boxblur=24:2[bgb];"
        f"[fg]scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=decrease[fgs];"
        f"[bgb][fgs]overlay=(W-w)/2:(H-h)/2,setsar=1,fps=30,format=yuv420p[v]"
    )
    fade_start = max(seconds - 1.5, 0)

    cmd = [cfg.ffmpeg, "-hide_banner", "-y", "-i", str(raw)]
    if silent:
        cmd += ["-stream_loop", "-1", "-i", str(cfg.music_file)]
        audio_filter = f"[1:a]atrim=0:{seconds:.2f},afade=t=out:st={fade_start:.2f}:d=1.5,aresample=48000[a]"
    else:
        audio_filter = f"[0:a]aresample=48000,loudnorm=I=-14:TP=-1.5:LRA=11[a]"

    cmd += [
        "-filter_complex", f"{video_filter};{audio_filter}",
        "-map", "[v]", "-map", "[a]",
        "-t", f"{seconds:.2f}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-profile:v", "high",
        "-c:a", "aac", "-b:a", "192k", "-ac", "2",
        "-movflags", "+faststart",
        str(dest),
    ]
    res = _run(cmd, timeout=1800)
    if res.returncode != 0 or not dest.exists():
        raise Skip(f"render failed: {res.stderr.strip()[-300:]}")
    return Rendered(dest, seconds, silent)
