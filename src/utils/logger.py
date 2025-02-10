import logging
from datetime import datetime
from logging.handlers import RotatingFileHandler

import pytz


class HoustonFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        houston_tz = pytz.timezone('America/Chicago')  # Houston follows Central Time
        dt = datetime.fromtimestamp(record.created, houston_tz)
        return dt.strftime(datefmt if datefmt else "%Y-%m-%d %H:%M:%S")

def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)

    file_handler = RotatingFileHandler('app.log', maxBytes=1000000, backupCount=3)
    file_handler.setLevel(logging.DEBUG)

    formatter = HoustonFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger


logger = setup_logger()