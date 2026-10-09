"""Narrated fact Shorts: Turkish TTS, one-word captions and fast cuts over licensed photos."""
import argparse
import asyncio
import html
import logging
import math
import random
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import edge_tts

from . import config
from .edit import HEIGHT, WIDTH, Skip, Transient, _duration, _run, probe
from .license import License, from_creative_commons
from .metadata import Metadata
from .sources.base import Http
from .stories import Story, by_id

log = logging.getLogger(__name__)

COMMONS_API = "https://commons.wikimedia.org/w/api.php"
VOICE = "tr-TR-AhmetNeural"
VOICE_RATE = "+12%"
SHOT_SECONDS = 1.4
MUSIC_VOLUME = 0.12
FONT = "Anton"
FONT_FILE = config.ROOT / "assets" / "fonts" / "Anton-Regular.ttf"
MIN_PHOTOS = 6
BLOCKED_PHOTO_WORDS = (
    "logo", "emblem", "badge", "drawing", "sketch", "replica", "concept", "toy", "lego",
    "diecast", "die-cast", "scale model", "1:18", "1:43", "1:24", "matchbox", "hot wheels",
)


@dataclass
class Word:
    start: float
    end: float
    text: str


@dataclass
class Photo:
    url: str
    page_url: str
    title: str
    author: str
    license: License


