import customtkinter as ctk
from typing import Union, Optional
import sys
import time
import os

# Custom imports
from CustomLogger import CustomLogger
from Constants import FILE, FRAME, BRIGHTEN_COLOR
from FileManager import FileManager
from SaveManager import SaveManager
from Updater import Updater
from Instalocker import Instalocker
from Tools import Tools
from ThemeManager import ThemeManager

# UI Imports
from CustomElements import *
from GUIFrames import *


class VALocker(ctk.CTk):
    # VERSION
    VERSION: str = "2.0.0"

    # Custom Classes
    logger: CustomLogger = CustomLogger("VALocker").get_logger()
    file_manager: FileManager = FileManager()
    save_manager: SaveManager = SaveManager(file_manager)
    updater: Updater = Updater(VERSION, file_manager)
    theme_manager: ThemeManager = ThemeManager()
    instalocker: Instalocker
    tools: Tools

    # Variables
    theme: dict[str, str]

    # Variables
    instalocker_thread_running: ctk.BooleanVar
    instalocker_status: ctk.BooleanVar
    safe_mode_enabled: ctk.BooleanVar
    safe_mode_strength: ctk.IntVar
    current_save_name: ctk.StringVar
    selected_agent: ctk.StringVar
    last_lock: ctk.StringVar
    average_lock: ctk.StringVar
    times_used: ctk.StringVar
    agent_times_locked: ctk.StringVar

    # Instalocker Variables

    hover: ctk.BooleanVar
    random_select: ctk.BooleanVar
    exclusiselect: ctk.BooleanVar
    map_specific: ctk.BooleanVar
    agent_index: ctk.IntVar
    box_coords: list

    agent_status: dict[str, tuple[ctk.BooleanVar, ctk.BooleanVar]]

    # Tools Variables
    tools_thread_running: ctk.BooleanVar
    anti_afk: ctk.BooleanVar
    drop_spike: ctk.BooleanVar

    # UI
    frames: Dict[
        FRAME,
        Union[
            OverviewFrame,
            AgentToggleFrame,
            RandomSelectFrame,
            SaveFilesFrame,
            
        ],
    ] = dict()

    def __init__(self):
        super().__init__()

        self.logger.info(f"Initializing VALocker v{self.VERSION}")

        start_time = time.time()

        # Sets up file manager
        self.logger.info("Setting up file manager")
        self.file_manager.setup()

        # Sets up save manager
        self.logger.info("Setting up save manager")
        self.save_manager.setup()

        # Checks for updates
        # self.logger.info("Checking for updates")
        # self.check_for_updates()

        # Loads theme
        self.logger.info("Loading theme")
        theme_name = self.file_manager.get_value(FILE.SETTINGS, "theme")
        self.theme = self.theme_manager.get_theme(theme_name)
        self.logger.info(f'Theme "{theme_name}" loaded')

        # region: Variable Setup

        self.instalocker_thread_running = ctk.BooleanVar(
            value=self.file_manager.get_value(FILE.SETTINGS, "enableOnStartup")
        )

        self.instalocker_status = ctk.BooleanVar(value=True)

        self.safe_mode_enabled = ctk.BooleanVar(
            value=self.file_manager.get_value(FILE.SETTINGS, "safeModeOnStartup")
        )

        self.safe_mode_strength = ctk.IntVar(
            value=self.file_manager.get_value(
                FILE.SETTINGS, "safeModeStrengthOnStartup"
            )
        )

        self.agent_status = {
            agent: (ctk.BooleanVar(value=False), ctk.BooleanVar(value=False))
            for role in self.file_manager.get_value(
                FILE.AGENT_CONFIG, "allAgents"
            ).items()
            for agent in role[1]
        }

        self.agent_status = dict(sorted(self.agent_status.items()))

        self.current_save_name = ctk.StringVar()
        self.selected_agent = ctk.StringVar()

        self.last_lock = ctk.StringVar()
        self.average_lock = ctk.StringVar()
        self.times_used = ctk.StringVar()

        self.update_stats()

        # Instalocker Vars
        self.hover = ctk.BooleanVar(value=False)
        self.random_select = ctk.BooleanVar(value=False)
        self.exclusiselect = ctk.BooleanVar(value=False)
        self.map_specific = ctk.BooleanVar(value=False)
        self.agent_index = ctk.IntVar(value=0)
        self.box_coords = []

        # Tools Vars
        self.tools_thread_running = ctk.BooleanVar(value=False)
        self.anti_afk = ctk.BooleanVar(value=False)
        self.drop_spike = ctk.BooleanVar(value=False)

        # endregion

        # Load save
        self.logger.info("Loading Save")
        self.load_save(self.file_manager.get_value(FILE.SETTINGS, "activeSaveFile"))

        self.logger.info("Creating UI")
        self.initUI()

        # region: Traces

        # Run the agent_unlock_status_changed method when the status of an agent is changed
        # This method is called every time the status of an agent is changed,
        # Even when all of them are changed in a for loop, I might want to revisit
        # This to make it only run once after all of them are changed
        # for variable in self.agent_status.values():
        #     variable[0].trace_add("write", self.agent_unlock_status_changed)

        # Update stats when the safe mode is enabled or the safe mode strength is changed
        self.safe_mode_enabled.trace_add("write", self.update_stats)
        self.safe_mode_strength.trace_add("write", self.update_stats)

        # endregion

        # Initialize Instalocker
        self.logger.info("Initializing Instalocker")
        self.instalocker = Instalocker(self)

        self.logger.info("Managing Instalocker thread")
        self.manage_instalocker_thread()
        self.instalocker_thread_running.trace_add(
            "write", self.manage_instalocker_thread
        )

        # Initialize Tools
        self.logger.info("Initializing Tools")
        self.tools = Tools(self)

        self.logger.info("Managing Tools thread")
        self.manage_tools_thread()
        self.tools_thread_running.trace_add("write", self.manage_tools_thread)

        self.protocol("WM_DELETE_WINDOW", self.exit)

        end_time = time.time()

        self.logger.info(f"VALocker initialized in {end_time - start_time:.2f} seconds")

    def exit(self):
        """
        Saves the current configuration and exits the program.
        """

        self.logger.info("Exiting VALocker")

        # Saves the current configuration
        self.save_data()

        # Exits
        self.destroy()
        sys.exit()

    def check_for_updates(self) -> None:
        """
        Checks for updates and performs necessary actions if updates are available.

        This method checks if the frequency for update checks is met. If it is, it proceeds to check for
        config updates and version updates. If a version update is available, it logs the update and
        provides a placeholder for implementing the update code.

        If the frequency is not met, it logs a message indicating that update checks are skipped.
        """
        if self.updater.check_frequency_met():
            # Checks for config updates
            self.logger.info("Checking for config updates")
            self.updater.check_for_config_updates()

            # Checks for version updates
            self.logger.info("Checking for version updates")
            version_update_available = self.updater.check_for_version_update()

            self.updater.update_last_checked()

            # If version update is available
            if version_update_available:
                self.logger.info("Update available")
                # TODO: Implement update code
        else:
            self.logger.info("Check frequency not met, skipping update checks")

    def update_stats(self, *_) -> None:
        """
        Gets the current stats of the program.

        Args:
            _: Unused.
        """
        stats = self.file_manager.get_config(FILE.STATS)

        # Set times used
        times_used = stats.get("timesUsed", 0)

        if not self.safe_mode_enabled.get():
            time_to_lock = stats.get("timeToLock", None)
        else:
            time_to_lock = stats.get("timeToLockSafe", None)

            if time_to_lock is not None:
                time_to_lock = time_to_lock[self.safe_mode_strength.get()]

        if time_to_lock is None or len(time_to_lock) == 0:
            self.times_used.set("N/A")
            self.average_lock.set("N/A")
            self.last_lock.set("N/A")

            self.logger.info(
                f"Could not retrieve stats for SM:{self.safe_mode_enabled.get()} and SMS:{self.safe_mode_strength.get()}. (They might be unset)"
            )
            return

        if time_to_lock is not None:
            average_lock = sum(time_to_lock) / len(time_to_lock)
            last_lock = time_to_lock[-1]

        self.times_used.set(f"{times_used} times")
        self.average_lock.set(f"{average_lock:.2f} ms")
        self.last_lock.set(f"{last_lock:.2f} ms")

    # region: Thread Management

    def manage_instalocker_thread(self, *args) -> None:
        """
        Manages the Instalocker thread, tied to the `is_thread_running` variable.

        Args:
            *args: Unused.
        """
        if self.instalocker_thread_running.get():
            self.instalocker.start()
        else:
            self.instalocker.stop()

    def manage_tools_thread(self, *args) -> None:
        """
        Manages the Tools thread, tied to the `is_thread_running` variable.

        Args:
            *args: Unused.
        """
        if self.tools_thread_running.get():
            self.tools.start()
        else:
            self.tools.stop()

    # endregion

    # region: UI

    def initUI(self) -> None:
        """
        Initializes the user interface.

        Sets the window size, title, and grid configuration.
        Creates navigation frame and frames for different sections.
        Raises the "Overview" frame by default.
        """
        self.geometry("700x400")
        self.minsize(700, 400)
        # self.resizable(False, False)
        self.title("VALocker")
        self.configure(fg_color=self.theme["background"])
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_propagate(False)

        self.frames = {
            FRAME.OVERVIEW: OverviewFrame(self),
            FRAME.AGENT_TOGGLE: AgentToggleFrame(self),
            # FRAME.RANDOM_SELECT: RandomSelectFrame(self),
            # FRAME.MAP_TOGGLE: SettingsFrame(self),
            FRAME.SAVE_FILES: SaveFilesFrame(self),
            # FRAME.TOOLS: SettingsFrame(self),
            # FRAME.SETTINGS: SettingsFrame(self),
        }

        nav_width = 150
        self.nav_frame = NavigationFrame(self, width=150)
        self.nav_frame.grid(row=0, column=0, sticky="nswe")
        self.grid_columnconfigure(0, minsize=nav_width)

        for frame in self.frames.values():
            frame.grid(row=0, column=1, sticky="nswe", padx=(10, 10))

        self.select_frame(FRAME.SAVE_FILES)

    def select_frame(self, frame: FRAME) -> None:
        """
        Raises the given frame to the front.

        Args:
            frame (FRAME): The enum of the frame to raise.
        """
        frame_obj: SideFrame = self.frames[frame]
        frame_obj.on_raise()
        frame_obj.tkraise()
        self.nav_frame.highlight_button(frame)

    def agent_unlock_status_changed(self, *_) -> None:
        """
        Called when the status of an agent is changed.

        Args:
            _: Unused.
        """
        unlocked_agents = [
            agent[0].capitalize()
            for agent in self.agent_status.items()
            if agent[1][0].get()
        ]

        if not self.selected_agent.get() in unlocked_agents:
            self.selected_agent.set(value=unlocked_agents[0])

        for frame_key, method, *args in [
            (FRAME.OVERVIEW, "update_dropdown", unlocked_agents)
        ]:
            try:
                getattr(self.frames[frame_key], method)(*args)
            except KeyError:
                pass

    # endregion

    # region: Modifying Tkinter Variables

    def toggle_boolean(self, variable: ctk.BooleanVar, value: Optional[bool] = None) -> None:
        """
        Toggles the value of the given boolean variable.

        Args:
            var (ctk.BooleanVar): The boolean variable to toggle.
            value (bool, optional): The value to set the variable to. If not provided, it will be toggled.
        """
        if value is None:
            value = not variable.get()

        variable.set(value)

    def increment_int(self, variable: ctk.IntVar, max: int, value: Optional[int] = None) -> None:
        """
        Increments the value of the given integer variable.

        Args:
            variable (ctk.IntVar): The integer variable to increment.
            max (int): The maximum value the variable can reach. If the value exceeds this, it will be reset to 0.
            value (int, optional): The value to increment by. If not provided, it will be incremented by 1.
        """
        if value is None:
            value = variable.get() + 1

        value = value % max

        variable.set(value)

    # endregion

    # region: Save Management

    def save_data(self) -> None:
        save_data = self.save_manager.get_save_data()
        save_data["selectedAgent"] = self.selected_agent.get().lower()
        save_data["agents"] = {
            agent: [status[0].get(), status[1].get()]
            for agent, status in self.agent_status.items()
        }

        # TODO: Implement This
        save_data["mapSpecificAgents"] = {
            map_name: None
            for map_name in self.file_manager.get_value(FILE.AGENT_CONFIG, "maps")
        }

        self.save_manager.save_file(save_data)

    def load_save(self, save_name: str, save_current_config=False) -> None:
        if save_current_config:
            self.save_data()

        self.save_manager.load_save(save_name)

        self.current_save_name.set(self.save_manager.get_current_save_name())
        self.selected_agent.set(
            value=self.save_manager.get_current_agent().capitalize()
        )

        for agent in self.save_manager.get_agent_status().items():
            self.agent_status[agent[0]][0].set(agent[1][0])
            self.agent_status[agent[0]][1].set(agent[1][1])

        self.agent_unlock_status_changed()

    # endregion


class SettingsFrame(SideFrame):
    def __init__(self, parent: "VALocker"):
        super().__init__(parent)

        label = ThemedLabel(self, text="Settings")
        label.pack()



if __name__ == "__main__":
    root = VALocker()
    root.mainloop()
