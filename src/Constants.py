from enum import Enum
import os
from typing import Optional

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

    AGENT_CONFIG: str = f"{FOLDER.DATA.value}/agent_config.yaml"
    LOCKING_CONFIG: str = f"{FOLDER.DATA.value}/locking_config.yaml"
    STATS: str = f"{FOLDER.DATA.value}/stats.yaml"
    SETTINGS: str = f"{FOLDER.SETTINGS.value}/settings.yaml"
    DEFAULT_SAVE: str = f"{FOLDER.SAVE_FILES.value}/default.yaml"
    DEFAULT_THEME: str = f"{FOLDER.THEMES.value}/default-theme.yaml"


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


class Region:
    """
    Represents a region with coordinates, size, and color.

    Attributes:
        x (int): The x-coordinate of the region.
        y (int): The y-coordinate of the region.
        width (int): The width of the region. Default is 1.
        height (int): The height of the region. Default is 1.
        color (tuple[int, int, int]): The color of the region represented as an RGB tuple. The entire area must be this color.

    Raises:
        ValueError: If width or height is less than or equal to 0.
    """

    x: int
    x_end: int
    y: int
    y_end: int
    color: tuple[int, int, int]

    def __init__(
        self,
        x: int,
        y: int,
        color: tuple[int, int, int],
        width: Optional[int] = 1,
        height: Optional[int] = 1,
        x_end: Optional[int] = None,
        y_end: Optional[int] = None,
    ) -> None:

        if (width <= 0 or height <= 0) and (x_end is None or y_end is None):
            raise ValueError(
                "Width and height must be greater than 0 or x_end and y_end must be provided."
            )

        self.x = x
        self.y = y
        self.color = color
        
        self.x_end = x_end or x + width
        self.y_end = y_end or y + height

        self.width = width if width else x_end - x 
        self.height = height if height else y_end - y


    def __repr__(self) -> str:
        return f"Region(x: {self.x} -> {self.x_end}, y: {self.y} -> {self.y_end}, w.h: {self.width} . {self.height}, color: {self.color})"

'''
class Save():
    """
    Represents a save file with a name and data.

    Attributes:
        name (str): The name of the save file.
        data (dict): The data of the save file.
    """

    name: str
    selectedAgent: str
    agents: dict[str, tuple[bool, bool] | tuple[bool]]
    maps: dict[str, str | None]

    def __init__(self, name: str) -> None:
        self.name = name
        
    def set_selected_agent(self, agent: str) -> None:
        self.selectedAgent = agent
    
    def set_agents(self, agents: dict[str, tuple[bool, bool] | tuple[bool]]) -> None:
        self.agents = agents
    
    def set_maps(self, maps: dict[str, str | None]) -> None:
        self.maps = maps
        
    def get_all_data(self) -> dict:
        return {
            "selectedAgent": self.selectedAgent,
            "agents": self.agents,
            "mapSpecificAgents": self.maps
        }

    def __repr__(self) -> str:
        return f"Save(name={self.name}, data={self.data})"

    def __str__(self) -> str:
        return f"{self.name}"
'''

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
