import logging
import requests
import telebot

from logging.config import dictConfig
from bs4 import BeautifulSoup

logger = logging.getLogger('main_bot_logger')

from auth import TG_API_KEY
from conf import LOGGING_CONFIG
from database import *
from horoscope import signs, date
from stonks import stock_info
from utils import ERROR_MESSAGE
from weather import weather_info


dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('main_bot_logger')
init_db()
bot = telebot.TeleBot(TG_API_KEY)

# Weather

@bot.message_handler(commands=["weather"])
@provide_session
def weather(message, session=None):
    try:
        user = session.query(User).filter(User.id == message.from_user.id).first()
        logger.info(f'User {message.from_user.username} id-{message.from_user.id} using bot (weather)')

        if user and getattr(user, 'location', None): 
            text="Ты уже вводил местоположение. Хочешь использовать предыдущее? Тогда отправь точку '.'\n" \
                "Если хочешь обновить местоположение то введи наименование города и страны по примеру:\nКазань Россия"
        else:
            text = "Введи наименование города и страны по примеру:\nКазань Россия"

        message = bot.send_message(
            chat_id=message.chat.id,
            text= text
        )
        bot.register_next_step_handler(message, weather_info, bot=bot)
    except Exception as e:
        logger.error('Ошибка сервера:\n')
        logger.error(e)
        bot.send_message(message.chat.id, ERROR_MESSAGE)

# Stocks

@bot.message_handler(commands=["stonks"])
def stonks(message):
    try:
        logger.info(f'User {message.from_user.username} id-{message.from_user.id} using bot (stonks)')
        message = bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.id, 
            text="Введи котировку (прим. aapl): "
        )
        bot.register_next_step_handler(message, stock_info, bot=bot)
    except Exception as e:
        logger.error('Ошибка сервера:\n')
        logger.error(e)
        bot.send_message(message.chat.id, ERROR_MESSAGE)

# Horoscope

@bot.message_handler(commands=["horoscope"])
@provide_session
def horoscope(message, session=None, change=False):
    try:
        user = session.query(User).filter(User.id == message.from_user.id).first()
        logger.info(f'User {message.from_user.username} id-{message.from_user.id} using bot (horoscope)')
        
        if user and getattr(user, 'horo_sign', None) and not change:
            horoscope_timeline(message=message, sign=user.horo_sign)
        else:
            horo_markup = telebot.types.InlineKeyboardMarkup(False)
            b1 = telebot.types.InlineKeyboardButton('Овен', callback_data='aries')
            b2 = telebot.types.InlineKeyboardButton('Телец', callback_data='taurus')
            b3 = telebot.types.InlineKeyboardButton('Близнецы', callback_data='gemini')
            b4 = telebot.types.InlineKeyboardButton('Рак', callback_data='cancer')
            b5 = telebot.types.InlineKeyboardButton('Лев', callback_data='leo')
            b6 = telebot.types.InlineKeyboardButton('Дева', callback_data='virgo')
            b7 = telebot.types.InlineKeyboardButton('Весы', callback_data='libra')
            b8 = telebot.types.InlineKeyboardButton('Скорпион', callback_data='scorpio')
            b9 = telebot.types.InlineKeyboardButton('Стрелец', callback_data='sagittarius')
            b10 = telebot.types.InlineKeyboardButton('Козерог', callback_data='capricorn')
            b11 = telebot.types.InlineKeyboardButton('Водолей', callback_data='aquarius')
            b12 = telebot.types.InlineKeyboardButton('Рыбы', callback_data='pisces')
            buttons = horo_markup.add(b1, b2, b3, b4, b5, b6, b7, b8, b9, b10, b11, b12)
            text="Выбери знак зодиака:"

            if change:
                bot.edit_message_text(
                    chat_id=message.chat.id,
                    message_id=message.id,
                    text=text, 
                    reply_markup=buttons
                )
            else:
                bot.send_message(
                    chat_id=message.chat.id,
                    text=text, 
                    reply_markup=buttons
                )
    except Exception as e:
        logger.error('Ошибка сервера:\n')
        logger.error(e)
        bot.send_message(message.chat.id, ERROR_MESSAGE)


@bot.callback_query_handler(func=lambda c: c.data in signs)
def horoscope_timeline(callback_query: telebot.types.CallbackQuery=None, message=None, sign=None):
    if callback_query:
        update_user(callback_query.from_user.id, horo=callback_query.data)
        bot.answer_callback_query(callback_query.id)
        sign = callback_query.data

    day_markup = telebot.types.InlineKeyboardMarkup(False)
    b1 = telebot.types.InlineKeyboardButton('Сегодня', callback_data=sign + ' today')
    b2 = telebot.types.InlineKeyboardButton('Завтра', callback_data=sign + ' tomorrow')
    b3 = telebot.types.InlineKeyboardButton('Неделя', callback_data=sign + ' week')
    b4 = telebot.types.InlineKeyboardButton('Месяц', callback_data=sign + ' month')
    b5 = telebot.types.InlineKeyboardButton('Год', callback_data=sign + ' year')
    b6 = telebot.types.InlineKeyboardButton('Сменить знак зодиака', callback_data='change')
    buttons = day_markup.add(b1, b2, b3, b4, b5, b6)
    text = "Выбери период времени:"

    if callback_query:
        bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.id,
            text=text, 
            reply_markup=buttons
        )
    else:
        bot.send_message(
            chat_id=message.chat.id,
            text=text, 
            reply_markup=buttons
        )


@bot.callback_query_handler(func=lambda c: c.data == 'change')
def change_sign(callback_query: telebot.types.CallbackQuery):
    horoscope(callback_query.message, change=True)


@bot.callback_query_handler(func=lambda c: (c.data.split()[0] in signs) and (c.data.split()[1] in date))
def horoscope_info(callback_query: telebot.types.CallbackQuery):
    try:
        bot.answer_callback_query(callback_query.id)
        sign, date = callback_query.data.split()

        r = requests.get(f'https://horo.mail.ru/prediction/{sign}/{date}/')

        soup = BeautifulSoup(r.content, 'html.parser')
        body = soup.find_all('h1')[0].text + '\n\n'

        if date != 'month':
            text = soup.find_all('p')
        else:
            text = soup.find_all('p')[:-1]

        for elem in text:
            body += elem.text
    except Exception as e:
        logger.error(e)
        body = ERROR_MESSAGE

    bot.send_message(callback_query.from_user.id, body)

bot.polling()