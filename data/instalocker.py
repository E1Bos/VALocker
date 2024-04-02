"""
MIT License

Copyright (c) 2024 E1Bos

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

## ADD SUPPORT FOR 1440x1080 4:3


# region Imports

import sys

# Imports all modules, if it fails it will install them
if getattr(sys, "frozen", True):
    try:
        # Modules that are not installed by default
        import customtkinter, pystray, PIL.Image, mss, requests
        import pynput.mouse as pynmouse
        import pynput.keyboard as pynkeyboard
        import numpy as np

    except ModuleNotFoundError:
        # Installs missing modules if exception is raised
        import subprocess

        subprocess.run(["pip", "install", "-r", "requirements.txt"])

        import customtkinter, pystray, PIL.Image, mss, requests
        import pynput.mouse as pynmouse
        import pynput.keyboard as pynkeyboard
        import numpy as np

    # Imports modules that are installed with Python
    import json, os, random, threading, time, ctypes, shutil, re, webbrowser, sys
    import tkinter as tk

# endregion


# region PyInstaller Requirement
def resource_path(relative):
    return os.path.join(os.environ.get("_MEIPASS2", os.path.abspath(".")), relative)


# endregion


# region Customtkinter Global Settings
customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("dark-blue")
# endregion


class InstalockerGUIMain(customtkinter.CTk):
    # region Init and Exit Function

    def __init__(self):
        super().__init__()

        # Version
        CURRENT_VERSION = "v1.6.0"

        # Locking Variables
        self.coords = {
            # Locking Screen
            "locking": (947, 782, 952, 783),
            # Finding Menu
            "main_menu": (815, 243, 820, 244),
            "play_button": (920, 45, 930, 50),
            "progress_text": (1325, 337, 1327, 349),
            "progress_text_ranked": (1477, 337, 1479, 349),
            # Tools
            "spectating": (135, 856, 138, 861),
            "has_spike": (1852, 684, 1856, 687),
            "can_plant": (910, 140, 920, 141),
            "is_planting": (832, 174, 833, 193),
        }
        self.pixel_patterns = {
            # Locking Screen
            "locking": (234, 238, 178),
            # Menu Screen
            "main_menu": (246, 244, 240),
            "red_button": (216, 57, 70),
            # Tools
            "spectating": (170, 237, 225),
            "is_planting": (235, 238, 178),
            # Pure White (Used by menu screen and tools)
            "pure_white": (255, 255, 255),
        }
        self.enabled = False
        self.active_thread = True
        self.locking = True
        self.map_selection_coords = (878, 437, 1047, 646)
        self.agent_coords_offset = (15, 15)

        # Tool Variables
        self.running_tools = set()
        self.enable_tools = False
        self.tools_thread = None
        self.auto_drop_spike = False
        self.spike_drop_confirmations_required = 2
        self.anti_afk = False
        self.register_keyboard_input = True
        self.anti_aim = False
        self.chat_is_open = False

        # GUI Settings
        self.window_width = 650
        self.window_height = 400
        self.main_font = "Roboto"
        self.label_font_and_size = (self.main_font, 16)
        self.button_font_and_size = (self.main_font, 14)
        self.title("VALocker")
        self.button_colors = {"enabled": "sea green", "disabled": "#b52d3b"}
        self.role_colors = {
            "controllers": "#f5a623",
            "controllers_disabled": "#ae7008",
            "duelists": "#e91e63",
            "duelists_disabled": "#9c0f3f",
            "initiators": "#2196f3",
            "initiators_disabled": "#0963aa",
            "sentinels": "#4caf50",
            "sentinels_disabled": "#317234",
        }

        # Modes
        self.map_specific_mode = False
        self.random_agent_mode = False
        self.hover_mode = False
        self.random_agent_exclusiselect = False

        # Safe Mode
        self.safe_mode = True
        self.safe_mode_strength = 0
        self.safe_mode_timing = {
            "Low": (0.2, 0.4),
            "Medium": (0.4, 0.7),
            "High": (0.7, 1.0),
        }

        # Default/Empty Variables
        self.current_save_file = "default"
        self.box_coords = dict()
        self.lock_button = list()
        self.favorited_save_files = list()
        self.default_agents = list()
        self.selected_agent = str()
        self.all_agents = list()
        self.map_lookup = dict()
        self.save_files = list()
        self.current_account_id = None
        self.grab_keybinds = False
        self.is_1920x1080 = True

        # Stats
        self.total_games_used = 0
        self.time_to_lock_list = list(
            list() for _ in range(len(self.safe_mode_timing) + 1)
        )

        # Icons
        self.icons = dict(
            disabled="images/icons/valocker-disabled.ico",
            locking="images/icons/valocker-locking.ico",
            waiting="images/icons/valocker-waiting.ico",
        )
        self.current_icon = self.icons["disabled"]
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("VALocker.GUI")

        # Finds the latest version
        latest_version = self.get_latest_version()
        if latest_version is not None:
            needs_update = self.compare_versions(CURRENT_VERSION, latest_version)
            if needs_update:
                update_now = UpdatePopup(
                    window_geometry=self.winfo_geometry(),
                    current_version=CURRENT_VERSION,
                    latest_version=latest_version,
                    colors=self.button_colors,
                    main_font=self.main_font,
                ).get_input()

                # Opens the latest release page and closes the program if the
                # user wants to update
                if update_now:
                    webbrowser.open(
                        "https://www.github.com/E1Bos/VALocker/releases/latest/"
                    )
                    self.exit()
                    sys.exit()

        # Defines Controllers
        self.mouse = pynmouse.Controller()
        self.keyboard = pynkeyboard.Controller()
        self.locking_screenshotter = None
        self.tools_screenshotter = None
        self.tools_keyboard_listener = None

        # Finds all save files
        self.find_save_files()

        # Loads data from save files
        self.load_data_from_files(first_run=True)

        # Creates GUI
        self.create_gui()
        self.update_icon()

        # Checks if program should close to tray
        if self.minimize_to_tray is True:
            self.protocol("WM_DELETE_WINDOW", self.withdraw_window)
            self.create_tray_icon()

            if self.start_minimized is True:
                self.withdraw_window()
        else:
            self.protocol("WM_DELETE_WINDOW", self.exit)

        # Creates Threads
        valorant_files_thread = threading.Thread(target=self.valorant_log_reader)
        self.agent_thread = threading.Thread(target=self.locking_main)
        self.tools_thread = threading.Thread(target=self.tools_main)

        self.agent_thread.start()
        self.tools_thread.start()
        valorant_files_thread.start()

    def exit(self):
        self.active_thread = False
        self.enable_tools = False

        try:
            if self.tools_keyboard_listener.running is True:
                self.tools_keyboard_listener.stop()
        except AttributeError:
            pass

        try:
            self.icon.stop()
        except AttributeError:
            pass

        self.destroy()
        sys.exit()

    # endregion

    # region GUI

    # region GUI Creation
    def create_gui(self):
        self.geometry(f"{self.window_width}x{self.window_height}")
        self.resizable(False, False)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # region Navigation Frame

        self.navigation_frame = customtkinter.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")

        self.navigation_frame_label = customtkinter.CTkLabel(
            self.navigation_frame,
            text="VALocker",
            font=(self.main_font, 18, "bold"),
        )
        self.navigation_frame_label.grid(row=0, column=0, padx=10, pady=10)

        # Creates the navigation buttons
        self.nav_buttons = dict()
        button_names = [
            "Overview",
            "Agent Toggle",
            "Random Agent",
            "Map Specific",
            "Save File",
            "Tools",
            "Settings",
        ]

        for row, button_name in enumerate(button_names):
            row = row + 1
            self.nav_buttons[button_name] = customtkinter.CTkButton(
                self.navigation_frame,
                corner_radius=0,
                height=40,
                border_spacing=10,
                text=button_name,
                anchor=tk.W,
                font=self.button_font_and_size,
                fg_color="transparent",
                text_color=("gray10", "gray90"),
                hover_color=("gray70", "gray30"),
                command=lambda tab_name=button_name: self.select_frame_by_name(
                    tab_name
                ),
            )
            self.nav_buttons[button_name].grid(row=row, column=0, sticky="ew")

        self.navigation_frame.rowconfigure(len(self.nav_buttons), weight=1)

        self.overview_frame = customtkinter.CTkFrame(
            self, corner_radius=0, fg_color="transparent"
        )
        self.agent_toggle_frame = customtkinter.CTkFrame(
            self, corner_radius=0, fg_color="transparent"
        )
        self.random_agent_frame = customtkinter.CTkFrame(
            self, corner_radius=0, fg_color="transparent"
        )
        self.map_specific_frame = customtkinter.CTkFrame(
            self, corner_radius=0, fg_color="transparent"
        )
        self.save_file_frame = customtkinter.CTkFrame(
            self, corner_radius=0, fg_color="transparent"
        )
        self.tools_frame = customtkinter.CTkFrame(
            self, corner_radius=0, fg_color="transparent"
        )
        self.settings_frame = customtkinter.CTkFrame(
            self, corner_radius=0, fg_color="transparent"
        )

        quit_button = customtkinter.CTkButton(
            self.navigation_frame,
            text="Exit",
            font=self.button_font_and_size,
            fg_color=self.button_colors["disabled"],
            corner_radius=5,
            hover=False,
            command=self.exit,
        )
        quit_button.grid(
            row=len(self.nav_buttons) + 2, column=0, sticky="sew", padx=10, pady=10
        )

        # endregion

        # region Overview Tab
        self.overview_frame.rowconfigure(0, weight=1)

        current_status_frame = customtkinter.CTkFrame(self.overview_frame)
        current_status_frame.grid(row=0, column=0, pady=20, padx=10, sticky="nsew")

        current_status_label = customtkinter.CTkLabel(
            current_status_frame, text="Instalocker:", font=self.label_font_and_size
        )
        current_status_label.pack(padx=10, pady=(5, 0))

        self.current_status_button = customtkinter.CTkButton(
            current_status_frame,
            text="Running" if self.enabled is True else "Stopped",
            hover=False,
            height=35,
            width=140,
            fg_color=(
                self.button_colors["enabled"]
                if self.enabled
                else self.button_colors["disabled"]
            ),
            font=self.button_font_and_size,
            command=self.toggle_active,
        )
        self.current_status_button.pack(padx=10, pady=(0, 5))

        current_task_label = customtkinter.CTkLabel(
            current_status_frame, text="Current Task:", font=self.label_font_and_size
        )
        current_task_label.pack(padx=10, pady=(5, 0))

        self.current_task_button = customtkinter.CTkButton(
            current_status_frame,
            text=(
                "None"
                if self.enabled is False
                else "Locking" if self.locking is True else "In Game"
            ),
            hover=False,
            height=35,
            width=140,
            font=self.button_font_and_size,
            command=self.toggle_thread_mode,
            state=tk.NORMAL if self.enabled else tk.DISABLED,
        )
        self.current_task_button.pack(padx=10, pady=(0, 5))

        safe_mode_frame = customtkinter.CTkFrame(
            current_status_frame, width=140, height=70, fg_color="transparent"
        )
        safe_mode_frame.pack(padx=10, pady=(5, 0), ipadx=0)

        safe_mode_label = customtkinter.CTkLabel(
            safe_mode_frame, text="Safe Mode:", font=self.label_font_and_size
        )
        safe_mode_label.pack(anchor=tk.N, padx=10)

        self.safe_mode_enabled_button = customtkinter.CTkButton(
            safe_mode_frame,
            width=int(f"{139 if self.safe_mode is False else 70}"),
            height=35,
            hover=False,
            text="On" if self.safe_mode is True else "Off",
            fg_color=(
                self.button_colors["enabled"]
                if self.safe_mode
                else self.button_colors["disabled"]
            ),
            font=self.button_font_and_size,
            command=self.toggle_safe_mode,
        )
        self.safe_mode_enabled_button.pack(side=tk.LEFT, padx=0, pady=(0, 5))

        self.safe_mode_strength_button = customtkinter.CTkButton(
            safe_mode_frame,
            width=69,
            height=35,
            hover=False,
            text=f"{list(self.safe_mode_timing.keys())[self.safe_mode_strength]}",
            font=self.button_font_and_size,
            command=self.toggle_safe_mode_strength,
        )
        if self.safe_mode is True:
            self.safe_mode_strength_button.pack(side=tk.RIGHT, padx=0, pady=(0, 5))
        else:
            self.safe_mode_strength_button.pack_forget()

        current_save_label = customtkinter.CTkLabel(
            current_status_frame,
            text="Current Save:",
            font=self.label_font_and_size,
        )
        current_save_label.pack(padx=10, pady=(5, 0))

        self.current_save_button = customtkinter.CTkButton(
            current_status_frame,
            text=self.current_save_file,
            hover=False,
            fg_color="gray20",
            corner_radius=5,
            height=35,
            width=140,
            font=self.button_font_and_size,
            command=lambda tab_name="Save File": self.select_frame_by_name(tab_name),
        )
        self.current_save_button.pack(padx=10, pady=(0, 10))

        select_agent_frame = customtkinter.CTkFrame(self.overview_frame)
        select_agent_frame.grid(row=0, column=1, pady=20, padx=10, sticky="nsew")

        select_agent_label = customtkinter.CTkLabel(
            select_agent_frame, text="Selected Agent:", font=self.label_font_and_size
        )
        select_agent_label.pack(padx=10, pady=(5, 0))

        self.select_agent_dropdown = customtkinter.CTkOptionMenu(
            select_agent_frame,
            dynamic_resizing=False,
            values=list(
                agent
                for agent, unlock_status in self.unlocked_agents_dict.items()
                if unlock_status is True
            ),
            height=35,
            width=140,
            command=lambda x: self.toggle_selected_agent(x),
            font=self.button_font_and_size,
        )
        self.select_agent_dropdown.set(f"{self.selected_agent}")
        self.select_agent_dropdown.pack(padx=10, pady=(0, 5))

        select_agent_frame_options_label = customtkinter.CTkLabel(
            select_agent_frame, text="Options:", font=self.label_font_and_size
        )
        select_agent_frame_options_label.pack(padx=10, pady=(5, 0))

        self.hover_mode_button = customtkinter.CTkButton(
            select_agent_frame,
            text="Hover",
            hover=False,
            height=35,
            width=140,
            fg_color=(
                self.button_colors["enabled"]
                if self.hover_mode
                else self.button_colors["disabled"]
            ),
            font=self.button_font_and_size,
            command=self.toggle_hover_mode,
        )
        self.hover_mode_button.pack(padx=10, pady=(0, 5))

        self.select_map_specific_button = customtkinter.CTkButton(
            select_agent_frame,
            text="Map Specific",
            hover=False,
            height=35,
            width=140,
            fg_color=(
                self.button_colors["enabled"]
                if self.map_specific_mode
                else self.button_colors["disabled"]
            ),
            font=self.button_font_and_size,
            command=self.toggle_map_specific,
            state=(
                tk.NORMAL
                if all(
                    agent is not None
                    for agent in self.map_specific_agents_dict.values()
                )
                else tk.DISABLED
            ),
        )
        self.select_map_specific_button.pack(padx=10, pady=5)

        self.toggle_random_agent_button = customtkinter.CTkButton(
            select_agent_frame,
            text="Random Agent",
            hover=False,
            height=35,
            width=140,
            fg_color=(
                self.button_colors["enabled"]
                if self.random_agent_mode
                else self.button_colors["disabled"]
            ),
            font=self.button_font_and_size,
            command=self.toggle_random_agent_mode,
            state=(
                tk.NORMAL
                if any(is_selected for is_selected in self.random_agents_dict.values())
                else tk.DISABLED
            ),
        )
        self.toggle_random_agent_button.pack(padx=10, pady=(5, 0))

        overview_tools_label = customtkinter.CTkLabel(
            select_agent_frame, text="Tools:", font=self.label_font_and_size
        )
        overview_tools_label.pack(padx=10, pady=(5, 0))

        self.overview_anti_afk_button = customtkinter.CTkButton(
            select_agent_frame,
            text="Anti AFK",
            hover=False,
            height=35,
            width=140,
            fg_color=(
                self.button_colors["enabled"]
                if self.anti_afk
                else self.button_colors["disabled"]
            ),
            font=self.button_font_and_size,
            command=self.toggle_anti_afk,
        )
        self.overview_anti_afk_button.pack(padx=10, pady=5)

        self.overview_drop_spike_button = customtkinter.CTkButton(
            select_agent_frame,
            text="Drop Spike",
            hover=False,
            height=35,
            width=140,
            fg_color=(
                self.button_colors["enabled"]
                if self.auto_drop_spike
                else self.button_colors["disabled"]
            ),
            font=self.button_font_and_size,
            command=self.toggle_auto_drop_spike,
        )
        self.overview_drop_spike_button.pack(padx=10, pady=5)

        stats_frame = customtkinter.CTkFrame(self.overview_frame)
        stats_frame.grid(row=0, column=2, pady=20, padx=10, sticky="nsew")

        stats_label = customtkinter.CTkLabel(
            stats_frame, text="Last Lock:", font=self.label_font_and_size
        )
        stats_label.pack(padx=10, pady=(5, 0))

        if self.safe_mode is False:
            stats_index = -1
        else:
            stats_index = self.safe_mode_strength

        time_to_lock_text = (
            self.time_to_lock_list[stats_index][-1]
            if len(self.time_to_lock_list[stats_index]) != 0
            else "-"
        )
        average_time_to_lock_text = (
            round(
                sum(self.time_to_lock_list[stats_index])
                / len(self.time_to_lock_list[stats_index]),
                2,
            )
            if len(self.time_to_lock_list[stats_index]) != 0
            else "-"
        )

        self.time_to_lock_label = customtkinter.CTkLabel(
            stats_frame,
            text=f"{time_to_lock_text} ms",
            height=35,
            font=self.button_font_and_size,
        )
        self.time_to_lock_label.pack(padx=10, pady=(0, 5))

        average_time_to_lock_label = customtkinter.CTkLabel(
            stats_frame, text="Average:", font=self.label_font_and_size
        )
        average_time_to_lock_label.pack(padx=10, pady=(5, 0))

        self.average_time_to_lock_value = customtkinter.CTkLabel(
            stats_frame,
            text=f"{average_time_to_lock_text} ms",
            height=35,
            font=self.button_font_and_size,
        )
        self.average_time_to_lock_value.pack(padx=10, pady=(0, 5))

        total_games_locked_label = customtkinter.CTkLabel(
            stats_frame, text="Deployed:", font=self.label_font_and_size
        )
        total_games_locked_label.pack(padx=10, pady=(5, 0))

        self.total_games_locked_value = customtkinter.CTkLabel(
            stats_frame,
            text=f"{self.total_games_used} {'times' if self.total_games_used != 1 else 'time'}",
            height=35,
            font=self.button_font_and_size,
        )
        self.total_games_locked_value.pack(padx=10, pady=(0, 5))

        self.overview_frame.columnconfigure((0, 1, 2), weight=1)

        # endregion

        # region Agent Toggle Tab
        mass_select_frame = customtkinter.CTkFrame(self.agent_toggle_frame)
        mass_select_frame.pack(padx=10, pady=20)

        mass_select_frame.grid_columnconfigure((0, 1), weight=1)

        all_agents_selected = all(
            self.unlocked_agents_dict[agent] is True
            for agent in self.unlocked_agents_dict
        )

        self.toggle_all_agent_button = customtkinter.CTkCheckBox(
            mass_select_frame,
            text="All",
            width=100,
            font=self.button_font_and_size,
            command=lambda: self.toggle_unlocked_agent_status("all"),
            state=tk.DISABLED if all_agents_selected else tk.NORMAL,
        )
        if all_agents_selected:
            self.toggle_all_agent_button.select()
        self.toggle_all_agent_button.grid(row=0, column=0, pady=10, padx=(10, 5))

        no_agents_selected = all(
            self.unlocked_agents_dict[agent] is False
            for agent in self.unlocked_agents_dict
            if agent not in self.default_agents
        )
        self.toggle_none_agent_button = customtkinter.CTkCheckBox(
            mass_select_frame,
            text="None",
            width=100,
            font=self.button_font_and_size,
            command=lambda: self.toggle_unlocked_agent_status("none"),
            state=tk.DISABLED if no_agents_selected else tk.NORMAL,
        )
        if no_agents_selected:
            self.toggle_none_agent_button.select()
        self.toggle_none_agent_button.grid(row=0, column=1, pady=10, padx=(5, 10))

        toggle_agent_checkbox_frame = customtkinter.CTkFrame(self.agent_toggle_frame)
        toggle_agent_checkbox_frame.pack(pady=10, padx=0)

        interior_toggle_agent_checkbox_frame = customtkinter.CTkFrame(
            toggle_agent_checkbox_frame, fg_color="transparent"
        )
        interior_toggle_agent_checkbox_frame.pack(padx=15, pady=10)

        unlockable_agents = [
            agent for agent in self.all_agents if agent not in self.default_agents
        ]

        self.agent_checkboxes = {}
        for index, agent in enumerate(unlockable_agents):
            column, row = index % 4, index // 4

            self.agent_checkboxes[f"self.{agent}_checkbox"] = customtkinter.CTkCheckBox(
                interior_toggle_agent_checkbox_frame,
                text=agent,
                font=self.button_font_and_size,
                command=lambda agent=agent: self.toggle_unlocked_agent_status(agent),
            )
            if self.unlocked_agents_dict[agent]:
                self.agent_checkboxes[f"self.{agent}_checkbox"].select()
            self.agent_checkboxes[f"self.{agent}_checkbox"].grid(
                row=row, column=column, pady=10, padx=5
            )

        # endregion

        # region Random Agent Tab
        random_agent_allnone_button_frame = customtkinter.CTkFrame(
            self.random_agent_frame, fg_color="transparent"
        )
        random_agent_allnone_button_frame.pack(padx=10, pady=(20, 10), anchor=tk.NW)

        self.random_agent_exclusiselect_button = customtkinter.CTkButton(
            random_agent_allnone_button_frame,
            width=50,
            height=40,
            text="ExclusiSelect",
            hover=False,
            font=self.button_font_and_size,
            fg_color=(
                self.button_colors["enabled"]
                if self.random_agent_exclusiselect
                else self.button_colors["disabled"]
            ),
            command=self.toggle_random_agent_exclusiselect,
        )
        self.random_agent_exclusiselect_button.pack(
            side=tk.LEFT,
            padx=(0, 11),
            pady=0,
        )

        random_agent_all_none_toggle_frame = customtkinter.CTkFrame(
            random_agent_allnone_button_frame, height=100
        )
        random_agent_all_none_toggle_frame.pack(padx=0, pady=0)

        all_selected = all(
            self.random_agents_dict[agent]
            for agent in self.unlocked_agents_dict
            if self.unlocked_agents_dict[agent]
        )

        self.all_random_agent_radio_button = customtkinter.CTkCheckBox(
            random_agent_all_none_toggle_frame,
            text="All",
            font=self.button_font_and_size,
            command=lambda: self.toggle_random_agent_status("all"),
            state=tk.DISABLED if all_selected else tk.NORMAL,
        )
        if all_selected:
            self.all_random_agent_radio_button.select()
        self.all_random_agent_radio_button.pack(side="left", padx=(20, 0), pady=10)

        none_selected = all(
            value is False for value in self.random_agents_dict.values()
        )
        self.none_random_agent_radio_button = customtkinter.CTkCheckBox(
            random_agent_all_none_toggle_frame,
            text="None",
            font=self.button_font_and_size,
            command=lambda: self.toggle_random_agent_status("none"),
            state=tk.DISABLED if none_selected else tk.NORMAL,
        )
        if none_selected:
            self.none_random_agent_radio_button.select()
        self.none_random_agent_radio_button.pack(side="right", padx=20, pady=10)

        random_agent_role_toggle_frame = customtkinter.CTkFrame(self.random_agent_frame)
        random_agent_role_toggle_frame.pack(padx=10, pady=10, fill=tk.X)

        # Creates the checkboxes for each role
        self.agent_role_checkboxes = dict()
        for index, role_upper in enumerate(self.config_file_agents.keys()):
            role = role_upper.lower()

            self.agent_role_checkboxes[role] = customtkinter.CTkCheckBox(
                random_agent_role_toggle_frame,
                text=role.capitalize(),
                font=self.button_font_and_size,
                width=110,
                text_color=self.role_colors[role],
                text_color_disabled=self.role_colors[f"{role}_disabled"],
                command=lambda role=role: self.toggle_random_agent_status(role),
            )
            # padx_amount = (5, 10) if index == 0 else 10
            if all(
                self.random_agents_dict[agent] is True
                for agent in self.config_file_agents[role_upper]
            ):
                self.agent_role_checkboxes[role].select()
            self.agent_role_checkboxes[role].grid(row=0, column=index, padx=5, pady=10)

        # Creates frames for agents of each role
        random_agent_individual_toggle_frame = customtkinter.CTkFrame(
            self.random_agent_frame, fg_color="transparent"
        )
        random_agent_individual_toggle_frame.pack(padx=0, pady=0)

        role_frames = dict()
        for index, role in enumerate(self.config_file_agents.keys()):
            role = role.lower()

            role_frames[role] = customtkinter.CTkFrame(
                random_agent_individual_toggle_frame,
                width=120,
                height=100,
            )
            role_frames[role].grid(row=0, column=index % 4, padx=5, pady=5, sticky="n")

            role_frames[role].columnconfigure(index, weight=1)

        # Creates the checkboxes for each agent
        self.random_agent_checkboxes, agent_role = dict(), str()
        for index, agent in enumerate(self.all_agents):
            for role, agent_list in self.config_file_agents.items():
                if agent in agent_list:
                    agent_role = role.lower()
                    break

            frame = role_frames[agent_role]

            self.random_agent_checkboxes[f"self.{agent}_random_checkbox"] = (
                customtkinter.CTkCheckBox(
                    frame,
                    text=agent,
                    text_color=self.role_colors[agent_role],
                    font=self.button_font_and_size,
                    command=lambda agent=agent: self.toggle_random_agent_status(agent),
                    state=(
                        tk.NORMAL if self.unlocked_agents_dict[agent] else tk.DISABLED
                    ),
                )
            )
            if self.random_agents_dict[agent]:
                self.random_agent_checkboxes[f"self.{agent}_random_checkbox"].select()
            self.random_agent_checkboxes[f"self.{agent}_random_checkbox"].pack(
                padx=5, pady=5
            )
        # endregion

        # region Map Specific Tab
        self.map_specific_frame.rowconfigure(
            [i for i in range(len(self.map_names) // 2 + 1)], weight=1
        )

        map_frames, map_labels, self.map_dropdowns = dict(), dict(), dict()
        for index, map_name in enumerate(self.map_names):
            row, column = index // 2, index % 2

            map_frames[f"{map_name}_frame"] = customtkinter.CTkFrame(
                self.map_specific_frame, width=230
            )

            pady_amount = (
                (20, 5)
                if row == 0
                else (5, 20) if row == len(self.map_names) // 2 else 5
            )
            map_frames[f"{map_name}_frame"].grid(
                row=row, column=column, padx=10, pady=pady_amount, sticky="nsew"
            )
            map_labels[f"{map_name}_label"] = customtkinter.CTkLabel(
                map_frames[f"{map_name}_frame"],
                text=f"{map_name}:",
                font=self.label_font_and_size,
            )
            map_labels[f"{map_name}_label"].pack(padx=10, pady=5, side=tk.LEFT)

            self.map_dropdowns[map_name] = customtkinter.CTkOptionMenu(
                map_frames[f"{map_name}_frame"],
                values=list(
                    agent
                    for agent, unlock_status in self.unlocked_agents_dict.items()
                    if unlock_status
                ),
                width=110,
                font=self.button_font_and_size,
                command=lambda agent_name, map_name=map_name: self.toggle_map_specific_agent(
                    agent_name=agent_name, map_name=map_name
                ),
            )

            if (
                self.map_specific_agents_dict[map_name] is not None
                and self.unlocked_agents_dict[self.map_specific_agents_dict[map_name]]
            ):
                self.map_dropdowns[map_name].configure(
                    fg_color="#1f6aa5", button_color="#203a4f", hover=True
                )
                self.map_dropdowns[map_name].set(
                    self.map_specific_agents_dict[map_name]
                )
            else:
                self.map_dropdowns[map_name].set("None")
                self.map_dropdowns[map_name].configure(
                    fg_color=self.button_colors["disabled"],
                    button_color="#4e2126",
                    hover=False,
                )

            self.map_dropdowns[map_name].pack(padx=(0, 10), pady=5, side=tk.RIGHT)

        self.map_specific_frame.columnconfigure((0, 1), weight=1)  # type: ignore

        # endregion

        # region Save File Tab
        self.save_file_scrollable_frame = customtkinter.CTkScrollableFrame(
            self.save_file_frame
        )
        self.save_file_scrollable_frame.pack(
            fill=tk.BOTH, expand=True, padx=10, pady=(20, 0)
        )

        self.save_file_frame_items = dict()
        self.save_file_icons = dict(
            favorite_empty=customtkinter.CTkImage(
                dark_image=PIL.Image.open(
                    resource_path("images/gui_icons/favorite_empty.png")
                ),
                size=(20, 20),
            ),
            favorite_filled=customtkinter.CTkImage(
                dark_image=PIL.Image.open(
                    resource_path("images/gui_icons/favorite_filled.png")
                ),
                size=(20, 20),
            ),
            rename=customtkinter.CTkImage(
                dark_image=PIL.Image.open(resource_path("images/gui_icons/rename.png")),
                size=(20, 20),
            ),
            delete=customtkinter.CTkImage(
                dark_image=PIL.Image.open(resource_path("images/gui_icons/delete.png")),
                size=(20, 20),
            ),
            new_file=customtkinter.CTkImage(
                dark_image=PIL.Image.open(
                    resource_path("images/gui_icons/new_file.png")
                ),
                size=(25, 25),
            ),
        )

        ordered_save_files = self.favorited_save_files + [
            save_file
            for save_file in self.save_files
            if save_file not in self.favorited_save_files
        ]
        for save_file in ordered_save_files:
            self.individual_save_file_items(save_file)

        new_save_file_button = customtkinter.CTkButton(
            self.save_file_frame,
            text="",
            image=self.save_file_icons["new_file"],
            command=self.new_save_file,
            fg_color="transparent",
            hover_color="gray22",
            width=25,
            height=25,
        )
        new_save_file_button.pack(padx=10, pady=5, anchor=tk.NE)

        # endregion

        # region Tools Tab
        self.toggle_tools_button = customtkinter.CTkButton(
            self.tools_frame,
            text=f"Tools {'Enabled' if self.enable_tools is True else 'Disabled'}",
            hover=False,
            height=40,
            fg_color=(
                self.button_colors["enabled"]
                if self.enable_tools
                else self.button_colors["disabled"]
            ),
            font=(self.main_font, 16),
            command=self.explicitly_toggle_tools,
        )
        self.toggle_tools_button.pack(padx=10, pady=20, fill=tk.X)

        scrollable_frame = customtkinter.CTkScrollableFrame(self.tools_frame)
        scrollable_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 20))

        scrollable_frame.columnconfigure((0, 1), weight=1)
        scrollable_frame.rowconfigure((0, 1), weight=1)

        self.auto_drop_spike_button = customtkinter.CTkButton(
            scrollable_frame,
            text="Auto Drop Spike",
            height=40,
            hover=False,
            fg_color=(
                self.button_colors["enabled"]
                if self.auto_drop_spike
                else self.button_colors["disabled"]
            ),
            font=self.button_font_and_size,
            command=self.toggle_auto_drop_spike,
        )
        self.auto_drop_spike_button.grid(
            row=0, column=0, padx=10, pady=10, sticky="nsew"
        )

        self.anti_afk_button = customtkinter.CTkButton(
            scrollable_frame,
            text="Anti AFK",
            height=40,
            hover=False,
            fg_color=(
                self.button_colors["enabled"]
                if self.anti_afk
                else self.button_colors["disabled"]
            ),
            font=self.button_font_and_size,
            command=self.toggle_anti_afk,
        )
        self.anti_afk_button.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # self.anti_aim_button = customtkinter.CTkButton(
        #     scrollable_frame,
        #     text="Anti Aim",
        #     height=40,
        #     hover=False,
        #     fg_color=self.button_colors['enabled'] if self.anti_aim else self.button_colors['disabled'],
        #     font=self.button_font_and_size,
        #     command=self.toggle_anti_aim,
        # )
        # self.anti_aim_button.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # endregion

        # region Settings Tab
        scrolling_settings_frame = customtkinter.CTkScrollableFrame(self.settings_frame)
        scrolling_settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=20)

        # General Settings

        general_settings_frame = customtkinter.CTkFrame(
            scrolling_settings_frame, fg_color="gray16"
        )
        general_settings_frame.pack(padx=10, pady=10, ipady=5, fill=tk.X)
        general_settings_frame.columnconfigure((0, 1), weight=1)

        general_settings_label = customtkinter.CTkLabel(
            general_settings_frame,
            text="General Settings:",
            font=self.label_font_and_size,
        )
        general_settings_label.grid(
            column=0, row=0, padx=10, pady=5, sticky="nsew", columnspan=2
        )

        self.minimize_to_tray_button = customtkinter.CTkButton(
            general_settings_frame,
            text="Minimize to Tray",
            height=40,
            width=200,
            hover=False,
            fg_color=(
                self.button_colors["enabled"]
                if self.minimize_to_tray
                else self.button_colors["disabled"]
            ),
            font=self.button_font_and_size,
            command=lambda: self.toggle_setting("minimize_to_tray"),
        )
        self.minimize_to_tray_button.grid(
            column=0, row=1, padx=10, pady=5, sticky="nsew"
        )

        self.persistent_random_agents_button = customtkinter.CTkButton(
            general_settings_frame,
            text="Persistent Random Agents",
            height=40,
            width=200,
            hover=False,
            fg_color=(
                self.button_colors["enabled"]
                if self.persistent_random_agents
                else self.button_colors["disabled"]
            ),
            font=self.button_font_and_size,
            command=lambda: self.toggle_setting("persistent_random_agents"),
        )
        self.persistent_random_agents_button.grid(
            column=1, row=1, padx=10, pady=5, sticky="nsew"
        )

        self.hide_default_save_file_button = customtkinter.CTkButton(
            general_settings_frame,
            text="Hide Default Save File",
            height=40,
            width=200,
            hover=False,
            fg_color=(
                self.button_colors["enabled"]
                if self.hide_default_save_file
                else self.button_colors["disabled"]
            ),
            font=self.button_font_and_size,
            command=lambda: self.toggle_setting("hide_default_save_file"),
        )
        self.hide_default_save_file_button.grid(
            column=0, row=2, padx=10, pady=5, sticky="nsew"
        )

        self.anti_afk_mode_button = customtkinter.CTkButton(
            general_settings_frame,
            text=f"Anti AFK Mode: {self.anti_afk_mode.title()}",
            height=40,
            width=200,
            hover=False,
            font=self.button_font_and_size,
            command=lambda: self.toggle_setting("change_anti_afk_mode"),
        )
        self.anti_afk_mode_button.grid(column=1, row=2, padx=10, pady=5, sticky="nsew")

        self.anti_afk_toggles_auto_drop_button = customtkinter.CTkButton(
            general_settings_frame,
            text="Anti AFK Drops Spike",
            height=40,
            width=200,
            hover=False,
            fg_color=(
                self.button_colors["enabled"]
                if self.anti_afk_toggles_auto_drop is True
                else self.button_colors["disabled"]
            ),
            font=self.button_font_and_size,
            command=lambda: self.toggle_setting("anti_afk_toggles_auto_drop"),
        )
        self.anti_afk_toggles_auto_drop_button.grid(
            column=0, row=3, padx=10, pady=5, sticky="nsew"
        )

        self.detect_open_chat_mode_button = customtkinter.CTkButton(
            general_settings_frame,
            text="Detect Opened Chat (KB)",
            height=40,
            width=200,
            hover=False,
            fg_color=(
                self.button_colors["enabled"]
                if self.detect_open_chat_keyboard is True
                else self.button_colors["disabled"]
            ),
            font=self.button_font_and_size,
            command=lambda: self.toggle_setting("detect_open_chat_keyboard"),
        )
        self.detect_open_chat_mode_button.grid(
            column=1, row=3, padx=10, pady=5, sticky="nsew"
        )

        self.start_tools_thread_automatically_button = customtkinter.CTkButton(
            general_settings_frame,
            text="Auto Start Tools",
            height=40,
            width=200,
            hover=False,
            fg_color=(
                self.button_colors["enabled"]
                if self.start_tools_thread_automatically is True
                else self.button_colors["disabled"]
            ),
            font=self.button_font_and_size,
            command=lambda: self.toggle_setting("start_tools_thread_automatically"),
        )
        self.start_tools_thread_automatically_button.grid(
            column=0, row=4, padx=10, pady=5, sticky="nsew"
        )

        # On Startup Settings
        on_startup_frame = customtkinter.CTkFrame(
            scrolling_settings_frame, fg_color="gray16"
        )
        on_startup_frame.pack(padx=10, pady=10, ipady=5, fill=tk.X)
        on_startup_frame.columnconfigure((0, 1), weight=1)

        on_startup_label = customtkinter.CTkLabel(
            on_startup_frame, text="On Startup:", font=self.label_font_and_size
        )
        on_startup_label.grid(
            column=0, row=0, padx=10, pady=5, sticky="nsew", columnspan=2
        )

        self.start_minimized_button = customtkinter.CTkButton(
            on_startup_frame,
            text="Start Minimized",
            height=40,
            width=200,
            hover=False,
            fg_color=(
                self.button_colors["enabled"]
                if self.start_minimized
                else self.button_colors["disabled"]
            ),
            font=self.button_font_and_size,
            state=tk.DISABLED if self.minimize_to_tray is False else tk.NORMAL,
            command=lambda: self.toggle_setting("start_minimized"),
        )

        self.start_minimized_button.grid(
            column=0, row=1, padx=10, pady=5, sticky="nsew"
        )

        self.enable_on_startup_button = customtkinter.CTkButton(
            on_startup_frame,
            text="Enable Instalocker",
            height=40,
            width=200,
            hover=False,
            fg_color=(
                self.button_colors["enabled"]
                if self.enable_on_startup
                else self.button_colors["disabled"]
            ),
            font=self.button_font_and_size,
            command=lambda: self.toggle_setting("enable_on_startup"),
        )
        self.enable_on_startup_button.grid(
            column=1, row=1, padx=10, pady=5, sticky="nsew"
        )

        self.safe_mode_on_startup_button = customtkinter.CTkButton(
            on_startup_frame,
            text="Enable Safe Mode",
            height=40,
            width=200,
            hover=False,
            fg_color=(
                self.button_colors["enabled"]
                if self.safe_mode_on_startup
                else self.button_colors["disabled"]
            ),
            font=self.button_font_and_size,
            command=lambda: self.toggle_setting("safe_mode_on_startup"),
        )
        self.safe_mode_on_startup_button.grid(
            column=0, row=2, padx=10, pady=5, sticky="nsew"
        )

        self.safe_mode_strength_on_startup_button = customtkinter.CTkButton(
            on_startup_frame,
            text=f"Safe Mode Strength: {list(self.safe_mode_timing.keys())[self.safe_mode_strength_on_startup]}",
            height=40,
            hover=False,
            font=self.button_font_and_size,
            command=lambda: self.toggle_setting("safe_mode_strength_on_startup"),
        )
        self.safe_mode_strength_on_startup_button.grid(
            column=1, row=2, padx=10, pady=5, sticky="nsew"
        )

        self.grab_keybinds_button = customtkinter.CTkButton(
            on_startup_frame,
            text="Grab Keybinds",
            height=40,
            width=200,
            hover=False,
            fg_color=(
                self.button_colors["enabled"]
                if self.grab_keybinds
                else self.button_colors["disabled"]
            ),
            font=self.button_font_and_size,
            command=lambda: self.toggle_setting("grab_keybinds"),
        )
        self.grab_keybinds_button.grid(column=0, row=3, padx=10, pady=5, sticky="nsew")

        # endregion

        self.select_frame_by_name("Overview")

    # Creates the list of save file items
    def individual_save_file_items(self, file_name, just_icons=False):
        if just_icons is False:
            self.save_file_frame_items[f"{file_name}_frame"] = customtkinter.CTkFrame(
                self.save_file_scrollable_frame,
                height=50,
                fg_color=(
                    "grey16" if file_name != self.current_save_file else "dark green"
                ),
            )

            if file_name != "default" or self.hide_default_save_file is False:
                self.save_file_frame_items[f"{file_name}_frame"].pack(
                    fill=tk.X, padx=(5, 0), pady=3
                )

            self.save_file_frame_items[f"{file_name}_button"] = customtkinter.CTkButton(
                self.save_file_frame_items[f"{file_name}_frame"],
                text=file_name,
                font=self.label_font_and_size,
                fg_color="transparent",
                hover_color="gray22",
                hover=True if file_name != self.current_save_file else False,
                command=lambda save_file=file_name: self.change_current_save_file(
                    save_file
                ),
                anchor="w",
            )
            self.save_file_frame_items[f"{file_name}_button"].pack(
                side=tk.LEFT, padx=10, pady=5
            )

        for icon_name in reversed(
            ["favorite", "rename", "delete"] if file_name != "default" else ["favorite"]
        ):
            icon_image = (
                self.save_file_icons[icon_name]
                if icon_name != "favorite"
                else self.save_file_icons[
                    f"{icon_name}_{'filled' if file_name in self.favorited_save_files else 'empty'}"
                ]
            )
            self.save_file_frame_items[f"{file_name}_{icon_name}"] = (
                customtkinter.CTkButton(
                    self.save_file_frame_items[f"{file_name}_frame"],
                    image=icon_image,
                    text="",
                    fg_color="transparent",
                    hover_color="gray22",
                    width=20,
                    height=20,
                    command=lambda save_file=file_name, icon_name=icon_name: eval(
                        f"self.{icon_name}_save_file(save_file)",
                        {"self": self, "save_file": save_file},
                    ),
                )
            )
            self.save_file_frame_items[f"{file_name}_{icon_name}"].pack(
                side=tk.RIGHT, padx=(0, 5), pady=5
            )

    # endregion

    # region GUI Updates

    # Updates overview tab
    def update_overview_tab(self):
        # Stats
        if self.safe_mode is False:
            average_time_to_lock_index = -1
        else:
            average_time_to_lock_index = self.safe_mode_strength

        self.average_time_to_lock_value.configure(
            text=f"{'-' if len(self.time_to_lock_list[average_time_to_lock_index]) == 0 else round(sum(self.time_to_lock_list[average_time_to_lock_index])/len(self.time_to_lock_list[average_time_to_lock_index]),2)} ms",
        )
        self.time_to_lock_label.configure(
            text=f"{'-' if len(self.time_to_lock_list[average_time_to_lock_index]) == 0 else self.time_to_lock_list[average_time_to_lock_index][-1]} ms"
        )
        self.total_games_locked_value.configure(
            text=f"{self.total_games_used} {'times' if self.total_games_used != 1 else 'time'}"
        )

        # Buttons Left Column
        self.current_status_button.configure(
            text="Running" if self.enabled else "Stopped",
            fg_color=(
                self.button_colors["enabled"]
                if self.enabled
                else self.button_colors["disabled"]
            ),
        )

        self.current_task_button.configure(
            text=(
                "None"
                if self.enabled is False
                else "Locking" if self.locking is True else "In Game"
            ),
            state=tk.DISABLED if self.enabled is False else tk.NORMAL,
        )

        self.safe_mode_enabled_button.configure(
            text="On" if self.safe_mode is True else "Off",
            fg_color=(
                self.button_colors["enabled"]
                if self.safe_mode is True
                else self.button_colors["disabled"]
            ),
            width=int(f"{139 if self.safe_mode is False else 70}"),
        )

        if self.safe_mode is True:
            self.safe_mode_strength_button.pack(side=tk.RIGHT, padx=0, pady=(0, 5))
        else:
            self.safe_mode_strength_button.pack_forget()

        self.safe_mode_strength_button.configure(
            text=f"{list(self.safe_mode_timing.keys())[self.safe_mode_strength]}"
        )

        self.current_save_button.configure(text=self.current_save_file)

        # Buttons Middle Column

        self.hover_mode_button.configure(
            text="Hover",
            fg_color=(
                self.button_colors["enabled"]
                if self.hover_mode is True
                else self.button_colors["disabled"]
            ),
        )

        self.select_map_specific_button.configure(
            text="Map Specific",
            fg_color=(
                self.button_colors["enabled"]
                if self.map_specific_mode
                else self.button_colors["disabled"]
            ),
        )

        self.toggle_random_agent_button.configure(
            text="Random Agent",
            fg_color=(
                self.button_colors["enabled"]
                if self.random_agent_mode
                else self.button_colors["disabled"]
            ),
        )

        self.select_agent_dropdown.configure(
            values=list(
                agent
                for agent, unlock_status in self.unlocked_agents_dict.items()
                if unlock_status is True
            )
        )
        self.select_agent_dropdown.set(f"{self.selected_agent}")

        # Disables random agent if map specific mode is enabled and vice versa
        match self.map_specific_mode, self.random_agent_mode:
            case False, False:
                self.select_agent_dropdown.configure(state=tk.NORMAL)
                if any(value is True for value in self.random_agents_dict.values()):
                    self.toggle_random_agent_button.configure(state=tk.NORMAL)
                else:
                    self.toggle_random_agent_button.configure(state=tk.DISABLED)
                if any(
                    value is None for value in self.map_specific_agents_dict.values()
                ):
                    self.select_map_specific_button.configure(state=tk.DISABLED)
                else:
                    self.select_map_specific_button.configure(state=tk.NORMAL)
            case True, False:
                self.toggle_random_agent_button.configure(state=tk.DISABLED)
                self.select_agent_dropdown.configure(state=tk.DISABLED)
            case False, True:
                self.select_map_specific_button.configure(state=tk.DISABLED)
                self.select_agent_dropdown.configure(state=tk.DISABLED)
            case True, True:
                self.map_specific_mode = False
                self.random_agent_mode = False
                self.update_overview_tab()

        self.update_icon()

    # Updates agent toggle tab
    def update_agent_toggle_tab(self, agent_name=None, loading_new_save=None):
        match agent_name:
            case "all":
                self.toggle_all_agent_button.configure(state=tk.DISABLED)
                self.toggle_none_agent_button.deselect()
                self.toggle_none_agent_button.configure(state=tk.NORMAL)

                for agent in self.unlocked_agents_dict:
                    if agent not in self.default_agents:
                        self.agent_checkboxes[f"self.{agent}_checkbox"].select()

            case "none":
                self.toggle_none_agent_button.configure(state=tk.DISABLED)
                self.toggle_all_agent_button.deselect()
                self.toggle_all_agent_button.configure(state=tk.NORMAL)

                for agent in self.unlocked_agents_dict:
                    if agent not in self.default_agents:
                        self.agent_checkboxes[f"self.{agent}_checkbox"].deselect()

            case _:  # Updates a single agent
                all_agents_selected = all(
                    self.unlocked_agents_dict[agent] is True
                    for agent in self.unlocked_agents_dict
                )
                no_agents_selected = all(
                    self.unlocked_agents_dict[agent] is False
                    for agent in self.unlocked_agents_dict
                    if agent not in self.default_agents
                )

                if all_agents_selected is True:
                    self.toggle_all_agent_button.select()
                    self.toggle_all_agent_button.configure(state=tk.DISABLED)
                else:
                    self.toggle_all_agent_button.deselect()
                    self.toggle_all_agent_button.configure(state=tk.NORMAL)

                if no_agents_selected is True:
                    self.toggle_none_agent_button.select()
                    self.toggle_none_agent_button.configure(state=tk.DISABLED)
                else:
                    self.toggle_none_agent_button.deselect()
                    self.toggle_none_agent_button.configure(state=tk.NORMAL)

                if loading_new_save:
                    for agent, value in self.unlocked_agents_dict.items():
                        if agent not in self.default_agents:
                            if value:
                                self.agent_checkboxes[f"self.{agent}_checkbox"].select()
                            else:
                                self.agent_checkboxes[
                                    f"self.{agent}_checkbox"
                                ].deselect()

    # Updates random agent tab
    def update_random_agent_tab(
        self,
        agent_name=None,
        toggled_agent_name=None,
        exclusiselect_mode=False,
        loading_new_save=False,
    ):
        match agent_name:
            case "all":
                self.all_random_agent_radio_button.configure(state=tk.DISABLED)
                self.none_random_agent_radio_button.deselect()
                self.none_random_agent_radio_button.configure(state=tk.NORMAL)

                for agent in self.random_agents_dict:
                    if self.unlocked_agents_dict[agent] is True:
                        self.random_agent_checkboxes[
                            f"self.{agent}_random_checkbox"
                        ].select()

                for role in self.config_file_agents:
                    self.agent_role_checkboxes[role.lower()].select()

            case "none":
                self.all_random_agent_radio_button.deselect()
                self.all_random_agent_radio_button.configure(state=tk.NORMAL)
                self.none_random_agent_radio_button.configure(state=tk.DISABLED)

                for agent in self.random_agents_dict:
                    if self.unlocked_agents_dict[agent] is True:
                        self.random_agent_checkboxes[
                            f"self.{agent}_random_checkbox"
                        ].deselect()

                for role in self.config_file_agents:
                    self.agent_role_checkboxes[role.lower()].deselect()

            case "controllers" | "duelists" | "initiators" | "sentinels":
                role = agent_name.upper()
                all_role_agents_selected = all(
                    self.random_agents_dict[agent] is True
                    for agent in self.config_file_agents[role]
                    if self.unlocked_agents_dict[agent] is True
                )
                if all_role_agents_selected is True:
                    for agent in self.config_file_agents[role]:
                        if self.unlocked_agents_dict[agent] is True:
                            self.random_agent_checkboxes[
                                f"self.{agent}_random_checkbox"
                            ].select()
                else:
                    for agent in self.config_file_agents[role]:
                        self.random_agent_checkboxes[
                            f"self.{agent}_random_checkbox"
                        ].deselect()

                if all(
                    self.random_agents_dict[agent] is True
                    for agent in self.unlocked_agents_dict
                    if self.unlocked_agents_dict[agent] is True
                ):
                    self.all_random_agent_radio_button.select()
                    self.all_random_agent_radio_button.configure(state=tk.DISABLED)
                else:
                    self.all_random_agent_radio_button.deselect()
                    self.all_random_agent_radio_button.configure(state=tk.NORMAL)

                if all(value is False for value in self.random_agents_dict.values()):
                    self.none_random_agent_radio_button.select()
                    self.none_random_agent_radio_button.configure(state=tk.DISABLED)
                else:
                    self.none_random_agent_radio_button.deselect()
                    self.none_random_agent_radio_button.configure(state=tk.NORMAL)

            case "toggle_unlocked_agent_status":
                match toggled_agent_name:
                    case "all":
                        for agent in self.unlocked_agents_dict:
                            if agent not in self.default_agents:
                                self.random_agent_checkboxes[
                                    f"self.{agent}_random_checkbox"
                                ].configure(state=tk.NORMAL)
                    case "none":
                        for agent in self.unlocked_agents_dict:
                            if agent not in self.default_agents:
                                self.random_agent_checkboxes[
                                    f"self.{agent}_random_checkbox"
                                ].configure(state=tk.DISABLED)
                                self.random_agent_checkboxes[
                                    f"self.{agent}_random_checkbox"
                                ].deselect()
                    case _:
                        if self.unlocked_agents_dict[toggled_agent_name] is True:
                            self.random_agent_checkboxes[
                                f"self.{toggled_agent_name}_random_checkbox"
                            ].configure(state=tk.NORMAL)
                        else:
                            self.random_agent_checkboxes[
                                f"self.{toggled_agent_name}_random_checkbox"
                            ].configure(state=tk.DISABLED)
                            self.random_agent_checkboxes[
                                f"self.{toggled_agent_name}_random_checkbox"
                            ].deselect()

                        # Finds the role of the toggled agent
                        for role, agent_list in self.config_file_agents.items():
                            if toggled_agent_name in agent_list:
                                agent_role = role.lower()
                                break
                        if all(
                            self.random_agents_dict[agent] is True
                            for agent in self.config_file_agents[agent_role.upper()]
                            if self.unlocked_agents_dict[agent] is True
                        ):
                            self.agent_role_checkboxes[agent_role].select()
                        else:
                            self.agent_role_checkboxes[agent_role].deselect()

                if toggled_agent_name in ["all", "none"]:
                    if all(
                        self.random_agents_dict[agent] is True
                        for agent in self.unlocked_agents_dict
                        if self.unlocked_agents_dict[agent] is True
                    ):
                        self.all_random_agent_radio_button.select()
                        self.all_random_agent_radio_button.configure(state=tk.DISABLED)
                    else:
                        self.all_random_agent_radio_button.deselect()
                        self.all_random_agent_radio_button.configure(state=tk.NORMAL)

                    # Select none if no agents are selected
                    if all(
                        value is False for value in self.random_agents_dict.values()
                    ):
                        self.none_random_agent_radio_button.select()
                        self.none_random_agent_radio_button.configure(state=tk.DISABLED)
                    else:
                        self.none_random_agent_radio_button.deselect()
                        self.none_random_agent_radio_button.configure(state=tk.NORMAL)

                    # Selects all roles if all possible agents are selected
                    for role in self.config_file_agents:
                        if all(
                            self.random_agents_dict[agent] is True
                            for agent in self.config_file_agents[role]
                            if self.unlocked_agents_dict[agent] is True
                        ):
                            self.agent_role_checkboxes[role.lower()].select()
                        else:
                            self.agent_role_checkboxes[role.lower()].deselect()

            case _:  # Updates the tab when a single agent is selected
                if exclusiselect_mode and agent_name is not None:
                    self.random_agent_checkboxes[
                        f"self.{agent_name}_random_checkbox"
                    ].deselect()

                # Select none if no agents are selected
                if all(value is False for value in self.random_agents_dict.values()):
                    self.none_random_agent_radio_button.select()
                    self.none_random_agent_radio_button.configure(state=tk.DISABLED)
                else:
                    self.none_random_agent_radio_button.deselect()
                    self.none_random_agent_radio_button.configure(state=tk.NORMAL)

                # Select all if all possible agents are selected
                if all(
                    self.random_agents_dict[agent] is True
                    for agent in self.unlocked_agents_dict
                    if self.unlocked_agents_dict[agent] is True
                ):
                    self.all_random_agent_radio_button.select()
                    self.all_random_agent_radio_button.configure(state=tk.DISABLED)
                else:
                    self.all_random_agent_radio_button.deselect()
                    self.all_random_agent_radio_button.configure(state=tk.NORMAL)

                # Selects role if all agents in role are selected
                for role in self.config_file_agents:
                    if all(
                        self.random_agents_dict[agent] is True
                        for agent in self.config_file_agents[role]
                        if self.unlocked_agents_dict[agent] is True
                    ):
                        self.agent_role_checkboxes[role.lower()].select()
                    else:
                        self.agent_role_checkboxes[role.lower()].deselect()

                if loading_new_save:
                    for agent, value in self.unlocked_agents_dict.items():
                        if agent not in self.default_agents:
                            if self.random_agents_dict[agent]:
                                self.random_agent_checkboxes[
                                    f"self.{agent}_random_checkbox"
                                ].select()
                            else:
                                self.random_agent_checkboxes[
                                    f"self.{agent}_random_checkbox"
                                ].deselect()

                            if value:
                                self.random_agent_checkboxes[
                                    f"self.{agent}_random_checkbox"
                                ].configure(state=tk.NORMAL)
                            else:
                                self.random_agent_checkboxes[
                                    f"self.{agent}_random_checkbox"
                                ].configure(state=tk.DISABLED)

    # Updates map specific tab
    def update_map_specific_tab(self):
        unlocked_agents = list(
            agent
            for agent, unlock_status in self.unlocked_agents_dict.items()
            if unlock_status
        )

        for map_name in self.map_names:
            self.map_dropdowns[map_name].configure(values=unlocked_agents)

            if self.map_specific_agents_dict[map_name] is None:
                self.map_dropdowns[map_name].set("None")
                self.map_dropdowns[map_name].configure(
                    fg_color=self.button_colors["disabled"],
                    button_color="#4e2126",
                    hover=False,
                )
            else:
                self.map_dropdowns[map_name].set(
                    f"{self.map_specific_agents_dict[map_name]}"
                )
                self.map_dropdowns[map_name].configure(
                    fg_color="#1f6aa5", button_color="#203a4f", hover=True
                )

    # Updates the save file tab
    def update_save_file_tab(self):
        ordered_save_files = self.favorited_save_files + [
            save_file
            for save_file in self.save_files
            if save_file not in self.favorited_save_files
        ]
        for save_file in self.save_files:
            self.save_file_frame_items[f"{save_file}_frame"].configure(
                fg_color=(
                    "grey16" if save_file != self.current_save_file else "dark green"
                )
            )
            self.save_file_frame_items[f"{save_file}_button"].configure(
                hover=True if save_file != self.current_save_file else False
            )

            if save_file in self.favorited_save_files:
                self.save_file_frame_items[f"{save_file}_favorite"].configure(
                    image=self.save_file_icons["favorite_filled"]
                )
            else:
                self.save_file_frame_items[f"{save_file}_favorite"].configure(
                    image=self.save_file_icons["favorite_empty"]
                )
            self.save_file_frame_items[f"{save_file}_frame"].pack_forget()
        for save_file in ordered_save_files:
            if save_file != "default" or self.hide_default_save_file is False:
                self.save_file_frame_items[f"{save_file}_frame"].pack(
                    fill=tk.X, padx=(5, 0), pady=3
                )

    # Updates the tools tab
    def update_tools_tab(self):
        self.toggle_tools_button.configure(
            text=f"Tools {'Enabled' if self.enable_tools is True else 'Disabled'}",
            fg_color=(
                self.button_colors["enabled"]
                if self.enable_tools
                else self.button_colors["disabled"]
            ),
        )

        anto_drop_spike_color = (
            self.button_colors["enabled"]
            if self.auto_drop_spike is True
            else self.button_colors["disabled"]
        )
        self.auto_drop_spike_button.configure(
            fg_color=anto_drop_spike_color,
        )
        self.overview_drop_spike_button.configure(
            fg_color=anto_drop_spike_color,
        )

        anti_afk_color = (
            self.button_colors["enabled"]
            if self.anti_afk is True
            else self.button_colors["disabled"]
        )
        self.anti_afk_button.configure(
            fg_color=anti_afk_color,
        )
        self.overview_anti_afk_button.configure(
            fg_color=anti_afk_color,
        )

    # Changes the active frame
    def select_frame_by_name(self, frame_name):
        frame_mapping = {
            "Overview": self.overview_frame,
            "Agent Toggle": self.agent_toggle_frame,
            "Random Agent": self.random_agent_frame,
            "Map Specific": self.map_specific_frame,
            "Save File": self.save_file_frame,
            "Tools": self.tools_frame,
            "Settings": self.settings_frame,
        }

        for button_name in self.nav_buttons:
            self.nav_buttons[button_name].configure(
                fg_color=(
                    ("gray75", "gray25") if frame_name == button_name else "transparent"
                )
            )

            if frame_name == button_name:
                frame_mapping[button_name].grid(row=0, column=1, sticky="nsew")
            else:
                frame_mapping[button_name].grid_forget()

    # endregion

    # endregion

    # region Icon

    # Creates the tray icon
    def create_tray_icon(self):
        self.icon_menu = pystray.Menu(
            pystray.MenuItem(
                lambda x: f"Show GUI", lambda x: self.show_window(), default=True
            ),
            pystray.MenuItem(
                lambda x: f'Status: {"Enabled" if self.enabled else "Disabled"}',
                lambda x: self.toggle_active(),
                checked=lambda x: self.enabled,
            ),
            pystray.MenuItem(
                lambda x: f"Status: {'None' if self.enabled is False else 'Locking' if self.locking is True else 'In Game (Waiting)'}",
                lambda x: self.toggle_thread_mode(),
            ),
            pystray.MenuItem("Exit", lambda x: self.exit()),
        )

    # Updates GUI and tray icons
    def update_icon(self):
        if self.enabled is False:
            self.current_icon = self.icons["disabled"]
        elif self.locking is True:
            self.current_icon = self.icons["locking"]
        else:
            self.current_icon = self.icons["waiting"]

        self.wm_iconbitmap(resource_path(self.current_icon))
        try:
            self.icon.icon = PIL.Image.open(resource_path(self.current_icon))
        except AttributeError:
            pass

    # Shows the window when icon is clicked
    def show_window(self):
        try:
            self.icon.stop()
        except AttributeError:
            pass
        self.protocol("WM_DELETE_WINDOW", self.withdraw_window)
        self.after(0, self.deiconify)

    # Hides the window then the [X] is clicked
    def withdraw_window(self):
        self.withdraw()
        self.icon = pystray.Icon(
            "VALocker",
            PIL.Image.open(resource_path(self.current_icon)),
            "VALocker",
            self.icon_menu,
        )
        self.icon.run()

    # endregion

    # region Toggles

    def toggle_setting(self, setting_name, setting_value=None):
        with open(resource_path("data/user_settings.json"), "r") as user_settings_file:
            user_settings = json.load(user_settings_file)
            match setting_name:
                case "minimize_to_tray":
                    self.minimize_to_tray = (
                        not self.minimize_to_tray
                        if setting_value is None
                        else setting_value
                    )
                    user_settings["MINIMIZE_TO_TRAY"] = self.minimize_to_tray

                    self.minimize_to_tray_button.configure(
                        fg_color=(
                            self.button_colors["enabled"]
                            if self.minimize_to_tray
                            else self.button_colors["disabled"]
                        ),
                    )

                    if self.minimize_to_tray is True:
                        self.protocol("WM_DELETE_WINDOW", self.withdraw_window)
                        self.create_tray_icon()
                        self.start_minimized_button.configure(state=tk.NORMAL)

                    else:
                        self.start_minimized_button.configure(state=tk.DISABLED)
                        self.protocol("WM_DELETE_WINDOW", self.exit)
                        try:
                            self.icon.stop()
                        except AttributeError:
                            pass

                case "start_minimized":
                    user_settings["START_MINIMIZED"] = (
                        not user_settings["START_MINIMIZED"]
                        if setting_value is None
                        else setting_value
                    )

                    self.start_minimized_button.configure(
                        fg_color=(
                            self.button_colors["enabled"]
                            if user_settings["START_MINIMIZED"]
                            else self.button_colors["disabled"]
                        )
                    )
                case "enable_on_startup":
                    user_settings["ENABLE_ON_STARTUP"] = (
                        not user_settings["ENABLE_ON_STARTUP"]
                        if setting_value is None
                        else setting_value
                    )
                    self.enable_on_startup_button.configure(
                        fg_color=(
                            self.button_colors["enabled"]
                            if user_settings["ENABLE_ON_STARTUP"]
                            else self.button_colors["disabled"]
                        ),
                    )
                case "safe_mode_on_startup":
                    user_settings["SAFE_MODE_ON_STARTUP"] = (
                        not user_settings["SAFE_MODE_ON_STARTUP"]
                        if setting_value is None
                        else setting_value
                    )
                    self.safe_mode_on_startup_button.configure(
                        fg_color=(
                            self.button_colors["enabled"]
                            if user_settings["SAFE_MODE_ON_STARTUP"]
                            else self.button_colors["disabled"]
                        ),
                    )
                case "safe_mode_strength_on_startup":
                    self.safe_mode_strength_on_startup = user_settings[
                        "SAFE_MODE_STRENGTH_ON_STARTUP"
                    ]
                    if (
                        self.safe_mode_strength_on_startup
                        >= len(self.safe_mode_timing) - 1
                    ):
                        self.safe_mode_strength_on_startup = 0
                    else:
                        self.safe_mode_strength_on_startup += 1
                    user_settings["SAFE_MODE_STRENGTH_ON_STARTUP"] = (
                        self.safe_mode_strength_on_startup
                    )
                    self.safe_mode_strength_on_startup_button.configure(
                        text=f"Safe Mode Strength: {list(self.safe_mode_timing.keys())[self.safe_mode_strength_on_startup]}",
                    )
                case "persistent_random_agents":
                    self.persistent_random_agents = (
                        not self.persistent_random_agents
                        if setting_value is None
                        else setting_value
                    )
                    user_settings["PERSISTENT_RANDOM_AGENTS"] = (
                        self.persistent_random_agents
                    )

                    self.persistent_random_agents_button.configure(
                        fg_color=(
                            self.button_colors["enabled"]
                            if self.persistent_random_agents
                            else self.button_colors["disabled"]
                        ),
                    )
                case "grab_keybinds":
                    self.grab_keybinds = (
                        not self.grab_keybinds
                        if setting_value is None
                        else setting_value
                    )
                    user_settings["GRAB_KEYBINDS"] = self.grab_keybinds

                    self.grab_keybinds_button.configure(
                        fg_color=(
                            self.button_colors["enabled"]
                            if self.grab_keybinds
                            else self.button_colors["disabled"]
                        ),
                    )
                case "hide_default_save_file":
                    self.hide_default_save_file = (
                        not self.hide_default_save_file
                        if setting_value is None
                        else setting_value
                    )
                    user_settings["HIDE_DEFAULT_SAVE_FILE"] = (
                        self.hide_default_save_file
                    )

                    self.hide_default_save_file_button.configure(
                        fg_color=(
                            self.button_colors["enabled"]
                            if self.hide_default_save_file
                            else self.button_colors["disabled"]
                        ),
                    )
                    self.update_save_file_tab()

                case "change_anti_afk_mode":
                    states_list = [
                        "forward",
                        "strafe",
                        "circle",
                        "random",
                        "random ctr.",
                    ]
                    try:
                        current_index = states_list.index(
                            user_settings["ANTI_AFK_MODE"]
                        )
                        next_index = (current_index + 1) % len(states_list)
                        next_state = states_list[next_index]
                    except ValueError:
                        next_state = states_list[0]

                    user_settings["ANTI_AFK_MODE"] = (
                        next_state if setting_value is None else setting_value
                    )
                    self.anti_afk_mode = user_settings["ANTI_AFK_MODE"]

                    self.anti_afk_mode_button.configure(
                        text=f"Anti AFK Mode: {self.anti_afk_mode.title()}",
                    )

                case "anti_afk_toggles_auto_drop":
                    self.anti_afk_toggles_auto_drop = (
                        not self.anti_afk_toggles_auto_drop
                        if setting_value is None
                        else setting_value
                    )

                    user_settings["ANTIAFK_TOGGLES_AUTODROPSPIKE"] = (
                        self.anti_afk_toggles_auto_drop
                    )

                    self.anti_afk_toggles_auto_drop_button.configure(
                        fg_color=(
                            self.button_colors["enabled"]
                            if self.anti_afk_toggles_auto_drop
                            else self.button_colors["disabled"]
                        ),
                    )

                case "detect_open_chat_keyboard":
                    self.detect_open_chat_keyboard = (
                        not self.detect_open_chat_keyboard
                        if setting_value is None
                        else setting_value
                    )
                    user_settings["DETECT_OPEN_CHAT_THROUGH_KEYBOARD"] = (
                        self.detect_open_chat_keyboard
                    )

                    self.detect_open_chat_mode_button.configure(
                        fg_color=(
                            self.button_colors["enabled"]
                            if self.detect_open_chat_keyboard
                            else self.button_colors["disabled"]
                        ),
                    )

                case "start_tools_thread_automatically":
                    self.start_tools_thread_automatically = (
                        not self.start_tools_thread_automatically
                        if setting_value is None
                        else setting_value
                    )
                    user_settings["START_TOOLS_THREAD_AUTOMATICALLY"] = (
                        self.start_tools_thread_automatically
                    )

                    self.start_tools_thread_automatically_button.configure(
                        fg_color=(
                            self.button_colors["enabled"]
                            if self.start_tools_thread_automatically
                            else self.button_colors["disabled"]
                        ),
                    )

        with open(resource_path("data/user_settings.json"), "w") as user_settings_file:
            json.dump(user_settings, user_settings_file, indent=4)

    # Toggles the active state of the program between running and stopped
    def toggle_active(self):
        self.enabled = not self.enabled
        self.update_overview_tab()
        self.update_icon()

    # Toggles the thread between locking and waiting
    def toggle_thread_mode(self):
        self.locking = not self.locking
        self.update_overview_tab()
        self.update_icon()

    # Toggles the safe mode
    def toggle_safe_mode(self):
        self.safe_mode = not self.safe_mode
        self.update_overview_tab()

    # Increases the safe mode strength
    def toggle_safe_mode_strength(self):
        if self.safe_mode_strength >= len(self.safe_mode_timing) - 1:
            self.safe_mode_strength = 0
        else:
            self.safe_mode_strength += 1
        self.update_overview_tab()

    # Toggles the map specific mode
    def toggle_map_specific(self):
        self.map_specific_mode = not self.map_specific_mode
        self.update_overview_tab()
        self.update_map_specific_tab()

    # Toggles the random agent mode
    def toggle_random_agent_mode(self):
        self.random_agent_mode = not self.random_agent_mode
        if self.random_agent_mode is False:
            self.find_agent_coords(self.selected_agent)
        self.update_overview_tab()

    # Toggles the hover mode
    def toggle_hover_mode(self):
        self.hover_mode = not self.hover_mode
        self.update_overview_tab()

    # Toggles exclusiselect mode
    def toggle_random_agent_exclusiselect(self):
        self.random_agent_exclusiselect = not self.random_agent_exclusiselect

        if self.random_agent_exclusiselect is True:
            self.random_agents_dict_backup = self.random_agents_dict.copy()
        else:
            self.random_agents_dict = self.random_agents_dict_backup.copy()

        self.random_agent_exclusiselect_button.configure(
            fg_color=(
                self.button_colors["enabled"]
                if self.random_agent_exclusiselect
                else self.button_colors["disabled"]
            ),
        )

        self.update_random_agent_tab(exclusiselect_mode=True)

    # Toggles different tools
    def explicitly_toggle_tools(self):
        # self.enable_tools = not self.enable_tools
        self.toggle_tools(explicit_toggle=True)
        self.update_tools_tab()

    # Toggles auto drop spike
    def toggle_auto_drop_spike(self):
        self.auto_drop_spike = not self.auto_drop_spike

        if self.auto_drop_spike:
            self.running_tools.add("auto_drop_spike")
        else:
            self.running_tools.discard("auto_drop_spike")

        self.toggle_tools()
        self.update_tools_tab()

    # Toggles anti afk
    def toggle_anti_afk(self):
        self.anti_afk = not self.anti_afk

        if self.anti_afk:
            self.running_tools.add("anti_afk")
        else:
            self.running_tools.discard("anti_afk")

        self.toggle_tools()
        self.update_tools_tab()

    # Toggles anti aim (not implemented yet)
    def toggle_anti_aim(self):
        self.anti_aim = not self.anti_aim
        self.toggle_tools()
        self.update_tools_tab()

    # endregion

    # region Config Files

    # Loads all the data from the config.json and current save file
    def load_data_from_files(self, first_run=False):
        # Loads the config.json file
        if first_run is True:
            with open(resource_path("data/config.json"), "r") as config_file:
                config = json.load(config_file)

                self.default_agents = config["DEFAULT_AGENTS"]
                self.box_info = config["BOX_INFO"]
                self.config_file_agents = config["ALL_AGENTS"]
                self.map_names = config["MAPS"]
                self.keybinds = config["DEFAULT_KEYBINDS"]

            # Loads the map images
            for map_name in self.map_names:
                try:
                    map_binary = PIL.Image.open(
                        resource_path(f"images/map_images/{map_name}.png")
                    ).tobytes()
                    self.map_lookup[map_binary] = map_name
                except (PIL.UnidentifiedImageError, FileNotFoundError):
                    self.map_lookup[None] = map_name

            # Loads the user_settings.json file, clears time_to_lock if new timings are added
            if not os.path.exists(resource_path("data/user_settings.json")):
                with open(resource_path("data/user_settings.json"), "w") as empty_file:
                    empty_file.write("{}")

            with open(
                resource_path("data/user_settings.json"), "r"
            ) as user_settings_file:
                user_settings = json.load(user_settings_file)

                active_save_file = user_settings.get("ACTIVE_SAVE_FILE", None)
                self.current_save_file = (
                    active_save_file
                    if active_save_file in self.save_files
                    else "default"
                )

                self.minimize_to_tray = user_settings.get("MINIMIZE_TO_TRAY", False)
                self.start_minimized = user_settings.get("START_MINIMIZED", False)

                self.enabled = self.enable_on_startup = user_settings.get(
                    "ENABLE_ON_STARTUP", False
                )

                self.safe_mode = self.safe_mode_on_startup = user_settings.get(
                    "SAFE_MODE_ON_STARTUP", True
                )
                self.safe_mode_strength = self.safe_mode_strength_on_startup = (
                    user_settings.get("SAFE_MODE_STRENGTH_ON_STARTUP", 0)
                )

                self.persistent_random_agents = user_settings.get(
                    "PERSISTENT_RANDOM_AGENTS", False
                )

                self.locking_confirmations_required = user_settings.get(
                    "LOCKING_CONFIRMATIONS", 3
                )
                self.menu_screen_confirmaions_required = user_settings.get(
                    "MENU_CONFIRMATIONS", 3
                )

                self.grab_keybinds = user_settings.get("GRAB_KEYBINDS", True)

                self.fast_mode_timings = user_settings.get(
                    "FAST_MODE_TIMINGS", [0.02, 0.02, 0.02]
                )

                self.hide_default_save_file = user_settings.get(
                    "HIDE_DEFAULT_SAVE_FILE", True
                )

                self.anti_afk_mode = user_settings.get("ANTI_AFK_MODE", "forward")

                self.anti_afk_toggles_auto_drop = user_settings.get(
                    "ANTIAFK_TOGGLES_AUTODROPSPIKE", False
                )

                self.detect_open_chat_keyboard = user_settings.get(
                    "DETECT_OPEN_CHAT_THROUGH_KEYBOARD", True
                )

                self.start_tools_thread_automatically = user_settings.get(
                    "START_TOOLS_THREAD_AUTOMATICALLY", True
                )

            with open(resource_path("data/user_settings.json"), "w") as us:
                user_settings_file_json = {
                    "ACTIVE_SAVE_FILE": self.current_save_file,
                    "ENABLE_ON_STARTUP": self.enable_on_startup,
                    "MINIMIZE_TO_TRAY": self.minimize_to_tray,
                    "START_MINIMIZED": self.start_minimized,
                    "SAFE_MODE_ON_STARTUP": self.safe_mode_on_startup,
                    "SAFE_MODE_STRENGTH_ON_STARTUP": self.safe_mode_strength_on_startup,
                    "LOCKING_CONFIRMATIONS": self.locking_confirmations_required,
                    "MENU_CONFIRMATIONS": self.menu_screen_confirmaions_required,
                    "FAST_MODE_TIMINGS": self.fast_mode_timings,
                    "GRAB_KEYBINDS": self.grab_keybinds,
                    "PERSISTENT_RANDOM_AGENTS": self.persistent_random_agents,
                    "HIDE_DEFAULT_SAVE_FILE": self.hide_default_save_file,
                    "ANTI_AFK_MODE": self.anti_afk_mode,
                    "ANTIAFK_TOGGLES_AUTODROPSPIKE": self.anti_afk_toggles_auto_drop,
                    "DETECT_OPEN_CHAT_THROUGH_KEYBOARD": self.detect_open_chat_keyboard,
                    "START_TOOLS_THREAD_AUTOMATICALLY": self.start_tools_thread_automatically,
                }
                us.write(json.dumps(user_settings_file_json, indent=4))

            # Loads stats
            try:
                with open(resource_path("data/stats.json"), "r") as stats_file:
                    stats_json = json.load(stats_file)
                    self.favorited_save_files = stats_json["FAVORITED_SAVE_FILES"]
                    self.total_games_used = stats_json["TIMES_USED"]
                    self.time_to_lock_list = stats_json["TIME_TO_LOCK"]

                if len(self.time_to_lock_list) != len(self.safe_mode_timing) + 1:
                    self.time_to_lock_list = list(
                        list() for _ in range(len(self.safe_mode_timing) + 1)
                    )

            # Creates stats file if it does not exist
            except Exception:
                with open(resource_path("data/stats.json"), "w") as stats:
                    stats_json = {
                        "FAVORITED_SAVE_FILES": self.favorited_save_files,
                        "TIMES_USED": self.total_games_used,
                        "TIME_TO_LOCK": self.time_to_lock_list,
                    }
                    stats.write(json.dumps(stats_json, indent=4))

        # Loads the save file data
        with open(
            resource_path(f"data/save_files/{self.current_save_file}.json"), "r"
        ) as sf:
            save_file_json = json.load(sf)
            self.selected_agent = save_file_json["SELECTED_AGENT"]
            self.unlocked_agents_dict = save_file_json["UNLOCKED_AGENTS"]
            self.random_agents_dict = save_file_json["RANDOM_AGENTS"]
            self.random_agents_dict_backup = self.random_agents_dict.copy()
            self.map_specific_agents_dict = save_file_json["MAP_SPECIFIC_AGENTS"]

        # Creates a list of all agents
        self.all_agents = list(
            agent
            for role in self.config_file_agents
            for agent in self.config_file_agents[role]
        )
        self.all_agents.sort()

        # Makes sure any new agents are added to the save file as unlocked
        for agent in self.all_agents:
            if agent not in self.unlocked_agents_dict:
                if agent in self.default_agents:
                    self.unlocked_agents_dict[agent] = True
                else:
                    self.unlocked_agents_dict[agent] = False

            if agent not in self.random_agents_dict:
                self.random_agents_dict[agent] = False

        # Removes any agents from save file that are not in the config file
        for agent in self.unlocked_agents_dict.copy():
            if agent not in self.all_agents:
                del self.unlocked_agents_dict[agent]

        for agent in self.random_agents_dict.copy():
            if agent not in self.all_agents:
                del self.random_agents_dict[agent]

        # Makes sure that all default agents are enabled
        for agent in self.default_agents:
            self.unlocked_agents_dict[agent] = True

        # Makes sure any new maps are added to the map specific agents dict
        for map_name in self.map_names:
            if map_name not in self.map_specific_agents_dict:
                self.map_specific_agents_dict[map_name] = None

        # Removes any maps from the save file that are not in the config file
        for map_name in self.map_specific_agents_dict.copy():
            if map_name not in self.map_names:
                del self.map_specific_agents_dict[map_name]

        # Calculates location of box coords
        if first_run is True:
            self.box_coords = dict()
            for box_index in range(len(self.all_agents)):
                position_x = self.box_info["TOPLEFT"][0] + (
                    (box_index % self.box_info["COLUMNS"])
                    * (self.box_info["SIZE"] + self.box_info["XDIST"])
                )
                position_y = self.box_info["TOPLEFT"][1] + (
                    (box_index // self.box_info["COLUMNS"])
                    * (self.box_info["SIZE"] + self.box_info["YDIST"])
                )
                self.box_coords[f"Box{box_index}"] = (position_x, position_y)

        # Sorts the agents alphabetically before saving them
        self.unlocked_agents_dict = dict(sorted(self.unlocked_agents_dict.items()))
        self.random_agents_dict = dict(sorted(self.random_agents_dict.items()))
        self.map_specific_agents_dict = dict(
            sorted(self.map_specific_agents_dict.items())
        )

        # Makes sure selected agent is unlocked
        if self.unlocked_agents_dict[self.selected_agent] is False:
            self.selected_agent = list(
                agent
                for agent, unlock_status in self.unlocked_agents_dict.items()
                if unlock_status is True
            )[0]

        # Sets map agents that are not unlocked to None
        for map_name in self.map_specific_agents_dict.keys():
            agent_name = self.map_specific_agents_dict[map_name]
            if (
                agent_name in self.unlocked_agents_dict
                and self.unlocked_agents_dict[agent_name] is False
            ):
                self.map_specific_agents_dict[map_name] = None

        # Gets Coords for the selected agent
        self.find_agent_coords(self.selected_agent)

        # Saves the data to the current save file
        self.save_current_data()

    # Saves all the data to the current save file
    def save_current_data(self):
        with open(
            resource_path(f"data/save_files/{self.current_save_file}.json"), "w"
        ) as sf:
            save_file_json = {
                "SELECTED_AGENT": self.selected_agent,
                "UNLOCKED_AGENTS": self.unlocked_agents_dict,
                "RANDOM_AGENTS": self.random_agents_dict,
                "MAP_SPECIFIC_AGENTS": self.map_specific_agents_dict,
            }
            sf.write(json.dumps(save_file_json, indent=4))

    # Updates the stats.json file
    def update_user_settings(self):
        with open(resource_path("data/stats.json"), "r") as stats_file:
            config = json.load(stats_file)
            config["FAVORITED_SAVE_FILES"] = self.favorited_save_files
            config["TIMES_USED"] = self.total_games_used
            config["TIME_TO_LOCK"] = self.time_to_lock_list
        with open(resource_path("data/stats.json"), "w") as file:
            file.write(json.dumps(config, indent=4))

    # endregion

    # region Save Files

    # Changes the current active save file
    def change_current_save_file(self, file_name):
        self.current_save_file = file_name

        with open(resource_path("data/user_settings.json"), "r") as config_file:
            config = json.load(config_file)
            config["ACTIVE_SAVE_FILE"] = file_name
        with open(resource_path("data/user_settings.json"), "w") as file:
            file.write(json.dumps(config, indent=4))

        self.load_data_from_files()

        self.update_save_file_tab()
        self.update_overview_tab()
        self.update_agent_toggle_tab(loading_new_save=True)
        self.update_map_specific_tab()
        self.update_random_agent_tab(loading_new_save=True)

    # Favorites the save file indicated by the file_name
    def favorite_save_file(self, file_name):
        if file_name in self.favorited_save_files.copy():
            self.favorited_save_files.remove(file_name)
        else:
            self.favorited_save_files.append(file_name)
        self.update_save_file_tab()
        self.update_user_settings()

    # Renames the save file indicated by the old_file_name
    def rename_save_file(self, old_file_name):
        new_file_name = None
        is_valid_file_name = False
        while is_valid_file_name is False:
            new_file_name = InputPopup(
                window_geometry=self.winfo_geometry(),
                title="Rename Save File",
                filled_in_text=new_file_name,
                file_name=old_file_name,
                colors=self.button_colors,
                main_font=self.main_font,
                is_new_file=False,
            ).get_input()

            is_valid_file_name = self.valid_file_name(new_file_name)

            if is_valid_file_name is None:
                return

        # Configures the button to use the new file name
        self.save_file_frame_items[f"{old_file_name}_button"].configure(
            text=new_file_name,
            command=lambda save_file=new_file_name: self.change_current_save_file(
                save_file
            ),
        )

        # Renames the button and frame to use the new file name
        self.save_file_frame_items[f"{new_file_name}_frame"] = (
            self.save_file_frame_items.pop(f"{old_file_name}_frame")
        )
        self.save_file_frame_items[f"{new_file_name}_button"] = (
            self.save_file_frame_items.pop(f"{old_file_name}_button")
        )

        for icon_name in ["favorite", "rename", "delete"]:
            self.save_file_frame_items[f"{old_file_name}_{icon_name}"].destroy()

        # Removes old icons and adds new icons with the new name
        self.individual_save_file_items(new_file_name, just_icons=True)

        # Updates the current save file if it was renamed
        if old_file_name == self.current_save_file:
            self.current_save_file = new_file_name

        # Updates the favorited save files if it was renamed
        if old_file_name in self.favorited_save_files:
            self.favorited_save_files[
                self.favorited_save_files.index(old_file_name)
            ] = new_file_name
            self.update_user_settings()

        # Renames the save file in the save_files folder
        os.rename(
            resource_path(f"./data/save_files/{old_file_name}.json"),
            resource_path(f"./data/save_files/{new_file_name}.json"),
        )

        # Updates the list of files and the save file tab
        self.find_save_files()
        self.update_save_file_tab()
        self.update_overview_tab()

    # Deletes the save file indicated by the file_name
    def delete_save_file(self, file_name):
        # Does not delete the save file if it is favorited
        if file_name in self.favorited_save_files:
            return

        # Failsafe to make sure the user does not delete the default save file or the current one
        if file_name == self.current_save_file or file_name == "default":
            return

        is_confirmed = ConfirmDeletePopup(
            window_geometry=self.winfo_geometry(),
            file_name=file_name,
            colors=self.button_colors,
            main_font=self.main_font,
        ).get_input()

        # Does not delete the save file if the user cancels
        if is_confirmed is not True:
            return

        # Removes the save file from the favorited save files
        if file_name in self.favorited_save_files.copy():
            self.favorited_save_files.remove(file_name)
            self.update_user_settings()

        # Removes the save file from the save file tab
        self.save_file_frame_items[f"{file_name}_frame"].destroy()

        # Deletes the save file from the save_files folder
        os.remove(resource_path(f"./data/save_files/{file_name}.json"))

        # Updates the list of files and the save file tab
        self.find_save_files()
        self.update_save_file_tab()

    # Creates a new save file
    def new_save_file(self):
        is_valid_file_name = False
        file_name = None
        while is_valid_file_name is False:
            file_name = InputPopup(
                window_geometry=self.winfo_geometry(),
                title="Create New Save File",
                file_name="",
                filled_in_text=file_name,
                colors=self.button_colors,
                is_new_file=True,
                main_font=self.main_font,
            ).get_input()

            is_valid_file_name = self.valid_file_name(file_name)

            if is_valid_file_name is None:
                return

        # Opens the default save file and turns all values to default
        with open(resource_path(f"./data/save_files/default.json"), "r") as sf:
            default_save_file_json = json.load(sf)
            for agent in default_save_file_json["UNLOCKED_AGENTS"]:
                default_save_file_json["UNLOCKED_AGENTS"][agent] = False
            for agent in default_save_file_json["RANDOM_AGENTS"]:
                default_save_file_json["RANDOM_AGENTS"][agent] = False
            for map in default_save_file_json["MAP_SPECIFIC_AGENTS"]:
                default_save_file_json["MAP_SPECIFIC_AGENTS"][map] = None

            save_file_json = {
                "SELECTED_AGENT": default_save_file_json["SELECTED_AGENT"],
                "UNLOCKED_AGENTS": default_save_file_json["UNLOCKED_AGENTS"],
                "RANDOM_AGENTS": default_save_file_json["RANDOM_AGENTS"],
                "MAP_SPECIFIC_AGENTS": default_save_file_json["MAP_SPECIFIC_AGENTS"],
            }

        # Creates the new save file
        with open(resource_path(f"./data/save_files/{file_name}.json"), "w") as sf:
            sf.write(json.dumps(save_file_json, indent=4))

        # Finds the save file and adds it to the list
        self.individual_save_file_items(file_name)
        self.find_save_files()
        self.update_save_file_tab()

        # Changes the current save file to the new one
        self.change_current_save_file(file_name)

    # Checks the name of the save file to make sure it is valid
    def valid_file_name(self, new_file_name):
        if new_file_name is None:
            return None

        if new_file_name == "":
            cancel_event = ErrorPopup(
                window_geometry=self.winfo_geometry(),
                title="Invalid File Name",
                message="File Name Cannot Be Empty",
                colors=self.button_colors,
                main_font=self.main_font,
            ).get_input()
            return cancel_event

        if new_file_name in self.save_files:
            cancel_event = ErrorPopup(
                window_geometry=self.winfo_geometry(),
                title="Invalid File Name",
                message="File Name Already Exists",
                colors=self.button_colors,
                main_font=self.main_font,
            ).get_input()
            return cancel_event

        for disallowed_char in ["/", "\\", ":", "*", "?", '"', "<", ">", "|"]:
            if disallowed_char in new_file_name:
                cancel_event = ErrorPopup(
                    window_geometry=self.winfo_geometry(),
                    title="Invalid File Name",
                    message='File Name Cannot Contain:\n/ \\ : * ? " < > |',
                    colors=self.button_colors,
                    main_font=self.main_font,
                ).get_input()
                return cancel_event

        return True

    # Finds all save files in data/save_files
    def find_save_files(self):
        self.save_files = ["default"]
        for file in os.listdir(resource_path("./data/save_files")):
            if file.endswith(".json") and file.startswith("default") is False:
                self.save_files.append(file.removesuffix(".json"))

    # endregion

    # region Agent Toggles

    # Toggles the default / locking agent
    def toggle_selected_agent(self, agent_name):
        self.selected_agent = agent_name
        self.find_agent_coords(self.selected_agent)
        self.save_current_data()
        self.update_overview_tab()

    # Toggles whether or not the agent is unlocked
    def toggle_unlocked_agent_status(self, agent_name):
        match agent_name:
            case "all":
                for agent in self.all_agents:
                    self.unlocked_agents_dict[agent] = True
            case "none":
                for agent in self.all_agents:
                    if agent not in self.default_agents:
                        self.unlocked_agents_dict[agent] = False
                        self.random_agents_dict[agent] = False
            case _:
                self.unlocked_agents_dict[agent_name] = not self.unlocked_agents_dict[
                    agent_name
                ]
                if self.unlocked_agents_dict[agent_name] is False:
                    self.random_agents_dict[agent_name] = False

        # Makes sure selected agent is unlocked
        if self.unlocked_agents_dict[self.selected_agent] is False:
            self.selected_agent = list(
                agent
                for agent, unlock_status in self.unlocked_agents_dict.items()
                if unlock_status is True
            )[0]

        self.update_agent_toggle_tab(agent_name)
        self.update_random_agent_tab(
            "toggle_unlocked_agent_status", toggled_agent_name=agent_name
        )

        self.update_agent_toggle_tab()
        self.update_overview_tab()
        self.update_map_specific_tab()
        self.update_random_agent_tab()

        self.find_agent_coords(self.selected_agent)
        self.save_current_data()

    # Toggles the agent in the random agent tab
    def toggle_random_agent_status(self, agent_name, exclusiselect_toggle=False):
        match agent_name:
            case "all":
                for agent in self.all_agents:
                    if self.unlocked_agents_dict[agent] is True:
                        self.random_agents_dict[agent] = True
            case "none":
                for agent in self.all_agents:
                    self.random_agents_dict[agent] = False
                self.random_agent_mode = False
            case "controllers" | "duelists" | "initiators" | "sentinels":
                if all(
                    self.random_agents_dict[agent] is True
                    for agent in self.config_file_agents[agent_name.upper()]
                    if self.unlocked_agents_dict[agent] is True
                ):
                    for agent in self.config_file_agents[agent_name.upper()]:
                        if self.unlocked_agents_dict[agent] is True:
                            self.random_agents_dict[agent] = False
                else:
                    for agent in self.config_file_agents[agent_name.upper()]:
                        if self.unlocked_agents_dict[agent] is True:
                            self.random_agents_dict[agent] = True
            case _:
                self.random_agents_dict[agent_name] = not self.random_agents_dict[
                    agent_name
                ]

        # Only updates the list if a checkbox is selected, not when the ExclusiSelect mode is toggled
        if self.persistent_random_agents is False and (
            self.random_agent_exclusiselect is True and exclusiselect_toggle is False
        ):
            self.random_agents_dict_backup = self.random_agents_dict.copy()

        self.update_random_agent_tab(
            agent_name, exclusiselect_mode=exclusiselect_toggle
        )
        self.update_overview_tab()
        if exclusiselect_toggle is False:
            self.save_current_data()

    # Toggles which agent is selected for a specific map
    def toggle_map_specific_agent(self, agent_name, map_name):
        self.map_specific_agents_dict[map_name] = agent_name
        self.update_map_specific_tab()
        self.update_overview_tab()
        self.save_current_data()

    # endregion

    # region Check Updates

    def get_latest_version(self, timeout=1):
        URL = "https://api.github.com/repos/E1Bos/VALocker/releases/latest"
        try:
            r = requests.get(URL, timeout=timeout)
            if r.status_code == 200:
                return r.json()["tag_name"]
            else:
                return None
        except requests.exceptions.Timeout:
            return None

    def compare_versions(self, current_version, latest_version):
        current_version = current_version[1:].split(
            "."
        )  # Remove 'v' and split into parts
        latest_version = latest_version[1:].split(".")

        for v1, v2 in zip(current_version, latest_version):
            if int(v1) < int(v2):
                return True  # The latest version is higher and requires an update
            elif int(v1) > int(v2):
                return False  # The current version is higher or equal, no update needed

        if len(current_version) < len(latest_version):
            return (
                True  # The latest version has more parts, indicating a higher version
            )
        elif len(current_version) == len(latest_version):
            return False  # Both versions are equal

    # endregion

    # region Locking Thread

    # Starts the locking thread, calls the locking function based on the mode
    def locking_main(self):
        time.sleep(1)
        if self.locking_screenshotter is None:
            self.locking_screenshotter = mss.mss()
        while self.active_thread is True:
            time.sleep(0.3)
            if self.enabled is True and self.active_thread is True:
                self.lock_button = (
                    self.box_info["LOCK_COORDS"][0]
                    + random.randint(0, self.box_info["LOCK_SIZE"][0]),
                    self.box_info["LOCK_COORDS"][1]
                    + random.randint(0, self.box_info["LOCK_SIZE"][1]),
                )
                if self.locking is True:
                    if self.map_specific_mode is False:
                        self.locate_agent_screen()
                    else:
                        self.locate_map_screen()
                else:
                    self.find_game_end()

    # Detects which map the game is on
    def locate_map_screen(self):
        game_map = None
        while (
            game_map == None
            and self.active_thread is True
            and self.locking is True
            and self.enabled is True
            and self.map_specific_mode is True
        ):
            time.sleep(0.1)

            current_map = self.return_screenshot_bytes(
                self.locking_screenshotter, self.map_selection_coords
            )
            game_map = self.map_lookup.get(current_map)

        if game_map is not None:
            self.find_agent_coords(self.map_specific_agents_dict[game_map])
            self.locate_agent_screen(True)
        else:
            self.find_game_end()

    # Detects when in the agent select screen
    def locate_agent_screen(self, map_specific_toggle=False):
        confirmations = 0
        self.start_lock = float()
        while (
            self.active_thread is True
            and self.locking is True
            and self.enabled is True
            and self.map_specific_mode is map_specific_toggle
        ):
            if self.compare_screenshot_to_pattern(
                self.locking_screenshotter,
                self.coords["locking"],
                self.pixel_patterns["locking"],
            ):
                confirmations += 1

                if confirmations >= self.locking_confirmations_required:
                    self.lock_agent()
            else:
                confirmations = 0
        self.find_game_end()

    # Locks the agent
    def lock_agent(self):
        start_time = time.time()
        if self.random_agent_mode is True:
            randomly_selected_agent = random.choice(
                list(
                    agent
                    for agent in self.random_agents_dict
                    if self.random_agents_dict[agent] is True
                )
            )
            self.find_agent_coords(randomly_selected_agent)

        if self.safe_mode is False:
            self.mouse.position = (self.agent_coords[0], self.agent_coords[1])
            time.sleep(self.fast_mode_timings[0])
            self.mouse.click(pynmouse.Button.left, 1)
            time.sleep(self.fast_mode_timings[1])

            if self.hover_mode is False:
                self.mouse.position = (self.lock_button[0], self.lock_button[1])
                time.sleep(self.fast_mode_timings[2])
                self.mouse.click(pynmouse.Button.left, 1)

        else:
            low_timing = (
                list(self.safe_mode_timing.values())[self.safe_mode_strength][0] / 4
            )
            high_timing = (
                list(self.safe_mode_timing.values())[self.safe_mode_strength][1] / 4
            )

            time.sleep(round(random.uniform(low_timing, high_timing), 2))
            self.mouse.position = (self.agent_coords[0], self.agent_coords[1])
            time.sleep(round(random.uniform(low_timing, high_timing), 2))
            self.mouse.click(pynmouse.Button.left, 1)
            time.sleep(round(random.uniform(low_timing, high_timing), 2))

            if self.hover_mode is False:
                self.mouse.position = (self.lock_button[0], self.lock_button[1])
                time.sleep(round(random.uniform(low_timing, high_timing), 2))
                self.mouse.click(pynmouse.Button.left, 1)

        time_to_lock = round((time.time() - start_time) * 1000, 2)

        if self.safe_mode is True:
            self.time_to_lock_list[self.safe_mode_strength].append(time_to_lock)
        else:
            self.time_to_lock_list[-1].append(time_to_lock)

        if self.random_agent_mode is True and self.random_agent_exclusiselect is True:
            self.toggle_random_agent_status(
                randomly_selected_agent, exclusiselect_toggle=True
            )
            if all(value is False for value in self.random_agents_dict.values()):
                self.toggle_random_agent_exclusiselect()

        self.locking = False
        self.total_games_used += 1

        last_five_data_points = list()
        for timing_list in self.time_to_lock_list:
            if len(timing_list) >= 5:
                last_five_data_points.append(timing_list[-5:])
            else:
                last_five_data_points.append(timing_list)
        self.time_to_lock_list = last_five_data_points

        self.update_overview_tab()
        self.update_user_settings()

    # Finds the end of the game
    def find_game_end(self):
        confirmations = 0
        while (
            self.enabled is True
            and self.active_thread is True
            and self.locking is False
        ):
            player_banner = self.compare_screenshot_to_pattern(
                self.locking_screenshotter,
                self.coords["main_menu"],
                self.pixel_patterns["main_menu"],
            )

            red_button = self.compare_screenshot_to_pattern(
                self.locking_screenshotter,
                self.coords["play_button"],
                self.pixel_patterns["red_button"],
            )

            progress_text = self.compare_screenshot_to_pattern(
                self.locking_screenshotter,
                self.coords["progress_text"],
                self.pixel_patterns["pure_white"],
            )

            progress_text_ranked = self.compare_screenshot_to_pattern(
                self.locking_screenshotter,
                self.coords["progress_text_ranked"],
                self.pixel_patterns["pure_white"],
            )

            if player_banner or red_button or progress_text or progress_text_ranked:
                confirmations += 1

                if confirmations >= self.menu_screen_confirmaions_required:
                    self.locking = True
                    self.update_overview_tab()
                    try:
                        self.icon.update_menu()
                    except AttributeError:
                        pass
                    break
                time.sleep(0.1)
            else:
                confirmations = 0
                time.sleep(1)
        return

    # Returns the coords for the agent selected
    def find_agent_coords(self, agent_name):
        try:
            # Turns agent dict into list of agents with True values
            unlocked_agents = list(
                agent
                for agent, unlock_status in self.unlocked_agents_dict.items()
                if unlock_status is True
            )

            # Finds the index of the agent selected
            agent_index = unlocked_agents.index(agent_name)

            # Finds the corner coords of the box the agent is in
            corner_coords = self.box_coords[f"Box{agent_index}"]

            # Box Offset
            min_offset_x, max_offset_x = (
                self.agent_coords_offset[0],
                self.box_info["SIZE"] - self.agent_coords_offset[0],
            )
            min_offset_y, max_offset_y = (
                self.agent_coords_offset[1],
                self.box_info["SIZE"] - self.agent_coords_offset[1],
            )

            offset_x = random.randint(min_offset_x, max_offset_x)
            offset_y = random.randint(min_offset_y, max_offset_y)

            # Returns the coords of the agent with a random offset
            self.agent_coords = (
                corner_coords[0] + offset_x,
                corner_coords[1] + offset_y,
            )

        # Disable instalocking if the agent trying to be selected is not unlocked
        except ValueError:
            self.enabled = False

    # endregion

    # region Tools Thread

    def toggle_tools(self, explicit_toggle: bool = False):
        if explicit_toggle:
            self.enable_tools = not self.enable_tools

        if self.start_tools_thread_automatically and not explicit_toggle:
            if len(self.running_tools) > 0:
                self.enable_tools = True
            else:
                self.enable_tools = False

    def tools_main(self):
        if self.tools_screenshotter is None:
            self.tools_screenshotter = mss.mss()
        if self.tools_keyboard_listener is None:
            self.tools_keyboard_listener = pynkeyboard.Listener(
                on_press=self.tools_keyboard_on_press
            )
            self.tools_keyboard_listener.start()
        spike_drop_confirmations = 0
        last_press_time = None
        while self.active_thread is True:
            if self.enable_tools is True and (
                self.locking is False or self.enabled is False
            ):
                if not self.tools_keyboard_listener.running:
                    self.tools_keyboard_listener.start()

                time.sleep(0.1)

                # region Check Spectating
                is_spectating = self.compare_screenshot_to_pattern(
                    self.tools_screenshotter,
                    self.coords["spectating"],
                    self.pixel_patterns["spectating"],
                )
                if is_spectating:
                    # print("Spectating, waiting...")
                    time.sleep(3)
                    continue

                # endregion

                # region Auto Drop Spike
                if (
                    self.auto_drop_spike
                    or (self.anti_afk_toggles_auto_drop and self.anti_afk)
                ) and not self.chat_is_open:
                    has_spike = self.compare_screenshot_to_pattern(
                        self.tools_screenshotter,
                        self.coords["has_spike"],
                        self.pixel_patterns["pure_white"],
                    )
                    can_plant = self.compare_screenshot_to_pattern(
                        self.tools_screenshotter,
                        self.coords["can_plant"],
                        self.pixel_patterns["pure_white"],
                    )
                    is_planting = self.compare_screenshot_to_pattern(
                        self.tools_screenshotter,
                        self.coords["is_planting"],
                        self.pixel_patterns["is_planting"],
                    )

                    if (
                        has_spike is True
                        and can_plant is False
                        and is_planting is False
                    ):
                        spike_drop_confirmations += 1

                        if (
                            spike_drop_confirmations
                            >= self.spike_drop_confirmations_required
                        ):
                            self.keyboard.tap(self.keybinds["Activate_Level"])
                            time.sleep(0.1)
                            self.keyboard.tap(self.keybinds["DropEquippable"])
                            spike_drop_confirmations = 0

                    else:
                        spike_drop_confirmations = 0
                # endregion

                # region Anti AFK
                if self.anti_afk and not self.chat_is_open:
                    if last_press_time is None:
                        last_press_time = time.time()

                    current_time = time.time()

                    if current_time - last_press_time >= 7.5:
                        self.register_keyboard_input = False
                        self.anti_afk_method(anti_afk_type=self.anti_afk_mode)
                        self.register_keyboard_input = True
                        last_press_time = current_time
                # endregion

            else:
                if self.tools_keyboard_listener.running:
                    self.tools_keyboard_listener.stop()
                    self.tools_keyboard_listener = pynkeyboard.Listener(
                        on_press=self.tools_keyboard_on_press
                    )
                time.sleep(1)

    def anti_afk_method(self, anti_afk_type: str = None, hold_time: float = 0.2):
        match anti_afk_type:
            case "forward":
                for key in [
                    self.keybinds["MoveForward"],
                    self.keybinds["MoveBackward"],
                ]:
                    self.keyboard.press(key)
                    time.sleep(hold_time if hold_time > 0 else random.uniform(0.1, 0.3))
                    self.keyboard.release(key)
                    time.sleep(hold_time if hold_time > 0 else random.uniform(0.1, 0.3))

            case "strafe":
                for key in [self.keybinds["MoveRight"], self.keybinds["MoveLeft"]]:
                    self.keyboard.press(key)
                    time.sleep(hold_time if hold_time > 0 else random.uniform(0.1, 0.3))
                    self.keyboard.release(key)
                    time.sleep(hold_time if hold_time > 0 else random.uniform(0.1, 0.3))

            case "circle":
                for key in [
                    self.keybinds["MoveForward"],
                    self.keybinds["MoveRight"],
                    self.keybinds["MoveBackward"],
                    self.keybinds["MoveLeft"],
                ]:
                    self.keyboard.press(key)
                    time.sleep(hold_time if hold_time > 0 else random.uniform(0.1, 0.3))
                    self.keyboard.release(key)
                    time.sleep(hold_time if hold_time > 0 else random.uniform(0.1, 0.3))

            case "random":
                hold_time = 0  # bmakes the hold time random, hold time will be an available setting to change later
                possible_directions = [
                    self.keybinds["MoveForward"],
                    self.keybinds["MoveRight"],
                    self.keybinds["MoveBackward"],
                    self.keybinds["MoveLeft"],
                ]
                direction = random.choice(possible_directions)

                self.keyboard.press(direction)
                time.sleep(hold_time if hold_time > 0 else random.uniform(0.1, 0.3))
                self.keyboard.release(direction)

            case "random ctr.":
                hold_time = 0  # makes the hold time random, hold time will be an available setting to change later
                direction = random.choice(
                    ["long", "lat", "longreversed", "latreversed"]
                )
                match direction:
                    case "long":
                        keybind_order = [
                            self.keybinds["MoveForward"],
                            self.keybinds["MoveBackward"],
                        ]
                    case "longreversed":
                        keybind_order = [
                            self.keybinds["MoveBackward"],
                            self.keybinds["MoveForward"],
                        ]
                    case "lat":
                        keybind_order = [
                            self.keybinds["MoveRight"],
                            self.keybinds["MoveLeft"],
                        ]
                    case "latreversed":
                        keybind_order = [
                            self.keybinds["MoveLeft"],
                            self.keybinds["MoveRight"],
                        ]

                for key in keybind_order:
                    self.keyboard.press(key)
                    time.sleep(hold_time if hold_time > 0 else random.uniform(0.1, 0.3))
                    self.keyboard.release(key)
                    time.sleep(hold_time if hold_time > 0 else random.uniform(0.1, 0.3))

            case _:  # default in case something goes wrong, same as forward
                for key in [
                    self.keybinds["MoveForward"],
                    self.keybinds["MoveBackward"],
                ]:
                    self.keyboard.press(key)
                    time.sleep(hold_time if hold_time > 0 else random.uniform(0.1, 0.3))
                    self.keyboard.release(key)
                    time.sleep(hold_time if hold_time > 0 else random.uniform(0.1, 0.3))

    def tools_keyboard_on_press(self, key):
        if self.detect_open_chat_keyboard:
            if self.chat_is_open and (
                key == pynkeyboard.Key.enter or key == pynkeyboard.Key.esc
            ):
                self.chat_is_open = False
            elif key == pynkeyboard.Key.enter:
                self.chat_is_open = True

        if (
            hasattr(key, "char")
            and self.register_keyboard_input
            and self.enable_tools
            and self.anti_afk
            and not self.chat_is_open
        ):
            if key.char in [
                self.keybinds["MoveForward"],
                self.keybinds["MoveRight"],
                self.keybinds["MoveBackward"],
                self.keybinds["MoveLeft"],
            ]:
                self.anti_afk = False
                self.update_tools_tab()

    # endregion

    # region Screenshotter
    def return_screenshot_bytes(self, screenshotter, coords):
        screenshot = screenshotter.grab(coords)
        screenshot = PIL.Image.frombytes(
            "RGB",
            screenshot.size,
            screenshot.bgra,
            "raw",
            "BGRX",
        ).tobytes()
        return screenshot

    def compare_screenshot_to_pattern(  # Average 0.0163127713s
        self,
        sct: mss,
        bbox: tuple[int, int, int, int],
        expected_pattern: tuple[int, int, int],
    ) -> bool:
        pixel_data = sct.grab(bbox).pixels

        processed_pixels = np.array(pixel_data, dtype=np.uint8)

        rgb_values = processed_pixels.reshape(-1, 3)

        return all(np.all(rgb_values == expected_pattern, axis=1))

    def _compare_screenshot_to_pattern_alternative(  # Average 0.0164257998s
        self,
        sct: mss,
        bbox: tuple[int, int, int, int],
        expected_pattern: tuple[int, int, int],
    ) -> bool:
        pixel_data = sct.grab(bbox).pixels

        return np.allclose(pixel_data, expected_pattern)

    # endregion

    # region Valorant Log Reader

    # Starts the valorant log reader thread
    def valorant_log_reader(self):
        try:
            self.get_valorant_log()
            self.get_user_id()
            self.get_current_account_config_files()
            self.get_game_resolution()
            if self.grab_keybinds is True:
                self.get_custom_keybinds()

        except Exception:
            self.toggle_settings("grab_keybinds", False)
            self.grab_keybinds = False

            ErrorPopup(
                window_geometry=self.winfo_geometry(),
                title="Error",
                message="Error reading Valorant log file.\nGrab keybinds has been disabled.",
                colors=self.button_colors,
                main_font=self.main_font,
            ).get_input()

    # Clone the valorant log file to the data folder
    def get_valorant_log(self):
        original_log = (
            os.getenv("LOCALAPPDATA") + "/VALORANT/Saved/Logs/ShooterGame.log"
        )
        destination_path = resource_path("data/valorant_files/")

        if not os.path.exists(destination_path):
            os.makedirs(destination_path)

        shutil.copy(original_log, destination_path)

    # Gets the user id from the log file
    def get_user_id(self):
        log_file_path = resource_path("data/valorant_files/ShooterGame.log")
        pattern = r".*Logged in user changed: (.*)"

        with open(log_file_path, "r", encoding="utf-8") as file:
            log_content = file.read()
            match = re.search(pattern, log_content)

        if match:
            self.current_account_id = match.group(1)
        else:
            time.sleep(5)
            self.get_user_id()

    # Clones the keybinds and game settings files for the current account
    def get_current_account_config_files(self):
        if self.current_account_id is None:
            return None

        for file in os.listdir(os.getenv("LOCALAPPDATA") + "/VALORANT/Saved/Config/"):
            if file.startswith(self.current_account_id):
                self.current_account_config_file = file
                break

        game_settings = f"{os.getenv('LOCALAPPDATA')}/VALORANT/Saved/Config/{self.current_account_config_file}/Windows/GameUserSettings.ini"
        keybinds = f"{os.getenv('LOCALAPPDATA')}/VALORANT/Saved/Config/{self.current_account_config_file}/WindowsClient/BackupKeybinds.json"

        shutil.copy(game_settings, resource_path("data/valorant_files/"))
        shutil.copy(keybinds, resource_path("data/valorant_files/"))

    # Finds the game resolution from the gameusersettings.ini file
    def get_game_resolution(self):
        with open(
            resource_path("data/valorant_files/GameUserSettings.ini"), "r"
        ) as file:
            game_settings = file.read()
            resolution_size_x = re.search(r"ResolutionSizeX=(.*)", game_settings).group(
                1
            )
            resolution_size_y = re.search(r"ResolutionSizeY=(.*)", game_settings).group(
                1
            )
            fullscreen_mode = re.search(r"FullscreenMode=(.*)", game_settings).group(1)

            self.screen_resolution = (int(resolution_size_x), int(resolution_size_y))

            if self.screen_resolution != (1920, 1080):
                self.is_1920x1080 = False
                ErrorPopup(
                    window_geometry=self.winfo_geometry(),
                    title="Warning",
                    message=f"Your game resolution is {self.screen_resolution}.\nPlease change it to 1920x1080\nin fullscreen or windowed fullscreen",
                    colors=self.button_colors,
                    main_font=self.main_font,
                ).get_input()
            elif fullscreen_mode == "2":
                ErrorPopup(
                    window_geometry=self.winfo_geometry(),
                    title="Warning",
                    message="Your game is in windowed mode.\nPlease change it to 1920x1080\nin fullscreen or windowed fullscreen",
                    colors=self.button_colors,
                    main_font=self.main_font,
                ).get_input()

    # Grabs the changed keybinds from the backup keybinds file
    def get_custom_keybinds(self):
        custom_keybinds = dict()
        with open(
            resource_path("data/valorant_files/BackupKeybinds.json"), "r"
        ) as file:
            json_file = json.load(file)

            for keybind in json_file["actionMappings"]:
                if keybind["bindIndex"] == 0:
                    custom_keybinds[keybind["name"]] = self.convert_keybind(
                        keybind["key"]
                    )

            for keybind in json_file["axisMappings"]:
                if keybind["bindIndex"] == 0:
                    match keybind["name"], keybind["scale"]:
                        case "MoveForward", 1:
                            key_name = "MoveForward"
                        case "MoveForward", -1:
                            key_name = "MoveBackward"
                        case "MoveRight", 1:
                            key_name = "MoveRight"
                        case "MoveRight", -1:
                            key_name = "MoveLeft"
                    custom_keybinds[key_name] = self.convert_keybind(keybind["key"])

            for keybind_name in custom_keybinds.keys():
                if keybind_name in self.keybinds.keys():
                    self.keybinds[keybind_name] = custom_keybinds[keybind_name]

    # Converts valorant keybinds to custom mappings
    def convert_keybind(self, key):
        custom_mappings = {
            "One": "1",
            "Two": "2",
            "Three": "3",
            "Four": "4",
            "Five": "5",
            "Six": "6",
            "Seven": "7",
            "Eight": "8",
            "Nine": "9",
            "Zero": "0",
        }

        if key in custom_mappings.keys():
            return custom_mappings[key]
        else:
            return key.lower()

    # endregion


# region Popups


# Error popup when save renamed incorrectly
class ErrorPopup(customtkinter.CTkToplevel):
    def __init__(self, window_geometry, title, message, colors, main_font):
        super().__init__()
        self.title(title)
        _, x, y = window_geometry.split("+")
        self.main_window_x, self.main_window_y = int(x), int(y)
        self.small_window_width, self.small_window_height = map(
            int, self.geometry().split("+")[0].split("x")
        )
        self.message = message
        self.colors = colors
        self.main_font = main_font

        # GUI Settings
        self.lift()  # lift window on top
        self.attributes("-topmost", True)  # keep window on top
        self.protocol("WM_DELETE_WINDOW", self.cancel_event)
        self.resizable(False, False)
        self.grab_set()  # make other windows not clickable

        self.is_cancel_action = False

        self.create_error_message()

    def create_error_message(self):
        self.geometry("300x120")
        self.geometry(
            "+%d+%d"
            % (
                self.main_window_x + self.small_window_width / 2,
                self.main_window_y + self.small_window_height / 2,
            )
        )
        self.grid_columnconfigure((0, 1), weight=1)
        self.rowconfigure(0, weight=1)

        self.message = customtkinter.CTkLabel(
            self, text=self.message, font=(self.main_font, 14)
        )
        self.message.grid(
            row=1, column=0, columnspan=2, padx=0, pady=(20, 0), sticky="ew"
        )

        self.cancel_button = customtkinter.CTkButton(
            master=self,
            width=100,
            border_width=0,
            text="Cancel",
            font=(self.main_font, 14),
            fg_color=self.colors["disabled"],
            command=self.cancel_event,
        )
        self.cancel_button.grid(
            row=2, column=0, columnspan=1, padx=10, pady=20, sticky="ew"
        )

        self.ok_button = customtkinter.CTkButton(
            master=self,
            width=100,
            border_width=0,
            text="Ok",
            font=(self.main_font, 14),
            fg_color=self.colors["enabled"],
            command=self.okay_event,
        )
        self.ok_button.grid(
            row=2, column=1, columnspan=1, padx=10, pady=20, sticky="ew"
        )

        self.bind("<Return>", self.okay_event)
        self.bind("<Escape>", self.cancel_event)

    def okay_event(self, event=None):
        self.is_cancel_action = False
        self.grab_release()
        self.destroy()

    def cancel_event(self, event=None):
        self.is_cancel_action = None
        self.grab_release()
        self.destroy()

    def get_input(self):
        self.wait_window()
        return self.is_cancel_action


# Input popup when renaming saves
class InputPopup(customtkinter.CTkToplevel):
    def __init__(
        self,
        window_geometry,
        title,
        file_name,
        colors,
        main_font,
        is_new_file=False,
        filled_in_text=None,
    ):
        super().__init__()
        self.title(title)
        _, x, y = window_geometry.split("+")
        self.main_window_x, self.main_window_y = int(x), int(y)
        self.small_window_width, self.small_window_height = map(
            int, self.geometry().split("+")[0].split("x")
        )
        self.file_name = file_name
        self.colors = colors
        self.is_new_file = is_new_file
        self.filled_in_text = filled_in_text
        self.main_font = main_font

        # GUI Settings
        self.lift()  # lift window on top
        self.attributes("-topmost", True)  # keep window on top
        self.protocol("WM_DELETE_WINDOW", self.cancel_event)
        self.resizable(False, False)
        self.grab_set()  # make other windows not clickable

        self.user_input = None

        self.create_input_popup()

    def create_input_popup(self):
        self.geometry(
            "+%d+%d"
            % (
                self.main_window_x + self.small_window_width / 2,
                self.main_window_y + self.small_window_height / 2,
            )
        )
        self.grid_columnconfigure((0, 1), weight=1)
        self.rowconfigure(0, weight=1)

        if self.is_new_file is False:
            message = f"Rename {self.file_name}:"
        else:
            message = "New file name:"

        self.label = customtkinter.CTkLabel(
            master=self,
            text=message,
            width=300,
            wraplength=300,
            font=(self.main_font, 16),
        )
        self.label.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="ew")

        self.entry = customtkinter.CTkEntry(
            master=self, width=230, font=(self.main_font, 14)
        )
        self.entry.grid(row=1, column=0, columnspan=2, padx=20, pady=0, sticky="ew")
        if self.filled_in_text is None:
            self.entry.insert(0, self.file_name)
        else:
            self.entry.insert(0, self.filled_in_text)

        self.cancel_button = customtkinter.CTkButton(
            master=self,
            width=100,
            border_width=0,
            text="Cancel",
            font=(self.main_font, 14),
            fg_color=self.colors["disabled"],
            command=self.cancel_event,
        )
        self.cancel_button.grid(
            row=2, column=0, columnspan=1, padx=20, pady=20, sticky="ew"
        )

        self.ok_button = customtkinter.CTkButton(
            master=self,
            width=100,
            border_width=0,
            text="Ok",
            font=(self.main_font, 14),
            fg_color=self.colors["enabled"],
            command=self.ok_event,
        )
        self.ok_button.grid(
            row=2, column=1, columnspan=1, padx=20, pady=20, sticky="ew"
        )

        self.after(150, lambda: self.entry.focus())
        self.entry.bind("<Return>", self.ok_event)
        self.entry.bind("<Escape>", self.cancel_event)

    def ok_event(self, event=None):
        self.user_input = self.entry.get()
        self.grab_release()
        self.destroy()

    def cancel_event(self, event=None):
        self.user_input = None
        self.grab_release()
        self.destroy()

    def get_input(self):
        self.wait_window()
        return self.user_input


# Confirmation popup when deleting saves
class ConfirmDeletePopup(customtkinter.CTkToplevel):
    def __init__(self, window_geometry, file_name, colors, main_font):
        super().__init__()
        _, x, y = window_geometry.split("+")
        self.main_window_x, self.main_window_y = int(x), int(y)
        self.small_window_width, self.small_window_height = map(
            int, self.geometry().split("+")[0].split("x")
        )
        self.title("Confirm Deletion")
        self.file_name = file_name
        self.colors = colors
        self.main_font = main_font

        # GUI Settings
        self.lift()  # lift window on top
        self.attributes("-topmost", True)  # keep window on top
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.resizable(False, False)
        self.grab_set()  # make other windows not clickable

        self.user_input = False

        self.create_confirmation_popup()

    def confirm_event(self):
        self.user_input = True
        self.grab_release()
        self.destroy()

    def cancel_event(self, event=None):
        self.user_input = False
        self.grab_release()
        self.destroy()

    def on_closing(self):
        self.grab_release()
        self.destroy()

    def get_input(self):
        self.wait_window()
        return self.user_input

    def create_confirmation_popup(self):
        self.geometry("400x200")
        self.geometry(
            "+%d+%d"
            % (
                self.main_window_x + self.small_window_width / 2,
                self.main_window_y + self.small_window_height / 2,
            )
        )
        message = customtkinter.CTkLabel(
            self,
            text=f"Confirm deletion for:\n{self.file_name}\n\nThis action cannot be undone.",
            font=(self.main_font, 16),
        )
        message.pack(padx=10, pady=10)

        self.ok_button = customtkinter.CTkButton(
            master=self,
            width=100,
            border_width=0,
            text="Ok",
            font=(self.main_font, 14),
            fg_color=self.colors["disabled"],
            command=self.confirm_event,
        )
        self.ok_button.pack(padx=20, pady=10, side=tk.LEFT)

        self.cancel_button = customtkinter.CTkButton(
            master=self,
            width=100,
            border_width=0,
            text="Cancel",
            font=(self.main_font, 14),
            fg_color=self.colors["enabled"],
            command=self.cancel_event,
        )
        self.cancel_button.pack(padx=20, pady=10, side=tk.RIGHT)

        self.bind("<Return>", self.cancel_event)
        self.bind("<Escape>", self.cancel_event)


# Popup when update is available
class UpdatePopup(customtkinter.CTkToplevel):
    def __init__(
        self, window_geometry, current_version, latest_version, colors, main_font
    ):
        super().__init__()
        _, x, y = window_geometry.split("+")
        self.main_window_x, self.main_window_y = int(x), int(y)
        self.small_window_width, self.small_window_height = map(
            int, self.geometry().split("+")[0].split("x")
        )
        self.title("Update Available")
        self.current_version = current_version
        self.latest_version = latest_version
        self.colors = colors
        self.main_font = main_font

        # GUI Settings
        self.lift()  # lift window on top
        self.attributes("-topmost", True)  # keep window on top
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.resizable(False, False)
        self.grab_set()  # make other windows not clickable

        self.user_input = False

        self.create_confirmation_popup()

    def confirm_event(self, event=None):
        self.user_input = True
        self.grab_release()
        self.destroy()

    def cancel_event(self, event=None):
        self.user_input = False
        self.grab_release()
        self.destroy()

    def on_closing(self):
        self.grab_release()
        self.destroy()

    def get_input(self):
        self.wait_window()
        return self.user_input

    def create_confirmation_popup(self):
        self.geometry("400x150")
        self.geometry(
            "+%d+%d"
            % (
                self.main_window_x + self.small_window_width / 2,
                self.main_window_y + self.small_window_height / 2,
            )
        )
        message = customtkinter.CTkLabel(
            self,
            text=f"{self.latest_version} is available.\nYou currently have {self.current_version} installed.\n\nWould you like to be taken to the download page?",
            font=(self.main_font, 16),
        )
        message.pack(padx=10, pady=10)

        self.yes_button = customtkinter.CTkButton(
            master=self,
            width=150,
            border_width=0,
            text="Yes",
            font=(self.main_font, 14),
            fg_color=self.colors["enabled"],
            command=self.confirm_event,
        )
        self.yes_button.pack(padx=20, pady=10, side=tk.RIGHT)

        self.no_button = customtkinter.CTkButton(
            master=self,
            width=150,
            border_width=0,
            text="No",
            font=(self.main_font, 14),
            fg_color=self.colors["disabled"],
            command=self.cancel_event,
        )
        self.no_button.pack(padx=20, pady=10, side=tk.LEFT)

        self.bind("<Return>", self.confirm_event)
        self.bind("<Escape>", self.cancel_event)


# endregion


if __name__ == "__main__":
    main_gui = InstalockerGUIMain()
    main_gui.mainloop()
