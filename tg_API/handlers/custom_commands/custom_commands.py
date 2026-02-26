from telebot.types import Message
from loguru import logger

from loader import bot
from tg_API.states.user_data import UserInputInfo
import tg_API.utils.input_information   # noqa


@bot.message_handler(commands=['lowprice', 'highprice', 'customlocation'])
def custom_commands(message: Message) -> None:
    """
    Функция реагирует на команду, присваивает пользователю состояние и запрашивает название города для поиска.
    """
    bot.delete_state(message.from_user.id, message.chat.id)
    logger.info(f'Пользователь {message.from_user.full_name} (ID {message.from_user.id}) выбрал команду {message.text}')
    bot.set_state(message.from_user.id, UserInputInfo.input_city, message.chat.id)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data['input_command'] = message.text
    if message.text == '/lowprice':
        bot.send_message(message.from_user.id, 'Ищем самые дешёвые отели.'
                                               '\nВведите город, в котором хотели бы остановиться (латиницей): ')
    elif message.text == '/highprice':
        bot.send_message(message.from_user.id, 'Ищем самые дорогие отели.'
                                               '\nВведите город, в котором хотели бы остановиться (латиницей): ')
    elif message.text == '/customlocation':
        bot.send_message(message.from_user.id, 'Ищем наиболее подходящие отели по расположению от центра города.'
                                               '\nВведите город, в котором хотели бы остановиться (латиницей): ')
