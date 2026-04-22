import logging
import sys


def setup_logger(name="rpa_mr_letters", level=logging.DEBUG):
    """Create (or retrieve) and return a configured logger.

    A StreamHandler pointing at stdout is added only if the logger has no
    handlers yet, so calling this function multiple times is idempotent.
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
