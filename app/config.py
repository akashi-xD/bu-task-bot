from dataclasses import dataclass
from zoneinfo import ZoneInfo
import os

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Config:
    telegram_bot_token: str
    caldav_url: str
    caldav_username: str
    caldav_password: str
    calendar_name: str
    timezone: ZoneInfo
    poll_seconds: int
    remind_minutes: int
    lookahead_hours: int
    db_path: str


def load_config() -> Config:
    return Config(
        telegram_bot_token=os.environ["TELEGRAM_BOT_TOKEN"].strip(),
        caldav_url=os.environ["CALDAV_URL"].strip(),
        caldav_username=os.environ["CALDAV_USERNAME"].strip(),
        caldav_password=os.environ["CALDAV_PASSWORD"].strip(),
        calendar_name=os.environ["CALENDAR_NAME"].strip(),
        timezone=ZoneInfo(os.getenv("TIMEZONE", "Asia/Yakutsk")),
        poll_seconds=int(os.getenv("POLL_SECONDS", "30")),
        remind_minutes=int(os.getenv("REMIND_MINUTES", "10")),
        lookahead_hours=int(os.getenv("LOOKAHEAD_HOURS", "24")),
        db_path=os.getenv("DB_PATH", "/app/data/bot.sqlite3").strip(),
    )