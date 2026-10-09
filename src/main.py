"""Find licensed classic car clips, turn them into Shorts, and upload them.

    python -m src.main            upload up to VIDEOS_PER_RUN (never more than DAILY_LIMIT per day)
    python -m src.main --dry-run  render into out/ with metadata, no upload, nothing marked as used
    python -m src.main --mode story|clip   force one kind (default: stories, clips only as fallback)
"""

import argparse
import json
import logging
import random
import shutil
import sys
import time
from logging.handlers import RotatingFileHandler

import requests

from . import config, edit, metadata, story_video, youtube
from .db import Store
from .stories import STORIES, Story
from .sources import Candidate, archive, pexels, pixabay, wikimedia
from .sources.base import Http

log = logging.getLogger("bot")

QUERIES = [
    "classic car", "vintage car", "oldtimer", "muscle car", "retro car", "antique car",
    "classic car show", "vintage car driving", "hot rod", "vintage convertible", "old car",
    "classic car interior", "vintage car engine", "classic car chrome", "vintage car street",
    "car meet classic", "american classic car", "cadillac classic", "chevrolet classic",
    "chevrolet impala", "chevrolet bel air", "corvette classic", "camaro classic",
    "ford mustang classic", "ford thunderbird", "ford model t", "pontiac classic", "dodge charger classic",
    "plymouth classic", "buick classic", "lincoln continental", "volkswagen beetle", "volkswagen bus",
    "porsche classic", "porsche 911 classic", "mercedes oldtimer", "jaguar classic", "ferrari classic",
    "alfa romeo classic", "fiat 500 classic", "citroen 2cv", "citroen ds", "mini cooper classic",
    "rolls royce vintage", "bentley vintage", "bmw classic", "lada classic", "volga classic",
]

WIKIMEDIA_PAUSE = 1.5


def setup_logging(cfg: config.Config) -> None:
    cfg.log_dir.mkdir(parents=True, exist_ok=True)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
    file_handler = RotatingFileHandler(cfg.log_dir / "bot.log", maxBytes=2_000_000, backupCount=5, encoding="utf-8")
    file_handler.setFormatter(fmt)
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(fmt)
    logging.basicConfig(level=logging.INFO, handlers=[file_handler, console])
    logging.getLogger("googleapiclient.discovery_cache").setLevel(logging.ERROR)


def _wikimedia(http: Http, q: str) -> list[Candidate]:
    try:
        return wikimedia.search(http, q)
    except requests.HTTPError as err:
        if err.response is not None and err.response.status_code == 429:
            time.sleep(WIKIMEDIA_PAUSE * 10)
            return wikimedia.search(http, q)
        raise


def gather(cfg: config.Config, http: Http, store: Store) -> list[Candidate]:
    # Every query runs each time; responses are cached for 24h, so only the first run of a day hits the APIs.
    searches = []
    for q in QUERIES:
        searches.append(("pixabay", lambda q=q: pixabay.search(http, cfg.pixabay_key, q)))
        searches.append(("pexels", lambda q=q: pexels.search(http, cfg.pexels_key, q)))
        searches.append(("wikimedia", lambda q=q: _wikimedia(http, q)))
    searches.append(("archive", lambda: archive.search(
        http, "classic car OR vintage car OR antique car OR automobile OR oldtimer OR hot rod"
    )))

    found: dict[str, Candidate] = {}
    failures: dict[str, int] = {}
    for name, run in searches:
        try:
            for cand in run():
                if cand.key not in found and not store.is_seen(cand.source, cand.source_id):
                    found[cand.key] = cand
        except Exception as err:  # one source failing must not stop the others
            failures[name] = failures.get(name, 0) + 1
            log.debug("%s search failed: %s", name, err)
    for name, count in failures.items():
        log.warning("%s: %d searches failed", name, count)

    cands = list(found.values())
    random.shuffle(cands)
    # Stock sites first; archive films are a fallback.
    cands.sort(key=lambda c: c.source == "archive")
    log.info("candidates: %d (%s)", len(cands), ", ".join(
        f"{s}={sum(c.source == s for c in cands)}" for s in ("pixabay", "pexels", "wikimedia", "archive")
    ))
    if not cands:
        log.warning("no unused licensed clips left; add queries or sources")
    return cands


