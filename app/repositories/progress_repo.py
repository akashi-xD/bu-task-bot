from datetime import datetime, date, timedelta

from app.db.database import Database


class ProgressRepository:
    def __init__(self, db: Database) -> None:
        self.db = db

    def save_progress(
        self,
        chat_id: int,
        log_date: date,
        ds_hours: float,
        diploma_hours: float,
        workout_done: bool,
        university_done: bool,
        notes: str,
        xp_earned: int,
    ) -> None:
        self.db.execute(
            """
            INSERT INTO progress_log(
                chat_id, log_date, ds_hours, diploma_hours,
                workout_done, university_done, notes, xp_earned, created_at
            )
            VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                chat_id,
                log_date.isoformat(),
                ds_hours,
                diploma_hours,
                1 if workout_done else 0,
                1 if university_done else 0,
                notes,
                xp_earned,
                datetime.utcnow().isoformat(),
            ),
        )

    def add_xp(self, chat_id: int, xp: int) -> None:
        row = self.db.fetchone(
            "SELECT total_xp FROM user_stats WHERE chat_id = ?",
            (chat_id,),
        )
        current_xp = int(row["total_xp"]) if row else 0

        self.db.execute(
            """
            UPDATE user_stats
            SET total_xp = ?, updated_at = ?
            WHERE chat_id = ?
            """,
            (current_xp + xp, datetime.utcnow().isoformat(), chat_id),
        )

    def set_level(self, chat_id: int, level: int) -> None:
        self.db.execute(
            """
            UPDATE user_stats
            SET level = ?, updated_at = ?
            WHERE chat_id = ?
            """,
            (level, datetime.utcnow().isoformat(), chat_id),
        )

    def get_user_stats(self, chat_id: int):
        return self.db.fetchone(
            """
            SELECT total_xp, level, current_streak, best_streak
            FROM user_stats
            WHERE chat_id = ?
            """,
            (chat_id,),
        )

    def get_last_7_days_stats(self, chat_id: int) -> dict:
        since = (date.today() - timedelta(days=6)).isoformat()

        row = self.db.fetchone(
            """
            SELECT
                COALESCE(SUM(ds_hours), 0) AS ds_hours,
                COALESCE(SUM(diploma_hours), 0) AS diploma_hours,
                COALESCE(SUM(workout_done), 0) AS workouts,
                COALESCE(SUM(university_done), 0) AS university_done,
                COALESCE(SUM(xp_earned), 0) AS xp_earned
            FROM progress_log
            WHERE chat_id = ? AND log_date >= ?
            """,
            (chat_id, since),
        )

        return {
            "ds_hours": float(row["ds_hours"]),
            "diploma_hours": float(row["diploma_hours"]),
            "workouts": int(row["workouts"]),
            "university_done": int(row["university_done"]),
            "xp_earned": int(row["xp_earned"]),
        }

    def get_or_create_draft(self, chat_id: int):
        row = self.db.fetchone(
            """
            SELECT chat_id, ds_hours, diploma_hours, workout_done, university_done, notes
            FROM checkin_draft
            WHERE chat_id = ?
            """,
            (chat_id,),
        )

        if row is not None:
            return row

        self.db.execute(
            """
            INSERT INTO checkin_draft(
                chat_id, ds_hours, diploma_hours, workout_done,
                university_done, notes, updated_at
            )
            VALUES(?, 0, 0, 0, 0, '', ?)
            """,
            (chat_id, datetime.utcnow().isoformat()),
        )

        return self.db.fetchone(
            """
            SELECT chat_id, ds_hours, diploma_hours, workout_done, university_done, notes
            FROM checkin_draft
            WHERE chat_id = ?
            """,
            (chat_id,),
        )

    def update_draft_hours(self, chat_id: int, field_name: str, delta: float) -> None:
        if field_name not in {"ds_hours", "diploma_hours"}:
            raise ValueError("Invalid draft field")

        self.get_or_create_draft(chat_id)
        self.db.execute(
            f"""
            UPDATE checkin_draft
            SET {field_name} = {field_name} + ?, updated_at = ?
            WHERE chat_id = ?
            """,
            (delta, datetime.utcnow().isoformat(), chat_id),
        )

    def set_draft_flag(self, chat_id: int, field_name: str, value: bool) -> None:
        if field_name not in {"workout_done", "university_done"}:
            raise ValueError("Invalid draft flag")

        self.get_or_create_draft(chat_id)
        self.db.execute(
            f"""
            UPDATE checkin_draft
            SET {field_name} = ?, updated_at = ?
            WHERE chat_id = ?
            """,
            (1 if value else 0, datetime.utcnow().isoformat(), chat_id),
        )

    def reset_draft(self, chat_id: int) -> None:
        self.get_or_create_draft(chat_id)
        self.db.execute(
            """
            UPDATE checkin_draft
            SET ds_hours = 0,
                diploma_hours = 0,
                workout_done = 0,
                university_done = 0,
                notes = '',
                updated_at = ?
            WHERE chat_id = ?
            """,
            (datetime.utcnow().isoformat(), chat_id),
        )

    def delete_draft(self, chat_id: int) -> None:
        self.db.execute(
            "DELETE FROM checkin_draft WHERE chat_id = ?",
            (chat_id,),
        )