from telebot.types import Message, CallbackQuery
from telegram_bot_calendar import DetailedTelegramCalendar
from loguru import logger
import re
import datetime

from loader import bot
from TelegramBot_Hotels.tg_API.states.user_data import UserInputInfo
from TelegramBot_Hotels.tg_API.utils.search_destination_id import destination_id, cities_buttons
from TelegramBot_Hotels.database.common.models import db, Cities
from TelegramBot_Hotels.tg_API.utils.search_hotel import hotels_options

LSTEP_RU: dict[str, str] = {'y': 'год', 'm': 'месяц', 'd': 'день'}


@bot.message_handler(state=UserInputInfo.input_city)
def city_search(message: Message) -> None:
    """
    Функция "ловит" состояние пользователя, вызывает функцию, создающую кнопки вариантов пункта назначения
     и выводит их пользователю
    """
    logger.info(f'Пользователь {message.from_user.full_name} (ID {message.from_user.id}) ввёл город: {message.text}')
    if re.search(r'^[a-zA-Z]+$', message.text) or re.search(r'^[a-zA-Z]+[\s\S][a-zA-Z]+$', message.text):
        possible_cities = destination_id(message)
        if possible_cities:
            bot.send_message(message.from_user.id, 'Пожалуйста, уточните город: ',
                             reply_markup=cities_buttons(possible_cities))
            logger.info(f'Пользователю {message.from_user.full_name} (ID {message.from_user.id}) выводятся кнопки с '
                        f'возможными пунктами назначения')
            bot.set_state(message.from_user.id, UserInputInfo.city_id, message.chat.id)
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['input_city'] = message.text.title()
        else:
            logger.info('Запрос пуст! Пункт назначения с таким названием не найден!')
            bot.send_message(message.from_user.id, 'Пункт назначения с таким названием не найден!'
                                                   '\nПовторите, пожалуйста, ввод города, в котором хотели бы '
                                                   'остановиться латиницей: ')
    else:
        logger.info(f'Пользователь {message.from_user.full_name} (ID {message.from_user.id}) ошибся при вводе названия '
                    f'города: {message.text}')
        bot.send_message(message.from_user.id, 'Ошибка ввода!'
                                               '\nПовторите, пожалуйста, ввод города, в котором хотели бы остановиться '
                                               'латиницей: ')


@bot.callback_query_handler(func=lambda call: call.data.isdigit())
def callback_city_search(call: CallbackQuery) -> None:
    """
    Функция ловит callback кнопки и запоминает выбранный пользователем вариант пункта назначения.
    Запрашивает дату заезда в отель.
    """
    if call.data:
        bot.send_message(call.message.chat.id, f'Пункт назначения выбран: ID - {call.data}.')
        logger.info(f'Пункт назначения выбран: ID - {call.data}')
        with bot.retrieve_data(call.message.chat.id) as data:
            data['city_id'] = call.data
            with db.atomic():
                Cities.create(user=call.from_user.id, city_name=data['input_city'], city_id=call.data)
        bot.delete_message(call.message.chat.id, call.message.message_id)  # удаляем сообщение с кнопками
        bot.send_message(call.message.chat.id, 'Пожалуйста, выберете желаемую дату заезда в отель.')
        run_calendar_date_of_entry(call.message)


def run_calendar_date_of_entry(message: Message) -> None:
    """
    Функция, формирующая инлайн-календарь даты заезда в отель.
    """
    calendar, step = DetailedTelegramCalendar(calendar_id=1, locale='ru', min_date=datetime.date.today()).build()
    bot.send_message(message.chat.id, f'Пожалуйста, выберите {LSTEP_RU[step]}', reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=1))
