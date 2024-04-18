from enum import Enum
import os
import colorsys


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

    # Specific folder to use (None for AppData/roaming)
    STORAGE_FOLDER = "app_defaults"
    # STORAGE_FOLDER = None
    UI_FOLDER = "ui_files"

    # Where default files are stored
    DEFAULTS = "app_defaults"

    # Name of parent folder
    PARENT_FOLDER = "VALocker"

    # Folders in parent folder
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


class FRAME(Enum):
    """
    Emum for frame names used in the project
    """

    OVERVIEW = "Overview"
    AGENT_TOGGLE = "Agent Toggle"
    RANDOM_SELECT = "Random Select"
    MAP_TOGGLE = "Map Toggle"
    SAVE_FILES = "Save Files"
    TOOLS = "Tools"
    SETTINGS = "Settings"


def GET_WORKING_DIR():
    """
    Returns the working directory of the project
    """
    if FOLDER.STORAGE_FOLDER.value:
        return FOLDER.STORAGE_FOLDER.value
    else:
        return os.path.join(os.environ["APPDATA"], FOLDER.PARENT_FOLDER.value)