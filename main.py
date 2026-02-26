from loader import bot
from telebot import custom_filters

import tg_API.handlers   # noqa
from tg_API.utils.set_bot_commands import set_default_commands
from database.common.models import create_tables


if __name__ == '__main__':
    bot.add_custom_filter(custom_filters.StateFilter(bot))    # фильтрация по состояниям
    set_default_commands(bot)
    create_tables()
    bot.infinity_polling()
