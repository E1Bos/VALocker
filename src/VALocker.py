from __future__ import annotations
from customtkinter import CTk, BooleanVar, StringVar, IntVar
from typing import Optional
from sys import exit as sys_exit

from webbrowser import open as web_open
from threading import Lock
from ctypes import windll

# Custom imports
from CustomLogger import CustomLogger
from Constants import FILE, FOLDER, FRAME, ICON, LOCKING_CONFIG, ANTI_AFK, ROLE, AgentIndex
from FileManager import FileManager
from SaveManager import SaveManager
from Updater import Updater
from Instalocker import Instalocker
from Tools import Tools
from ThemeManager import ThemeManager

# UI Imports
# from CustomElements import *
from GUIFrames import *


class VALocker(CTk):
    """
    VALocker is a tool that quickly locks agents for you in Valorant, along with other tools.
    @author: [E1Bos](https://www.github.com/E1Bos)
    """

    # VERSION
    VERSION: str = "2.1.0"

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
    instalocker_thread_running: BooleanVar
    instalocker_status: BooleanVar
    fast_mode_timings: tuple[int, int, int]
    safe_mode_enabled: BooleanVar
    safe_mode_strength: IntVar
    safe_mode_timings: list[tuple[int, int]]
    current_save_name: StringVar
    selected_agent: StringVar
    last_lock: StringVar
    average_lock: StringVar
    times_used: StringVar
    # agent_times_locked: StringVar

    # Instalocker Variables
    agent_states: dict[str, tuple[BooleanVar, BooleanVar] | BooleanVar]
    instalocker_thread_lock: Lock = Lock()
    total_agents: int
    hover: BooleanVar
    random_select_available: BooleanVar
    random_select: BooleanVar
    temp_random_agents: dict[str, bool]
    exclusiselect: BooleanVar
    map_specific: BooleanVar
    agent_index: AgentIndex

    # Tools Variables
    num_running_tools: int = 0
    tools_thread_lock: Lock = Lock()
    pause_tools_thread: BooleanVar
    tools_thread_running: BooleanVar
    anti_afk: BooleanVar
    anti_afk_mode = ANTI_AFK = ANTI_AFK.RANDOM_CENTERED
    # drop_spike: BooleanVar

    # UI
    update_frame: UpdateFrame = None
    frames: Dict[
        FRAME, OverviewFrame | AgentToggleFrame | RandomSelectFrame | SaveFilesFrame
    ] = dict()

    # Settings Frame
    update_called: bool = False
    start_tools_automatically: BooleanVar

    def __init__(self) -> None:
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
        windll.shell32.SetCurrentProcessExplicitAppUserModelID("VALocker.GUI")

        # Start UI and check for updates
        self.logger.info("Starting UI")
        self.initUI()

        self.after_idle(self.load_threads)

    # region: Setup
    def load_variables(self) -> None:
        """
        Defines all the variables used in the program.

        Runs at the start of the program to define all the variables used in the program.
        """

        self.instalocker_thread_running = BooleanVar(
            value=self.file_manager.get_value(FILE.SETTINGS, "enableOnStartup", False)
        )

        self.instalocker_status = BooleanVar(value=True)

        fast_mode_timings = self.file_manager.get_config(FILE.SETTINGS).get(
            "fastModeTimings", {
                "clickDelay": 0.04,
                "moveDelay": 0.04
            }
        )
        
        self.fast_mode_timings = [
            (
                fast_mode_timings.get("clickDelay")
                if i % 2 == 0
                else fast_mode_timings.get("moveDelay")
            )
            for i in range(5)
        ]
        
        print(self.fast_mode_timings)
            

        self.safe_mode_enabled = BooleanVar(
            value=self.file_manager.get_value(FILE.SETTINGS, "safeModeOnStartup", False)
        )

        self.safe_mode_strength = IntVar(
            value=self.file_manager.get_value(
                FILE.SETTINGS, "safeModeStrengthOnStartup", 0
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
                (BooleanVar(value=False), BooleanVar(value=False))
                if agent not in default_agents
                else (BooleanVar(value=False),)
            )
            for agent in self.all_agents
        }

        self.current_save_name = StringVar()
        self.selected_agent = StringVar()

        self.last_lock = StringVar()
        self.average_lock = StringVar()
        self.times_used = StringVar()

        self.update_stats()

        # Instalocker Vars
        self.total_agents = len(self.all_agents)

        self.hover = BooleanVar(value=False)
        self.random_select_available = BooleanVar(value=False)
        self.random_select = BooleanVar(value=False)
        self.temp_random_agents = None
        self.exclusiselect = BooleanVar(value=False)
        self.map_specific = BooleanVar(value=False)
        self.agent_index = AgentIndex(ROLE.CONTROLLER, 0)

        # Tools Vars
        self.pause_tools_thread = BooleanVar(value=False)
        self.tools_thread_running = BooleanVar(value=False)
        self.anti_afk = BooleanVar(value=False)
        # self.drop_spike = BooleanVar(value=False)

        # Settings Vars
        self.start_tools_automatically = BooleanVar(
            value=self.file_manager.get_value(
                FILE.SETTINGS, "startToolsAutomatically", True
            )
        )

        self.anti_afk_mode = ANTI_AFK.from_name(
            self.file_manager.get_value(FILE.SETTINGS, "antiAfkMode", "Random Centered")
        )

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
        self.change_locking_config(
            self.file_manager.get_locking_config_by_file_name(
                self.file_manager.get_value(FILE.SETTINGS, "lockingConfig")
            )
        )

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
        self.after_idle(self.destroy)
        sys_exit()

    def check_for_updates(self, force_check_update: bool = False) -> None:
        """
        Checks for updates and performs necessary actions if updates are available.
        """
        # Checks for version updates
        self.logger.info("Checking for version updates")

        version_update = self.updater.check_for_version_update(
            main_window=self,
            stringVar=self.update_frame.version_variable,
        )

        # If version update is available
        if version_update is not None:
            self.update_frame.stop_progress()
            self.logger.info("Version update available")

            go_to_update = ConfirmPopup(
                self,
                title="Update Available",
                message=f"VALocker v{version_update} is available\nYou're currently on v{self.VERSION}.\nWould you like to be taken to the download page?",
                default_no=False,
                geometry="400x150",
            ).get_input()

            if go_to_update:
                self.logger.info("Opening update page")
                web_open("https://www.github.com/E1Bos/VALocker/releases/latest/")
                self.exit()
            else:
                self.logger.info("User chose not to update")
                self.update_frame.resume_progress()

        # Checks for config updates
        self.logger.info("Checking for config updates")

        for file in self.updater.ITEMS_TO_CHECK:
            self.updater.check_for_config_update(
                item=file,
                main_window=self,
                stringVar=self.update_frame.status_variables[file],
            )

        # Ensure config files are compatible with the current VALocker version
        def handle_incompatible(config_enum: FILE | LOCKING_CONFIG) -> None:
            self.update_frame.stop_progress()
            self.logger.error(f"Config file '{config_enum.name}' is not compatible")

            go_to_update = ConfirmPopup(
                self,
                title="Update Required",
                message=f"Config file {config_enum.name} is not compatible with this version of VALocker.\nPlease download the latest version or you will not be able to run VALocker.",
                default_no=False,
                geometry="600x150",
            ).get_input()

            if go_to_update:
                self.logger.info("Opening update page")
                web_open("https://www.github.com/E1Bos/VALocker/releases/latest/")
                self.exit()
            else:
                self.logger.info("User chose not to update")
                self.exit()

        for item in self.updater.ITEMS_TO_CHECK:
            if type(item) is FOLDER:

                files = self.file_manager.get_files_in_folder(item)

                for config_file in files:
                    try:
                        config_enum = LOCKING_CONFIG(config_file)

                        if not self.updater.meets_required_version(config_enum):
                            handle_incompatible(config_enum)

                        self.logger.info(
                            f"Config file '{config_enum.name}' is compatible"
                        )

                    except ValueError:
                        data = self.file_manager.get_config(config_file)

                        if (
                            data.get("custom", False)
                            or data.get("version", None) is None
                        ):
                            self.logger.info(
                                f"Found custom config \"{data.get('title')}\", skipping"
                            )
                        else:
                            self.logger.error(
                                f"Failed to parse config file {config_file}"
                            )
            else:
                if not self.updater.meets_required_version(item):
                    handle_incompatible(item)

                self.logger.info(f"Config file '{item}' is compatible")

        self.updater.update_last_checked()
        self.update_frame.finished_checking_updates()

        if force_check_update:
            self.after(
                1000,
                lambda go_to_frame=FRAME.SETTINGS: self.initMainUI(go_to_frame),
            )
        else:
            self.after(1000, lambda: self.initMainUI())

    # region: Thread Management

    def manage_instalocker_thread(self, *args) -> None:
        """
        Manages the Instalocker thread, tied to the `is_thread_running` variable.
        """
        with self.instalocker_thread_lock:
            if self.instalocker_thread_running.get():
                self.instalocker.start()
            else:
                self.instalocker.stop()

    def manage_tools_thread(self, *args) -> None:
        """
        Manages the Tools thread, tied to the `is_thread_running` variable.
        """
        with self.tools_thread_lock:
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

    def autostart_tools(self) -> None:
        """
        Automatically starts the tools thread if the tool is activated from the overview frame.
        """
        if not self.start_tools_automatically.get():
            return

        # If no tools are running, disable tools thread
        if self.num_running_tools == 0:
            self.toggle_boolean(self.tools_thread_running, False)
        else:  # Enable tools thread
            self.toggle_boolean(self.tools_thread_running, True)

    # endregion

    # region: UI

    def initUI(self, force_check_update: bool = False) -> None:
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

        if self.update_frame is not None and type(self.update_frame) is UpdateFrame:
            self.update_frame.destroy()
            del self.update_frame

        self.update_frame = UpdateFrame(self)

        if self.updater.check_frequency_met() or force_check_update:
            if not force_check_update:
                self.logger.info("Check frequency met, checking for updates")
            else:
                self.logger.info("Manually checking for updates")
            self.update_frame.pack(fill="both", expand=True)
            self.update()

            if not self.update_called:
                self.update_called = True
                self.check_for_updates(force_check_update=force_check_update)
        else:
            self.initMainUI()

    def initMainUI(self, open_to_frame: FRAME = FRAME.OVERVIEW) -> None:
        """
        Initializes the main user interface.

        Sets the grid configuration.
        Creates navigation frame and frames for different sections.
        Raises the "Overview" frame by default.
        """
        # self.resizable(False, False)
        try:
            self.update_frame.destroy()
            del self.update_frame
        except Exception as e:
            self.logger.error(f"Error destroying update frame: {e}")
            self.update_frame = None

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_propagate(False)

        if len(self.frames) == 0:
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
            self.nav_frame.grid(row=0, column=0, sticky=ctk.NSEW)
            self.grid_columnconfigure(0, minsize=nav_width)

        for frame in self.frames.values():
            frame.grid(row=0, column=1, sticky=ctk.NSEW, padx=10)

        self.agent_unlock_status_changed()
        self.select_frame(open_to_frame)

        self.update_called = False

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
            self.wm_iconbitmap(ICON.DISABLED.value)
            self.title("VALocker")
        elif self.instalocker_status.get():
            self.wm_iconbitmap(ICON.LOCKING.value)
            self.title("VALocker - Locking")
        else:
            self.wm_iconbitmap(ICON.WAITING.value)
            self.title("VALocker - Waiting")

    # endregion

    # region: Modifying Tkinter Variables

    def toggle_boolean(
        self, variable: BooleanVar, value: Optional[bool] = None
    ) -> None:
        """
        Toggles the value of the given boolean variable.

        Args:
            var (BooleanVar): The boolean variable to toggle.
            value (bool, optional): The value to set the variable to. If not provided, it will be toggled.
        """
        if value is None:
            value = not variable.get()

        variable.set(value)

    def toggle_boolean_and_run_function(
        self, variable: BooleanVar, function, value: Optional[bool] = None
    ) -> None:
        """
        Toggles the value of the given boolean variable and runs the given function.
        """

        if value is None:
            value = not variable.get()

        variable.set(value)
        function()

    def increment_int(
        self, variable: IntVar, max: int, value: Optional[int] = None
    ) -> None:
        """
        Increments the value of the given integer variable.

        Args:
            variable (IntVar): The integer variable to increment.
            max (int): The maximum value the variable can reach. If the value exceeds this, it will be reset to 0.
            value (int, optional): The value to increment by. If not provided, it will be incremented by 1.
        """
        if value is None:
            value = variable.get() + 1

        value = value % max

        variable.set(value)

    # endregion

    # region: Save Management

    def save_data(self, filename: str = None) -> None:
        """Saves the data of the current configuration to the given file.

        Args:
            filename (str, optional): The filename. Defaults to None. If none
                is provided, the current save file will be used.
        """
        save_data = self.save_manager.get_save_data()
        save_data["selectedAgent"] = self.selected_agent.get().lower()

        save_data["agents"] = {}
        for agent_name, values in self.agent_states.items():
            if len(values) == 1:
                save_data["agents"][agent_name] = (values[0].get(),)
                continue

            save_data["agents"][agent_name] = [values[0].get(), values[1].get()]

        # SAVE MAP SPECIFIC AGENTS (when functionality is added, not sure when)
        for map_name in self.file_manager.get_value(FILE.AGENT_CONFIG, "maps"):
            save_data["mapSpecificAgents"][map_name] = None

        self.save_manager.save_file(save_data, filename)

    def load_save(self, save_name: str, save_current_config: bool = False) -> None:
        """
        Loads the given save file and sets the current configuration to it.

        Args:
            save_name (str): the name of the save file to load.
            save_current_config (bool, optional): Whether to save the current file to disk.
                Defaults to False.
        """

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

    # region: Locking Functions
    def get_agent_role_and_index(self, agent: str) -> tuple[ROLE, int]:
        """
        Returns the role and index of the given agent.

        Args:
            agent (str): The agent to get the role and index of.

        Returns:
            tuple[ROLE, int]: The role and index of the agent.
        """
        for role in self.file_manager.get_value(FILE.AGENT_CONFIG, "roles"):
            agents = self.file_manager.get_value(FILE.AGENT_CONFIG, role)

            if agent in agents:
                unlocked_role_agents = [
                    agent for agent in agents if agent in self.get_unlocked_agents()
                ]

                
                return ROLE(role), unlocked_role_agents.index(agent)

        return None

    def set_locking_agent(self, *_) -> None:
        """
        Sets the agent index to the selected agent.
        """
        role, index = self.get_agent_role_and_index(self.selected_agent.get().lower())

        self.agent_index.set_agent(role, index)
        
    def get_unlocked_agents(self) -> list[str]:
        """
        Returns a list of all unlocked agents, sorted alphabetically.
        """
        return sorted(
            [
                agent_name
                for agent_name, values in self.agent_states.items()
                if len(values) == 1 or values[0].get()
            ]
        )

    def change_locking_config(self, file: LOCKING_CONFIG | str) -> None:
        self.instalocker.set_locking_config(file)

        if type(file) is LOCKING_CONFIG:
            file = os.path.basename(file.value)

        self.file_manager.set_value(FILE.SETTINGS, "lockingConfig", file)

    # endregion

    # region: Stats Functions

    def update_stats(self, *_) -> None:
        """
        Gets the current stats of the program.
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

        if time_to_lock is None:
            self.logger.error(
                "Stats field 'timeToLock' or 'timeToLockSafe' is missing from the stats file"
            )

        if time_to_lock is None or len(time_to_lock) == 0:
            self.times_used.set("N/A")
            self.average_lock.set("N/A")
            self.last_lock.set("N/A")

            self.logger.info(
                "Not enough data to calculate average lock time or last lock time"
            )
            return

        if time_to_lock is not None:
            average_lock = sum(time_to_lock) / len(time_to_lock)
            last_lock = time_to_lock[-1]

        self.times_used.set(f"{times_used} times")
        self.average_lock.set(f"{average_lock:.2f} ms")
        self.last_lock.set(f"{last_lock:.2f} ms")

    def add_stat(self, time: float) -> None:
        """
        Adds a stat to the stats file.

        Args:
            time (float): The time it took to lock the agent, in seconds.
        """
        time = round(time * 1000, 2)

        stats = self.file_manager.get_config(FILE.STATS)

        time_to_lock: list[float] = []
        if not self.safe_mode_enabled.get():
            time_to_lock = stats["timeToLock"]
        else:
            time_to_lock = stats["timeToLockSafe"][self.safe_mode_strength.get()]

        time_to_lock.append(time)

        if len(time_to_lock) > 25:
            time_to_lock.pop(0)

        if not self.safe_mode_enabled.get():
            stats["timeToLock"] = time_to_lock
        else:
            stats["timeToLockSafe"][self.safe_mode_strength.get()] = time_to_lock

        stats["timesUsed"] = stats.get("timesUsed", 0) + 1

        self.file_manager.set_config(FILE.STATS, stats)

        self.update_stats()

    # endregion

    # region: ExclusiSelect Functions

    def exclusiselect_update_gui(self) -> None:
        """
        Bound to the exclusiselect variable, updates the GUI to reflect the state of the variable.
        """
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

        # If exclusive select is disabled
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

    # endregion

    # region: Tools Functions
    def next_anti_afk_mode(self) -> ANTI_AFK:
        """
        Changes the anti-afk mode to the next mode in the list and returns the new mode.
        """
        self.anti_afk_mode = self.anti_afk_mode.next()
        self.tools.change_movement_type(self.anti_afk_mode)
        return self.anti_afk_mode

    # endregion


if __name__ == "__main__":
    root = VALocker()
    root.mainloop()
