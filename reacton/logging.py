"""Sets up logging for react.

See `configuration of logging <conf.html#logging>`_ how to configure logging.

"""
import logging
import os
from typing import Optional

logger = logging.getLogger("react")
log_handler: Optional[logging.Handler] = None


def set_log_level(loggers=["react"], level=logging.DEBUG):
    """set log level to debug"""
    for logger in loggers:
        logging.getLogger(logger).setLevel(level)


def set_log_level_debug(loggers=["react"]):
    """set log level to debug"""
    set_log_level(loggers, logging.DEBUG)


def set_log_level_info(loggers=["react"]):
    """set log level to info"""
    set_log_level(loggers, logging.INFO)


def set_log_level_warning(loggers=["react"]):
    """set log level to warning"""
    set_log_level(loggers, logging.WARNING)


def set_log_level_error(loggers=["react"]):
    """set log level to exception/error"""
    set_log_level(loggers, logging.ERROR)


def remove_handler():
    """Disabled logging, remove default hander and add null handler"""
    if log_handler is not None:
        logging.getLogger("react").removeHandler(log_handler)
    logging.getLogger("react").addHandler(logging.NullHandler())


def reset():
    """Reset configuration of logging (i.e. remove the default handler)"""
    if log_handler is not None:
        logging.getLogger("react").removeHandler(log_handler)


def _set_log_level(conf, level):
    if conf:
        if conf.startswith("react"):
            set_log_level(conf.split(","), level=level)
        else:
            set_log_level(level=level)


def setup():
    """Setup logging based on the configuration in ``react.settings``

    This function is automatically called when importing react. If settings are changed, call :func:`reset` and this function again
    to re-apply the settings.
    """
    global log_handler
    logger.setLevel(logging.DEBUG)

    log_handler = logging.StreamHandler()

    # create formatter
    formatter = logging.Formatter("%(levelname)s:%(threadName)s:%(name)s:%(message)s")

    # add formatter to console handler
    log_handler.setFormatter(formatter)

    # from rich.logging import RichHandler

    # log_handler = RichHandler()
    # assert log_handler is not None
    # log_handler.setLevel(logging.DEBUG)
    # # add console handler to logger
    logger.addHandler(log_handler)

    logging.getLogger("react").setLevel(logging.ERROR)
    # _set_log_level(react.settings.main.logging.error, logging.ERROR)
    # _set_log_level(react.settings.main.logging.warning, logging.WARNING)
    # _set_log_level(react.settings.main.logging.info, logging.INFO)
    # _set_log_level(react.settings.main.logging.debug, logging.DEBUG)
    # # reactonIVE_DEBUG behaves similar to reactonIVE_LOGGING_DEBUG, but has more effect
    DEBUG_MODE = os.environ.get("REACT_DEBUG", "")
    if DEBUG_MODE:
        _set_log_level(DEBUG_MODE, logging.DEBUG)


setup()
