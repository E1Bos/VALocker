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
    STORAGE_FOLDER = "app_defaults/"
    # STORAGE_FOLDER = None

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


def GET_WORKING_DIR():
    """
    Returns the working directory of the project
    """
    if FOLDER.STORAGE_FOLDER.value:
        return FOLDER.STORAGE_FOLDER.value
    else:
        return os.path.join(os.environ["APPDATA"], FOLDER.PARENT_FOLDER.value)


def BRIGHTEN_COLOR(hex_color, increase_factor):
    # Remove the '#' from the start of hex_color
    hex_color = hex_color.lstrip("#")

    # Convert hex color to RGB
    rgb_color = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))

    # Convert RGB to HLS
    h, l, s = colorsys.rgb_to_hls(
        rgb_color[0] / 255.0, rgb_color[1] / 255.0, rgb_color[2] / 255.0
    )

    # Increase the lightness
    l = max(min(l * increase_factor, 1), 0)

    # Convert back to RGB
    r, g, b = colorsys.hls_to_rgb(h, l, s)

    # Convert RGB back to hex and return with '#'
    return "#{:02x}{:02x}{:02x}".format(int(r * 255), int(g * 255), int(b * 255))
