import datetime as dt
import json
import logging
import os

import requests

from database import User, provide_session
from utils import ERROR_MESSAGE, alpha_2, is_cyrillic, translate, translit

logger = logging.getLogger("main_bot_logger")

WEATHER_KEY = os.getenv("WEATHER_KEY")


@provide_session
def weather_info(message, session=None, bot=None):
    try:
        user = session.query(User).filter(User.id == message.from_user.id).one()
        country_code = None

        if message.text == ".":
            user_location = json.loads(user.location)
            city = user_location["city"]
            country_code = user_location["code"]
        else:
            city = message.text.split()[0].capitalize()  # munich -> Munich
            country = message.text.split()[1].capitalize()  # Россия -> Russia -> RU
            logger.info("Ищу прогноз погоды для: {}, {}".format(city, country))

            city = translit(city) if is_cyrillic(city) else city
            country = translate(country) if is_cyrillic(country) else country

            for name in alpha_2:
                if country in name:
                    country_code = alpha_2[name]
                    break

        if not country_code:
            raise Exception(f"Не удалось определить код страны: {country}")

        r_1 = requests.get(
            f"https://api.openweathermap.org/data/2.5/forecast?q={city},{country_code}&lang=ru&appid={WEATHER_KEY}"
        )
        dct = json.loads(r_1.content)
        coor = list(dct["city"]["coord"].values())
        city = dct["city"]["name"].split()[0]

        r_2 = requests.get(
            f"https://api.openweathermap.org/data/2.5/onecall?lat={coor[0]}&lon={coor[1]}&exclude=minutely,hourly,alerts&units=metric&lang=ru&appid={WEATHER_KEY}"
        )
        result = create_weather_string(json.loads(r_2.content), city)

        user.location = json.dumps({"city": city, "code": country_code})
        bot.send_message(message.chat.id, result)
    except Exception as e:
        logger.error(e)
        bot.send_message(
            message.chat.id,
            "Не удалось распознать город или страну, попробуй еще раз...",
        )


def create_weather_string(dct, city):
    current = dct["current"]

    now = (
        f'Сейчас ({city}): {current["weather"][0]["description"]}\n'
        + f'🌡️{round(current["feels_like"])}°, 💧{current["humidity"]}%, ☀{round(current["uvi"])}, ☁ {current["clouds"]}%, 💨{round(current["wind_speed"], 1)}m/s\n\n'
    )

    forecast = "------------------------------\n"
    count = 0
    for day in dct["daily"]:
        if count == 5:
            break

        date = dt.datetime.fromtimestamp(day["dt"]).strftime("%d-%m-%Y")
        forecast += (
            f'{date} ({day["weather"][0]["description"]})\n'
            + f'💧{day["humidity"]}%, ☔{round(day["pop"]*100)}%, ☀{round(day["uvi"])}, ☁{day["clouds"]}%, 💨{round(day["wind_speed"], 1)}m/s\n'
            + f'УТРО  : 🌡️{round(day["feels_like"]["morn"])}°\n'
            + f'ДЕНЬ  : 🌡️{round(day["feels_like"]["day"])}°\n'
            + f'ВЕЧЕР : 🌡️{round(day["feels_like"]["eve"])}°\n'
            + f'НОЧЬ  : 🌡️{round(day["feels_like"]["night"])}°\n'
            + f"------------------------------\n"
        )
        count += 1

    return now + forecast
