from telebot.types import Message
from loguru import logger

from loader import bot


@bot.message_handler(commands=['help'])
def help_message(message: Message) -> None:
    """
    Функция выводит информационное сообщение о возможностях бота при нажатии команды 'help'
    """
    logger.info(f'Выполняется команда: /help - Пользователь {message.from_user.full_name} '
                f'(ID {message.from_user.id})')
    bot.send_message(message.from_user.id, '\nБОТ-помощник поможет Вам подобрать: '
                                           '\n'
                                           '\n/lowprice - Самые дешёвые отели'
                                           '\n/highprice - Самые дорогие отели'
                                           '\n/customlocation - Наиболее подходящие отели по расположению от центра '
                                           'города'
                                           '\n/history - История поиска отелей'
                                           '\n'
                                           '\nДля начала нажмите /start')