def _plain(value: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", value or "")).strip()


def _years(title: str) -> list[int]:
    years = [int(y) for y in re.findall(r"\b(1[89]\d\d|20\d\d)\b", title)]
    years += [(1900 if int(y) >= 20 else 2000) + int(y) for y in re.findall(r"'(\d\d)\b", title)]
    return years


def _wanted(story: Story, title: str) -> bool:
    lower = title.lower()
    if not any(word in lower for word in story.must_contain):
        return False
    if any(re.search(rf"(?<![a-z0-9]){re.escape(word)}(?![a-z0-9])", lower)
           for word in (*BLOCKED_PHOTO_WORDS, *story.exclude)):
        return False
    return not (story.max_year and any(y > story.max_year for y in _years(title)))


def find_photos(http: Http, story: Story) -> list[Photo]:
    pages = {}
    for query in story.image_queries:
        data = http.get_json(COMMONS_API, params={
            "action": "query", "format": "json", "generator": "search",
            "gsrsearch": f"filetype:bitmap {query}", "gsrnamespace": 6, "gsrlimit": 50,
            "prop": "imageinfo", "iiprop": "url|extmetadata|size", "iiurlwidth": 1600,
        })
        pages.update((data.get("query") or {}).get("pages", {}))

    photos = []
    for page in pages.values():
        info = (page.get("imageinfo") or [{}])[0]
        meta = info.get("extmetadata") or {}
        title = page.get("title", "")
        if not _wanted(story, title) or not re.search(r"\.jpe?g$", title, re.I):
            continue
        if (info.get("width") or 0) < 1200 or (info.get("width") or 0) < (info.get("height") or 0):
            continue
        lic = from_creative_commons(
            (meta.get("LicenseShortName") or {}).get("value", ""),
            (meta.get("LicenseUrl") or {}).get("value", ""),
        )
        if lic is None or not info.get("thumburl"):
            continue
        photos.append(Photo(
            url=info["thumburl"],
            page_url=info.get("descriptionurl", ""),
            title=re.sub(r"^File:", "", title),
            author=_plain((meta.get("Artist") or {}).get("value", "")) or "Wikimedia Commons",
            license=lic,
        ))
    return photos


async def _speak(text: str, dest: Path) -> list[Word]:
    words = []
    tts = edge_tts.Communicate(text, VOICE, rate=VOICE_RATE, boundary="WordBoundary")
    with dest.open("wb") as f:
        async for chunk in tts.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                start = chunk["offset"] / 1e7
                words.append(Word(start, start + chunk["duration"] / 1e7, chunk["text"]))
    return words


def speak(text: str, dest: Path) -> list[Word]:
    return asyncio.run(_speak(text, dest))


def _upper_tr(text: str) -> str:
    return text.replace("i", "İ").replace("ı", "I").upper()


def _ass_time(seconds: float) -> str:
    cs = int(round(seconds * 100))
    return f"{cs // 360000}:{cs // 6000 % 60:02d}:{cs // 100 % 60:02d}.{cs % 100:02d}"


def write_captions(words: list[Word], dest: Path) -> None:
    header = (
        "[Script Info]\nScriptType: v4.00+\nPlayResX: 1080\nPlayResY: 1920\nWrapStyle: 2\n\n"
        "[V4+ Styles]\n"
        "Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, "
        "Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, "
        "Alignment, MarginL, MarginR, MarginV, Encoding\n"
        f"Style: Word,{FONT},150,&H0000E5FF,&H0000E5FF,&H00000000,&H80000000,"
        "0,0,0,0,100,100,2,0,1,8,4,5,40,40,0,1\n\n"
        "[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
    )
    lines = []
    for i, word in enumerate(words):
        end = words[i + 1].start if i + 1 < len(words) else word.end + 0.4
        end = min(end, word.end + 0.6)
        pop = r"{\fscx70\fscy70\t(0,90,\fscx100\fscy100)}"
        lines.append(
            f"Dialogue: 0,{_ass_time(word.start)},{_ass_time(end)},Word,,0,0,0,,{pop}{_upper_tr(word.text)}"
        )
    dest.write_text(header + "\n".join(lines) + "\n", encoding="utf-8")


def _download(http: Http, url: str, dest: Path) -> None:
    resp = http.session.get(url, timeout=60)
    resp.raise_for_status()
    dest.write_bytes(resp.content)


def render_shot(cfg: config.Config, image: Path, dest: Path, seconds: float, zoom_in: bool) -> None:
    grow = "0.10*t/{d}" if zoom_in else "0.10*(1-t/{d})"
    grow = grow.format(d=f"{seconds:.3f}")
    vf = (
        f"[0:v]split=2[a][b];"
        f"[a]scale={WIDTH}:{HEIGHT}:force_original_aspect_ratio=increase,crop={WIDTH}:{HEIGHT},boxblur=30:2[bg];"
        f"[b]scale=-2:1000,crop='min(iw,{WIDTH})':1000[fg];"
        f"[bg][fg]overlay=(W-w)/2:(H-h)/2-80,"
        f"scale=w='trunc({WIDTH}*(1.02+{grow})/2)*2':h=-2:eval=frame,"
        f"crop={WIDTH}:{HEIGHT},setsar=1,format=yuv420p[v]"
    )
    res = _run([
        cfg.ffmpeg, "-hide_banner", "-y", "-loop", "1", "-framerate", "30", "-t", f"{seconds:.3f}",
        "-i", str(image), "-filter_complex", vf, "-map", "[v]",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-r", "30", str(dest),
    ], timeout=300)
    if res.returncode != 0:
        raise Skip(f"shot render failed: {res.stderr.strip()[-300:]}")


def build(cfg: config.Config, story: Story, keep_work: bool = False) -> tuple[Path, list[Photo]]:
    http = Http(cfg.data_dir / "cache")
    work = cfg.work_dir / f"story_{story.id}"
    shutil.rmtree(work, ignore_errors=True)
    work.mkdir(parents=True)

    voice = work / "voice.mp3"
    try:
        words = speak(story.text, voice)
    except Exception as err:
        raise Transient(f"tts failed: {err}") from err
    if not words:
        raise Transient("tts returned no word timings")
    seconds = _duration(probe(cfg, str(voice))) + 0.6
    write_captions(words, work / "subs.ass")
    log.info("voice: %.1fs, %d words", seconds, len(words))

    shots_needed = math.ceil(seconds / SHOT_SECONDS)
    photos = find_photos(http, story)
    random.shuffle(photos)
    used: list[Photo] = []
    images: list[Path] = []
    for photo in photos:
        if len(images) >= shots_needed:
            break
        image = work / f"img_{len(images):02d}.jpg"
        try:
            _download(http, photo.url, image)
        except Exception as err:
            log.warning("photo download failed %s: %s", photo.page_url, err)
            continue
        images.append(image)
        used.append(photo)
    if len(images) < min(MIN_PHOTOS, shots_needed):
        raise Skip(f"only {len(images)} usable licensed photos for {story.image_queries}")

    shot_files = []
    for i in range(shots_needed):
        shot = work / f"shot_{i:02d}.mp4"
        length = min(SHOT_SECONDS, seconds - i * SHOT_SECONDS)
        render_shot(cfg, images[i % len(images)], shot, length, zoom_in=i % 2 == 0)
        shot_files.append(shot)

    fonts = work / "fonts"
    fonts.mkdir()
    if FONT_FILE.exists():
        shutil.copy(FONT_FILE, fonts / FONT_FILE.name)

    (work / "shots.txt").write_text("".join(f"file '{p.name}'\n" for p in shot_files), encoding="utf-8")

    cfg.out_dir.mkdir(parents=True, exist_ok=True)
    dest = cfg.out_dir / f"story_{story.id}.mp4"
    music = ["-stream_loop", "-1", "-i", str(cfg.music_file)] if cfg.music_file.exists() else []
    audio = (
        f"[1:a]aresample=48000,apad=pad_dur=1[voice];"
        f"[2:a]volume={MUSIC_VOLUME},aresample=48000[music];"
        f"[voice][music]amix=inputs=2:duration=first:normalize=0,"
        f"afade=t=out:st={seconds - 0.8:.2f}:d=0.8,loudnorm=I=-14:TP=-1.5:LRA=11[a]"
        if music else
        f"[1:a]aresample=48000,apad=pad_dur=1,loudnorm=I=-14:TP=-1.5:LRA=11[a]"
    )
    # Run inside the work dir so the subtitles filter gets a path without a drive colon to escape.
    res = _run_in(cfg, work, [
        "-f", "concat", "-safe", "0", "-i", "shots.txt",
        "-i", "voice.mp3", *music,
        "-filter_complex", f"[0:v]subtitles=subs.ass:fontsdir=fonts[v];{audio}",
        "-map", "[v]", "-map", "[a]", "-t", f"{seconds:.2f}",
        "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-profile:v", "high",
        "-c:a", "aac", "-b:a", "192k", "-ac", "2", "-movflags", "+faststart",
        str(dest),
    ])
    if res.returncode != 0 or not dest.exists():
        raise Skip(f"final render failed: {res.stderr.strip()[-500:]}")
    if not keep_work:
        shutil.rmtree(work, ignore_errors=True)
    return dest, used


def _run_in(cfg: config.Config, cwd: Path, args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        [cfg.ffmpeg, "-hide_banner", "-y", *args],
        capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900, cwd=cwd,
    )


def description(story: Story, photos: list[Photo]) -> str:
    credits = "\n".join(
        f"- {p.title} by {p.author} ({p.license.name}{', ' + p.license.url if p.license.url else ''}) {p.page_url}"
        for p in photos
    )
    return (
        f"{story.text}\n\n"
        "Daha fazla klasik araba hikâyesi için abone ol!\n\n"
        f"Fotoğraflar (Wikimedia Commons):\n{credits}\n\n"
        "Seslendirme yapay zekâ ile üretilmiştir.\n\n"
        + " ".join(story.hashtags)
    )


def metadata(story: Story, photos: list[Photo]) -> Metadata:
    model = re.sub(r"^\W+", "", story.title.rsplit("!", 1)[-1]).strip()
    tags, total = [], 0
    for tag in [model, *(h.lstrip("#") for h in story.hashtags if h != "#shorts"),
                "klasik araba", "klasik arabalar", "eski arabalar", "otomobil tarihi", "classic cars", "shorts"]:
        if tag and tag not in tags and total + len(tag) + 1 <= 480:
            tags.append(tag)
            total += len(tag) + 1
    return Metadata(story.title[:100], description(story, photos)[:4900], tags, language="tr")


def main() -> None:
    parser = argparse.ArgumentParser(description="Render one narrated story Short without uploading.")
    parser.add_argument("--id", required=True)
    parser.add_argument("--keep-work", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    cfg = config.load()
    story = by_id(args.id)
    dest, used = build(cfg, story, keep_work=args.keep_work)
    print(f"VIDEO: {dest}")
    print(f"TITLE: {story.title}")
    print(description(story, used))


if __name__ == "__main__":
    main()