def get_date_of_entry(call: CallbackQuery) -> None:
    """
    Функция проверяет актуальность выбранной даты заезда в отель.
    В случае акутальности даты, запоминает её и запрашивает желаемую дату выезда из отеля.
    """
    result, key, step = DetailedTelegramCalendar(calendar_id=1, locale='ru',
                                                 min_date=datetime.date.today()).process(call.data)
    if not result and key:
        bot.edit_message_text(f'Выберите {LSTEP_RU[step]}',
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f'Вы выбрали дату: {result}',
                              call.message.chat.id,
                              call.message.message_id)
        logger.info(f'Пользователь {call.from_user.full_name} (ID {call.from_user.id}) выбрал дату заезда '
                    f'{result}')
        with bot.retrieve_data(call.message.chat.id) as data:
            data['date_of_entry'] = result
        logger.info(f'Дата заезда {result} записана')
        bot.send_message(call.message.chat.id, 'Пожалуйста, введите желаемую дату выезда из отеля.')
        run_calendar_date_of_departure(call.message)


def run_calendar_date_of_departure(message: Message) -> None:
    """
    Функция, формирующая инлайн-календарь даты выезда из отеля.
    """
    with bot.retrieve_data(message.chat.id) as data:
        calendar, step = DetailedTelegramCalendar(calendar_id=2, locale='ru',
                                                  min_date=data['date_of_entry']).build()
    bot.send_message(message.chat.id, f'Пожалуйста, выберите {LSTEP_RU[step]}', reply_markup=calendar)


@bot.callback_query_handler(func=DetailedTelegramCalendar.func(calendar_id=2))
def get_date_of_departure(call: CallbackQuery) -> None:
    """
    Функция проверяет актуальность выбранной даты выезда из отеля.
    В случае акутальности даты, запоминает её и запрашивает количество взрослых гостей.
    """
    with bot.retrieve_data(call.message.chat.id) as data:
        result, key, step = DetailedTelegramCalendar(calendar_id=2, locale='ru',
                                                     min_date=data['date_of_entry']).process(call.data)
    if not result and key:
        bot.edit_message_text(f'Выберите {LSTEP_RU[step]}',
                              call.message.chat.id,
                              call.message.message_id,
                              reply_markup=key)
    elif result:
        bot.edit_message_text(f'Вы выбрали дату: {result}',
                              call.message.chat.id,
                              call.message.message_id)
        logger.info(f'Пользователь {call.from_user.full_name} (ID {call.from_user.id}) выбрал дату выезда '
                    f'{result}')
        with bot.retrieve_data(call.message.chat.id) as data:
            if result > data['date_of_entry']:
                data['date_of_departure'] = result
                logger.info(f'Дата выезда {result} записана')
                bot.send_message(call.message.chat.id, 'Укажите, пожалуйста, количество взрослых гостей: ')
            else:
                logger.info(f'Дата выезда {result} неактуальна')
                bot.send_message(call.message.chat.id, f'Выбранная дата выезда не может совпадать с датой заезда '
                                                       f'({data["date_of_entry"]})! '
                                                       f'\nПожалуйста введите актуальную дату выезда из отеля.')
                run_calendar_date_of_departure(call.message)


@bot.message_handler(state=UserInputInfo.city_id)
def numbers_adults(message: Message) -> None:
    """
    Функция проверяет ввод количества взрослых гостей на соответствие числовому значению.
    Если ввод является числом, то запоминает введенное количество взрослых гостей и следом запрашивает
    максимальную удаленность отеля от центра города.
    Если ввод не верен, то повторно запрашивает количество взрослых гостей.
    """
    if message.text.isdigit():
        logger.info(f'Пользователь {message.from_user.full_name} (ID {message.from_user.id}) ввёл количество взрослых '
                    f'гостей: {message.text}')
        if int(message.text) <= 0:
            logger.info(f'Введённое количество гостей меньше 1')
            bot.send_message(message.from_user.id, 'Количество взрослых гостей должно быть больше 0! '
                                                   '\nПовторите, пожалуйста, ввод количества взрослых гостей')
        else:
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['numbers_adults'] = message.text
            logger.info(f'Введённое количество гостей записано: {message.text}')
            bot.set_state(message.from_user.id, UserInputInfo.max_distance_from_destination, message.chat.id)
            bot.send_message(message.from_user.id, 'Укажите, пожалуйста, максимальную удаленность отеля от центра '
                                                   'города (mile): ')
    else:
        logger.info(f'Введённое Пользователем {message.from_user.full_name} (ID {message.from_user.id}) количество '
                    f'гостей не является числом!')
        bot.send_message(message.from_user.id, 'Ваш ввод не является числом! '
                                               '\nПовторите, пожалуйста, ввод количества взрослых гостей')


