import os
import time
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import caldav
from caldav.elements import dav, cdav
from dotenv import load_dotenv

from aiogram import Bot

load_dotenv()


@dataclass(frozen=True)
class Config:
    tg_token: str
    tg_chat_id: int
    caldav_url: str
    caldav_username: str
    caldav_password: str
    tz: ZoneInfo
    poll_seconds: int
    remind_minutes: int
    lookahead_hours: int


def load_config() -> Config:
    tz_name = os.getenv("TIMEZONE", "Asia/Yakutsk")
    return Config(
        tg_token=os.environ["TELEGRAM_BOT_TOKEN"],
        tg_chat_id=int(os.environ["TELEGRAM_CHAT_ID"]),
        caldav_url=os.environ["CALDAV_URL"],
        caldav_username=os.environ["CALDAV_USERNAME"],
        caldav_password=os.environ["CALDAV_PASSWORD"],
        tz=ZoneInfo(tz_name),
        poll_seconds=int(os.getenv("POLL_SECONDS", "30")),
        remind_minutes=int(os.getenv("REMIND_MINUTES", "10")),
        lookahead_hours=int(os.getenv("LOOKAHEAD_HOURS", "24")),
    )


class SentStore:
    """SQLite-хранилище, чтобы не отправлять дубликаты уведомлений."""
    def __init__(self, path: str = "sent.sqlite3"):
        self.conn = sqlite3.connect(path)
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sent (
                key TEXT PRIMARY KEY,
                sent_at TEXT NOT NULL
            )
            """
        )
        self.conn.commit()

    def was_sent(self, key: str) -> bool:
        cur = self.conn.execute("SELECT 1 FROM sent WHERE key=?", (key,))
        return cur.fetchone() is not None

    def mark_sent(self, key: str) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO sent(key, sent_at) VALUES(?, ?)",
            (key, datetime.utcnow().isoformat()),
        )
        self.conn.commit()


def connect_caldav(cfg: Config) -> caldav.DAVClient:
    return caldav.DAVClient(
        url=cfg.caldav_url,
        username=cfg.caldav_username,
        password=cfg.caldav_password,
    )


def get_primary_calendar(client: caldav.DAVClient) -> caldav.Calendar:
    principal = client.principal()
    calendars = principal.calendars()
    if not calendars:
        raise RuntimeError("CalDAV: calendars() вернул пусто — проверь доступ/URL/логин.")
    # Берём первый календарь как “основной”
    return calendars[0]


def fetch_events(cal: caldav.Calendar, start: datetime, end: datetime):
    # date_search работает по диапазону времени
    return cal.date_search(start=start, end=end)


def format_event_message(summary: str, start_dt: datetime, end_dt: datetime, kind: str) -> str:
    # kind: "soon" / "start"
    start_s = start_dt.strftime("%H:%M")
    end_s = end_dt.strftime("%H:%M")
    if kind == "soon":
        return f"⏰ Через 10 минут\n\n{summary}\n{start_s}–{end_s}"
    return f"✅ Старт\n\n{summary}\n{start_s}–{end_s}"


def normalize_dt(dt: datetime, tz: ZoneInfo) -> datetime:
    # caldav может отдавать aware dt, но на всякий случай приводим в нужную TZ
    if dt.tzinfo is None:
        return dt.replace(tzinfo=tz)
    return dt.astimezone(tz)


async def run_loop(cfg: Config):
    bot = Bot(token=cfg.tg_token)
    store = SentStore()

    client = connect_caldav(cfg)
    cal = get_primary_calendar(client)

    remind_delta = timedelta(minutes=cfg.remind_minutes)

    while True:
        now = datetime.now(cfg.tz)
        window_end = now + timedelta(hours=cfg.lookahead_hours)

        try:
            events = fetch_events(cal, start=now - timedelta(minutes=1), end=window_end)
        except Exception as e:
            # если CalDAV временно недоступен — не падаем
            await bot.send_message(cfg.tg_chat_id, f"⚠️ CalDAV ошибка: {e}")
            time.sleep(cfg.poll_seconds)
            continue

        for ev in events:
            try:
                ical = ev.vobject_instance
                vevent = ical.vevent

                summary = str(getattr(vevent, "summary").value) if hasattr(vevent, "summary") else "(Без названия)"
                dtstart = normalize_dt(vevent.dtstart.value, cfg.tz)
                dtend = normalize_dt(vevent.dtend.value, cfg.tz)

                # Два момента: за remind_minutes и в старт
                notify_times = [
                    ("soon", dtstart - remind_delta),
                    ("start", dtstart),
                ]

                for kind, t_notify in notify_times:
                    # округление по секундам, чтобы ключ был стабильным
                    key = f"{ev.url}::{kind}::{dtstart.strftime('%Y%m%dT%H%M')}"
                    if store.was_sent(key):
                        continue

                    # если время пришло (в пределах poll_seconds)
                    if now >= t_notify and now <= t_notify + timedelta(seconds=cfg.poll_seconds):
                        msg = format_event_message(summary, dtstart, dtend, kind)
                        await bot.send_message(cfg.tg_chat_id, msg)
                        store.mark_sent(key)

            except Exception:
                # пропускаем битые события, но не валим весь цикл
                continue

        time.sleep(cfg.poll_seconds)


if __name__ == "__main__":
    import asyncio
    cfg = load_config()
    asyncio.run(run_loop(cfg))