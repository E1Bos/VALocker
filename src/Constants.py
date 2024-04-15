from enum import Enum


class URL(Enum):
    """
    Enum for URLs used in the project
    """

    DOWNLOAD_URL = "https://raw.githubusercontent.com/E1Bos/VALocker/valocker-v2"
    RELEASE_URL = "https://github.com/E1Bos/VALocker/releases/latest"
    API_RELEASE_URL = "https://api.github.com/repos/E1Bos/VALocker/releases/latest"


class FOLDER(Enum):
    """
    Enum for Folders used in the project
    """

    DEFAULTS = "app_defaults"
    SAVE_FILES = "save_files"
    DATA = "data"
    LOGS = "logs"
    SETTINGS = "settings"
    THEMES = "themes"


class FILE(Enum):
    """
    Enum for Files used in the project
    """

    AGENT_CONFIG = f"{FOLDER.DATA.value}/agent_config.json"
    LOCKING_INFO = f"{FOLDER.DATA.value}/locking_info.json"
    STATS = f"{FOLDER.DATA.value}/stats.json"
    SETTINGS = f"{FOLDER.SETTINGS.value}/settings.json"
    USER_SETTINGS = f"{FOLDER.SETTINGS.value}/user_settings.json"
    DEFAULT_SAVE = f"{FOLDER.SAVE_FILES.value}/default.json"
    DEFAULT_THEME = f"{FOLDER.THEMES.value}/default-theme.json"
