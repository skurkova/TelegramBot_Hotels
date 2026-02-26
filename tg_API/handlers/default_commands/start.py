from telebot.types import Message
from loguru import logger

from loader import bot
from database.common.models import db, User


@bot.message_handler(commands=['start'])
@bot.message_handler(func=lambda message: message.text.title() == 'Привет')
def start_message(message: Message) -> None:
    """
    Функция выводит приветственное сообщение пользователю при выборе команды 'start' или, если пользователь вводит
    слово 'Привет'
    """
    bot.send_message(message.from_user.id, f'\nЗдравствуйте, {message.from_user.full_name}!'
                                           '\nПриятно познакомиться! '
                                           '\n'
                                           '\nВас приветствует БОТ-помощник компании HotelsTravel!'
                                           '\nЯ помогу Вам подобрать лучшиий отель в городе.'
                                           '\n'
                                           '\nПожалуйста, выберете интересующий Вас запрос: '
                                           '\n/lowprice - Самые дешёвые отели'
                                           '\n/highprice - Самые дорогие отели'
                                           '\n/customlocation - Наиболее подходящие отели по расположению от центра '
                                           'города'
                                           '\n/history - История поиска отелей')
    logger.info(f'Выполняется команда: /start - Пользователь {message.from_user.full_name} '
                f'(ID {message.from_user.id})')
    with db.atomic():
        if not User.select(User.user_id):
            User.create(user_id=message.from_user.id, user_full_name=message.from_user.full_name)
            logger.info(f'Регистрация нового пользователя: ID {message.from_user.id} - {message.from_user.full_name}')
