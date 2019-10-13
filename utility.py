import logging


def create_logger(name: str = 'main.log', level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(__name__)
    logger.setLevel(level)

    # create a file handler
    handler = logging.FileHandler(name, mode='w+')
    handler.setLevel(level)

    # create a logging format
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(handler)

    logger.info(f'Logger {name} initialized')

    return logger


def validate_logger(logger: logging.Logger) -> logging.Logger:
    if logger is None:
        return create_logger('main.log', logging.INFO)
    else:
        return logger
