import random
from typing import Any, Dict
from telebot.types import Message, InputMediaPhoto
from loguru import logger

from loader import bot
from TelegramBot_Hotels.site_API.utils.site_api_handler import api_request
from TelegramBot_Hotels.database.common.models import db, Hotels
from TelegramBot_Hotels.tg_API.utils.ending_dialogue import final_question


def search_possible_hotels(data: Dict) -> Any:
    """
    Функция ищет варианты отелей в выбранном пользователем городе.
    Если пользователь выбрал команду '/lowprice', то формируется отсортированный список отелей по минимальной цене.
    Если пользователь выбрал команду '/highprice', то формируется отсортированный список отелей по максимальной цене.
    Если пользователь выбрал команду '/customlocation', то формируется отсортированный список отелей по удаленности
    от центра города.

    : param possible_hotels: dict
        список отелей
    : param low_price_hotels: dict
        отсортированный список отелей по минимальной цене
    : param high_price_hotels: dict
        отсортированный список отелей по максимальной цене
    : param distance_from_center: dict
        отсортированный список отелей по удаленности от центра города
    """
    logger.info('Отправляем запрос на сервер для поиска подходящих отелей')
    payload = {"currency": "USD",
               "eapid": 1,
               "locale": "en_US",
               "siteId": 300000001,
               "destination": {"regionId": data['city_id']},
               "checkInDate": {"day": int(data['date_of_entry'].day),
                               "month": int(data['date_of_entry'].month),
                               "year": int(data['date_of_entry'].year)},
               "checkOutDate": {"day": int(data['date_of_departure'].day),
                                "month": int(data['date_of_departure'].month),
                                "year": int(data['date_of_departure'].year)},
               "rooms": [{"adults": int(data['numbers_adults'])}],
               "resultsStartingIndex": 0,
               "resultsSize": int(data['numbers_hotels']),
               "sort": "PRICE_LOW_TO_HIGH",
               "filters": {"price": {"max": int(data['price_max']),
                                     "min": int(data['price_min'])}}}

    data_hotels = api_request(method_endswith='/properties/v2/list', params=payload, method_type='POST')
    logger.info(f'Ответ от сервера: {data_hotels}')
    possible_hotels = dict()
    for hotel in data_hotels['data']['propertySearch']['properties']:
        possible_hotels[hotel['id']] = {
            'name': hotel['name'],
            'distanceFromDestination': int(hotel['destinationInfo']['distanceFromDestination']['value']),
            'price': int(hotel['price']['lead']['amount'])}

    if data['input_command'] == '/lowprice':
        low_price_hotels = dict(sorted(possible_hotels.items(), key=lambda items: items[1]['price']))
        logger.info(f'Сформирован отсортированный список отелей по возрастанию стоимости проживания')
        return low_price_hotels

    elif data['input_command'] == '/highprice':
        high_price_hotels = dict(sorted(possible_hotels.items(), key=lambda items: items[1]['price'], reverse=True))
        logger.info(f'Сформирован отсортированный список отелей по снижению стоимости проживания')
        return high_price_hotels

    elif data['input_command'] == '/customlocation':
        distance_from_center = dict(sorted(possible_hotels.items(),
                                           key=lambda items: items[1]['distanceFromDestination']))
        logger.info(f'Сформирован отсортированный список отелей по увеличению удаленности от центра города')
        return distance_from_center


def hotels_options(message: Message, data: Dict) -> None:
    """
    Функция ищет и выдает пользователю информацию по отелям, пока их число не достигнет пользовательского значения.
    Далее спрашивает у пользователя, нужна ли ему ещё какая-либо помощь и выводит клавиатуру с ответами "Да" и "Нет".
    Если ответ "Да", то выводит команду 'help'.
    Если ответ "Нет" - то выводит прощальное сообщение.

    : param count: int
        количество отелей для вывода пользователю
    """
    bot.send_message(message.from_user.id, f'{message.from_user.full_name}, подбираем для Вас варианты отелей, '
                                           f'ожидайте... ')
    hotel_options = search_possible_hotels(data)
    count = 0
    for hotel, options in hotel_options.items():
        count += 1
        if count <= int(data['numbers_hotels']):
            logger.info(f'Отправляем запрос на сервер для поиска информации по отелю {options["name"]}')
            payload_hotel = {
                "currency": "USD",
                "eapid": 1,
                "locale": "en_US",
                "siteId": 300000001,
                "propertyId": hotel}

            data_hotel = api_request(method_endswith='/properties/v2/detail', params=payload_hotel,
                                     method_type='POST')
            logger.info(f'Ответ от сервера: {data_hotel}')
            hotel_data = {'id': data_hotel['data']['propertyInfo']['summary']['id'],
                          'name': data_hotel['data']['propertyInfo']['summary']['name'],
                          'address': data_hotel['data']['propertyInfo']['summary']['location']['address']
                          ['addressLine'],
                          'images': [url['image']['url'] for url in
                                     data_hotel['data']['propertyInfo']['propertyGallery']['images']]}

            hotel_info = f'\nНазвание отеля: {hotel_data["name"]}' \
                         f'\nАдрес отеля: {hotel_data["address"]}' \
                         f'\nРасстояние до центра города: ' \
                         f'{options["distanceFromDestination"]} mille' \
                         f'\nСтоимость проживания: {options["price"]} $' \

            list_of_urls = random.choices(hotel_data["images"], k=5)
            media_group = []    # создаём список мультимедиа
            for number, url in enumerate(list_of_urls):
                if number == 0:
                    media_group.append(InputMediaPhoto(media=url, caption=hotel_info))
                else:
                    media_group.append(InputMediaPhoto(media=url))
            bot.send_media_group(message.from_user.id, media_group)
            logger.info(f'Пользователю {message.from_user.full_name} (ID {message.from_user.id}) выводится найденная '
                        f'информация по отелю {options["name"]}')
            with db.atomic():
                Hotels.create(city_id=data["city_id"],
                              hotel_name=hotel_data["name"],
                              distance_from_destination=options["distanceFromDestination"],
                              hotel_price=options["price"],
                              hotel_address_line=hotel_data["address"],
                              hotel_images=','.join(list_of_urls))
    logger.info(f'Список отелей окончен.')
    bot.send_message(message.from_user.id, 'Это были все варианты отелей.')
    final_question(message)
