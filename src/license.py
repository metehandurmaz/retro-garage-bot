import re
from dataclasses import dataclass


@dataclass(frozen=True)
class License:
    name: str
    url: str
    needs_credit: bool


PIXABAY = License("Pixabay Content License", "https://pixabay.com/service/license-summary/", False)
PEXELS = License("Pexels License", "https://www.pexels.com/license/", False)

# NC blocks monetization, ND blocks editing, SA forces the upload itself under CC.
_BLOCKED = re.compile(r"(^|[\s/_-])(nc|nd|sa)([\s/_.-]|$)", re.I)


def from_creative_commons(name: str, url: str) -> License | None:
    """Accept only public domain, CC0 and plain CC-BY. Anything else, or unknown, is rejected."""
    name = (name or "").strip()
    url = (url or "").strip()
    text = f"{name} {url}".lower()
    if not text.strip():
        return None

    if "publicdomain" in text or "public domain" in text or re.search(r"\bpd\b", text):
        return License(name or "Public Domain", url, False)
    if "cc0" in text or "/zero/" in text:
        return License(name or "CC0", url, False)

    is_by = "licenses/by/" in text or re.search(r"\bcc[\s-]?by\b", text)
    if is_by and not _BLOCKED.search(name.lower().replace("cc by", "")) and not re.search(
        r"licenses/by-(nc|nd|sa)", text
    ):
        return License(name or "CC BY", url, True)
    return None
