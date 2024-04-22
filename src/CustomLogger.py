from logging import Logger, FileHandler, StreamHandler, Formatter, INFO, getLogger
import os
from Constants import FOLDER, GET_WORKING_DIR


class CustomLogger(Logger):
    """
    A custom logger class for logging messages to a file.

    Args:
        name (str): The name of the logger.
        log_dir (str): The directory where the log file will be stored.
        log_file (str): The name of the log file, defaults to "VALocker.log".

    Attributes:
        logger (logging.Logger): The logger object.

    """

    def __init__(self, name: str, log_file: str = "VALocker.log"):
        super().__init__(name)
        self.logger: Logger = getLogger(name)
        
        self.setLevel(INFO)
        formatter = Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        log_path: str = os.path.join(GET_WORKING_DIR(), FOLDER.LOGS.value, log_file)
        

        # Create the log directory if it doesn't exist
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

        # File handler
        file_handler: FileHandler = FileHandler(log_path, mode="a")
        file_handler.setFormatter(formatter)
        self.addHandler(file_handler)

        # Stream handler
        stream_handler: StreamHandler = StreamHandler()
        stream_handler.setFormatter(formatter)
        self.addHandler(stream_handler)

    def get_logger(self):
        """
        Get the logger object.

        Returns:
            Logger: The logger object.

        """
        return self
