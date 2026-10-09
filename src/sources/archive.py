import logging
from urllib.parse import quote

from ..license import from_creative_commons
from .base import Candidate, Http, looks_like_classic_car

log = logging.getLogger(__name__)

SEARCH = "https://archive.org/advancedsearch.php"
METADATA = "https://archive.org/metadata/{}"
MAX_FILE_BYTES = 800 * 1024 * 1024


def _as_list(value) -> list[str]:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _pick_file(files: list[dict]) -> dict | None:
    mp4s = [
        f for f in files
        if f.get("name", "").lower().endswith(".mp4") and int(f.get("size") or 0) < MAX_FILE_BYTES
    ]
    if not mp4s:
        return None
    # Prefer the derivative h.264 file; originals are often huge.
    return min(mp4s, key=lambda f: (f.get("source") != "derivative", int(f.get("size") or 0)))


def search(http: Http, query: str, limit: int = 20) -> list[Candidate]:
    # Archive rejects OR between leading-wildcard terms, so each license family is its own query.
    docs = []
    for lic_filter in ("licenseurl:*publicdomain*", "licenseurl:*licenses/by/*"):
        data = http.get_json(
            SEARCH,
            params={
                "q": f"({query}) AND mediatype:movies AND {lic_filter}",
                "fl[]": ["identifier", "title", "licenseurl", "subject"],
                "rows": 100,
                "output": "json",
                "sort[]": "downloads desc",
            },
        )
        docs += (data.get("response") or {}).get("docs", [])

    out = []
    for doc in docs:
        lic = from_creative_commons("", doc.get("licenseurl", ""))
        if lic is None:
            continue
        title = doc.get("title") or doc["identifier"]
        if isinstance(title, list):
            title = title[0]
        tags = _as_list(doc.get("subject"))
        text = f"{title} {' '.join(tags)}"
        if not looks_like_classic_car(text):
            continue

        meta = http.get_json(METADATA.format(doc["identifier"]))
        chosen = _pick_file(meta.get("files", []))
        if not chosen:
            continue
        md = meta.get("metadata", {})
        out.append(
            Candidate(
                source="archive",
                source_id=doc["identifier"],
                media_url=f"https://archive.org/download/{doc['identifier']}/{quote(chosen['name'])}",
                page_url=f"https://archive.org/details/{doc['identifier']}",
                title=title,
                tags=tags,
                license=lic,
                author=", ".join(_as_list(md.get("creator"))),
                duration=float(chosen["length"]) if str(chosen.get("length", "")).replace(".", "").isdigit() else None,
            )
        )
        if len(out) >= limit:
            break
    return out
