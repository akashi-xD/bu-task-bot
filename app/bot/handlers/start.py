from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from app.container import container

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    container.users_repo.upsert_user(
        chat_id=message.chat.id,
        username=message.from_user.username if message.from_user else None,
        full_name=message.from_user.full_name if message.from_user else "Unknown",
    )
    await message.answer(
        "Готово. Я сохранил этот чат.\n\n"
        "Команды:\n"
        "/on\n"
        "/off\n"
        "/status\n"
        "/chatid\n"
        "/calendars\n"
        "/today\n"
        "/next\n"
        "/done\n"
        "/stats\n"
        "/level"
    )


@router.message(Command("on"))
async def on_handler(message: Message) -> None:
    container.users_repo.upsert_user(
        chat_id=message.chat.id,
        username=message.from_user.username if message.from_user else None,
        full_name=message.from_user.full_name if message.from_user else "Unknown",
    )
    container.users_repo.set_enabled(message.chat.id, True)
    await message.answer("Уведомления включены.")


@router.message(Command("off"))
async def off_handler(message: Message) -> None:
    container.users_repo.set_enabled(message.chat.id, False)
    await message.answer("Уведомления выключены.")


@router.message(Command("status"))
async def status_handler(message: Message) -> None:
    enabled = container.users_repo.is_enabled(message.chat.id)
    text = "включены" if enabled else "выключены"
    await message.answer(f"Уведомления для этого чата: {text}.")


@router.message(Command("chatid"))
async def chatid_handler(message: Message) -> None:
    await message.answer(f"chat_id: {message.chat.id}")