import asyncio

from aiogram import Bot, Dispatcher

from app.bot.routers import setup_routers
from app.config import load_config
from app.container import container
from app.db.database import Database
from app.jobs.caldav_poller import run_caldav_poller
from app.repositories.notifications_repo import NotificationsRepository
from app.repositories.progress_repo import ProgressRepository
from app.repositories.users_repo import UsersRepository
from app.services.caldav_service import CaldavService

import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

async def main() -> None:
    cfg = load_config()

    db = Database(cfg.db_path)
    db.init_schema()

    container.config = cfg
    container.db = db
    container.users_repo = UsersRepository(db)
    container.notifications_repo = NotificationsRepository(db)
    container.progress_repo = ProgressRepository(db)
    container.caldav_service = CaldavService()

    bot = Bot(token=cfg.telegram_bot_token)
    dp = Dispatcher()
    dp.include_router(setup_routers())

    await asyncio.gather(
        dp.start_polling(bot),
        run_caldav_poller(bot),
    )


if __name__ == "__main__":
    asyncio.run(main())