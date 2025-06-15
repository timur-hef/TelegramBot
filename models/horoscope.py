from collections import namedtuple

SIGNS = [
    "aries",
    "taurus",
    "gemini",
    "cancer",
    "leo",
    "virgo",
    "libra",
    "scorpio",
    "sagittaruis",
    "capricorn",
    "aquarius",
    "pisces",
]

DATES = ["today", "tomorrow", "weekly", "monthly"]


PeriodData = namedtuple("PeriodData", ["title", "resp_field_name"])

MAP_PERIOD_DATA = {
    "daily": PeriodData("DAY: ", "date"),
    "weekly": PeriodData("WEEK: ", "week"),
    "monthly": PeriodData("MONTH: ", "month"),
}