@bot.message_handler(state=UserInputInfo.max_distance_from_destination)
def distance_from_destination(message: Message) -> None:
    """
    Функция проверяет ввод удаленности отеля от центра города на соответствие числовому значению.
    Если ввод является числом, запоминает значение удаленности отеля от центра города и следом запрашивает
    максимальную стоимость отеля.
    Если ввод не верен, то повторно запрашивает ввод максимальной удаленности отеля от центра города.
    """
    if message.text.isdigit():
        logger.info(f'Пользователь {message.from_user.full_name} (ID {message.from_user.id}) ввёл максимальную '
                    f'удаленность отеля от центра города (mile): {message.text}')
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['max_distance_from_destination'] = message.text
        logger.info('Значение максимальной удаленности отеля от центра города записано')
        bot.set_state(message.from_user.id, UserInputInfo.price_max, message.chat.id)
        bot.send_message(message.from_user.id, 'Укажите, пожалуйста, максимальную стоимость проживания в '
                                               'отеле (USD/сут.): ')
    else:
        logger.info(f'Введённое Пользователем {message.from_user.full_name} (ID {message.from_user.id}) значение '
                    f'максимальной удаленности отеля от центра города не является числом!')
        bot.send_message(message.from_user.id, 'Ваш ввод не является числом! '
                                               '\nПовторите, пожалуйста, ввод максимальной удаленности отеля от центра '
                                               'города (mile): ')


@bot.message_handler(state=UserInputInfo.price_max)
def max_price(message: Message) -> None:
    """
    Функция проверяет максимальную стоимость отеля на соответствие числовому значению.
    Если ввод является числом, то запоминает максимальную стоимость отеля и следом запрашивает
    минимальную стоимость отеля.
    Если ввод не верен, то повторно запрашивает ввод максимальной стоимости отеля.
    """
    if message.text.isdigit():
        logger.info(f'Пользователь {message.from_user.full_name} (ID {message.from_user.id}) ввёл максимальную '
                    f'стоимость проживания в отеле (USD/сут.): {message.text}')
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['price_max'] = message.text
        logger.info('Значение максимальной стоимости проживания в отеле записано')
        bot.set_state(message.from_user.id, UserInputInfo.price_min, message.chat.id)
        bot.send_message(message.from_user.id, 'Укажите, пожалуйста, минимальную стоимость проживания в '
                                               'отеле (USD/сут.): ')
    else:
        logger.info(f'Введённое Пользователем {message.from_user.full_name} (ID {message.from_user.id}) значение '
                    f'максимальной стоимости проживания в отеле не является числом!')
        bot.send_message(message.from_user.id, 'Ваш ввод не является числом! '
                                               '\nПовторите, пожалуйста, ввод максимальной стоимости отеля '
                                               '(USD/сут.)')


