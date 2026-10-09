import logging

from ..license import PIXABAY
from .base import Candidate, Http, looks_like_classic_car

log = logging.getLogger(__name__)

API = "https://pixabay.com/api/videos/"


PER_PAGE = 200
MAX_PAGES = 3


def _hits(http: Http, api_key: str, query: str) -> list[dict]:
    hits = []
    for page in range(1, MAX_PAGES + 1):
        data = http.get_json(
            API,
            params={
                "key": api_key,
                "q": query,
                "video_type": "film",
                "safesearch": "true",
                "per_page": PER_PAGE,
                "page": page,
                "order": "popular",
            },
        )
        hits += data.get("hits", [])
        if page * PER_PAGE >= int(data.get("totalHits") or 0):
            break
    return hits


def search(http: Http, api_key: str, query: str) -> list[Candidate]:
    if not api_key:
        return []
    out = []
    for hit in _hits(http, api_key, query):
        tags = [t.strip() for t in hit.get("tags", "").split(",") if t.strip()]
        videos = hit.get("videos", {})
        media = next(
            (videos[s]["url"] for s in ("large", "medium", "small") if videos.get(s, {}).get("url")),
            None,
        )
        if not media:
            continue
        cand = Candidate(
            source="pixabay",
            source_id=str(hit["id"]),
            media_url=media,
            page_url=hit.get("pageURL", ""),
            title=", ".join(tags),
            tags=tags,
            license=PIXABAY,
            author=hit.get("user", ""),
            duration=float(hit.get("duration") or 0) or None,
        )
        if looks_like_classic_car(cand.text()):
            out.append(cand)
    return out
