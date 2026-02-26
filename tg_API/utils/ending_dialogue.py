from telebot.types import Message, CallbackQuery
from loguru import logger

from loader import bot
from tg_API.keyboards.inline.buttons_yes_no import calling_buttons_yes_no


def final_question(message: Message) -> None:
    """
    Функция спрашивает у пользователя, нужна ли ему ещё какая-либо помощь и выводит клавиатуру с ответами "Да" и "Нет".
    """
    bot.send_message(message.from_user.id, 'Могу я Вам ещё чем-то помочь?', reply_markup=calling_buttons_yes_no())
    logger.info(f'Пользователю {message.from_user.full_name} (ID {message.from_user.id}) выводится вопрос о помощи')


@bot.callback_query_handler(func=lambda call: call.data == 'Да' or call.data == 'Нет')
def answer_final_question(call: CallbackQuery) -> None:
    """
    Функция ловит ответ выбранной кнопки пользователем.
    Если ответ "Да", то выводится информационное сообщение.
    Если ответ "Нет" - то выводит прощальное сообщение.
    """
    logger.info(f'Пользователь {call.message.from_user.full_name} (ID {call.message.from_user.id}) ввёл ответ: '
                f'{call.data}')
    bot.delete_message(call.message.chat.id, call.message.message_id)
    if call.data == 'Да':
        bot.send_message(call.message.chat.id, 'Что Вас интересует?'
                                               '\n'
                                               '\n/lowprice - Самые дешёвые отели'
                                               '\n/highprice - Самые дорогие отели'
                                               '\n/customlocation - Наиболее подходящие по цене и расположению'
                                               '\n/history - История поиска отелей')
        logger.info(f'Пользователю {call.message.from_user.full_name} (ID {call.message.from_user.id}) выводится '
                    f'информационное сообщение')
    elif call.data == 'Нет':
        bot.send_message(call.message.chat.id, 'Спасибо, что воспользовались услугами нашей компании!\n'
                                               'Желаем Вам хорошего отдыха!')
        logger.info(f'Пользователю {call.message.from_user.full_name} (ID {call.message.from_user.id}) выводится '
                    f'прощальное сообщение')
