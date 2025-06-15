import os
import sys
from typing import Any, Dict

from dotenv import load_dotenv

load_dotenv()

TG_BOT_LOG_FOLDER = os.getenv("TG_BOT_LOG_FOLDER")


LOGGING_CONFIG: Dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {"format": "[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": sys.stdout,
            "level": "ERROR",
        },
        "file": {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "formatter": "default",
            "level": "INFO",
            "filename": f"{TG_BOT_LOG_FOLDER}ioparlo.log",  # change on linux
            "when": "midnight",
            "interval": 1,
            "backupCount": 7,
        },
    },
    "loggers": {
        "main_bot_logger": {
            "handlers": ["file"],
            "propagate": False,
        },
        "utils": {
            "handlers": ["file"],
            "propagate": False,
        },
    },
    "root": {
        "handlers": ["file"],
        "level": "DEBUG",
    },
}
