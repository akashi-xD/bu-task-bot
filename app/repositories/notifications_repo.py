from datetime import datetime

from app.db.database import Database


class NotificationsRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def was_sent(self, dedupe_key: str) -> bool:
        row = self.db.fetchone(
            "SELECT 1 FROM sent_notifications WHERE dedupe_key = ?",
            (dedupe_key,),
        )
        return row is not None

    def mark_sent(self, dedupe_key: str) -> None:
        self.db.execute(
            """
            INSERT OR REPLACE INTO sent_notifications(dedupe_key, sent_at)
            VALUES(?, ?)
            """,
            (dedupe_key, datetime.utcnow().isoformat()),
        )