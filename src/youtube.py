import logging
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

from .config import Config
from .metadata import Metadata

log = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube",
]
AUTOS_AND_VEHICLES = "2"


def credentials(cfg: Config) -> Credentials:
    if not cfg.token_file.exists():
        raise RuntimeError(f"{cfg.token_file} not found. Run: python -m src.authorize")
    creds = Credentials.from_authorized_user_file(str(cfg.token_file), SCOPES)
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            cfg.token_file.write_text(creds.to_json(), encoding="utf-8")
        else:
            raise RuntimeError("YouTube token is invalid. Run: python -m src.authorize")
    return creds


def channel(service) -> tuple[str, str]:
    items = service.channels().list(part="snippet", mine=True).execute().get("items", [])
    if not items:
        raise RuntimeError("The authorized Google account has no YouTube channel.")
    return items[0]["id"], items[0]["snippet"]["title"]


def upload(cfg: Config, video: Path, meta: Metadata) -> str:
    service = build("youtube", "v3", credentials=credentials(cfg), cache_discovery=False)
    channel_id, title = channel(service)
    if cfg.channel_id and channel_id != cfg.channel_id:
        raise RuntimeError(
            f"Token belongs to '{title}' ({channel_id}), expected {cfg.channel_id}. "
            "Run python -m src.authorize and pick the right channel."
        )
    body = {
        "snippet": {
            "title": meta.title,
            "description": meta.description,
            "tags": meta.tags,
            "categoryId": AUTOS_AND_VEHICLES,
            "defaultLanguage": meta.language,
            "defaultAudioLanguage": meta.language,
        },
        "status": {
            "privacyStatus": cfg.privacy_status,
            "selfDeclaredMadeForKids": False,
            "containsSyntheticMedia": False,
        },
    }
    media = MediaFileUpload(str(video), mimetype="video/mp4", chunksize=8 * 1024 * 1024, resumable=True)
    request = service.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    retries = 0
    while response is None:
        try:
            status, response = request.next_chunk()
            if status:
                log.info("upload %d%%", int(status.progress() * 100))
        except HttpError as err:
            if err.resp.status in (500, 502, 503, 504) and retries < 5:
                retries += 1
                log.warning("upload retry %d after HTTP %s", retries, err.resp.status)
                continue
            raise
    return response["id"]
