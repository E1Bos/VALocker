"""
@author: [E1Bos](https://www.github.com/E1Bos)
"""

from __future__ import annotations
from enum import Enum
import os
import sys
from typing import Optional

LOGGER_LEVEL = "INFO"

def RESOURCE_PATH(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class URL(Enum):
    """
    Enum for URLs used in the project
    """

    DOWNLOAD_URL: str = "https://raw.githubusercontent.com/E1Bos/VALocker/main"
    RELEASE_URL: str = "https://github.com/E1Bos/VALocker/releases/latest"
    API_RELEASE_URL: str = "https://api.github.com/repos/E1Bos/VALocker/releases/latest"


class FOLDER(Enum):
    """
    Enum for Folders used in the project
    """

    # Specific folder to use (None for AppData/roaming)
    # Defaults to AppData/roaming if not in debug mode
    STORAGE_FOLDER: str = "app_defaults" if "--debug" in sys.argv else None

    # Where default files are stored
    DEFAULTS: str = "app_defaults"

    # Name of parent folder
    PARENT_FOLDER: str = "VALocker"

    # Folders in parent folder
    SAVE_FILES: str = "save-files"
    DATA: str = "data"
    LOCKING_CONFIGS: str = f"{DATA}/locking-configs"
    LOGS: str = "logs"
    SETTINGS: str = "settings"
    THEMES: str = "themes"


class FILE(Enum):
    """
    Enum for Files used in the project
    """

    AGENT_CONFIG: str = f"{FOLDER.DATA.value}/agent-config.yaml"
    STATS: str = f"{FOLDER.DATA.value}/stats.yaml"
    SETTINGS: str = f"{FOLDER.SETTINGS.value}/settings.yaml"
    DEFAULT_SAVE: str = f"{FOLDER.SAVE_FILES.value}/default.yaml"
    DEFAULT_THEME: str = f"{FOLDER.THEMES.value}/default-theme.yaml"

    @property
    def download_url(self) -> str:
        return f"{URL.DOWNLOAD_URL.value}/app_defaults/{self.value}"

    @property
    def file_name(self) -> str:
        return self.value.split("/")[-1]


class LOCKING_CONFIG(Enum):
    """
    Enum for Locking Configs used in the project
    """

    CONFIG_1920_1080_16_9: str = "locking-config-1920-1080-16-9.yaml"
    CONFIG_1650_1080_16_10: str = "locking-config-1680-1050-16-10.yaml"
    CONFIG_1280_1024_5_4: str = "locking-config-1280-1024-5-4.yaml"

    # Sets all values to the full path
    def __getattribute__(self, name):
        if name == "value":
            return f"{FOLDER.LOCKING_CONFIGS.value}/{super().__getattribute__(name)}"
        else:
            return super().__getattribute__(name)

    @property
    def download_url(self) -> str:
        return f"{URL.DOWNLOAD_URL.value}/app_defaults/{self.value}"


class FRAME(Enum):
    """
    Enum for frame names used in the project
    """

    OVERVIEW: str = "Overview"
    AGENT_TOGGLE: str = "Agent Toggle"
    RANDOM_SELECT: str = "Random Select"
    MAP_TOGGLE: str = "Map Toggle"
    SAVE_FILES: str = "Save Files"
    TOOLS: str = "Tools"
    SETTINGS: str = "Settings"


class ICON(Enum):
    DEFAULT: str = "valocker.ico"
    DISABLED: str = "valocker-disabled.ico"
    LOCKING: str = "valocker-locking.ico"
    WAITING: str = "valocker-waiting.ico"

    NEW_FILE: str = "new_file.png"
    DELETE: str = "delete.png"
    FAVORITE_ON: str = "favorite_on.png"
    FAVORITE_OFF: str = "favorite_off.png"
    RENAME: str = "rename.png"

    def __getattribute__(self, name):
        if name == "value":
            return RESOURCE_PATH(f"images/icons/{super().__getattribute__(name)}")
        else:
            return super().__getattribute__(name)


class AgentIndex:
    _role: ROLE
    _index: int

    def __init__(self, role: ROLE, index: int) -> None:
        self._role = role
        self._index = index

    def set_agent(self, role: ROLE, index: int) -> None:
        self._role = role
        self._index = index

    def get_agent(self) -> tuple[ROLE, int]:
        return (self._role, self._index)

    @property
    def role(self) -> ROLE:
        return self._role

    @property
    def index(self) -> int:
        return self._index


class AgentGrid:
    _rows: int
    _columns: int

    def __init__(self, rows: int, columns: int) -> None:
        self._rows = rows
        self._columns = columns

    def set_grid(self, rows: int, columns: int) -> None:
        self._rows = rows
        self._columns = columns

    def get_grid(self) -> tuple[int, int]:
        return (self._rows, self._columns)

    @property
    def rows(self) -> int:
        return self._rows

    @property
    def columns(self) -> int:
        return self._columns


class ROLE(Enum):
    """
    Enum for agent roles
    """

    DEFAULT: str = "default"
    DUELIST: str = "duelist"
    CONTROLLER: str = "controller"
    INITIATOR: str = "initiator"
    SENTINEL: str = "sentinel"

    @classmethod
    def from_name(cls, name: str) -> ROLE:
        """
        Returns the enum member with the name given, if not found returns the first member.
        """
        for member in cls:
            if member.name == name:
                return member
        return next(iter(cls))


class ANTI_AFK(Enum):
    """
    ### Enum for Anti-AFK movement types

    CENTERED: Random key presses but end up back in the center
    STRAFE: Go right to left
    RANDOM: Random key presses
    CIRCLE: Go in a circle

    ### Methods
    next: Returns the next movement type in the enum
    """

    CENTERED = "Centered"
    STRAFE = "Strafe"
    RANDOM = "Random"
    CIRCLE = "Circle"

    def next(self) -> ANTI_AFK:
        members = list(ANTI_AFK)
        current_index = members.index(self)
        next_index = (current_index + 1) % len(members)
        return members[next_index]

    @property
    def index(self) -> int:
        return list(ANTI_AFK).index(self)

    @classmethod
    def from_name(cls, name: str) -> ANTI_AFK:
        """
        Returns the enum member with the name given, if not found returns the first member.
        """
        for member in cls:
            if member.name == name:
                return member
        return next(iter(cls))


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
        location (tuple[int, int]): The top left corner of the region represented as an (x, y) tuple.
        size (tuple[int, int]): The width and height of the region represented as a (width, height) tuple.
        color (tuple[int, int, int]): The color of the region represented as an RGB tuple. The entire area must be this color.
        location_end (tuple[int, int]): The bottom right corner of the region represented as an (x, y) tuple.

    Raises:
        ValueError: If width or height is less than or equal to 0.
    """

    location: tuple[int, int]
    size: tuple[int, int]
    color: tuple[int, int, int]
    location_end: tuple[int, int]

    def __init__(
        self,
        location: tuple[int, int],
        color: tuple[int, int, int],
        size: tuple[int, int] = (1, 1),
        location_end: Optional[tuple[int, int]] = None,
    ) -> None:

        if (size[0] <= 0 or size[1] <= 0) and (location_end is None):
            raise ValueError(
                "Width and height must be greater than 0 or x_end and y_end must be provided."
            )

        self.location = location
        self.color = color

        self.location_end = (
            location_end
            if location_end
            else (location[0] + size[0], location[1] + size[1])
        )

        self.size = size

    def __repr__(self) -> str:
        return f"Region(x: {self.location[0]} -> {self.location_end[0]}, y: {self.location[1]} -> {self.location_end[1]}, w.h: {self.size[0]} . {self.size[1]}, color: {self.color})"

    @property
    def x(self) -> int:
        return self.location[0]

    @property
    def y(self) -> int:
        return self.location[1]

    @property
    def x_end(self) -> int:
        return self.location_end[0]

    @property
    def y_end(self) -> int:
        return self.location_end[1]

    @property
    def width(self) -> int:
        return self.size[0]

    @property
    def height(self) -> int:
        return self.size[1]

    @property
    def center(self) -> tuple[int, int]:
        return (self.x + self.width // 2, self.y + self.height // 2)

    @property
    def as_tuple(self) -> tuple[int, int, int, int]:
        return (
            self.location[0],
            self.location[1],
            self.location_end[0],
            self.location_end[1],
        )

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

# endregion
