"""One-time YouTube sign-in. Opens a browser, then writes the refresh token to YOUTUBE_TOKEN."""

import sys

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from . import config
from .youtube import SCOPES, channel


def main() -> None:
    cfg = config.load()
    if not cfg.client_secrets.exists():
        raise SystemExit(f"Client JSON not found: {cfg.client_secrets}")
    flow = InstalledAppFlow.from_client_secrets_file(str(cfg.client_secrets), SCOPES)
    open_browser = "--no-browser" not in sys.argv
    if not open_browser:
        print("Open the link below in a private/incognito window.", flush=True)
    creds = flow.run_local_server(
        port=0, prompt="consent select_account", access_type="offline", open_browser=open_browser
    )

    channel_id, title = channel(build("youtube", "v3", credentials=creds, cache_discovery=False))
    if cfg.channel_id and channel_id != cfg.channel_id:
        raise SystemExit(
            f"Wrong channel: '{title}' ({channel_id}). Expected {cfg.channel_id}. "
            "Run again and choose the Retro Garage channel. Token not saved."
        )

    cfg.token_file.parent.mkdir(parents=True, exist_ok=True)
    cfg.token_file.write_text(creds.to_json(), encoding="utf-8")
    print(f"Saved {cfg.token_file} for channel '{title}' ({channel_id})")


if __name__ == "__main__":
    main()
