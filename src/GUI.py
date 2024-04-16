import customtkinter as ctk
import pystray
import sys

# Custom imports
from CustomLogger import CustomLogger
from ProjectUtils import FILE, BRIGHTEN_COLOR
from FileManager import FileManager
from SaveManager import SaveManager
from Updater import Updater
from Instalocker import Instalocker
from Tools import Tools
from CustomElements import *
from GUIFrames import *


class GUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.VERSION = "2.0.0"

        # Sets up logging
        self.logger = CustomLogger("GUI").get_logger()

        self.logger.info(f"Initializing VALocker v{self.VERSION}")

        # Creates an instance of the FileManager class and initializes it
        self.logger.info("Initializing file manager")
        self.file_manager = FileManager()
        self.file_manager.setup()

        # Creates an instance of the SaveManager class and initializes it
        self.logger.info("Initializing save manager")
        self.save_manager = SaveManager(self.file_manager)
        self.save_manager.setup()
        self.save_manager.set_active(
            self.file_manager.get_value(FILE.USER_SETTINGS, "ACTIVE_SAVE_FILE")
        )

        # Creates an instance of the Updater class
        self.logger.info("Initializing updater")
        self.updater = Updater(self.VERSION, self.file_manager)
        # TODO: Uncomment in prod: self.check_for_updates()

        # Loads theme
        self.logger.info("Loading theme")
        theme_name = self.file_manager.get_value(FILE.SETTINGS, "THEME")
        self.theme = self.file_manager.get_theme(theme_name)
        self.setup_theme()
        self.logger.info(f'Theme "{theme_name}" loaded')

        # region: Default Vars

        # If the Instalocker thread is running
        self.is_thread_running = ctk.BooleanVar()

        # If the Instalocker is Running (true) or Waiting (false)
        self.instalocker_status = ctk.BooleanVar(value=True)

        # Safe Mode Enabled
        self.safe_mode_enabled = ctk.BooleanVar()

        # Safe Mode Strength, 0=Low, 1=Medium, 2=High
        self.safe_mode_strength = ctk.IntVar()

        # Current Save
        self.current_save_name = ctk.StringVar()

        # Selected Agent
        self.selected_agent = ctk.StringVar()
        self.agent_unlock_status = {
            agent: ctk.BooleanVar(value=False)
            for agent in self.save_manager.get_agent_names()
        }
        self.agent_random_status = {
            agent: ctk.BooleanVar(value=False)
            for agent in self.save_manager.get_agent_names()
        }

        # Stats
        self.last_lock = ctk.StringVar()
        self.average_lock = ctk.StringVar()
        self.times_used = ctk.StringVar()

        self.setup_vars()
        # endregion

        self.logger.info(f"Run on startup: {self.is_thread_running.get()}")

        self.logger.info("Initializing Instalocker")
        self.instalocker = Instalocker()

        self.logger.info("Initializing Tools")
        self.tools = Tools()

        self.load_save()

        self.logger.info("Creating UI")
        self.initUI()

    def exit(self):
        """
        Stops the icon and destroys the GUI window, then exits the program.
        """
        try:
            self.icon.stop()
        except AttributeError:
            pass

        self.destroy()
        sys.exit()

    def setup_theme(self):
        """
        Sets up the theme for the GUI.
        """
        # Brightens certain colors for hover effects
        for element_to_brighten in [
            "accent",
            "button-enabled",
            "button-disabled",
            "foreground-highlight",
        ]:
            self.theme[f"{element_to_brighten}-hover"] = BRIGHTEN_COLOR(
                self.theme[element_to_brighten], 1.1
            )
        self.theme["label"] = (self.theme["font"], 16)
        self.theme["button"] = (self.theme["font"], 14)

    def check_for_updates(self) -> None:
        """
        Checks for updates and performs necessary actions if updates are available.

        This method checks if the frequency for update checks is met. If it is, it proceeds to check for
        config updates and version updates. If a version update is available, it logs the update and
        provides a placeholder for implementing the update code.

        If the frequency is not met, it logs a message indicating that update checks are skipped.
        """
        if self.updater.check_frequency_met(self.file_manager):
            # Checks for config updates
            self.logger.info("Checking for config updates")
            self.updater.check_for_config_updates(self.file_manager)

            # Checks for version updates
            self.logger.info("Checking for version updates")
            version_update_available = self.updater.check_for_version_update()

            self.updater.update_last_checked(self.file_manager)

            # If version update is available
            if version_update_available:
                self.logger.info("Update available")
                # TODO: Implement update code
        else:
            self.logger.info("Check frequency not met, skipping update checks")

    def setup_vars(self):
        self.is_thread_running.set(
            self.file_manager.get_value(FILE.SETTINGS, "ENABLE_ON_STARTUP")
        )

        self.safe_mode_enabled.set(
            self.file_manager.get_value(FILE.SETTINGS, "SAFE_MODE_ON_STARTUP")
        )

        self.safe_mode_strength.set(
            self.file_manager.get_value(FILE.SETTINGS, "SAFE_MODE_STRENGTH_ON_STARTUP")
        )

        self.update_stats()
        self.load_save()

    def update_stats(self) -> None:
        """
        Gets the current stats of the program.
        """
        stats = self.file_manager.get_config(FILE.STATS)

        # Set times used
        times_used = stats.get("TIMES_USED", 0)

        if not self.safe_mode_enabled.get():
            time_to_lock = stats.get("TTL", None)
        else:
            time_to_lock = stats.get("TTL_SAFE", None)

            if time_to_lock is not None:
                time_to_lock = time_to_lock[self.safe_mode_strength.get()]

        if time_to_lock is None or len(time_to_lock) == 0:
            self.times_used.set("N/A")
            self.average_lock.set("N/A")
            self.last_lock.set("N/A")

            self.logger.warning(
                f"Could not retrieve stats for SM:{self.safe_mode_enabled.get()} and SMS:{self.safe_mode_strength.get()}. (They might be unset)"
            )
            return

        if time_to_lock is not None:
            average_lock = sum(time_to_lock) / len(time_to_lock)
            last_lock = time_to_lock[-1]

        self.times_used.set(f"{times_used} times")
        self.average_lock.set(f"{average_lock:.2f} ms")
        self.last_lock.set(f"{last_lock:.2f} ms")

    def load_save(self) -> None:
        """
        Updates the current save file.
        """
        self.current_save_name.set(self.save_manager.get_current_save_name())
        self.selected_agent.set(self.save_manager.get_current_agent())

        for agent, status in self.save_manager.get_agents_status().items():
            self.agent_unlock_status[agent].set(status)

        for agent, status in self.save_manager.get_random_dict().items():
            self.agent_random_status[agent].set(status)

        # TODO: Load map specific

    def initUI(self) -> None:
        """
        Initializes the user interface.

        Sets the window size, title, and grid configuration.
        Creates navigation frame and frames for different sections.
        Raises the "Overview" frame by default.
        """
        self.geometry("700x400")
        self.minsize(700, 400)
        # TODO: Implement resizing
        # self.resizable(False, False)
        self.title("VALocker")
        self.configure(fg_color=self.theme["background"])
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_propagate(False)

        self.frames = dict()

        self.frames = {
            "Overview": OverviewFrame(self),
            "Agent Toggle": AgentToggleFrame(self),
            "Random Select": RandomSelectFrame(self),
            "Map Specific": SettingsFrame(self),
            "Save Files": SettingsFrame(self),
            "Tools": SettingsFrame(self),
            "Settings": SettingsFrame(self),
        }

        nav_width = 150
        self.nav_frame = NavigationFrame(self, width=nav_width)
        self.nav_frame.grid(row=0, column=0, sticky="nswe")
        self.grid_columnconfigure(0, minsize=nav_width)

        for frame in self.frames.values():
            frame.grid(row=0, column=1, sticky="nswe", padx=(10, 10))

        self.select_frame("Overview")

    def select_frame(self, frame_name: str) -> None:
        """
        Raises the frame with the given name and lowers all other frames.

        Args:
            frame_name (str): The name of the frame to raise.
        """
        self.nav_frame.highlight_button(frame_name)
        self.frames[frame_name].tkraise()
        self.frames[frame_name].on_raise()


class SettingsFrame(SideFrame):
    def __init__(self, parent: "GUI"):
        super().__init__(parent)
        self.parent = parent
        self.theme = parent.theme

        self.label = ctk.CTkLabel(
            self,
            text="Settings",
            font=self.parent.theme["label"],
            fg_color="transparent",
            text_color=("gray10", "gray90"),
        )
        self.label.pack()


if __name__ == "__main__":
    root = GUI()
    root.mainloop()
