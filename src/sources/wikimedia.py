import html
import logging
import re

from ..license import from_creative_commons
from .base import Candidate, Http, looks_like_classic_car

log = logging.getLogger(__name__)

API = "https://commons.wikimedia.org/w/api.php"


def _plain(value: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", value or "")).strip()


def search(http: Http, query: str) -> list[Candidate]:
    data = http.get_json(
        API,
        params={
            "action": "query",
            "format": "json",
            "generator": "search",
            "gsrsearch": f"filetype:video {query}",
            "gsrnamespace": 6,
            "gsrlimit": 50,
            "prop": "imageinfo",
            "iiprop": "url|extmetadata|mime|size",
        },
    )
    out = []
    for page in (data.get("query") or {}).get("pages", {}).values():
        info = (page.get("imageinfo") or [{}])[0]
        meta = info.get("extmetadata") or {}
        lic = from_creative_commons(
            (meta.get("LicenseShortName") or {}).get("value", ""),
            (meta.get("LicenseUrl") or {}).get("value", ""),
        )
        if lic is None or not info.get("url"):
            continue
        title = re.sub(r"^File:", "", page.get("title", ""))
        title = re.sub(r"\.(webm|ogv|ogg|mp4|mpg|mpeg)$", "", title, flags=re.I).replace("_", " ")
        categories = _plain((meta.get("Categories") or {}).get("value", "")).split("|")
        cand = Candidate(
            source="wikimedia",
            source_id=str(page.get("pageid")),
            media_url=info["url"],
            page_url=info.get("descriptionurl", ""),
            title=title,
            tags=[c for c in categories if c],
            license=lic,
            author=_plain((meta.get("Artist") or {}).get("value", "")),
            duration=float(info["duration"]) if info.get("duration") else None,
        )
        if looks_like_classic_car(cand.text()):
            out.append(cand)
    return out
