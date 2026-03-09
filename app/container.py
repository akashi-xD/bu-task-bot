from dataclasses import dataclass

from app.config import Config


@dataclass
class AppContainer:
    config: Config | None = None
    db: object | None = None
    users_repo: object | None = None
    notifications_repo: object | None = None
    progress_repo: object | None = None
    caldav_service: object | None = None


container = AppContainer()