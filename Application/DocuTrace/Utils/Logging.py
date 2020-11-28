import logging
import sys

logging.basicConfig(format='[ %(levelname)s ] %(message)s', level=logging.INFO, stream=sys.stdout)
logger = logging.getLogger('DocuTrace')


def debug(func):
    """Decorator to show debug log messages

    Args:
        func (Any -> Any): Any function
    """
    def inner(*args, **kwargs):
        logger.setLevel(logging.DEBUG)
        func(*args, **kwargs)
        logger.setLevel(logging.WARN)
    return inner
