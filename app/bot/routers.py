from aiogram import Router

from app.bot.handlers.start import router as start_router
from app.bot.handlers.calendar import router as calendar_router
from app.bot.handlers.progress import router as progress_router


def setup_routers() -> Router:
    root = Router()
    root.include_router(start_router)
    root.include_router(calendar_router)
    root.include_router(progress_router)
    return root