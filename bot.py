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

# greeting
@bot.message_handler(commands=["start"])
def greet(message):
    try:
        add_user(message.from_user.id)
        markup = telebot.types.InlineKeyboardMarkup(False)
        itembtn1 = telebot.types.InlineKeyboardButton('Погода', callback_data='weather')
        itembtn2 = telebot.types.InlineKeyboardButton('Гороскоп', callback_data='horoscope')
        itembtn3 = telebot.types.InlineKeyboardButton('Акции', callback_data='price')
        buttons = markup.add(itembtn1, itembtn2, itembtn3)
        logger.info(f'User {message.from_user.username} id-{message.from_user.id} using bot')
        bot.send_message(message.from_user.id, f"{message.from_user.first_name}, wassup my brotha?\n\nВыбери:", reply_markup=buttons)
    except Exception as e:
        logger.error('Ошибка сервера:\n')
        logger.error(e)
        bot.send_message(message.chat.id, ERROR_MESSAGE)

# Weather

@bot.callback_query_handler(func=lambda c: c.data == 'weather')
def weather(callback_query: telebot.types.CallbackQuery):
    try:
        bot.answer_callback_query(callback_query.id)
        message = bot.send_message(
            chat_id=callback_query.message.chat.id,
            text="Введи наименование города и страны по примеру:\nКазань Россия"
        )
        bot.register_next_step_handler(message, weather_info, bot=bot)
    except Exception as e:
        logger.error('Ошибка сервера:\n')
        logger.error(e)
        bot.send_message(message.chat.id, ERROR_MESSAGE)

# Stocks

@bot.callback_query_handler(func=lambda c: c.data == 'price')
def stonks(callback_query: telebot.types.CallbackQuery):
    try:
        bot.answer_callback_query(callback_query.id)
        message = bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.id, 
            text="Введи котировку (прим. aapl): "
        )
        bot.register_next_step_handler(message, stock_info, bot=bot)
    except Exception as e:
        logger.error('Ошибка сервера:\n')
        logger.error(e)
        bot.send_message(message.chat.id, ERROR_MESSAGE)

# Horoscope

@bot.callback_query_handler(func=lambda c: c.data == 'horoscope')
def horoscope_type(callback_query: telebot.types.CallbackQuery):
    try:
        bot.answer_callback_query(callback_query.id)

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
        bot.edit_message_text(
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.id,
            text="Выбери знак зодиака:", 
            reply_markup=buttons
        )
    except Exception as e:
        logger.error('Ошибка сервера:\n')
        logger.error(e)
        bot.send_message(callback_query.chat.id, ERROR_MESSAGE)


@bot.callback_query_handler(func=lambda c: c.data in signs)
def horoscope_timeline(callback_query: telebot.types.CallbackQuery):
    update_user(callback_query.from_user.id, horo=callback_query.data)

    bot.answer_callback_query(callback_query.id)    

    day_markup = telebot.types.InlineKeyboardMarkup(False)
    b1 = telebot.types.InlineKeyboardButton('Сегодня', callback_data=callback_query.data + ' today')
    b2 = telebot.types.InlineKeyboardButton('Завтра', callback_data=callback_query.data + ' tomorrow')
    b3 = telebot.types.InlineKeyboardButton('Неделя', callback_data=callback_query.data + ' week')
    b4 = telebot.types.InlineKeyboardButton('Месяц', callback_data=callback_query.data + ' month')
    b5 = telebot.types.InlineKeyboardButton('Год', callback_data=callback_query.data + ' year')
    buttons = day_markup.add(b1, b2, b3, b4, b5)
    bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.id,
        text="Выбери период времени:", 
        reply_markup=buttons
    )


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