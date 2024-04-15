import tkinter as tk
import customtkinter as ctk
import pystray
import sys

import colorsys

# Custom imports
from CustomLogger import CustomLogger
from Constants import FILE
from FileManager import FileManager
from Updater import Updater
from Instalocker import Instalocker
from CustomElements import ThemedFrame, ThemedLabel, IndependentButton, DependentButton, SideFrame


def brighten_color(hex_color, increase_factor):
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
        self.logger.info("File manager initialized")

        # Loads theme
        self.logger.info("Loading theme")
        self.theme = self.file_manager.get_theme("default-theme.json")
        # Brightens certain colors for hover effects
        for element_to_brighten in ["accent", "button-enabled", "button-disabled"]:
            self.theme[f"{element_to_brighten}-hover"] = brighten_color(
                self.theme[element_to_brighten], 1.1
            )
        self.theme["label"] = (self.theme["font"], 16)
        self.theme["button"] = (self.theme["font"], 14)
        self.logger.info("Theme loaded")

        # Creates an instance of the Updater class
        self.logger.info("Initializing updater")
        self.updater = Updater(self.VERSION)
        self.logger.info("Updater initialized")

        # Checks if the updater check frequency has been met
        # TODO: Uncomment in prod
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
        """

        #region: Default Vars

        # If the Instalocker thread is running
        self.is_thread_running = ctk.BooleanVar()

        # If the Instalocker is Running (true) or Waiting (false)
        self.instalocker_status = ctk.BooleanVar(value=True)

        self.is_thread_running.set(
            True
            if self.file_manager.get_value(FILE.SETTINGS, "ENABLE_ON_STARTUP")
            else False
        )
        
        #endregion

        self.logger.info(f"Run on startup: {self.is_thread_running.get()}")

        self.logger.info("Initializing Instalocker")
        self.instalocker = None
        # TODO: Implement Instalocker

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

        self.frames = {
            "Overview": OverviewFrame(self),
            "Settings": SettingsFrame(self),
        }

        nav_width = 150
        nav_frame = NavigationFrame(self, width=nav_width)
        nav_frame.grid(row=0, column=0, sticky="nswe")
        self.grid_columnconfigure(0, minsize=nav_width)

        for frame in self.frames.values():
            frame.grid(row=0, column=1, sticky="nswe", padx=(10, 10))

        self.frames["Overview"].tkraise()

        #endregion


class NavigationFrame(ctk.CTkFrame):
    def __init__(self, parent, width):
        super().__init__(
            parent, width=width, corner_radius=0, fg_color=parent.theme["foreground"]
        )
        self.parent = parent
        self.theme = parent.theme

        self.title_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.title_frame.pack(pady=10)

        self.title_label_frame = ctk.CTkFrame(self.title_frame, fg_color="transparent")
        self.title_label_frame.pack()

        self.valocker_label_left = ctk.CTkLabel(
            self.title_label_frame,
            text="VAL",
            fg_color="transparent",
            text_color="#BD3944",
            font=(self.parent.theme["font"], 20),
        )
        self.valocker_label_left.pack(side=tk.LEFT)

        self.valocker_label_right = ctk.CTkLabel(
            self.title_label_frame,
            text="ocker",
            fg_color="transparent",
            text_color=self.theme["text"],
            font=(self.parent.theme["font"], 20),
        )
        self.valocker_label_right.pack(side=tk.LEFT)

        self.version_label = ctk.CTkLabel(
            self.title_frame,
            text=f"v{self.parent.VERSION}",
            fg_color="transparent",
            text_color=brighten_color(self.theme["text"], 0.5),
            font=(self.parent.theme["font"], 12),
        )
        self.version_label.pack(pady=0)

        buttons = [
            "Overview",
            "Settings",
        ]

        for button_text in buttons:
            button = ctk.CTkButton(
                self,
                text=button_text,
                height=40,
                width=width,
                corner_radius=0,
                border_spacing=10,
                anchor=tk.W,
                fg_color="transparent",
                text_color=self.theme["text"],
                hover_color=brighten_color(self.theme["foreground"], 1.5),
                font=self.parent.theme["button"],
                command=lambda button=button_text: self.on_button_click(button),
            )
            button.pack(fill=ctk.X)

        self.exit_button = ctk.CTkButton(
            self,
            text="Exit",
            font=self.parent.theme["button"],
            fg_color=self.parent.theme["accent"],
            hover_color=self.parent.theme["accent-hover"],
            corner_radius=5,
            hover=True,
            command=self.quit_program,
        )
        self.exit_button.pack(side=tk.BOTTOM, pady=10, padx=10, fill=tk.X)

    def on_button_click(self, button):
        self.parent.frames[button].tkraise()

    def quit_program(self):
        self.parent.exit()


class OverviewFrame(SideFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.theme = parent.theme

        # Make each frame take up equal space
        for frame in range(3):
            self.grid_columnconfigure(frame, weight=1)

        # Make the frames take up the entire vertical space
        self.grid_rowconfigure(0, weight=1)

        # Segmented Frames
        self.left_frame = ThemedFrame(self, corner_radius=10)
        self.middle_frame = ThemedFrame(self, corner_radius=10)
        self.right_frame = ThemedFrame(self, corner_radius=10)

        # Grid the frames
        for index, frame in enumerate(
            [self.left_frame, self.middle_frame, self.right_frame]
        ):
            frame.configure(fg_color=self.theme["foreground"])
            frame.grid(
                row=0,
                column=index,
                sticky="nsew",
                padx=10 if index == 1 else 0,
                pady=10,
            )
            frame.grid_propagate(False)
            frame.columnconfigure(0, weight=1)

        # Left Frame
        self.program_status_label = ThemedLabel(
            self.left_frame,
            text="Instalocker:",
        )
        self.program_status_label.grid(
            row=0, column=0, sticky="nsew", padx=10, pady=(10, 0)
        )

        self.program_status_button = IndependentButton(
            self.left_frame,
            text=["Enabled", "Disabled"],
            variable=self.parent.is_thread_running,
            command=self.toggle_instalocker,
        )

        self.program_status_button.grid(
            row=1, column=0, sticky="nsew", padx=10, pady=(0, 10)
        )

        self.instalocker_status_label = ThemedLabel(self.left_frame, "Status")
        self.instalocker_status_label.grid(
            row=2, column=0, sticky="nsew", padx=10, pady=(10, 0)
        )

        self.instalocker_status_button = DependentButton(
            self.left_frame,
            variable=self.parent.instalocker_status,
            dependent_variable=self.parent.is_thread_running,
            text=["Locking", "Waiting", "None"],
            command=self.toggle_instalocker_state,
        )

        self.instalocker_status_button.grid(
            row=3, column=0, sticky="nsew", padx=10, pady=(0, 10)
        )

    def toggle_instalocker(self, value=None):
        if value is not None:
            self.parent.is_thread_running.set(value)
        else:
            self.parent.is_thread_running.set(not self.parent.is_thread_running.get())

    def toggle_instalocker_state(self, value=None):
        if value is not None:
            self.parent.instalocker_status.set(value)
        else:
            self.parent.instalocker_status.set(not self.parent.instalocker_status.get())


class SettingsFrame(SideFrame):
    def __init__(self, parent):
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
