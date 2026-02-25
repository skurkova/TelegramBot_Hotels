from telebot.types import Message
from loguru import logger

from loader import bot


@bot.message_handler(func=lambda message: True, state=None)
def bot_echo(message: Message) -> None:
    """
    Функция выводит информационное сообщение, если статус запроса пользователя не определен.
    """
    logger.info(f'Сработал ЭХО на ввод "{message.text}" Пользователем {message.from_user.full_name} '
                f'(ID {message.from_user.id})')
    bot.reply_to(message, 'Я не понимаю ваш запрос...'
                          '\n'
                          '\nПожалуйста, повторите ввод или выберете команду /help')
    