import logging
import os

import logging
import os

class CustomLogger:
    """
    A custom logger class for logging messages to a file.

    Args:
        name (str): The name of the logger.
        log_dir (str): The directory where the log file will be stored.
        log_file (str): The name of the log file.

    Attributes:
        logger (logging.Logger): The logger object.

    """

    def __init__(self, name: str, log_dir: str, log_file: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        log_path = os.path.join(log_dir, "logs", log_file)
        
        file_handler = logging.FileHandler(
            log_path, mode="w"
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

    def get_logger(self):
        """
        Get the logger object.

        Returns:
            logging.Logger: The logger object.

        """
        return self.logger