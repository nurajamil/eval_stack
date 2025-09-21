# Import libraries
import logging
import os
from datetime import datetime


def setup_logging(
    name: str, log_file: str = None, level: int = logging.DEBUG
) -> logging.Logger:
    """
    Set up and configure a centralised logging utility for the application with both console and file handlers.

    :param name: Name of the logger.
    :param log_file: Optional file to log messages.
    :param level: Logging level (default: DEBUG).
    :return: Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Avoid adding multiple handlers to the same logger
    if logger.hasHandlers():
        return logger

    # Formatter to define the log output format
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler (if log_file is provided)
    if log_file:
        # Ensure log directory exists
        log_dir = os.path.dirname(log_file)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
