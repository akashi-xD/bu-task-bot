from datetime import datetime, time, timedelta

import caldav

from app.container import container


class CaldavService:
    def __init__(self) -> None:
        self.cfg = container.config

    def connect(self) -> caldav.DAVClient:
        return caldav.DAVClient(
            url=self.cfg.caldav_url,
            username=self.cfg.caldav_username,
            password=self.cfg.caldav_password,
        )

    def calendar_display_name(self, cal) -> str:
        name = getattr(cal, "name", None)
        if isinstance(name, str) and name.strip():
            return name.strip()

        get_name = getattr(cal, "get_display_name", None)
        if callable(get_name):
            try:
                value = get_name()
                if isinstance(value, str) and value.strip():
                    return value.strip()
            except Exception:
                pass

        url = getattr(cal, "url", None)
        return str(url) if url else "(unknown)"

    def list_calendars(self) -> list[str]:
        client = self.connect()
        principal = client.principal()
        calendars = principal.calendars()
        return [self.calendar_display_name(cal) for cal in calendars]

    def get_calendar(self):
        client = self.connect()
        principal = client.principal()
        calendars = principal.calendars()

        wanted = self.cfg.calendar_name.casefold()
        available = []

        for cal in calendars:
            name = self.calendar_display_name(cal)
            available.append(name)
            if name.casefold() == wanted:
                return cal

        raise RuntimeError(
            f"Calendar not found: {self.cfg.calendar_name!r}. Available: {available}"
        )

    def normalize_dt(self, dt: datetime) -> datetime:
        if dt.tzinfo is None:
            return dt.replace(tzinfo=self.cfg.timezone)
        return dt.astimezone(self.cfg.timezone)

    def _event_to_dict(self, ev) -> dict:
        vevent = ev.vobject_instance.vevent
        summary = (
            str(vevent.summary.value)
            if hasattr(vevent, "summary")
            else "(Без названия)"
        )
        dtstart = self.normalize_dt(vevent.dtstart.value)
        dtend = self.normalize_dt(vevent.dtend.value)
        return {
            "summary": summary,
            "start": dtstart,
            "end": dtend,
            "url": str(getattr(ev, "url", "")),
        }

    def get_events_in_range(self, start_dt: datetime, end_dt: datetime) -> list[dict]:
        calendar = self.get_calendar()
        events = calendar.date_search(start=start_dt, end=end_dt)

        items = []
        for ev in events:
            try:
                items.append(self._event_to_dict(ev))
            except Exception:
                continue

        items.sort(key=lambda x: x["start"])
        return items

    def get_today_events(self) -> list[dict]:
        now = datetime.now(self.cfg.timezone)
        day_start = datetime.combine(now.date(), time(0, 0), tzinfo=self.cfg.timezone)
        day_end = day_start + timedelta(days=1)
        return self.get_events_in_range(day_start, day_end)

    def get_next_event(self) -> dict | None:
        now = datetime.now(self.cfg.timezone)
        end = now + timedelta(hours=self.cfg.lookahead_hours)
        events = self.get_events_in_range(now, end)

        for event in events:
            if event["start"] >= now:
                return event
        return None