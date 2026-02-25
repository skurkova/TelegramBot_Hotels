from telebot.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from loguru import logger

from TelegramBot_Hotels.site_API.utils.site_api_handler import api_request


def destination_id(message: Message) -> list:
    """
    Функция ищет возможные варианты пункта назначения на основе ввода пользователя

    : param possible_cities: list
        список возможных вариантов пункта назначения
    : return: list
    """
    logger.info('Отправляем запрос на сервер для поиска подходящих пунктов назначения')
    querystring = {"q": message.text, "locale": "en_US", "langid": "1033", "siteid": "300000001"}
    data_cities = api_request(method_endswith='/locations/v3/search', params=querystring, method_type='GET')
    logger.info(f'Ответ от сервера: {data_cities}')
    possible_cities = list()
    for i in data_cities['sr']:
        if i['type'] in ['CITY', 'NEIGHBORHOOD']:
            possible_cities.append({'destinationID': i['gaiaId'], 'fullCityName': i['regionNames']['fullName']})
    if len(possible_cities) != 0:
        return possible_cities


def cities_buttons(cities) -> InlineKeyboardMarkup:
    """
    Функция создает кнопки вариантов пункта назначения

    : param cities: list
        список возможных вариантов пункта назначения
    : return: InlineKeyboardMarkup
    """
    keyboard_cities = InlineKeyboardMarkup()
    for city in cities:
        keyboard_cities.add(InlineKeyboardButton(text=city['fullCityName'], callback_data=city['destinationID']))
    return keyboard_cities
