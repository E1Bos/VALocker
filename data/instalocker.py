"""
MIT License

Copyright (c) 2023 Luca Boscolo

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

# region Imports

# Imports all modules, if it fails it will install them
try:
    # Modules that are not installed by default
    import customtkinter, pystray, PIL.Image, mss
    import pynput.mouse as pynmouse
    import pynput.keyboard as pynkeyboard

except ModuleNotFoundError:
    # Installs missing modules if exception is raised
    import subprocess

    subprocess.run(["pip", "install", "-r", "requirements.txt"])

    import customtkinter, pystray, PIL.Image, mss
    import pynput.mouse as pynmouse
    import pynput.keyboard as pynkeyboard


# Imports modules that are installed with Python
import json, os, random, threading, time, ctypes
import tkinter as tk

# endregion


# region PyInstaller Requirement
def resource_path(relative):
    return os.path.join(os.environ.get("_MEIPASS2", os.path.abspath(".")), relative)


# endregion

customtkinter.set_appearance_mode("Dark")
customtkinter.set_default_color_theme("dark-blue")


class InstalockerGUIMain(customtkinter.CTk):
    # region Init and Exit Function

    def __init__(self):
        super().__init__()

        # Locking Values
        self.active = False
        self.active_thread = True
        self.locking = True
        self.locking_coords = (945, 866, 955, 867)
        self.map_selection_coords = (878, 437, 1047, 646)
        self.agent_coords_offset = (15, 15)
        self.menu_screen_coords = {'end_of_game': (814, 243, 892, 244),
                                   'main_menu': (1330, 330, 1455, 353)}
        self.locking_image_path = "images/agent_screen/agent_screen_bar.png"
        self.locking_button = None

        self.locking_confirmations_required = 2        
        self.menu_screen_confirmaions_required = 3

        # self.locking_coords = (958, 866, 870) # agent screen dot
        # self.locking_coords = (959, 867, 961, 869) # agent screen dot solid

        # Locking Images
        self.agent_select_image = PIL.Image.open(
            resource_path(self.locking_image_path)
        ).tobytes()
        self.in_menu_images = [
            PIL.Image.open(
                resource_path("images/in_menu/in_menu_normal_bar.png")
            ).tobytes(),
            PIL.Image.open(
                resource_path("images/in_menu/in_menu_comp_bar.png")
            ).tobytes(),
            PIL.Image.open(
                resource_path("images/in_menu/in_menu_progress_text_1.png")
            ).tobytes(),
            PIL.Image.open(
                resource_path("images/in_menu/in_menu_progress_text_2.png")
            ).tobytes(),
        ]

        # Map Specific
        self.map_specific_mode = False
        self.map_lookup = dict()

        # Safe Mode
        self.safe_mode = True
        self.safe_mode_strength = 0
        self.safe_mode_timing = {
            "Low": (0.2, 0.4),
            "Medium": (0.4, 0.7),
            "High": (0.7, 1.0),
        }

        # Random Agent Mode
        self.random_agent_mode = False

        # Hover Mode
        self.hover_mode = False

        # Agent Data
        self.default_agents = list()
        self.selected_agent = str()
        self.all_agents = list()
        self.random_agent_exclusiselect = False

        # Statistics
        self.total_games_used = 0
        self.time_to_lock_list = list(
            list() for _ in range(len(self.safe_mode_timing) + 1)
        )

        # Box Coords
        self.box_coords = dict()
        self.lock_button = list()

        # Save Files
        self.save_files = None
        self.favorited_save_files = list()

        # Tools
        self.enable_tools = False
        self.tools_images = {'spike': PIL.Image.open(resource_path("images/tools/auto_drop_spike/has_spike.png")).tobytes(),
                             'can_plant': PIL.Image.open(resource_path("images/tools/auto_drop_spike/can_plant.png")).tobytes(),
                             'is_planting': PIL.Image.open(resource_path("images/tools/auto_drop_spike/is_planting.png")).tobytes(),}
        self.tools_locations = {'spike': (1852, 684, 1856, 687), 'can_plant': (905, 139, 936, 141), 'is_planting': (832, 174, 833, 193),}
        self.auto_drop_spike = False
        self.spike_drop_confirmations_required = 2
        self.auto_gg = False
        self.auto_gg_confirmations_required = 2
        self.anti_afk = False


        # GUI SETTINGS
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

        # Icons
        self.icons = dict(
            disabled="images/icons/valocker-disabled.ico",
            locking="images/icons/valocker-locking.ico",
            waiting="images/icons/valocker-waiting.ico",
        )
        self.current_icon = self.icons["disabled"]
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("VALocker.GUI")

        # Default Save File
        self.current_save_file = "default"

        # Finds all save files
        self.find_save_files()

        # Loads data from save files
        self.load_data_from_files(first_run=True)

        # Defines Controllers
        self.mouse = pynmouse.Controller()
        self.keyboard = pynkeyboard.Controller()
        self.locking_screenshotter = None
        self.tools_screenshotter = None

        # Creates GUI
        self.create_gui()

        # Updates GUI
        self.update_gui()

        # Checks if program should close to tray
        if self.minimize_to_tray is True:
            self.protocol("WM_DELETE_WINDOW", self.withdraw_window)

            self.create_tray_icon()

            if self.start_minimized is True:
                self.withdraw_window()
        else:
            self.protocol("WM_DELETE_WINDOW", self.exit)

        # Creates Thread
        self.agent_thread = threading.Thread(target=self.locking_main).start()

        if self.enable_tools is True:
            self.tools_thread = threading.Thread(target=self.tools_main).start()

    def exit(self):
        self.active_thread = False
        self.enable_tools = False
        try:
            self.icon.stop()
        except AttributeError:
            pass
        self.destroy()

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
            # "Settings",
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

        # self.overview_frame.rowconfigure(0, weight=1)

        current_status_frame = customtkinter.CTkFrame(self.overview_frame)
        current_status_frame.grid(row=0, column=0, pady=20, padx=10, sticky="nsew")

        current_status_label = customtkinter.CTkLabel(
            current_status_frame, text="Instalocker:", font=self.label_font_and_size
        )
        current_status_label.pack(padx=10, pady=(5, 0))

        self.current_status_button = customtkinter.CTkButton(
            current_status_frame,
            text=f"{'Running' if self.active is True else 'Stopped'}",
            hover=False,
            fg_color=f"{self.button_colors['enabled'] if self.active is True else self.button_colors['disabled']}",
            font=self.button_font_and_size,
            command=self.toggle_active,
        )
        self.current_status_button.pack(padx=10, pady=(0, 5))

        current_task_label = customtkinter.CTkLabel(
            current_status_frame, text=f"Current Task:", font=self.label_font_and_size
        )
        current_task_label.pack(padx=10, pady=(5, 0))

        self.current_task_button = customtkinter.CTkButton(
            current_status_frame,
            text=f"{'None' if self.active is False else 'Locking' if self.locking is True else 'In Game'}",
            hover=False,
            font=self.button_font_and_size,
            command=self.toggle_thread_mode,
        )
        self.current_task_button.pack(padx=10, pady=(0, 5))

        safe_mode_frame = customtkinter.CTkFrame(
            current_status_frame, width=140, height=70, fg_color="transparent"
        )
        safe_mode_frame.pack(padx=10, pady=(5, 0), ipadx=0)

        safe_mode_label = customtkinter.CTkLabel(
            safe_mode_frame, text=f"Safe Mode:", font=self.label_font_and_size
        )
        safe_mode_label.pack(anchor=tk.N, padx=10)

        self.safe_mode_enabled_button = customtkinter.CTkButton(
            safe_mode_frame,
            width=int(f"{140 if self.safe_mode is False else 70}"),
            hover=False,
            text=f"{'On' if self.safe_mode is True else 'Off'}",
            fg_color=f"{self.button_colors['enabled'] if self.active is True else self.button_colors['disabled']}",
            font=self.button_font_and_size,
            command=self.toggle_safe_mode,
        )
        self.safe_mode_enabled_button.pack(side=tk.LEFT, padx=0, pady=(0, 5))

        self.safe_mode_strength_button = customtkinter.CTkButton(
            safe_mode_frame,
            width=70,
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
            text=f"Current Save:",
            font=self.label_font_and_size,
        )
        current_save_label.pack(padx=10, pady=(5, 0))

        self.current_save_button = customtkinter.CTkButton(
            current_status_frame,
            text=f"{self.current_save_file}",
            hover=False,
            fg_color="gray20",
            corner_radius=5,
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
            command=lambda x: self.toggle_selected_agent(x),
        )
        self.select_agent_dropdown.set(f"{self.selected_agent}")
        self.select_agent_dropdown.pack(padx=10, pady=(0, 5))

        self.select_map_enabled_label = customtkinter.CTkLabel(
            select_agent_frame, text="Map Specific:", font=self.label_font_and_size
        )
        self.select_map_enabled_label.pack(padx=10, pady=(5, 0))

        self.select_map_specific_button = customtkinter.CTkButton(
            select_agent_frame,
            text=f"{'Enabled' if self.map_specific_mode is True else 'Disabled'}",
            hover=False,
            fg_color=f"{self.button_colors['enabled'] if self.map_specific_mode is True else self.button_colors['disabled']}",
            font=self.button_font_and_size,
            command=self.toggle_map_specific,
        )
        self.select_map_specific_button.pack(padx=10, pady=(0, 5))

        random_agent_label = customtkinter.CTkLabel(
            select_agent_frame, text="Random Agent:", font=self.label_font_and_size
        )
        random_agent_label.pack(padx=10, pady=(5, 0))

        self.toggle_random_agent_button = customtkinter.CTkButton(
            select_agent_frame,
            text=f"{'Enabled' if self.random_agent_mode is True else 'Disabled'}",
            hover=False,
            fg_color=f"{self.button_colors['enabled'] if self.random_agent_mode is True else self.button_colors['disabled']}",
            font=self.button_font_and_size,
            command=self.toggle_random_agent_mode,
        )
        self.toggle_random_agent_button.pack(padx=10, pady=(0, 5))

        hover_mode_label = customtkinter.CTkLabel(
            select_agent_frame, text="Hover Mode:", font=self.label_font_and_size
        )
        hover_mode_label.pack(padx=10, pady=(5, 0))
        self.hover_mode_button = customtkinter.CTkButton(
            select_agent_frame,
            text=f"{'Enabled' if self.hover_mode is True else 'Disabled'}",
            hover=False,
            fg_color=f"{self.button_colors['enabled'] if self.hover_mode is True else self.button_colors['disabled']}",
            font=self.button_font_and_size,
            command=self.toggle_hover_mode,
        )
        self.hover_mode_button.pack(padx=10, pady=(0, 10))

        stats_frame = customtkinter.CTkFrame(self.overview_frame)
        stats_frame.grid(row=0, column=2, pady=20, padx=10, sticky="nsew")

        stats_label = customtkinter.CTkLabel(
            stats_frame, text="Last Lock:", font=self.label_font_and_size
        )
        stats_label.pack(padx=10, pady=(5, 0))

        if self.safe_mode is False:
            time_to_lock_text = f"{self.time_to_lock_list[-1] if len(self.time_to_lock_list[-1]) != 0 else '-'}"
        else:
            time_to_lock_text = f"{self.time_to_lock_list[self.safe_mode_strength][-1] if len(self.time_to_lock_list[self.safe_mode_strength]) != 0 else '-'}"

        self.time_to_lock_label = customtkinter.CTkLabel(
            stats_frame,
            text=f"{time_to_lock_text} ms",
            font=self.button_font_and_size,
        )
        self.time_to_lock_label.pack(padx=10, pady=(0, 5))

        average_time_to_lock_label = customtkinter.CTkLabel(
            stats_frame, text=f"Average:", font=self.label_font_and_size
        )
        average_time_to_lock_label.pack(padx=10, pady=(5, 0))

        self.average_time_to_lock_value = customtkinter.CTkLabel(
            stats_frame,
            text=f"{'-' if len(self.time_to_lock_list[self.safe_mode_strength]) == 0 else round(sum(self.time_to_lock_list[self.safe_mode_strength])/len(self.time_to_lock_list[self.safe_mode_strength]),2)} ms",
            font=self.button_font_and_size,
        )
        self.average_time_to_lock_value.pack(padx=10, pady=(0, 5))

        total_games_locked_label = customtkinter.CTkLabel(
            stats_frame, text=f"Deployed:", font=self.label_font_and_size
        )
        total_games_locked_label.pack(padx=10, pady=(5, 0))

        self.total_games_locked_value = customtkinter.CTkLabel(
            stats_frame,
            text=f"{self.total_games_used} {'times' if self.total_games_used != 1 else 'time'}",
            font=self.button_font_and_size,
        )
        self.total_games_locked_value.pack(padx=10, pady=(0, 5))

        self.overview_frame.columnconfigure((0, 1, 2), weight=1)

        # endregion

        # region Agent Toggle Tab

        mass_select_frame = customtkinter.CTkFrame(self.agent_toggle_frame)
        mass_select_frame.pack(padx=10, pady=20)

        mass_select_frame.grid_columnconfigure((0, 1), weight=1)

        self.toggle_all_agent_button = customtkinter.CTkCheckBox(
            mass_select_frame,
            text="All",
            width=100,
            font=self.button_font_and_size,
            command=lambda: self.toggle_unlocked_agent_status("all"),
        )
        self.toggle_all_agent_button.grid(row=0, column=0, pady=10, padx=(10, 5))

        self.toggle_none_agent_button = customtkinter.CTkCheckBox(
            mass_select_frame,
            text="None",
            width=100,
            font=self.button_font_and_size,
            command=lambda: self.toggle_unlocked_agent_status("none"),
        )
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
            fg_color=f"{self.button_colors['enabled'] if self.random_agent_exclusiselect is True else self.button_colors['disabled']}",
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

        self.all_random_agent_radio_button = customtkinter.CTkCheckBox(
            random_agent_all_none_toggle_frame,
            text="All",
            font=self.button_font_and_size,
            command=lambda: self.toggle_random_agent_status("all"),
        )
        self.all_random_agent_radio_button.pack(side="left", padx=(20, 0), pady=10)

        self.none_random_agent_radio_button = customtkinter.CTkCheckBox(
            random_agent_all_none_toggle_frame,
            text="None",
            font=self.button_font_and_size,
            command=lambda: self.toggle_random_agent_status("none"),
        )
        self.none_random_agent_radio_button.pack(side="right", padx=20, pady=10)

        random_agent_role_toggle_frame = customtkinter.CTkFrame(self.random_agent_frame)
        random_agent_role_toggle_frame.pack(padx=10, pady=10, fill=tk.X)

        # Creates the checkboxes for each role
        self.agent_role_checkboxes = dict()
        for index, role in enumerate(self.config_file_agents.keys()):
            role = role.lower()

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

            self.random_agent_checkboxes[
                f"self.{agent}_random_checkbox"
            ] = customtkinter.CTkCheckBox(
                frame,
                text=agent,
                text_color=self.role_colors[agent_role],
                font=self.button_font_and_size,
                command=lambda agent=agent: self.toggle_random_agent_status(agent),
            )
            self.random_agent_checkboxes[f"self.{agent}_random_checkbox"].pack(
                padx=5, pady=5
            )
        # endregion

        # region Map Specific Tab
        self.map_specific_frame.rowconfigure([i for i in range(len(self.map_names)//2 + 1)], weight=1)

        map_frames, map_labels, self.map_dropdowns = dict(), dict(), dict()
        for index, map_name in enumerate(self.map_names):
            row, column = index // 2, index % 2

            map_frames[f"{map_name}_frame"] = customtkinter.CTkFrame(
                self.map_specific_frame, width=230
            )

            pady_amount = (
                (20, 5)
                if row == 0
                else (5, 20)
                if row == len(self.map_names) // 2
                else 5
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
                    if unlock_status is True
                ),
                width=110,
                font=self.button_font_and_size,
                command=lambda agent_name, map_name=map_name: self.toggle_map_specific_agent(
                    agent_name=agent_name, map_name=map_name
                ),
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
            fg_color=f"{self.button_colors['enabled'] if self.enable_tools is True else self.button_colors['disabled']}",
            font=(self.main_font, 16),
            command=self.toggle_tools,
        )
        self.toggle_tools_button.pack(padx=10, pady=20, fill=tk.X)

        scrollable_frame = customtkinter.CTkScrollableFrame(self.tools_frame)
        scrollable_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 20))

        scrollable_frame.columnconfigure((0, 1), weight=1)
        scrollable_frame.rowconfigure((0, 1), weight=1)

        self.auto_drop_spike_button = customtkinter.CTkButton(
            scrollable_frame,
            text=f"Auto Drop Spike",
            height=40,
            hover=False,
            fg_color=f"{self.button_colors['enabled'] if self.auto_drop_spike is True else self.button_colors['disabled']}",
            font=self.button_font_and_size,
            command=self.toggle_auto_drop_spike,
        )
        self.auto_drop_spike_button.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.auto_gg_button = customtkinter.CTkButton(
            scrollable_frame,
            text=f"Auto GG",
            height=40,
            hover=False,
            fg_color=f"{self.button_colors['enabled'] if self.auto_gg is True else self.button_colors['disabled']}",
            font=self.button_font_and_size,
            command=self.toggle_auto_gg,
        )
        # self.auto_gg_button.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.anti_afk_button = customtkinter.CTkButton(
            scrollable_frame,
            text=f"Anti AFK",
            height=40,
            hover=False,
            fg_color=f"{self.button_colors['enabled'] if self.anti_afk is True else self.button_colors['disabled']}",
            font=self.button_font_and_size,
            command=self.toggle_anti_afk,
        )
        # self.anti_afk_button.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")


        # endregion

        # region Settings Tab

        scrolling_settings_frame = customtkinter.CTkScrollableFrame(self.settings_frame)
        scrolling_settings_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # endregion

        self.select_frame_by_name("Overview")

    # Creates the list of save file items
    def individual_save_file_items(self, file_name, just_icons=False):
        if just_icons is False:
            self.save_file_frame_items[f"{file_name}_frame"] = customtkinter.CTkFrame(
                self.save_file_scrollable_frame,
                height=50,
                fg_color="grey16"
                if file_name != self.current_save_file
                else "dark green",
            )

            if file_name != "default" or self.hide_default_save_file is False:
                self.save_file_frame_items[f"{file_name}_frame"].pack(
                    fill=tk.X, padx=(5, 0), pady=3
                )

            self.save_file_frame_items[f"{file_name}_button"] = customtkinter.CTkButton(
                self.save_file_frame_items[f"{file_name}_frame"],
                text=f"{file_name}",
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
            self.save_file_frame_items[
                f"{file_name}_{icon_name}"
            ] = customtkinter.CTkButton(
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
            self.save_file_frame_items[f"{file_name}_{icon_name}"].pack(
                side=tk.RIGHT, padx=(0, 5), pady=5
            )

    # endregion

    # region GUI Updates

    # Updates All GUI Elements
    def update_gui(self, from_agent_tab=False, from_save_tab=False):
        try:
            if from_save_tab is True:
                self.update_save_file_tab()
            if from_agent_tab is False:
                self.update_agent_toggle_tab()
                self.update_random_agent_tab()
                self.update_icon()
            self.update_overview_tab()
            self.update_map_specific_tab()
            self.update_tools_tab()
        except AttributeError:
            pass

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
            text=f"{'Running' if self.active is True else 'Stopped'}",
            fg_color=f"{self.button_colors['enabled'] if self.active is True else self.button_colors['disabled']}",
        )

        self.current_task_button.configure(
            text=f"{'None' if self.active is False else 'Locking' if self.locking is True else 'In Game'}",
            state=tk.DISABLED if self.active is False else tk.NORMAL,
        )

        self.safe_mode_enabled_button.configure(
            text=f"{'On' if self.safe_mode is True else 'Off'}",
            fg_color=f"{self.button_colors['enabled'] if self.safe_mode is True else self.button_colors['disabled']}",
            width=int(f"{140 if self.safe_mode is False else 70}"),
        )

        if self.safe_mode is True:
            self.safe_mode_strength_button.pack(side=tk.RIGHT, padx=0, pady=(0, 5))
        else:
            self.safe_mode_strength_button.pack_forget()

        self.safe_mode_strength_button.configure(
            text=f"{list(self.safe_mode_timing.keys())[self.safe_mode_strength]}"
        )

        self.current_save_button.configure(text=f"{self.current_save_file}")

        # Buttons Middle Column
        self.hover_mode_button.configure(
            text=f"{'Enabled' if self.hover_mode is True else 'Disabled'}",
            fg_color=f"{self.button_colors['enabled'] if self.hover_mode is True else self.button_colors['disabled']}",
        )

        self.select_map_specific_button.configure(
            text=f"{'Enabled' if self.map_specific_mode is True else 'Disabled'}",
            fg_color=f"{self.button_colors['enabled'] if self.map_specific_mode is True else self.button_colors['disabled']}",
        )

        self.select_agent_dropdown.configure(
            values=list(
                agent
                for agent, unlock_status in self.unlocked_agents_dict.items()
                if unlock_status is True
            )
        )
        self.select_agent_dropdown.set(f"{self.selected_agent}")

        self.toggle_random_agent_button.configure(
            text=f"{'Enabled' if self.random_agent_mode is True else 'Disabled'}",
            fg_color=f"{self.button_colors['enabled'] if self.random_agent_mode is True else self.button_colors['disabled']}",
        )

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
    def update_agent_toggle_tab(self, agent_name=None):
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

            case None:  # Updates the entire tab, used only when the tab is first created or when loading a new save file
                for agent in self.all_agents:
                    if agent not in self.default_agents:
                        if self.unlocked_agents_dict[agent] is True:
                            self.agent_checkboxes[f"self.{agent}_checkbox"].select()
                        else:
                            self.agent_checkboxes[f"self.{agent}_checkbox"].deselect()

                if all(
                    value is True
                    for agent, value in self.unlocked_agents_dict.items()
                    if agent not in self.default_agents
                ):
                    self.toggle_all_agent_button.select()
                    self.toggle_all_agent_button.configure(state=tk.DISABLED)
                else:
                    self.toggle_all_agent_button.deselect()
                    self.toggle_all_agent_button.configure(state=tk.NORMAL)

                if all(
                    value is False
                    for agent, value in self.unlocked_agents_dict.items()
                    if agent not in self.default_agents
                ):
                    self.toggle_none_agent_button.select()
                    self.toggle_none_agent_button.configure(state=tk.DISABLED)
                else:
                    self.toggle_none_agent_button.deselect()
                    self.toggle_none_agent_button.configure(state=tk.NORMAL)

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

    # Updates random agent tab
    def update_random_agent_tab(
        self, agent_name=None, toggled_agent_name=None, exclusiselect_mode=False
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
                    case None:
                        pass
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

            case None:  # Updates the entire tab, used only when the tab is first created or loading a new save file
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

                # Select none if no agents are selected
                if all(value is False for value in self.random_agents_dict.values()):
                    self.none_random_agent_radio_button.select()
                    self.none_random_agent_radio_button.configure(state=tk.DISABLED)
                else:
                    self.none_random_agent_radio_button.deselect()
                    self.none_random_agent_radio_button.configure(state=tk.NORMAL)

                # Selects all roles if all possible agents are selected
                for role in self.config_file_agents:
                    for agent in self.config_file_agents[role]:
                        if self.random_agents_dict[agent] is True:
                            self.random_agent_checkboxes[
                                f"self.{agent}_random_checkbox"
                            ].select()
                        else:
                            self.random_agent_checkboxes[
                                f"self.{agent}_random_checkbox"
                            ].deselect()
                    if all(
                        self.random_agents_dict[agent] is True
                        for agent in self.config_file_agents[role]
                        if self.unlocked_agents_dict[agent] is True
                    ):
                        self.agent_role_checkboxes[role.lower()].select()
                    else:
                        self.agent_role_checkboxes[role.lower()].deselect()

                # Disables agents that are not unlocked
                if exclusiselect_mode is False:
                    for agent in self.unlocked_agents_dict:
                        if (
                            agent not in self.default_agents
                            and self.unlocked_agents_dict[agent] is False
                        ):
                            self.random_agent_checkboxes[
                                f"self.{agent}_random_checkbox"
                            ].configure(state=tk.DISABLED)
                            self.random_agent_checkboxes[
                                f"self.{agent}_random_checkbox"
                            ].deselect()
                        else:
                            self.random_agent_checkboxes[
                                f"self.{agent}_random_checkbox"
                            ].configure(state=tk.NORMAL)

            case _:  # Updates the tab when a single agent is selected
                if exclusiselect_mode is True:
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

    # Updates map specific tab
    def update_map_specific_tab(self):
        unlocked_agents = list(
            agent
            for agent, unlock_status in self.unlocked_agents_dict.items()
            if unlock_status is True
        )
        for map_name in self.map_names:
            self.map_dropdowns[map_name].configure(values=unlocked_agents)
            if (
                self.map_specific_agents_dict[map_name] is not None
                and self.map_specific_agents_dict[map_name] in unlocked_agents
            ):
                self.map_dropdowns[map_name].configure(
                    fg_color="#1f6aa5", button_color="#203a4f"
                )
                self.map_dropdowns[map_name].set(
                    self.map_specific_agents_dict[map_name]
                )
            else:
                self.map_dropdowns[map_name].set("None")
                self.map_dropdowns[map_name].configure(
                    fg_color=self.button_colors["disabled"], button_color="#4e2126"
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
                fg_color="grey16"
                if save_file != self.current_save_file
                else "dark green"
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
            fg_color=f"{self.button_colors['enabled'] if self.enable_tools is True else self.button_colors['disabled']}",
        )

        self.auto_drop_spike_button.configure(
            fg_color=f"{self.button_colors['enabled'] if self.auto_drop_spike is True else self.button_colors['disabled']}",
        )

        self.auto_gg_button.configure(
            fg_color=f"{self.button_colors['enabled'] if self.auto_gg is True else self.button_colors['disabled']}",
        )

        self.anti_afk_button.configure(
            fg_color=f"{self.button_colors['enabled'] if self.anti_afk is True else self.button_colors['disabled']}",
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
                fg_color=("gray75", "gray25")
                if frame_name == button_name
                else "transparent"
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
                lambda x: f'Status: {"Enabled" if self.active else "Disabled"}',
                lambda x: self.toggle_active(),
                checked=lambda x: self.active,
            ),
            pystray.MenuItem(
                lambda x: f"Status: {'None' if self.active is False else 'Locking' if self.locking is True else 'In Game (Waiting)'}",
                lambda x: self.toggle_thread_mode(),
            ),
            pystray.MenuItem("Exit", lambda x: self.exit()),
        )

    # Updates GUI and tray icons
    def update_icon(self):
        if self.active is False:
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

    # Toggles the active state of the program between running and stopped
    def toggle_active(self):
        self.active = not self.active
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
            fg_color=f"{self.button_colors['enabled'] if self.random_agent_exclusiselect is True else self.button_colors['disabled']}",
        )

        self.update_random_agent_tab(exclusiselect_mode=True)

    # Toggles different tools
    def toggle_tools(self):
        self.enable_tools = not self.enable_tools

        if self.enable_tools is True:
            self.tools_thread = threading.Thread(target=self.tools_main).start()

        self.update_tools_tab()

    # Toggles auto drop spike
    def toggle_auto_drop_spike(self):
        self.auto_drop_spike = not self.auto_drop_spike
        self.update_tools_tab()

    # Toggles auto gg
    def toggle_auto_gg(self):
        self.auto_gg = not self.auto_gg
        self.update_tools_tab()

    # Toggles anti afk
    def toggle_anti_afk(self):
        self.anti_afk = not self.anti_afk
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
            try:
                with open(
                    resource_path("data/user_settings.json"), "r"
                ) as user_settings_file:
                    user_settings = json.load(user_settings_file)
                    self.current_save_file = (
                        user_settings["ACTIVE_SAVE_FILE"]
                        if user_settings["ACTIVE_SAVE_FILE"] in self.save_files
                        else "default"
                    )
                    self.minimize_to_tray = user_settings["MINIMIZE_TO_TRAY"]
                    self.start_minimized = user_settings["START_MINIMIZED"]
                    self.active = user_settings["INSTALOCK_ON_START"]
                    self.safe_mode = user_settings["SAFE_MODE_ENABLED_ON_START"]
                    self.safe_mode_strength = user_settings[
                        "SAFE_MODE_STRENGTH_ON_START"
                    ]
                    self.persistent_random_agents = user_settings[
                        "PERSISTENT_RANDOM_AGENTS"
                    ]
                    self.fast_mode_timings = user_settings["FAST_MODE_TIMINGS"]
                    self.hide_default_save_file = user_settings[
                        "HIDE_DEFAULT_SAVE_FILE"
                    ]
                    self.favorited_save_files = user_settings["FAVORITED_SAVE_FILES"]
                    self.total_games_used = user_settings["TIMES_USED"]
                    self.time_to_lock_list = user_settings["TIME_TO_LOCK"]

                    if len(self.time_to_lock_list) != len(self.safe_mode_timing) + 1:
                        self.time_to_lock_list = list(
                            list() for _ in range(len(self.safe_mode_timing) + 1)
                        )

            # Creates a new user_settings.json file if one does not exist
            except Exception:
                self.minimize_to_tray = False
                self.start_minimized = False
                self.persistent_random_agents = False
                self.hide_default_save_file = True
                self.fast_mode_timings = [0.2, 0.2, 0.2]

            with open(resource_path("data/user_settings.json"), "w") as us:
                user_settings_file_json = {
                    "ACTIVE_SAVE_FILE": self.current_save_file,
                    "MINIMIZE_TO_TRAY": self.minimize_to_tray,
                    "START_MINIMIZED": self.start_minimized,
                    "INSTALOCK_ON_START": self.active,
                    "SAFE_MODE_ENABLED_ON_START": self.safe_mode,
                    "SAFE_MODE_STRENGTH_ON_START": self.safe_mode_strength,
                    "PERSISTENT_RANDOM_AGENTS": self.persistent_random_agents,
                    "FAST_MODE_TIMINGS": self.fast_mode_timings,
                    "HIDE_DEFAULT_SAVE_FILE": self.hide_default_save_file,
                    "FAVORITED_SAVE_FILES": self.favorited_save_files,
                    "TIMES_USED": self.total_games_used,
                    "TIME_TO_LOCK": self.time_to_lock_list,
                }
                us.write(json.dumps(user_settings_file_json, indent=4))

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
                self.map_specific_agents_dict[map_name] = self.default_agents[0]

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
            if agent_name in self.unlocked_agents_dict:
                if self.unlocked_agents_dict[agent_name] is False:
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

    # Updates the stats in config.json
    def update_user_settings(self):
        with open(resource_path("data/user_settings.json"), "r") as config_file:
            config = json.load(config_file)
            config["FAVORITED_SAVE_FILES"] = self.favorited_save_files
            config["TIMES_USED"] = self.total_games_used
            config["TIME_TO_LOCK"] = self.time_to_lock_list
        with open(resource_path("data/user_settings.json"), "w") as file:
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

        self.update_gui(from_save_tab=True)

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
        self.save_file_frame_items[
            f"{new_file_name}_frame"
        ] = self.save_file_frame_items.pop(f"{old_file_name}_frame")
        self.save_file_frame_items[
            f"{new_file_name}_button"
        ] = self.save_file_frame_items.pop(f"{old_file_name}_button")

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

        is_confirmed = ConfirmationPopup(
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
        self.update_gui(from_agent_tab=True)
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
        if self.persistent_random_agents is False:
            if (
                self.random_agent_exclusiselect is True
                and exclusiselect_toggle is False
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

    # region Locking Thread

    # Starts the locking thread, calls the locking function based on the mode
    def locking_main(self):
        time.sleep(1)
        if self.locking_screenshotter is None:
            self.locking_screenshotter = mss.mss()
        while self.active_thread is True:
            time.sleep(0.3)
            if self.active is True and self.active_thread is True:
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
            and self.active is True
            and self.map_specific_mode is True
        ):
            time.sleep(0.1)

            current_map = self.return_screenshot_bytes(self.locking_screenshotter, self.map_selection_coords)
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
            and self.active is True
            and self.map_specific_mode is map_specific_toggle
        ):
            agent_screen_section = self.return_screenshot_bytes(self.locking_screenshotter, self.locking_coords)

            if agent_screen_section == self.agent_select_image:
                confirmations += 1

                if confirmations >= self.locking_confirmations_required:
                    self.lock_agent()
            else:
                confirmations = 0

        else:
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
            self.mouse.position = (self.lock_button[0], self.lock_button[1])
            time.sleep(self.fast_mode_timings[2])

            if self.hover_mode is False:
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
            self.mouse.position = (self.lock_button[0], self.lock_button[1])
            time.sleep(round(random.uniform(low_timing, high_timing), 2))

            if self.hover_mode is False:
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
            self.active is True and self.active_thread is True and self.locking is False
        ): 
            menu_screen_1 = self.return_screenshot_bytes(self.locking_screenshotter, self.menu_screen_coords['end_of_game'])
            menu_screen_2 = self.return_screenshot_bytes(self.locking_screenshotter, self.menu_screen_coords['main_menu'])

            if (
                menu_screen_1 in self.in_menu_images
                or menu_screen_2 in self.in_menu_images
            ):
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
            self.active = False

    # endregion

    # region Tools Thread

    def tools_main(self):
        if self.tools_screenshotter is None:
            self.tools_screenshotter = mss.mss()
        spike_drop_confirmations = 0
        while self.enable_tools is True:
            time.sleep(0.1)
            if self.locking is False or self.active is False:
                if self.auto_drop_spike is True:

                    spike_screenshot = self.return_screenshot_bytes(self.tools_screenshotter, self.tools_locations["spike"])
                    can_plant = self.return_screenshot_bytes(self.tools_screenshotter, self.tools_locations["can_plant"])
                    is_planting = self.return_screenshot_bytes(self.tools_screenshotter, self.tools_locations["is_planting"])

                    if spike_screenshot == self.tools_images["spike"] and can_plant != self.tools_images["can_plant"] and is_planting != self.tools_images["is_planting"]:
                        spike_drop_confirmations += 1
                            
                        if spike_drop_confirmations >= self.spike_drop_confirmations_required:
                            self.keyboard.press("4")
                            self.keyboard.release("4")
                            time.sleep(0.1)
                            self.keyboard.press("g")
                            self.keyboard.release("g")
                            spike_drop_confirmations = 0

                    else:
                        spike_drop_confirmations = 0

                if self.auto_gg is True:
                    pass

                if self.anti_afk is True:
                    pass

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
class ConfirmationPopup(customtkinter.CTkToplevel):
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


# endregion


if __name__ == "__main__":
    main_gui = InstalockerGUIMain()
    main_gui.mainloop()
