from telebot import TeleBot
from telebot.storage import StateMemoryStorage
from TelegramBot_Hotels.tg_API.config_data import config


storage = StateMemoryStorage()
bot = TeleBot(token=config.BOT_TOKEN, state_storage=storage)
