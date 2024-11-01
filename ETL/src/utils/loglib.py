import atexit
import logging
import logging.config
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path

_logging_rotating_file_config: dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "%(levelname)s: %(message)s"},
        "detailed": {"format": "[%(levelname)s|%(module)s|L:%(lineno)d] %(asctime)s: %(message)s", "datefmt": "%Y-%m-%dT%H:%M:%S%z"},
    },
    "handlers": {
        "stdout": {"class": "logging.StreamHandler", "level": "INFO", "formatter": "simple", "stream": "ext://sys.stdout"},
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "detailed",
            "filename": "logs/app.log",
            "maxBytes": 10 * 1024 * 1024,  # 10MB,
            "backupCount": 3,
        },
    },
    "loggers": {"root": {"level": "INFO", "handlers": ["stdout", "file"]}},
}

_timestamp = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")
_log_filename = f"logs/app_{_timestamp}.log"  # must be unique
_logging_unique_file_config: dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "%(levelname)s: %(message)s"},
        "detailed": {"format": "[%(levelname)s|%(module)s|L:%(lineno)d] %(asctime)s: %(message)s", "datefmt": "%Y-%m-%dT%H:%M:%S%z"},
    },
    "handlers": {
        "stdout": {"class": "logging.StreamHandler", "level": "INFO", "formatter": "simple", "stream": "ext://sys.stdout"},
        "file": {
            "class": "logging.FileHandler",
            "level": "INFO",
            "formatter": "detailed",
            "filename": _log_filename,
        },
    },
    "loggers": {"root": {"level": "INFO", "handlers": ["stdout", "file"]}},
}

_logging_queue_rotating_file_config: dict = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "simple": {"format": "%(levelname)s: %(message)s"},
        "detailed": {"format": "[%(levelname)s|%(module)s|L:%(lineno)d] %(asctime)s: %(message)s", "datefmt": "%Y-%m-%dT%H:%M:%S%z"},
    },
    "handlers": {
        "stdout": {"class": "logging.StreamHandler", "level": "INFO", "formatter": "simple", "stream": "ext://sys.stdout"},
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "level": "INFO",
            "formatter": "detailed",
            "filename": "logs/app.log",
            "maxBytes": 10 * 1024 * 1024,  # 10MB,
            "backupCount": 3,
        },
        "queue_handler": {"class": "logging.handlers.QueueHandler", "handlers": ["stdout", "file"], "respect_handler_level": True},
    },
    "loggers": {"root": {"level": "INFO", "handlers": ["queue_handler"]}},
}

_logging_queue_rotating_file_DEBUG_config: dict = {  # noqa: N816
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "detailed": {
            "format": "[PID:%(process)d|TID:%(thread)d][%(levelname)s|%(module)s|L:%(lineno)d] %(asctime)s: %(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S%z",
        },
    },
    "handlers": {
        "stdout": {"class": "logging.StreamHandler", "level": "DEBUG", "formatter": "detailed", "stream": "ext://sys.stdout"},
        "file": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "formatter": "detailed",
            "filename": "logs/DEBUG.log",
            "mode": "w",  # write file mode
        },
        "queue_handler": {"class": "logging.handlers.QueueHandler", "handlers": ["stdout", "file"], "respect_handler_level": True},
    },
    "loggers": {"root": {"level": "DEBUG", "handlers": ["queue_handler"]}},
}


class LoggerType(Enum):
    ROTATING_FILE: int = 0
    UNIQUE_FILE: int = 1
    QUEUE_ROTATING_FILE: int = 2
    DEBUG: int = 3


def _init_logger(logger_type: LoggerType, name: str) -> logging.Logger:
    log_path: Path = Path().cwd() / "logs"
    if not log_path.is_dir():
        log_path.mkdir()

    logger = logging.getLogger(name)
    match logger_type:
        case LoggerType.ROTATING_FILE:
            logging.config.dictConfig(_logging_rotating_file_config)
        case LoggerType.UNIQUE_FILE:
            logging.config.dictConfig(_logging_unique_file_config)
        case LoggerType.QUEUE_ROTATING_FILE:
            logging.config.dictConfig(_logging_queue_rotating_file_config)
        case LoggerType.DEBUG:
            logging.config.dictConfig(_logging_queue_rotating_file_DEBUG_config)
        case _:
            msg: str = f"Non existing logger type: {logger_type}"
            raise ValueError(msg)

    queue_handler = logging.getHandlerByName("queue_handler")
    if queue_handler is not None:
        queue_handler.listener.start()
        atexit.register(queue_handler.listener.stop)

    return logger


def get_logger(logger_type: LoggerType, logger_name: str) -> logging.Logger:
    return _init_logger(logger_type, logger_name)