def process(cfg: config.Config, cand: Candidate, dry_run: bool, store: Store) -> bool:
    work = cfg.work_dir / f"{cand.source}_{cand.source_id}".replace("/", "_")
    work.mkdir(parents=True, exist_ok=True)
    try:
        raw = work / "raw.mkv"
        final = work / "short.mp4"
        seconds = edit.fetch_segment(cfg, cand.media_url, raw, cand.duration)
        rendered = edit.render(cfg, raw, final, seconds)
        meta = metadata.build(cand, rendered.music_added, cfg.music_credit)
        log.info("title: %s", meta.title)

        if dry_run:
            cfg.out_dir.mkdir(parents=True, exist_ok=True)
            base = cfg.out_dir / f"{cand.source}_{cand.source_id}".replace("/", "_")
            shutil.copy(final, base.with_suffix(".mp4"))
            base.with_suffix(".json").write_text(
                json.dumps({"title": meta.title, "description": meta.description, "tags": meta.tags,
                            "music_added": rendered.music_added, "source": cand.page_url}, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            log.info("dry run: wrote %s", base.with_suffix(".mp4"))
            return True

        video_id = youtube.upload(cfg, final, meta)
        store.uploaded(cand.source, cand.source_id, video_id, meta.title, rendered.music_added)
        log.info("uploaded https://www.youtube.com/shorts/%s", video_id)
        return True
    except edit.Transient as err:
        log.warning("retry later %s: %s", cand.key, err)
        return False
    except edit.Skip as skip:
        log.info("skip %s: %s", cand.key, skip)
        if not dry_run:
            store.reject(cand.source, cand.source_id, str(skip))
        return False
    finally:
        shutil.rmtree(work, ignore_errors=True)


def next_story(store: Store) -> Story | None:
    fresh = [s for s in STORIES if not store.is_seen("story", s.id)]
    log.info("stories left: %d/%d", len(fresh), len(STORIES))
    return random.choice(fresh) if fresh else None


def process_story(cfg: config.Config, story: Story, dry_run: bool, store: Store) -> bool:
    log.info("story %s", story.id)
    try:
        video, photos = story_video.build(cfg, story)
        meta = story_video.metadata(story, photos)
        log.info("title: %s", meta.title)
        if dry_run:
            video.with_suffix(".json").write_text(
                json.dumps({"title": meta.title, "description": meta.description, "tags": meta.tags},
                           indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            log.info("dry run: wrote %s", video)
            return True
        video_id = youtube.upload(cfg, video, meta)
        store.uploaded("story", story.id, video_id, meta.title, cfg.music_file.exists())
        video.unlink(missing_ok=True)
        log.info("uploaded https://www.youtube.com/shorts/%s", video_id)
        return True
    except edit.Transient as err:
        log.warning("story %s retry later: %s", story.id, err)
        return False
    except edit.Skip as skip:
        log.info("skip story %s: %s", story.id, skip)
        if not dry_run:
            store.reject("story", story.id, str(skip))
        return False


def wants_story(mode: str, slot: int) -> bool:
    # Every upload is a narrated story; plain clips are only the fallback when a story fails or the bank is empty.
    return mode != "clip"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--count", type=int, help="override VIDEOS_PER_RUN")
    parser.add_argument("--mode", choices=("auto", "story", "clip"), default="auto")
    args = parser.parse_args()

    cfg = config.load()
    setup_logging(cfg)
    store = Store(cfg.data_dir / "seen.sqlite")

    wanted = args.count or cfg.videos_per_run
    if not args.dry_run:
        wanted = min(wanted, cfg.daily_limit - store.uploads_today())
        if wanted <= 0:
            log.info("daily limit of %d reached", cfg.daily_limit)
            return 0

    http = Http(cfg.data_dir / "cache")
    done = 0
    clips = None
    stories_ok = True
    while done < wanted:
        slot = store.uploads_today() + (done if args.dry_run else 0)
        if stories_ok and wants_story(args.mode, slot):
            story = next_story(store)
            if story is not None:
                try:
                    if process_story(cfg, story, args.dry_run, store):
                        done += 1
                        continue
                except Exception:
                    log.exception("story %s failed", story.id)
            # One failed story per run is enough; fall back to a clip instead of retrying.
            stories_ok = False
            log.info("falling back to a clip")
        if args.mode == "story":
            break

        if clips is None:
            clips = iter(gather(cfg, http, store))
        cand = next(clips, None)
        if cand is None:
            break
        log.info("trying %s %s", cand.key, cand.page_url)
        try:
            if process(cfg, cand, args.dry_run, store):
                done += 1
        except Exception:
            log.exception("stopping: %s failed", cand.key)
            break

    log.info("finished: %d/%d", done, wanted)
    return 0 if done == wanted else 1


if __name__ == "__main__":
    sys.exit(main())
