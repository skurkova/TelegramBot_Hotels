from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def calling_buttons_yes_no() -> InlineKeyboardMarkup:
    """
    Функция создает кнопки вариантов 'Да' и 'Нет'

    : return: InlineKeyboardMarkup
    """
    buttons = {'Да': 'Да', 'Нет': 'Нет'}
    keyboard_YesNo = InlineKeyboardMarkup()
    for key, value in buttons.items():
        keyboard_YesNo.add(InlineKeyboardButton(text=key, callback_data=value))
    return keyboard_YesNo

