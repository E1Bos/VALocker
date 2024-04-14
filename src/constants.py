from enum import Enum


class Urls(Enum):
    """
    Enum for URLs used in the project
    """

    DOWNLOAD_URL = "https://raw.githubusercontent.com/E1Bos/VALocker/valocker-v2"
    RELEASE_URL = "https://github.com/E1Bos/VALocker/releases/latest"
    API_RELEASE_URL = "https://api.github.com/repos/E1Bos/VALocker/releases/latest"


class Folders(Enum):
    """
    Enum for Folders used in the project
    """

    TEMPLATE_FOLDER_NAME = "app_defaults"


class Files(Enum):
    """
    Enum for Files used in the project
    """

    AGENT_CONFIG = "data/agent_config.json"
    LOCKING_INFO = "data/locking_info.json"
    STATS = "data/stats.json"
    SETTINGS = "settings/settings.json"
    USER_SETTINGS = "settings/user_settings.json"
    DEFAULT_SAVE = "save_files/default.json"
