import sys
from typing import Dict, Any


LOGGING_CONFIG: Dict[str, Any] = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {'format': '[%(asctime)s] {%(filename)s:%(lineno)d} %(levelname)s - %(message)s'},
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'default',
            'stream': sys.stdout,
            'level': 'INFO'
        },
        'file': {
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'formatter': 'default',
            'level': 'INFO',
            'filename': 'X:\Projects\TelegramBot\logs\ioparlo.log',  # change on linux
            'when': 'midnight',
            'interval': 1,
            'backupCount': 7
        },
    },
    'loggers': {
        'main_bot_logger': {
            'handlers': ['console', 'file'],
            'propagate': False,
        },
        'utils': {
            'handlers': ['file'],
            'propagate': False,
        }
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}

