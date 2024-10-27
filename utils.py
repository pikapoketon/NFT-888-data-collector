# utils.py

import logging


# Настройка логирования
def setup_logging():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    return logger


logger = setup_logging()
