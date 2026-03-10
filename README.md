![Python](https://img.shields.io/badge/python-3.11-blue)
![Docker](https://img.shields.io/badge/docker-ready-blue)
![Telegram](https://img.shields.io/badge/telegram-bot-blue)
![License](https://img.shields.io/badge/license-MIT-green)
BU! Telegram Productivity Assistant

Telegram-бот для управления расписанием, уведомлений из календаря и трекинга саморазвития.

Бот интегрируется с CalDAV (например, Яндекс.Календарь) и отправляет уведомления о событиях, а также позволяет отслеживать ежедневный прогресс (учёба, диплом, тренировки) и получать XP.

Возможности
Календарь

уведомления о событиях из CalDAV

напоминания перед началом события

просмотр событий на сегодня

Команды:

/today
/next
/calendars
Управление уведомлениями
/start
/on
/off
/status
Трекинг прогресса

Бот позволяет отслеживать ежедневный прогресс.

Через команду:

/done

открывается интерактивный чек-ин с кнопками:

DS +1ч / +2ч

Диплом +1ч / +2ч

Тренировка

СРС / ДЗ

После сохранения бот начисляет XP.

Статистика
/stats
/level

Показывает:

часы обучения

часы работы над дипломом

количество тренировок

XP

уровень

Пример уведомления
⏰ Через 10 минут

Deep Work Data Science
08:00–10:30
Архитектура проекта

Проект построен по принципам разделения слоев:

app
 ├ bot
 │  ├ handlers
 │  ├ keyboards
 │  └ routers
 ├ db
 ├ repositories
 ├ services
 ├ jobs
 └ main.py
Основные компоненты

handlers
Telegram команды

services
бизнес-логика (CalDAV, XP)

repositories
работа с базой данных

jobs
фоновые процессы (poller календаря)

db
инициализация SQLite

Используемые технологии

Python 3.11

aiogram 3

CalDAV

SQLite

Docker

Telegram Bot API
