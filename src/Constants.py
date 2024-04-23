from enum import Enum
import os

# Profile Imports
from cProfile import Profile
from pstats import Stats
from functools import wraps

def RESOURCE_PATH(relative_path: str) -> str:
    return os.path.join(
        os.environ.get("_MEIPASS2", os.path.abspath(".")), relative_path
    )


class URL(Enum):
    """
    Enum for URLs used in the project
    """

    DOWNLOAD_URL: str = "https://raw.githubusercontent.com/E1Bos/VALocker/valocker-v2"
    RELEASE_URL: str = "https://github.com/E1Bos/VALocker/releases/latest"
    API_RELEASE_URL: str = "https://api.github.com/repos/E1Bos/VALocker/releases/latest"


class FOLDER(Enum):
    """
    Enum for Folders used in the project
    """

    # Specific folder to use (None for AppData/roaming)
    STORAGE_FOLDER: str = "app_defaults"
    # STORAGE_FOLDER: str = None

    # Where default files are stored
    DEFAULTS: str = "app_defaults"

    # Name of parent folder
    PARENT_FOLDER: str = "VALocker"

    # Folders in parent folder
    SAVE_FILES: str = "save_files"
    DATA: str = "data"
    LOGS: str = "logs"
    SETTINGS: str = "settings"
    THEMES: str = "themes"


class FILE(Enum):
    """
    Enum for Files used in the project
    """

    AGENT_CONFIG: str = f"{FOLDER.DATA.value}/agent_config.json"
    LOCKING_INFO: str = f"{FOLDER.DATA.value}/locking_config.json"
    STATS: str = f"{FOLDER.DATA.value}/stats.json"
    SETTINGS: str = f"{FOLDER.SETTINGS.value}/settings.json"
    DEFAULT_SAVE: str = f"{FOLDER.SAVE_FILES.value}/default.json"
    DEFAULT_THEME: str = f"{FOLDER.THEMES.value}/default-theme.json"


class FRAME(Enum):
    """
    Emum for frame names used in the project
    """

    OVERVIEW: str = "Overview"
    AGENT_TOGGLE: str = "Agent Toggle"
    RANDOM_SELECT: str = "Random Select"
    MAP_TOGGLE: str = "Map Toggle"
    SAVE_FILES: str = "Save Files"
    TOOLS: str = "Tools"
    SETTINGS: str = "Settings"

class ICON(Enum):
    ICON_PATH: str = "images/icons"
    
    DISABLED: str = RESOURCE_PATH(f"{ICON_PATH}/valocker-disabled.ico")
    LOCKING: str = RESOURCE_PATH(f"{ICON_PATH}/valocker-locking.ico")
    WAITING: str = RESOURCE_PATH(f"{ICON_PATH}/valocker-waiting.ico")
    
    NEW_FILE: str = RESOURCE_PATH(f"{ICON_PATH}/new_file.png")
    DELETE: str = RESOURCE_PATH(f"{ICON_PATH}/delete.png")
    FAVORITE_ON: str = RESOURCE_PATH(f"{ICON_PATH}/favorite_on.png")
    FAVORITE_OFF: str = RESOURCE_PATH(f"{ICON_PATH}/favorite_off.png")
    RENAME: str = RESOURCE_PATH(f"{ICON_PATH}/rename.png")

def GET_WORKING_DIR() -> str:
    """
    Returns the working directory of the project
    """
    if FOLDER.STORAGE_FOLDER.value:
        return FOLDER.STORAGE_FOLDER.value
    else:
        return os.path.join(os.environ["APPDATA"], FOLDER.PARENT_FOLDER.value)


def BRIGHTEN_COLOR(color: str, factor: float) -> str:
    """
    Brightens a color by a factor
    """
    color = color.lstrip("#")
    r = int(color[0:2], 16)
    g = int(color[2:4], 16)
    b = int(color[4:6], 16)
    r = min(int(r * factor), 255)
    g = min(int(g * factor), 255)
    b = min(int(b * factor), 255)
    return f"#{r:02x}{g:02x}{b:02x}"




# region: Profiler


def profile(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        profiler = Profile()
        profiler.enable()
        result = func(*args, **kwargs)
        profiler.disable()

        print(f"\n\nStats for {func.__name__}:")
        stats = Stats(profiler)
        stats.strip_dirs()
        stats.sort_stats("cumulative")
        stats.print_stats()
        return result

    return wrapper


# endregion
