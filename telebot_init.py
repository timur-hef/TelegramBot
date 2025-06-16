import os

import telebot
from dotenv import load_dotenv

load_dotenv()

TG_BOT_API_KEY = os.getenv("TG_BOT_API_KEY")
bot = telebot.TeleBot(TG_BOT_API_KEY)
