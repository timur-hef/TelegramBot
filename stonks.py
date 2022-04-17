import telebot
import logging
import yfinance as yf

from utils import ERROR_MESSAGE


logger = logging.getLogger('main_bot_logger')


def stock_info(message, bot=None):
    name = message.text.lower()
    try:
        data = yf.download(tickers=name, period='5d')
        data = data.reset_index()

        time = list(data['Date'])

        result = ''
        for num, date in enumerate(time):
            date = date.strftime('%d.%m')
            result += f"{date}   {round(data['Close'][num], 1)}\n"
    except Exception as e:
        logger.error(e)
        result = ERROR_MESSAGE
        
    bot.send_message(message.chat.id, result)
