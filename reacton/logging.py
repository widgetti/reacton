"""Sets up logging for react.

See `configuration of logging <conf.html#logging>`_ how to configure logging.

"""
import logging
import os
from typing import Optional

logger = logging.getLogger("reacton")
log_handler: Optional[logging.Handler] = None


def set_log_level(loggers=["reacton"], level=logging.DEBUG):
    """set log level to debug"""
    for logger in loggers:
        logging.getLogger(logger).setLevel(level)


def remove_handler():
    """Disabled logging, remove default hander and add null handler"""
    if log_handler is not None:
        logging.getLogger("reacton").removeHandler(log_handler)
    logging.getLogger("reacton").addHandler(logging.NullHandler())


def reset():
    """Reset configuration of logging (i.e. remove the default handler)"""
    if log_handler is not None:
        logging.getLogger("reacton").removeHandler(log_handler)


def _set_log_level(conf, level):
    if conf:
        if conf.startswith("reacton"):
            set_log_level(conf.split(","), level=level)
        else:
            set_log_level(level=level)


def setup():
    """Setup logging based on the configuration in ``react.settings``

    This function is automatically called when importing react. If settings are changed, call :func:`reset` and this function again
    to re-apply the settings.
    """
    global log_handler
    applied_setup = False

    def apply_setup():
        log_handler = logging.StreamHandler()

        # create formatter
        formatter = logging.Formatter("%(levelname)s:%(threadName)s:%(name)s:%(message)s")

        # add formatter to console handler
        log_handler.setFormatter(formatter)

        # from rich.logging import RichHandler
        # log_handler = RichHandler()

        # # add console handler to logger
        logger.addHandler(log_handler)

    postfix_to_level = {
        "ERROR": logging.ERROR,
        "WARNING": logging.WARNING,
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
    }

    for name, level in postfix_to_level.items():
        key = f"REACTON_LOGGING_{name}"
        value = os.environ.get(key, "")
        if value:
            if not applied_setup:
                apply_setup()
                applied_setup = True
            _set_log_level(value, level)

    # logging.getLogger("reacton").setLevel(logging.ERROR)
    # _set_log_level(react.settings.main.logging.error, logging.ERROR)
    # _set_log_level(react.settings.main.logging.warning, logging.WARNING)
    # _set_log_level(react.settings.main.logging.info, logging.INFO)
    # _set_log_level(react.settings.main.logging.debug, logging.DEBUG)
    # # reactonIVE_DEBUG behaves similar to reactonIVE_LOGGING_DEBUG, but has more effect
    DEBUG_MODE = os.environ.get("REACTON_DEBUG", "")
    if DEBUG_MODE:
        if not applied_setup:
            apply_setup()
            applied_setup = True
        _set_log_level(DEBUG_MODE, logging.DEBUG)


setup()
