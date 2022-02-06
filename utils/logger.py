import logging


error_logger = logging.getLogger('errors')
error_logger.setLevel(logging.ERROR)

error_logger_handler = logging.FileHandler('logs/errors.log')
error_logger_handler.setFormatter(
    logging.Formatter('%(asctime)s - %(message)s')
)

error_logger.addHandler(error_logger_handler)
