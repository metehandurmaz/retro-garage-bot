import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS seen (
    source TEXT NOT NULL,
    source_id TEXT NOT NULL,
    status TEXT NOT NULL,
    reason TEXT,
    youtube_id TEXT,
    title TEXT,
    music_added INTEGER,
    created_at TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
    PRIMARY KEY (source, source_id)
);
"""


class Store:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(path)
        self.conn.executescript(SCHEMA)

    def is_seen(self, source: str, source_id: str) -> bool:
        row = self.conn.execute(
            "SELECT 1 FROM seen WHERE source = ? AND source_id = ?", (source, source_id)
        ).fetchone()
        return row is not None

    def reject(self, source: str, source_id: str, reason: str) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO seen (source, source_id, status, reason) VALUES (?, ?, 'rejected', ?)",
            (source, source_id, reason),
        )
        self.conn.commit()

    def uploaded(self, source: str, source_id: str, youtube_id: str, title: str, music_added: bool) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO seen (source, source_id, status, youtube_id, title, music_added) "
            "VALUES (?, ?, 'uploaded', ?, ?, ?)",
            (source, source_id, youtube_id, title, int(music_added)),
        )
        self.conn.commit()

    def uploads_today(self) -> int:
        row = self.conn.execute(
            "SELECT COUNT(*) FROM seen WHERE status = 'uploaded' "
            "AND date(created_at) = date('now', 'localtime')"
        ).fetchone()
        return row[0]
