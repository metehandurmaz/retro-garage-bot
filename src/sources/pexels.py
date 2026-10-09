import logging
import re

from ..license import PEXELS
from .base import Candidate, Http, looks_like_classic_car

log = logging.getLogger(__name__)

API = "https://api.pexels.com/videos/search"


def _slug_words(page_url: str) -> str:
    m = re.search(r"/video/([a-z0-9-]+?)-\d+/?$", page_url)
    return m.group(1).replace("-", " ") if m else ""


def search(http: Http, api_key: str, query: str) -> list[Candidate]:
    if not api_key:
        return []
    data = http.get_json(
        API,
        params={"query": query, "per_page": 40, "size": "medium"},
        headers={"Authorization": api_key},
    )
    out = []
    for video in data.get("videos", []):
        files = [
            f for f in video.get("video_files", [])
            if f.get("file_type") == "video/mp4" and f.get("link") and (f.get("height") or 0) <= 2160
        ]
        if not files:
            continue
        best = max(files, key=lambda f: (f.get("height") or 0) * (f.get("width") or 0))
        page = video.get("url", "")
        title = _slug_words(page)
        cand = Candidate(
            source="pexels",
            source_id=str(video["id"]),
            media_url=best["link"],
            page_url=page,
            title=title,
            tags=title.split(),
            license=PEXELS,
            author=(video.get("user") or {}).get("name", ""),
            duration=float(video.get("duration") or 0) or None,
        )
        if looks_like_classic_car(cand.text()):
            out.append(cand)
    return out
