import asyncio
from datetime import datetime, timedelta

from aiogram import Bot

from app.container import container


def format_notification(kind: str, summary: str, start_dt: datetime, end_dt: datetime) -> str:
    remind_minutes = container.config.remind_minutes

    if kind == "soon":
        return (
            f"⏰ Через {remind_minutes} минут\n\n"
            f"{summary}\n"
            f"{start_dt.strftime('%H:%M')}–{end_dt.strftime('%H:%M')}"
        )

    return (
        "✅ Старт\n\n"
        f"{summary}\n"
        f"{start_dt.strftime('%H:%M')}–{end_dt.strftime('%H:%M')}"
    )


async def run_caldav_poller(bot: Bot) -> None:
    cfg = container.config
    users_repo = container.users_repo
    notifications_repo = container.notifications_repo
    caldav_service = container.caldav_service

    remind_delta = timedelta(minutes=cfg.remind_minutes)

    while True:
        try:
            now = datetime.now(cfg.timezone)
            end = now + timedelta(hours=cfg.lookahead_hours)

            events = caldav_service.get_events_in_range(
                start_dt=now - timedelta(minutes=1),
                end_dt=end,
            )

            for event in events:
                notify_points = [
                    ("soon", event["start"] - remind_delta),
                    ("start", event["start"]),
                ]

                for kind, notify_at in notify_points:
                    dedupe_key = f"{event['url']}::{kind}::{event['start'].strftime('%Y%m%dT%H%M')}"

                    if notifications_repo.was_sent(dedupe_key):
                        continue

                    if now >= notify_at and now <= notify_at + timedelta(seconds=cfg.poll_seconds):
                        text = format_notification(
                            kind=kind,
                            summary=event["summary"],
                            start_dt=event["start"],
                            end_dt=event["end"],
                        )

                        for chat_id in users_repo.get_enabled_chat_ids():
                            try:
                                await bot.send_message(chat_id=chat_id, text=text)
                            except Exception as send_error:
                                print(f"Telegram send error to {chat_id}: {send_error}")

                        notifications_repo.mark_sent(dedupe_key)

        except Exception as e:
            print(f"CalDAV poller error: {e}")

        await asyncio.sleep(cfg.poll_seconds)