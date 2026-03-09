from datetime import date

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from app.bot.keyboards.checkin import build_checkin_keyboard
from app.container import container
from app.services.xp_service import calculate_level, calculate_xp

router = Router()


def _draft_to_text(draft) -> str:
    return (
        "📊 Чек-ин за день\n\n"
        f"DS: {draft['ds_hours']} ч\n"
        f"Диплом: {draft['diploma_hours']} ч\n"
        f"Тренировка: {'да' if draft['workout_done'] else 'нет'}\n"
        f"СРС/ДЗ: {'да' if draft['university_done'] else 'нет'}\n\n"
        "Нажимай кнопки ниже:"
    )


def parse_done_command(text: str) -> dict:
    result = {
        "ds": 0.0,
        "diploma": 0.0,
        "workout": False,
        "uni": False,
        "notes": "",
    }

    parts = text.split()
    for part in parts[1:]:
        if "=" not in part:
            continue
        key, value = part.split("=", 1)
        key = key.strip().lower()
        value = value.strip()

        if key == "ds":
            result["ds"] = float(value)
        elif key == "diploma":
            result["diploma"] = float(value)
        elif key == "workout":
            result["workout"] = value in {"1", "true", "yes", "да"}
        elif key == "uni":
            result["uni"] = value in {"1", "true", "yes", "да"}
        elif key == "notes":
            result["notes"] = value

    return result


@router.message(Command("done"))
async def done_handler(message: Message) -> None:
    text = message.text or "/done"

    # Старый режим остаётся: /done ds=2 diploma=1 workout=1 uni=1
    if "=" in text:
        try:
            parsed = parse_done_command(text)

            xp = calculate_xp(
                ds_hours=parsed["ds"],
                diploma_hours=parsed["diploma"],
                workout_done=parsed["workout"],
                university_done=parsed["uni"],
            )

            container.progress_repo.save_progress(
                chat_id=message.chat.id,
                log_date=date.today(),
                ds_hours=parsed["ds"],
                diploma_hours=parsed["diploma"],
                workout_done=parsed["workout"],
                university_done=parsed["uni"],
                notes=parsed["notes"],
                xp_earned=xp,
            )

            container.progress_repo.add_xp(message.chat.id, xp)
            stats = container.progress_repo.get_user_stats(message.chat.id)
            total_xp = int(stats["total_xp"])
            new_level = calculate_level(total_xp)
            container.progress_repo.set_level(message.chat.id, new_level)

            await message.answer(
                "Прогресс сохранён.\n\n"
                f"DS: {parsed['ds']} ч\n"
                f"Диплом: {parsed['diploma']} ч\n"
                f"Тренировка: {'да' if parsed['workout'] else 'нет'}\n"
                f"СРС/ДЗ: {'да' if parsed['uni'] else 'нет'}\n"
                f"XP: +{xp}\n"
                f"Уровень: {new_level}"
            )
            return
        except Exception as e:
            await message.answer(f"Ошибка сохранения: {e}")
            return

    # Новый режим: интерактивный check-in
    draft = container.progress_repo.get_or_create_draft(message.chat.id)
    await message.answer(
        _draft_to_text(draft),
        reply_markup=build_checkin_keyboard(),
    )


@router.callback_query(lambda c: c.data and c.data.startswith("checkin:"))
async def checkin_callback_handler(callback: CallbackQuery) -> None:
    if callback.message is None or callback.data is None:
        await callback.answer()
        return

    _, action, value = callback.data.split(":", 2)
    chat_id = callback.message.chat.id

    if action == "ds":
        container.progress_repo.update_draft_hours(chat_id, "ds_hours", float(value))
    elif action == "diploma":
        container.progress_repo.update_draft_hours(chat_id, "diploma_hours", float(value))
    elif action == "workout":
        draft = container.progress_repo.get_or_create_draft(chat_id)
        new_value = not bool(draft["workout_done"])
        container.progress_repo.set_draft_flag(chat_id, "workout_done", new_value)
    elif action == "uni":
        draft = container.progress_repo.get_or_create_draft(chat_id)
        new_value = not bool(draft["university_done"])
        container.progress_repo.set_draft_flag(chat_id, "university_done", new_value)
    elif action == "reset":
        container.progress_repo.reset_draft(chat_id)
    elif action == "save":
        draft = container.progress_repo.get_or_create_draft(chat_id)

        xp = calculate_xp(
            ds_hours=float(draft["ds_hours"]),
            diploma_hours=float(draft["diploma_hours"]),
            workout_done=bool(draft["workout_done"]),
            university_done=bool(draft["university_done"]),
        )

        container.progress_repo.save_progress(
            chat_id=chat_id,
            log_date=date.today(),
            ds_hours=float(draft["ds_hours"]),
            diploma_hours=float(draft["diploma_hours"]),
            workout_done=bool(draft["workout_done"]),
            university_done=bool(draft["university_done"]),
            notes=draft["notes"] or "",
            xp_earned=xp,
        )

        container.progress_repo.add_xp(chat_id, xp)
        stats = container.progress_repo.get_user_stats(chat_id)
        total_xp = int(stats["total_xp"])
        new_level = calculate_level(total_xp)
        container.progress_repo.set_level(chat_id, new_level)
        container.progress_repo.delete_draft(chat_id)

        await callback.message.edit_text(
            "✅ Прогресс сохранён.\n\n"
            f"DS: {draft['ds_hours']} ч\n"
            f"Диплом: {draft['diploma_hours']} ч\n"
            f"Тренировка: {'да' if draft['workout_done'] else 'нет'}\n"
            f"СРС/ДЗ: {'да' if draft['university_done'] else 'нет'}\n"
            f"XP: +{xp}\n"
            f"Уровень: {new_level}"
        )
        await callback.answer("Сохранено")
        return

    draft = container.progress_repo.get_or_create_draft(chat_id)
    await callback.message.edit_text(
        _draft_to_text(draft),
        reply_markup=build_checkin_keyboard(),
    )
    await callback.answer()


@router.message(Command("stats"))
async def stats_handler(message: Message) -> None:
    stats = container.progress_repo.get_last_7_days_stats(message.chat.id)
    user_stats = container.progress_repo.get_user_stats(message.chat.id)

    if user_stats is None:
        await message.answer("Статистика пока пустая.")
        return

    text = (
        "📊 За последние 7 дней:\n\n"
        f"DS: {stats['ds_hours']} ч\n"
        f"Диплом: {stats['diploma_hours']} ч\n"
        f"Тренировки: {stats['workouts']}\n"
        f"СРС/ДЗ: {stats['university_done']}\n"
        f"XP за 7 дней: {stats['xp_earned']}\n\n"
        f"Всего XP: {user_stats['total_xp']}\n"
        f"Уровень: {user_stats['level']}"
    )
    await message.answer(text)


@router.message(Command("level"))
async def level_handler(message: Message) -> None:
    stats = container.progress_repo.get_user_stats(message.chat.id)
    if stats is None:
        await message.answer("Уровень пока не найден. Сначала напиши /start.")
        return

    await message.answer(
        f"Твой уровень: {stats['level']}\n"
        f"Всего XP: {stats['total_xp']}"
    )