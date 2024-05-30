import customtkinter as ctk
from typing import Optional
import sys
import time
from PIL import Image
from threading import Thread

# Custom imports
from CustomLogger import CustomLogger
from Constants import FILE, FRAME, ICON, BRIGHTEN_COLOR
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
    fast_mode_timings: tuple[int, int, int]
    safe_mode_enabled: ctk.BooleanVar
    safe_mode_strength: ctk.IntVar
    safe_mode_timings: list[tuple[int, int]]
    current_save_name: ctk.StringVar
    selected_agent: ctk.StringVar
    last_lock: ctk.StringVar
    average_lock: ctk.StringVar
    times_used: ctk.StringVar
    agent_times_locked: ctk.StringVar

    # Instalocker Variables
    locking_config: dict
    total_agents: int
    hover: ctk.BooleanVar
    random_select_available: ctk.BooleanVar
    random_select: ctk.BooleanVar
    temp_random_agents: dict[str, bool]
    exclusiselect: ctk.BooleanVar
    map_specific: ctk.BooleanVar
    agent_index: ctk.IntVar

    # Tools Variables
    pause_tools_thread: ctk.BooleanVar
    tools_thread_running: ctk.BooleanVar
    anti_afk: ctk.BooleanVar
    drop_spike: ctk.BooleanVar

    # UI
    update_frame: UpdateFrame
    agent_states: dict[str, tuple[ctk.BooleanVar, ctk.BooleanVar] | ctk.BooleanVar]
    frames: Dict[
        FRAME, OverviewFrame | AgentToggleFrame | RandomSelectFrame | SaveFilesFrame
    ] = dict()

    def __init__(self):
        super().__init__()

        self.logger.info(f"Initializing VALocker v{self.VERSION}")

        # Sets up file manager
        self.logger.info("Setting up file manager")
        self.file_manager.setup()

        # Sets up save manager
        self.logger.info("Setting up save manager")
        self.save_manager.setup()

        # Loads theme
        self.logger.info("Loading theme")
        theme_name = self.file_manager.get_value(FILE.SETTINGS, "theme")
        self.theme = self.theme_manager.get_theme(theme_name)
        self.logger.info(f'Theme "{theme_name}" loaded')

        self.load_variables()

        # Load save
        self.logger.info("Loading Save")
        self.load_save(self.file_manager.get_value(FILE.SETTINGS, "activeSaveFile"))

        # Load exit handler
        self.protocol("WM_DELETE_WINDOW", self.exit)

        # Start UI and check for updates
        self.logger.info("Starting UI")
        self.initUI()

        self.after_idle(self.load_threads)

    # region: Setup
    def load_variables(self) -> None:
        self.instalocker_thread_running = ctk.BooleanVar(
            value=self.file_manager.get_value(FILE.SETTINGS, "enableOnStartup")
        )

        self.instalocker_status = ctk.BooleanVar(value=True)

        self.fast_mode_timings = self.file_manager.get_value(
            FILE.SETTINGS, "fastModeTimings"
        )

        self.safe_mode_enabled = ctk.BooleanVar(
            value=self.file_manager.get_value(FILE.SETTINGS, "safeModeOnStartup")
        )

        self.safe_mode_strength = ctk.IntVar(
            value=self.file_manager.get_value(
                FILE.SETTINGS, "safeModeStrengthOnStartup"
            )
        )

        self.safe_mode_timings = self.file_manager.get_value(
            FILE.SETTINGS, "safeModeTimings"
        )

        roles = self.file_manager.get_value(FILE.AGENT_CONFIG, "roles")
        self.all_agents = sorted(
            [
                agent
                for role in roles
                for agent in self.file_manager.get_value(FILE.AGENT_CONFIG, role)
            ]
        )

        default_agents = self.file_manager.get_value(FILE.AGENT_CONFIG, "defaultAgents")
        self.agent_states = {
            agent: (
                (ctk.BooleanVar(value=False), ctk.BooleanVar(value=False))
                if agent not in default_agents
                else (ctk.BooleanVar(value=False),)
            )
            for agent in self.all_agents
        }

        self.current_save_name = ctk.StringVar()
        self.selected_agent = ctk.StringVar()

        self.last_lock = ctk.StringVar()
        self.average_lock = ctk.StringVar()
        self.times_used = ctk.StringVar()

        self.update_stats()

        # Instalocker Vars
        self.locking_config = self.file_manager.get_config(FILE.LOCKING_CONFIG)
        self.total_agents = len(self.all_agents)

        self.hover = ctk.BooleanVar(value=False)
        self.random_select_available = ctk.BooleanVar(value=False)
        self.random_select = ctk.BooleanVar(value=False)
        self.temp_random_agents = None
        self.exclusiselect = ctk.BooleanVar(value=False)
        self.map_specific = ctk.BooleanVar(value=False)
        self.agent_index = ctk.IntVar(value=0)

        # Tools Vars
        self.pause_tools_thread = ctk.BooleanVar(value=False)
        self.tools_thread_running = ctk.BooleanVar(value=False)
        self.anti_afk = ctk.BooleanVar(value=False)
        self.drop_spike = ctk.BooleanVar(value=False)

        # region: Traces

        self.exclusiselect.trace_add("write", self.exclusiselect_toggled)

        # Update icon
        self.instalocker_thread_running.trace_add("write", self.update_title_and_icon)
        self.instalocker_status.trace_add("write", self.update_title_and_icon)

        # Update stats when the safe mode is enabled or the safe mode strength is changed
        self.safe_mode_enabled.trace_add("write", self.update_stats)
        self.safe_mode_strength.trace_add("write", self.update_stats)

        # Change agent index when the agent is changed
        self.selected_agent.trace_add("write", self.set_locking_agent)

        # Pause tools thread when instalocker is running
        self.instalocker_thread_running.trace_add("write", self.manage_tools_pause)
        self.instalocker_status.trace_add("write", self.manage_tools_pause)

        # endregion

    def load_threads(self) -> None:
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

    # endregion

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
        """
        self.logger.info("Checking for config updates")

        for file in self.updater.FILES_TO_CHECK:
            self.updater.check_for_config_update(
                file, self.update_frame.status_variables[file]
            )
            self.update_frame.update()

        # Checks for version updates
        self.logger.info("Checking for version updates")
        version_update_available = self.updater.check_for_version_update(
            self.update_frame.version_variable
        )
        self.update_frame.update()

        self.updater.update_last_checked()

        # If version update is available
        if version_update_available:
            self.logger.info("Update available")
            # TODO: Show update popup

        self.update_frame.finished_checking_updates()
        self.after(1000, self.initMainUI)

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

    def manage_tools_pause(self, *_) -> None:
        """
        Manages the tools thread based on the status of the Instalocker.
        When the instalocker is in the "Locking" state and the tools thread is running, it pauses the tools thread.
        This makes sure the instalocker can run without interference from the tools thread.
        """

        if self.pause_tools_thread.get():
            if self.tools_thread_running.get():
                return

            self.logger.info("Resuming Tools thread")
            self.tools_thread_running.set(True)
            self.pause_tools_thread.set(False)

        elif self.instalocker_thread_running.get():
            if not self.instalocker_status.get():
                return

            if not self.tools_thread_running.get():
                return

            self.logger.info("Pausing Tools thread, Instalocker is locking")
            self.pause_tools_thread.set(True)
            self.tools_thread_running.set(False)

    # endregion

    # region: UI

    def initUI(self) -> None:
        """
        Initializes the user interface.

        Sets the window size and minimum size.
        Updates the title and icon.
        Checks for updates and then initializes the main user interface.
        """

        self.geometry("700x400")
        self.minsize(700, 400)
        self.update_title_and_icon()
        self.configure(fg_color=self.theme["background"])

        self.update_frame = UpdateFrame(self)

        if self.updater.check_frequency_met():
            self.logger.info("Check frequency met, checking for updates")
            self.update_frame.pack(fill="both", expand=True)
            self.update()
            self.after(500, self.check_for_updates)
        else:
            self.initMainUI()

    def initMainUI(self) -> None:
        """
        Initializes the main user interface.

        Sets the grid configuration.
        Creates navigation frame and frames for different sections.
        Raises the "Overview" frame by default.
        """
        # self.resizable(False, False)
        self.update_frame.destroy()
        del self.update_frame

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_propagate(False)

        self.frames = {
            FRAME.OVERVIEW: OverviewFrame(self),
            FRAME.AGENT_TOGGLE: AgentToggleFrame(self),
            FRAME.RANDOM_SELECT: RandomSelectFrame(self),
            # FRAME.MAP_TOGGLE: MapToggleFrame(self),
            FRAME.SAVE_FILES: SaveFilesFrame(self),
            FRAME.TOOLS: ToolsFrame(self),
            FRAME.SETTINGS: SettingsFrame(self),
        }

        nav_width = 150
        self.nav_frame = NavigationFrame(self, width=150)
        self.nav_frame.grid(row=0, column=0, sticky="nswe")
        self.grid_columnconfigure(0, minsize=nav_width)

        for frame in self.frames.values():
            frame.grid(row=0, column=1, sticky="nswe", padx=(10, 10))

        self.agent_unlock_status_changed()
        self.select_frame(FRAME.OVERVIEW)

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
        unlocked_agents = self.get_unlocked_agents()
        unlocked_agents = [agent.capitalize() for agent in unlocked_agents]

        if not self.selected_agent.get() in unlocked_agents:
            self.selected_agent.set(value=unlocked_agents[0])

        for frame_key, method, *args in [
            (FRAME.OVERVIEW, "update_dropdown", unlocked_agents)
        ]:
            try:
                getattr(self.frames[frame_key], method)(*args)
            except KeyError:
                pass

    def update_title_and_icon(self, *_) -> None:
        """
        Manages the program icon and the window title.
        """

        if not self.instalocker_thread_running.get():
            self.iconbitmap(ICON.DISABLED.value)
            self.title("VALocker")
        elif self.instalocker_status.get():
            self.iconbitmap(ICON.LOCKING.value)
            self.title("VALocker - Locking")
        else:
            self.iconbitmap(ICON.WAITING.value)
            self.title("VALocker - Waiting")

    # endregion

    # region: Modifying Tkinter Variables

    def toggle_boolean(
        self, variable: ctk.BooleanVar, value: Optional[bool] = None
    ) -> None:
        """
        Toggles the value of the given boolean variable.

        Args:
            var (ctk.BooleanVar): The boolean variable to toggle.
            value (bool, optional): The value to set the variable to. If not provided, it will be toggled.
        """
        if value is None:
            value = not variable.get()

        variable.set(value)

    def increment_int(
        self, variable: ctk.IntVar, max: int, value: Optional[int] = None
    ) -> None:
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

        save_data["agents"] = {}
        for agent_name, values in self.agent_states.items():
            if len(values) == 1:
                save_data["agents"][agent_name] = (values[0].get(),)
                continue

            save_data["agents"][agent_name] = [values[0].get(), values[1].get()]

        # TODO: SAVE MAP SPECIFIC AGENTS
        for map_name in self.file_manager.get_value(FILE.AGENT_CONFIG, "maps"):
            save_data["mapSpecificAgents"][map_name] = None

        self.save_manager.save_file(save_data)

    def load_save(self, save_name: str, save_current_config=False) -> None:
        if save_current_config:
            self.save_data()

        self.file_manager.set_value(FILE.SETTINGS, "activeSaveFile", save_name)

        try:
            self.save_manager.load_save(save_name)
        except FileNotFoundError:
            self.file_manager.set_value(
                FILE.SETTINGS,
                "activeSaveFile",
                self.save_manager.get_current_save_file(),
            )

        for agent_name, values in self.save_manager.get_agent_status().items():
            if len(values) == 1:
                self.agent_states[agent_name][0].set(values[0])
                continue

            self.agent_states[agent_name][0].set(values[0])
            self.agent_states[agent_name][1].set(values[1])

        self.current_save_name.set(self.save_manager.get_current_save_name())
        self.selected_agent.set(
            value=self.save_manager.get_current_agent().capitalize()
        )

        self.agent_unlock_status_changed()

    # endregion

    def set_locking_agent(self, *_) -> None:
        unlocked_agents = self.get_unlocked_agents()

        index = unlocked_agents.index(self.selected_agent.get().lower())
        self.agent_index.set(index)

    def get_unlocked_agents(self) -> list[str]:
        return sorted(
            [
                agent_name
                for agent_name, values in self.agent_states.items()
                if len(values) == 1 or values[0].get()
            ]
        )

    def exclusiselect_update_gui(self) -> None:
        self.frames[FRAME.RANDOM_SELECT].on_raise()

    def exclusiselect_toggled(self, *_) -> None:
        """
        Called when the exclusive select variable is toggled.

        Creates a temporary dict with the current state of the agents.
        If exclusive select is enabled, it will clone the current state of the agents.
        If exclusive select is disabled, it will set the state of the agents to the temporary dict.
        """
        # If exclusiselect is enabled
        if self.exclusiselect.get():
            # Clone the current state of the agents
            agent_states_clone = self.agent_states.copy()

            # Create a temporary dict with the random agent states
            self.temp_random_agents: dict[str, bool] = dict()

            for agent_name, values in agent_states_clone.items():
                # Used for default agents
                if len(values) == 1:
                    self.temp_random_agents[agent_name] = values[0].get()
                    continue

                # Used for other agents
                self.temp_random_agents[agent_name] = values[1].get()

        # If exlusive select is disabled
        else:
            # If the temp_random_agents is None, return (error handling)
            if self.temp_random_agents is None:
                return

            # For all agents in the temporary dict
            for agent, value in self.temp_random_agents.items():
                # If the agent is a default agent, set the value
                if len(self.agent_states[agent]) == 1:
                    self.agent_states[agent][0].set(value)
                    continue

                # If the agent is not unlocked, continue (error handling)
                if not self.agent_states[agent][0].get():
                    continue

                # Set the value of the agent
                self.agent_states[agent][1].set(value)

            # Clear the temporary dict
            self.temp_random_agents = None

        # Update the random select frame to reflect the changes
        self.frames[FRAME.RANDOM_SELECT].on_raise()


class SettingsFrame(SideFrame):
    def __init__(self, parent: "VALocker"):
        super().__init__(parent)

        scrollable_frame = ThemedScrollableFrame(self, label_text="Settings")
        scrollable_frame.pack(fill="both", expand=True)


if __name__ == "__main__":
    root = VALocker()
    root.mainloop()