@bot.message_handler(state=UserInputInfo.price_min)
def min_price(message: Message) -> None:
    """
    Функция проверяет минимальную стоимость отеля на соответствие числовому значению.
    Если ввод является числом, то запоминает минимальную стоимость отеля и следом запрашивает
    количество отелей для вывода.
    Если ввод не верен, то повторно запрашивает ввод минимальной стоимости отеля.
    """
    if message.text.isdigit():
        logger.info(f'Пользователь {message.from_user.full_name} (ID {message.from_user.id}) ввёл минимальную '
                    f'стоимость проживания в отеле (USD/сут.): {message.text}')
        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            data['price_min'] = message.text
        logger.info('Значение минимальной стоимости проживания в отеле записано')
        bot.set_state(message.from_user.id, UserInputInfo.numbers_hotels, message.chat.id)
        bot.send_message(message.from_user.id, 'Какое количество отелей желаете посмотреть? (не более 10)')
    else:
        logger.info(f'Введённое Пользователем {message.from_user.full_name} (ID {message.from_user.id}) значение '
                    f'минимальной стоимости проживания в отеле не является числом!')
        bot.send_message(message.from_user.id, 'Ваш ввод не является числом! '
                                               '\nПовторите, пожалуйста, ввод минимальной стоимости проживания в '
                                               'отеле (USD/сут.):')


@bot.message_handler(state=UserInputInfo.numbers_hotels)
def numbers_hotels(message: Message) -> None:
    """
   Функция проверяет ввод количества отелей на соответствие числовому значению и допустимому диапазону.
   Если ввод верен, то запоминает количество отелей и выводит собранную информацию для поиска
   подходищих отелей.
   Если ввод не верен, то повторно запрашивает ввод количества отелей.
   """
    if message.text.isdigit():
        logger.info(f'Пользователь {message.from_user.full_name} (ID {message.from_user.id}) ввёл количества отелей: '
                    f'{message.text}')
        if 0 < int(message.text) <= 10:
            with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
                data['numbers_hotels'] = message.text
                logger.info('Значение количества отелей записано')
                logger.info(f"Вывод пользователю {message.from_user.full_name} (ID {message.from_user.id}) параметров "
                            f"поиска отелей \n"
                            f"Город: {data['input_city']}\n"
                            f"Дата заезда: {data['date_of_entry']}\n"
                            f"Дата выезда: {data['date_of_departure']}\n"
                            f"Кол-во взрослых госте: {int(data['numbers_adults'])}\n"
                            f"Максимальная удаленность от центра города: "
                            f"{int(data['max_distance_from_destination'])} mile\n"
                            f"Max стоимость проживания в отеле: "
                            f"{int(data['price_max'])} $\n"
                            f"Min стоимость проживания в отеле: "
                            f"{int(data['price_min'])} $\n"
                            f"Кол-во отелей: {int(data['numbers_hotels'])}")
                bot.send_message(message.from_user.id, f"Подбираем подходящие для Вас отели в городе: "
                                                       f"{data['input_city']}\n"
                                                       f"Дата заезда: {data['date_of_entry']}\n"
                                                       f"Дата выезда: {data['date_of_departure']}\n"
                                                       f"Кол-во взрослых госте: {int(data['numbers_adults'])}\n"
                                                       f"Максимальная удаленность от центра города: "
                                                       f"{int(data['max_distance_from_destination'])} mile\n"
                                                       f"Max стоимость проживания в отеле: "
                                                       f"{int(data['price_max'])} $\n"
                                                       f"Min стоимость проживания в отеле: "
                                                       f"{int(data['price_min'])} $\n"
                                                       f"Кол-ва отелей: {int(data['numbers_hotels'])}")

                hotels_options(message, data)
        else:
            logger.info('Значение количества отелей вне допустимого диаппазона!')
            bot.send_message(message.from_user.id, 'Ваше число вне допустимого диаппазона! '
                                                   '\nПожалуйста, введите количество отелей от 1 до 10.')
    else:
        logger.info(f'Введённое Пользователем {message.from_user.full_name} (ID {message.from_user.id}) значение '
                    f'количества отелей не является числом!')
        bot.send_message(message.from_user.id, 'Ваш ввод не является числом! '
                                               '\nПовторите, пожалуйста, ввод количества отелей')
    bot.delete_state(message.from_user.id, message.chat.id)
