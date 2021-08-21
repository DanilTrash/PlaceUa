import logging


def log(name):
    logger = logging.getLogger(name)
    console_handler = logging.StreamHandler()
    fileHandler = logging.FileHandler('log.log', encoding='utf-8')
    logger.addHandler(fileHandler)
    logger.addHandler(console_handler)
    formatter = logging.Formatter('%(asctime)s ~ %(name)s ~ %(levelname)s: %(message)s')
    fileHandler.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    console_handler.setLevel(logging.INFO)
    fileHandler.setLevel(logging.INFO)
    return logger
