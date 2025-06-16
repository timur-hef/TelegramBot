import logging
from logging.config import dictConfig

import requests
import telebot

from telebot_init import bot

logger = logging.getLogger("main_bot_logger")

from database import *
from log_conf import LOGGING_CONFIG
from models.horoscope import DATES, MAP_PERIOD_DATA, SIGNS
from stonks import stock_info
from utils import error_handler

dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("main_bot_logger")
init_db()


# Stocks


@bot.message_handler(commands=["stonks"])
@error_handler
def stonks(message: telebot.types.Message):
    logger.info(f"User {message.from_user.username} id-{message.from_user.id} using bot (stonks)")
    message = bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=message.id,
        text="Введи котировку (прим. aapl): ",
    )
    bot.register_next_step_handler(message, stock_info, bot=bot)


# Horoscope


@bot.message_handler(commands=["horoscope"])
@error_handler
def horoscope(message: telebot.types.Message, change: bool = False):
    logger.info(f"User {message.from_user.username} id-{message.from_user.id} using bot (horoscope)")
    horo_markup = telebot.types.InlineKeyboardMarkup(False)
    b1 = telebot.types.InlineKeyboardButton("Aries", callback_data="aries")
    b2 = telebot.types.InlineKeyboardButton("Taurus", callback_data="taurus")
    b3 = telebot.types.InlineKeyboardButton("Gemini", callback_data="gemini")
    b4 = telebot.types.InlineKeyboardButton("Cancer", callback_data="cancer")
    b5 = telebot.types.InlineKeyboardButton("Leo", callback_data="leo")
    b6 = telebot.types.InlineKeyboardButton("Virgo", callback_data="virgo")
    b7 = telebot.types.InlineKeyboardButton("Libra", callback_data="libra")
    b8 = telebot.types.InlineKeyboardButton("Scorpio", callback_data="scorpio")
    b9 = telebot.types.InlineKeyboardButton("Sagittarius", callback_data="sagittarius")
    b10 = telebot.types.InlineKeyboardButton("Capricorn", callback_data="capricorn")
    b11 = telebot.types.InlineKeyboardButton("Aquarius", callback_data="aquarius")
    b12 = telebot.types.InlineKeyboardButton("Pisces", callback_data="pisces")
    buttons = horo_markup.add(b1, b2, b3, b4, b5, b6, b7, b8, b9, b10, b11, b12)
    text = "Choose your sign:"

    if change:
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.id,
            text=text,
            reply_markup=buttons,
        )
    else:
        bot.send_message(chat_id=message.chat.id, text=text, reply_markup=buttons)


@bot.callback_query_handler(func=lambda c: c.data in SIGNS)
@error_handler
def horoscope_timeline(callback_query: telebot.types.CallbackQuery):
    sign = callback_query.data
    update_user(callback_query.from_user.id, horo_sign=sign)
    bot.answer_callback_query(callback_query.id)

    day_markup = telebot.types.InlineKeyboardMarkup(False)
    b1 = telebot.types.InlineKeyboardButton("Today", callback_data=sign + " today")
    b2 = telebot.types.InlineKeyboardButton("Tomorrow", callback_data=sign + " tomorrow")
    b3 = telebot.types.InlineKeyboardButton("Week", callback_data=sign + " weekly")
    b4 = telebot.types.InlineKeyboardButton("Month", callback_data=sign + " monthly")
    b5 = telebot.types.InlineKeyboardButton("Change sign", callback_data="change")
    buttons = day_markup.add(b1, b2, b3, b4, b5)
    text = "Choose time:"

    bot.edit_message_text(
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.id,
        text=text,
        reply_markup=buttons,
    )


@bot.callback_query_handler(func=lambda c: c.data == "change")
@error_handler
def change_sign(callback_query: telebot.types.CallbackQuery):
    horoscope(callback_query.message, change=True)


# old one
# @bot.callback_query_handler(lambda c: (c.data.split()[0] in SIGNS) and (c.data.split()[1] in DATES))
# def horoscope_info(callback_query: telebot.types.CallbackQuery):
#     try:
#         bot.answer_callback_query(callback_query.id)
#         sign, date = callback_query.data.split()

#         r = requests.get(f"https://horo.mail.ru/prediction/{sign}/{date}/")

#         soup = BeautifulSoup(r.content, "html.parser")
#         body = soup.find_all("h1")[0].text + "\n\n"

#         if date != "month":
#             text = soup.find_all("p")
#         else:
#             text = soup.find_all("p")[:-1]

#         for elem in text:
#             body += elem.text
#     except Exception as e:
#         logger.error(e)
#         body = ERROR_MESSAGE

#     bot.send_message(callback_query.from_user.id, body)


@bot.callback_query_handler(lambda c: (c.data.split()[0] in SIGNS) and (c.data.split()[1] in DATES))
@error_handler
def horoscope_info(callback_query: telebot.types.CallbackQuery):
    bot.answer_callback_query(callback_query.id)
    sign, timeline = callback_query.data.split()
    params = {"sign": sign}

    if timeline in ("today", "tomorrow"):
        period = "daily"
        params["day"] = timeline
    else:
        period = timeline

    r = requests.get(f"https://horoscope-app-api.vercel.app/api/v1/get-horoscope/{period}", params=params)
    data = r.json()["data"]
    period_data = MAP_PERIOD_DATA[period]
    body = period_data.title + data[period_data.resp_field_name] + "\n\n" + data["horoscope_data"]

    bot.send_message(callback_query.from_user.id, body)


bot.polling()
