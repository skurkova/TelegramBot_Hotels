from telebot.handler_backends import State, StatesGroup


class UserInputInfo(StatesGroup):
    """
    Класс записывает состояния пользователя

    : param input_command: str
        команда, которую выбрал пользователь
    : param input_city: str
        город, который ввёл пользователь
    : param city_id: int
        вариант, который выбрал пользователь
    : param date_of_entry: str
        дата заезда
    : param date_of_departure: str
        дата выезда
    : param numbers_adults: int
        кол-во взрослых
    : param numbers_hotels: int
        кол-во выводимых отелей
    : param price_max: int
        максимальная стоимость отеля
    : param price_min: int
        минимальная стоимость отеля
    : param max_distance_from_destination: int
        максимальная удаленность от центра города
    """
    input_command = State()
    input_city = State()
    city_id = State()
    date_of_entry = State()
    date_of_departure = State()
    numbers_adults = State()
    numbers_hotels = State()
    price_max = State()
    price_min = State()
    max_distance_from_destination = State()
