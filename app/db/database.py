import os
import sqlite3


class Database:
    def __init__(self, path: str) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        cur = self.conn.execute(query, params)
        self.conn.commit()
        return cur

    def fetchone(self, query: str, params: tuple = ()):
        cur = self.conn.execute(query, params)
        return cur.fetchone()

    def fetchall(self, query: str, params: tuple = ()):
        cur = self.conn.execute(query, params)
        return cur.fetchall()

    def column_exists(self, table_name: str, column_name: str) -> bool:
        rows = self.fetchall(f"PRAGMA table_info({table_name})")
        return any(row["name"] == column_name for row in rows)

    def init_schema(self) -> None:
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                chat_id INTEGER PRIMARY KEY,
                is_enabled INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS sent_notifications (
                dedupe_key TEXT PRIMARY KEY,
                sent_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS checkin_draft (
                chat_id INTEGER PRIMARY KEY,
                ds_hours REAL NOT NULL DEFAULT 0,
                diploma_hours REAL NOT NULL DEFAULT 0,
                workout_done INTEGER NOT NULL DEFAULT 0,
                university_done INTEGER NOT NULL DEFAULT 0,
                notes TEXT DEFAULT '',
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS progress_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                chat_id INTEGER NOT NULL,
                log_date TEXT NOT NULL,
                ds_hours REAL NOT NULL DEFAULT 0,
                diploma_hours REAL NOT NULL DEFAULT 0,
                workout_done INTEGER NOT NULL DEFAULT 0,
                university_done INTEGER NOT NULL DEFAULT 0,
                notes TEXT,
                xp_earned INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS user_stats (
                chat_id INTEGER PRIMARY KEY,
                total_xp INTEGER NOT NULL DEFAULT 0,
                level INTEGER NOT NULL DEFAULT 1,
                current_streak INTEGER NOT NULL DEFAULT 0,
                best_streak INTEGER NOT NULL DEFAULT 0,
                updated_at TEXT NOT NULL
            );
            """
        )
        self.conn.commit()

        if not self.column_exists("users", "username"):
            self.execute("ALTER TABLE users ADD COLUMN username TEXT")

        if not self.column_exists("users", "full_name"):
            self.execute("ALTER TABLE users ADD COLUMN full_name TEXT")