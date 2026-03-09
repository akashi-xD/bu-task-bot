from datetime import datetime

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.container import container

router = Router()


@router.message(Command("calendars"))
async def calendars_handler(message: Message) -> None:
    try:
        items = container.caldav_service.list_calendars()
        if not items:
            await message.answer("Календари не найдены.")
            return
        text = "Доступные календари:\n" + "\n".join(f"- {item}" for item in items)
        await message.answer(text)
    except Exception as e:
        await message.answer(f"Ошибка CalDAV: {e}")


@router.message(Command("today"))
async def today_handler(message: Message) -> None:
    try:
        events = container.caldav_service.get_today_events()
        if not events:
            await message.answer("На сегодня событий нет.")
            return

        lines = ["📅 Сегодня:"]
        for event in events:
            lines.append(
                f"{event['start'].strftime('%H:%M')}–{event['end'].strftime('%H:%M')} — {event['summary']}"
            )

        await message.answer("\n".join(lines))
    except Exception as e:
        await message.answer(f"Ошибка: {e}")


@router.message(Command("next"))
async def next_handler(message: Message) -> None:
    try:
        event = container.caldav_service.get_next_event()
        if event is None:
            await message.answer("Ближайших событий не найдено.")
            return

        now = datetime.now(container.config.timezone)
        delta = event["start"] - now
        minutes = max(int(delta.total_seconds() // 60), 0)

        text = (
            "⏭ Следующее событие:\n\n"
            f"{event['summary']}\n"
            f"{event['start'].strftime('%H:%M')}–{event['end'].strftime('%H:%M')}\n"
            f"Через {minutes} мин."
        )
        await message.answer(text)
    except Exception as e:
        await message.answer(f"Ошибка: {e}")