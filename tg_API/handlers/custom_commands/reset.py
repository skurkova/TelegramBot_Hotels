from telebot.types import Message
from loguru import logger

from loader import bot


@bot.message_handler(commands=['reset'])
def reset(message: Message) -> None:
    """
    Функция сбрасывает состояния, возвращаясь к началу диалога
    """
    bot.delete_state(message.from_user.id, message.chat.id)
    bot.send_message(message.from_user.id, 'Итак, начнем с начала'
                                           '\n'
                                           '\nПожалуйста, выберете интересующий Вас запрос: '
                                           '\n/lowprice - Самые дешёвые отели'
                                           '\n/highprice - Самые дорогие отели'
                                           '\n/customlocation - Наиболее подходящие отели по расположению от центра '
                                           'города'
                                           '\n/history - История поиска отелей')
    logger.info(f'Выполняется команда: /reset - Пользователь {message.from_user.full_name} '
                f'(ID {message.from_user.id})')
