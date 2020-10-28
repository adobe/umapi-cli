import logging
import sys

_LOGGER = logging.getLogger('main')

LOG_STRING_FORMAT = '%(asctime)s %(process)d %(levelname)s %(name)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

def init():
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(LOG_STRING_FORMAT, LOG_DATE_FORMAT))
    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.DEBUG)

debug = _LOGGER.debug
info = _LOGGER.info
warn = _LOGGER.warn
error = _LOGGER.error
critical = _LOGGER.critical
