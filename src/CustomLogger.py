import logging
from logging import Logger, FileHandler, StreamHandler, Formatter, INFO, getLogger
import os
import sys
import traceback
from typing import Optional
from Constants import FOLDER, GET_WORKING_DIR, LOGGER_LEVEL


class CustomLogger:
    """
    A custom logger class for logging messages to a file.

    Attributes:
        _name (str): The name of the logger.
        _logger (logging.Logger): The logger object.

    @author: [E1Bos](https://www.github.com/E1Bos)
    """

    _instance: Optional["CustomLogger"] = None

    @classmethod
    def get_instance(cls, name: str = "VALocker", log_file: str = "VALocker.log", log_level: int = LOGGER_LEVEL) -> "CustomLogger":
        """
        Get the logger instance.

        Args:
            name (str): The name of the logger.
            log_file (str): The name of the log file, defaults to "VALocker.log".
            log_level (int): The level of logging, defaults to logging.INFO.

        Returns:
            CustomLogger: The logger instance.

        """
        if cls._instance is None:
            cls._instance = cls()

            cls._instance._name = name
            cls._instance._logger = getLogger(name)

            cls._instance._logger.setLevel(log_level)
            formatter = Formatter(
                "%(asctime)s - %(levelname)s - %(name)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )

            log_path: str = os.path.join(GET_WORKING_DIR(), FOLDER.LOGS.value, log_file)

            # Create the log directory if it doesn't exist
            os.makedirs(os.path.dirname(log_path), exist_ok=True)

            # File handler
            file_handler: FileHandler = FileHandler(log_path, mode="a")
            file_handler.setFormatter(formatter)
            file_handler.setLevel(log_level)
            cls._instance._logger.addHandler(file_handler)

            # Stream handler
            stream_handler: StreamHandler = StreamHandler()
            stream_handler.setFormatter(formatter)
            stream_handler.setLevel(log_level)
            cls._instance._logger.addHandler(stream_handler)

            # Make sure that errors are logged
            sys.excepthook = cls._instance._log_exception

        return cls._instance

    @classmethod
    def get_logger(cls, name: str) -> Logger:
        """
        Get the logger with the given name.

        Args:
            name (str): The name of the logger.

        Returns:
            Logger: The logger with the given name.

        """
        return getLogger(f"{cls._instance._name}.{name}")

    def set_log_level(self, level: int) -> None:
        """
        Set the log level of the logger.

        Args:
            level (int): The level of logging.

        """
        self._logger.setLevel(level)
        for handler in self._logger.handlers:
            handler.setLevel(level)

    # region: Logging methods

    def debug(self, msg: str, *args, **kwargs) -> None:
        """
        Log a message with level DEBUG on the logger.

        The arguments are interpreted as for the print() function.

        """
        self._logger.debug(msg, *args, **kwargs)

    def info(self, msg: str, *args, **kwargs) -> None:
        """
        Log a message with level INFO on the logger.

        The arguments are interpreted as for the print() function.

        """
        self._logger.info(msg, *args, **kwargs)

    def warning(self, msg: str, *args, **kwargs) -> None:
        """
        Log a message with level WARNING on the logger.

        The arguments are interpreted as for the print() function.

        """
        self._logger.warning(msg, *args, **kwargs)

    def error(self, msg: str, *args, **kwargs) -> None:
        """
        Log a message with level ERROR on the logger.

        The arguments are interpreted as for the print() function.

        """
        self._logger.error(msg, *args, **kwargs)

    def exception(self, msg: str, *args, **kwargs) -> None:
        """
        Log a message with level ERROR on the logger, followed by a call to traceback.print_exception(*sys.exc_info()).

        The arguments are interpreted as for the print() function.

        """
        self._logger.exception(msg, *args, **kwargs)

    # endregion

    def _log_exception(self, exc_type, exc_value, exc_traceback):
        """
        Log an uncaught exception.

        This function is called by sys.excepthook().

        """
        self._logger.error(
            "".join(traceback.format_exception_only(exc_type, exc_value)),
            exc_info=(exc_type, exc_value, exc_traceback),
        )
