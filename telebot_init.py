import os

import telebot

TG_BOT_API_KEY = os.getenv("TG_BOT_API_KEY")
bot = telebot.TeleBot(TG_BOT_API_KEY)
