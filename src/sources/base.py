import hashlib
import json
import logging
import re
import time
from dataclasses import dataclass, field
from pathlib import Path

import requests

from ..license import License

log = logging.getLogger(__name__)

USER_AGENT = "RetroGarageBot/1.1 (https://metehandurmaz.github.io; metehan.durmaz.md@gmail.com)"
CACHE_TTL = 24 * 3600
MIN_INTERVAL = 0.8

CAR_WORDS = (
    "car", "cars", "automobile", "auto", "oldtimer", "vehicle", "roadster", "convertible",
    "coupe", "sedan", "muscle", "hot rod", "hotrod", "cadillac", "chevrolet", "chevy", "ford",
    "mustang", "porsche", "mercedes", "beetle", "volkswagen", "corvette", "jaguar", "ferrari",
    "pontiac", "dodge", "plymouth", "buick", "lincoln", "rolls", "bentley", "citroen", "fiat",
)
CLASSIC_WORDS = (
    "classic", "vintage", "oldtimer", "old", "retro", "antique", "muscle", "hot rod", "hotrod",
    "historic", "veteran",
)
CLASSIC_YEAR = re.compile(r"\b(19[2-8]\d|[2-8]0s)\b")
BLOCKED_WORDS = (
    "toy", "lego", "cartoon", "animation", "animated", "drawing", "game", "3d", "render",
    "crash test", "accident", "miniature", "model car", "rc car", "remote control",
)


@dataclass
class Candidate:
    source: str
    source_id: str
    media_url: str
    page_url: str
    title: str
    tags: list[str]
    license: License
    author: str = ""
    duration: float | None = None
    extra: dict = field(default_factory=dict)

    @property
    def key(self) -> str:
        return f"{self.source}:{self.source_id}"

    def text(self) -> str:
        return f"{self.title} {' '.join(self.tags)}".lower()


def looks_like_classic_car(text: str) -> bool:
    text = text.lower()
    words = set(re.findall(r"[a-z0-9]+", text))
    has_car = any((w in words) if " " not in w else (w in text) for w in CAR_WORDS)
    is_classic = any(w in words for w in CLASSIC_WORDS if " " not in w) or any(
        w in text for w in CLASSIC_WORDS if " " in w
    ) or bool(CLASSIC_YEAR.search(text))
    blocked = any((w in words) if " " not in w else (w in text) for w in BLOCKED_WORDS)
    return has_car and is_classic and not blocked


class Http:
    """GET with a 24h JSON cache. Pixabay requires caching search responses for 24 hours."""

    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers["User-Agent"] = USER_AGENT
        self._last_request = 0.0

    def get_json(self, url: str, params: dict | None = None, headers: dict | None = None) -> dict:
        key_src = url + json.dumps(params or {}, sort_keys=True)
        path = self.cache_dir / (hashlib.sha1(key_src.encode()).hexdigest() + ".json")
        if path.exists() and time.time() - path.stat().st_mtime < CACHE_TTL:
            return json.loads(path.read_text(encoding="utf-8"))

        # Pixabay allows 100 requests/minute; stay well under it.
        wait = MIN_INTERVAL - (time.time() - self._last_request)
        if wait > 0:
            time.sleep(wait)
        self._last_request = time.time()
        resp = self.session.get(url, params=params, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        path.write_text(json.dumps(data), encoding="utf-8")
        return data
