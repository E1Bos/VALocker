import logging
import os

class CustomLogger:
    """
    A custom logger class for logging messages to a file.

    Args:
        name (str): The name of the logger.
        log_dir (str): The directory where the log file will be stored.
        log_file (str): The name of the log file, defaults to "VALocker.log".

    Attributes:
        logger (logging.Logger): The logger object.

    """

    def __init__(self, name: str, log_file: str="VALocker.log"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        
        log_path = os.path.join(os.environ["APPDATA"], "VALocker", "logs", log_file)
        
        if not os.path.exists(os.path.dirname(log_path)):
            os.makedirs(os.path.dirname(log_path))
        
        # File handler
        file_handler = logging.FileHandler(
            log_path, mode="a"
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Stream handler
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)

    def get_logger(self):
        """
        Get the logger object.

        Returns:
            logging.Logger: The logger object.

        """
        return self.logger