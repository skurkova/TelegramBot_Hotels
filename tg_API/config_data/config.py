import os
from dotenv import load_dotenv, find_dotenv
from loguru import logger


if not find_dotenv():
    exit('Переменные окружения не загружены т.к. отсутствует файл ".env"')
else:
    load_dotenv()


BOT_TOKEN = os.getenv("BOT_TOKEN")
RAPID_API_KEY = os.getenv("RAPID_API_KEY")
RAPID_API_HOST = os.getenv("RAPID_API_HOST")

DEFAULT_COMMANDS = (
    ('start', 'Запустить бота'),
    ('help', 'Вывести справку'),
    ('lowprice', 'Самые дешёвые отели'),
    ('highprice', 'Самые дорогие отели'),
    ('customlocation', 'Наиболее подходящие отели по расположению от центра города'),
    ('history', 'История поиска отелей'),
    ('reset', 'Начать с начала')
)

logger.add('logging.txt', format="{time:YYYY-MM-DD at HH:mm:ss} {level} {message}", level="INFO",
           rotation="500 MB", compression="zip", serialize=True, enqueue=True, catch=True)
