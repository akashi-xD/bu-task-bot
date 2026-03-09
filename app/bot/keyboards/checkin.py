from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def build_checkin_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="DS +1ч", callback_data="checkin:ds:1"),
                InlineKeyboardButton(text="DS +2ч", callback_data="checkin:ds:2"),
            ],
            [
                InlineKeyboardButton(text="Диплом +1ч", callback_data="checkin:diploma:1"),
                InlineKeyboardButton(text="Диплом +2ч", callback_data="checkin:diploma:2"),
            ],
            [
                InlineKeyboardButton(text="Тренировка ✅", callback_data="checkin:workout:1"),
                InlineKeyboardButton(text="СРС/ДЗ ✅", callback_data="checkin:uni:1"),
            ],
            [
                InlineKeyboardButton(text="Сбросить", callback_data="checkin:reset:0"),
                InlineKeyboardButton(text="Готово", callback_data="checkin:save:0"),
            ],
        ]
    )