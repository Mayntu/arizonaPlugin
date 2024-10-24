from logging.config import dictConfig
from dotenv import load_dotenv
from os import environ

try:
    load_dotenv()
except Exception as e:
    print(e)

LOGS_FILE_PATH : str = environ.get("LOGS_FILE_PATH")


log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "[%(asctime)s] %(levelname)s | %(message)s",
        },
        "detailed": {
            "format": "[%(asctime)s] %(levelname)s | %(message)s",
        },
        "separator": {
            "format": "%(message)s",
        },
    },  
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
        "file": {
            "class": "logging.FileHandler",
            "formatter": "detailed",
            "filename": LOGS_FILE_PATH,
        },
        "separator_console": {
            "class": "logging.StreamHandler",
            "formatter": "separator",
        },
        "separator_file": {
            "class": "logging.FileHandler",
            "formatter": "separator",
            "filename": LOGS_FILE_PATH,
        },
    },
    "loggers": {
        "uvicorn": {
            "handlers": ["console", "file"],
            "level": "INFO",
        },
        "fastapi": {
            "handlers": ["console", "file"],
            "level": "INFO",
        },
        "__main__": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
        },
        "separator_logger": {
            "handlers": ["separator_console", "separator_file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

def setup_logging():
    dictConfig(log_config)