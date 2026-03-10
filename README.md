![Python](https://img.shields.io/badge/python-3.11-blue)
![Docker](https://img.shields.io/badge/docker-ready-blue)
![Telegram](https://img.shields.io/badge/telegram-bot-blue)
![License](https://img.shields.io/badge/license-MIT-green)

# BU! Productivity Assistant

![Python](https://img.shields.io/badge/python-3.11-blue)
![Docker](https://img.shields.io/badge/docker-ready-blue)
![Telegram](https://img.shields.io/badge/telegram-bot-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A Telegram productivity assistant that integrates with CalDAV calendars and tracks daily self-development progress using a gamified XP system.

The bot sends calendar notifications, tracks learning progress and helps maintain productive routines.

---

# Features

### Calendar Integration

- CalDAV support (Yandex, Nextcloud, etc.)
- event reminders
- upcoming event lookup
- daily schedule overview

Commands:
/today
/next
/calendars

---

### Productivity Tracking

Interactive daily check-in system.

Command:
/done

Opens inline keyboard:

DS +1h
DS +2h

Diploma +1h
Diploma +2h

Workout
University tasks


Progress converts into **XP points** and increases your level.

---

### Statistics

Commands:
/stats
/level


Displays:

- learning hours
- diploma progress
- workouts
- XP
- level

---

# Example Notification
⏰ In 10 minutes

Deep Work Data Science
08:00–10:30


---

# Architecture

Project structure:
app
├ bot
│ ├ handlers
│ ├ keyboards
│ └ routers
├ db
├ repositories
├ services
├ jobs
└ main.py


### Layers

**handlers**

Telegram commands

**services**

Business logic (CalDAV integration, XP system)

**repositories**

Database access layer

**jobs**

Background tasks (calendar polling)

---

# Tech Stack

- Python 3.11
- aiogram v3
- CalDAV
- SQLite
- Docker
- Telegram Bot API

---

# Installation

Clone repository:
git clone https://github.com/akashi-xD/bu-task-bot.git
cd bu-task-bot


Create `.env` file:
TELEGRAM_BOT_TOKEN=
CALDAV_URL=https://caldav.yandex.ru
CALDAV_USERNAME=
CALDAV_PASSWORD=
CALENDAR_NAME=
TIMEZONE=Asia/Yakutsk
POLL_SECONDS=30
REMIND_MINUTES=10
LOOKAHEAD_HOURS=24
DB_PATH=/app/data/bot.sqlite3


Run with Docker:
docker compose up --build -d
Check logs:
docker compose logs -f

---

# Development

Run locally:
python -m app.main

---

# Roadmap

Planned features:

- daily productivity reminder
- weekly productivity report
- streak tracking
- analytics dashboard
