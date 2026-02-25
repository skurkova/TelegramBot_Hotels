from telebot.types import Message, InputMediaPhoto
from loguru import logger

from loader import bot
import TelegramBot_Hotels.tg_API.utils.input_information   # noqa
from TelegramBot_Hotels.database.common.models import db, Hotels
from TelegramBot_Hotels.tg_API.utils.ending_dialogue import final_question


@bot.message_handler(commands=['history'])
def get_history(message: Message) -> None:
    """
    Функция реагирует на команду 'history' и выдаёт историю поиска отелей.
    """
    bot.send_message(message.from_user.id, 'История поиска отелей: \n')
    with db.atomic():
        count = 0
        for hotels in reversed(Hotels.select()):
            count += 1
            if count <= 10:
                hotel_info = f'\nНазвание отеля: {hotels.hotel_name}'\
                             f'\nАдрес отеля: {hotels.hotel_address_line}'\
                             f'\nРасстояние до центра города: {hotels.distance_from_destination} mille'\
                             f'\nСтоимость проживания: {hotels.hotel_price} $'
                media = []
                for number, url in enumerate(hotels.hotel_images.split(",")):
                    if number == 0:
                        media.append(InputMediaPhoto(media=url, caption=hotel_info))
                    else:
                        media.append(InputMediaPhoto(media=url))
                bot.send_media_group(message.from_user.id, media)
        if count == 0:
            bot.send_message(message.from_user.id, 'К сожалению, история поиска пуста...')
    logger.info(f'Пользователю {message.from_user.full_name} (ID {message.from_user.id}) выводится история '
                f'поиска отелей')
    final_question(message)
