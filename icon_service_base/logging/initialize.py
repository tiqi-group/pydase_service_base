import logging
import sys

from loguru import logger

from .LogBroadcastMessagePublisher import LogBroadcastMessagePublisher
from .LoguruInterceptHandler import LoguruInterceptHandler


def initialize_service_logging(
    loglevel: int, service_name: str, service_instance_name: str
) -> None:
    logger.debug("Configuring service logging.")
    originator = f"{service_name}.{service_instance_name}"

    _init_logger(originator, loglevel)


def initialize_script_logging(
    loglevel: str, script_name: str, use_central_logging: bool = True
) -> None:
    logger.debug("Configuring script logging.")

    originator = f"{script_name}"
    allowed_levels = ["DEBUG", "INFO", "ERROR"]

    if loglevel in allowed_levels:
        _init_logger(originator, logging.getLevelName(loglevel), use_central_logging)
    else:
        raise ValueError(f"Allowed log levels are: {allowed_levels}")


def _init_logger(
    originator: str, loglevel: int, use_central_logging: bool = True
) -> None:
    # default format
    fmt = (
        "<green>{time:DD.MM HH:mm:ss.SSS}</green> <level>{message}</level> "
        + "<dim>{name}:{function}:{line}@{process.name}/{thread.name}</dim>"
    )

    config = {
        "handlers": [
            {"sink": sys.stderr, "format": fmt, "level": loglevel},
        ],
        "extra": {
            "originator": originator,
        },
    }
    logger.configure(**config)

    if use_central_logging:
        exchange_logger = LogBroadcastMessagePublisher(originator)

        # DEBUG messages and above are sent to the central logging instance
        # note that this could be a problem if a lot of debug messages are sent per second
        logger.add(exchange_logger.send_msg, enqueue=True, level="DEBUG")  # type: ignore

    # see https://loguru.readthedocs.io/en/stable/api/logger.html#color
    logger.level("DEBUG", color="<magenta>")
    # celery default colors
    # 'DEBUG': COLORS['blue'],
    # 'WARNING': COLORS['yellow'],
    # 'ERROR': COLORS['red'],
    # 'CRITICAL': COLORS['magenta'],

    loguru_intercept_handler = LoguruInterceptHandler()

    logging.basicConfig(handlers=[loguru_intercept_handler], level=loglevel)

    # library default log levels
    # -> get name of logger using pythons logger "logging"
    # sqlalchemy spams statements to INFO level, therefore set to WARNING
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    # datamodel_code_generator spams debug messages, therefore set to INFO
    logging.getLogger("blib2to3.pgen2.driver").setLevel(logging.INFO)

    # add loguru handler
    logging.getLogger("sqlalchemy.engine").handlers = [loguru_intercept_handler]
    logging.getLogger("uvicorn").handlers = [loguru_intercept_handler]
