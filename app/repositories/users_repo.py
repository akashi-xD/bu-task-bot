from datetime import datetime

from app.db.database import Database


class UsersRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def upsert_user(self, chat_id: int, username: str | None, full_name: str) -> None:
        self.db.execute(
            """
            INSERT INTO users(chat_id, username, full_name, is_enabled, created_at)
            VALUES(?, ?, ?, 1, ?)
            ON CONFLICT(chat_id) DO UPDATE SET
                username = excluded.username,
                full_name = excluded.full_name
            """,
            (chat_id, username, full_name, datetime.utcnow().isoformat()),
        )

        self.db.execute(
            """
            INSERT INTO user_stats(chat_id, total_xp, level, current_streak, best_streak, updated_at)
            VALUES(?, 0, 1, 0, 0, ?)
            ON CONFLICT(chat_id) DO NOTHING
            """,
            (chat_id, datetime.utcnow().isoformat()),
        )

    def set_enabled(self, chat_id: int, enabled: bool) -> None:
        self.db.execute(
            "UPDATE users SET is_enabled = ? WHERE chat_id = ?",
            (1 if enabled else 0, chat_id),
        )

    def is_enabled(self, chat_id: int) -> bool:
        row = self.db.fetchone(
            "SELECT is_enabled FROM users WHERE chat_id = ?",
            (chat_id,),
        )
        if row is None:
            return False
        return bool(row["is_enabled"])

    def get_enabled_chat_ids(self) -> list[int]:
        rows = self.db.fetchall(
            "SELECT chat_id FROM users WHERE is_enabled = 1"
        )
        return [int(row["chat_id"]) for row in rows]