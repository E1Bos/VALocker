# region Imports

# Imports all modules, if it fails it will install them
try:
    # Modules that are not installed by default
    import customtkinter, pystray
    import PIL.Image, PIL.ImageGrab
    import pynput.mouse as pynmouse
except ModuleNotFoundError:
    # Installs missing modules if exception is raised
    import subprocess

    subprocess.run(["pip", "install", "-r", "requirements.txt"])
    import customtkinter, pystray
    import PIL.Image, PIL.ImageGrab
    import pynput.mouse as pynmouse

# Imports modules that are installed with Python
import json, os, random, threading, time, ctypes
import tkinter as tk

# endregion

# region PyInstaller Requirement
def resource_path(relative):
    return os.path.join(
        os.environ.get(
            "_MEIPASS2",
            os.path.abspath(".")
        ),
        relative
    )
# endregion

class Program(customtkinter.CTk):
    # region Init and Exit Function

    def __init__(self):
        super().__init__()

        # Default Save File
        self.current_save_file = "default"

        # Locking Values
        self.active = False
        self.active_thread = True
        self.locking = True
        self.locking_coords = (945, 866, 955, 867)
        self.locking_image_path = "images/agent_screen/agent_screen_bar.png"
        self.locking_confirmations = 2
        self.locking_button = None
        self.agent_coords_offset = (15, 15)
        # self.locking_coords = (958, 866, 962, 870) # agent screen dot
        # self.locking_coords = (959, 867, 961, 869) # agent screen dot solid

        # Locking Images
        self.agent_select_image = PIL.Image.open(resource_path(self.locking_image_path)).tobytes()
        self.in_menu_images = [
            PIL.Image.open(resource_path("images/in_menu/in_menu_normal_bar.png")).tobytes(),
            PIL.Image.open(resource_path("images/in_menu/in_menu_comp_bar.png")).tobytes(),
            PIL.Image.open(resource_path("images/in_menu/in_menu_progress_text_1.png")).tobytes(),
            PIL.Image.open(resource_path("images/in_menu/in_menu_progress_text_2.png")).tobytes(),
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

        # GUI SETTINGS
        self.window_width = 550
        self.window_height = 500
        self.label_font = ("Arial", 16)  # Arial Size 16
        self.button_font = ("Arial", 14)  # Arial Size 14
        customtkinter.set_appearance_mode("Dark")
        customtkinter.set_default_color_theme("blue")
        self.title("VALocker")
        self.button_colors = {"enabled": "#259969", "disabled": "#b52d3b"}
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
            disabled="images/icons/instalocker_disabled.ico",
            locking="images/icons/instalocker_enabled.ico",
            waiting="images/icons/instalocker_enabled.ico",
        )
        self.current_icon = self.icons["disabled"]
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("VALocker.GUI")


        # Loads data from save files
        self.load_data_from_files(first_run=True)

        # Finds all save files
        self.find_save_files()

        # Creates Mouse Controller
        self.mouse = pynmouse.Controller()

        # Creates GUI
        self.create_gui()

        # Updates GUI
        self.update_gui()

        # Checks if program should close to tray
        if self.minimize_to_tray is True:
            self.protocol("WM_DELETE_WINDOW", self.withdraw_window)

            self.create_icon()

            if self.start_minimized is True:
                self.withdraw_window()
        else:
            self.protocol("WM_DELETE_WINDOW", self.exit)

        # Creates Thread
        self.agent_thread = threading.Thread(target=self.locking_thread).start()

    def exit(self):
        self.active_thread = False
        try:
            self.icon.stop()
        except AttributeError:
            pass
        self.destroy()

    # endregion

    # region GUI Functions and Icon

    # region GUI Creation
    def create_gui(self):
        self.geometry(f"{self.window_width}x{self.window_height}")
        self.resizable(False, False)

        tabs = customtkinter.CTkTabview(
            self,
            corner_radius=10,
            width=self.window_width,
            height=self.window_height - 20,
        )
        tabs.pack(padx=10, pady=5, fill=tk.BOTH)

        overview_tab = tabs.add("Overview")
        agent_toggle_tab = tabs.add("Toggle Agents")
        random_agent_tab = tabs.add("Random Agents")
        map_specific_tab = tabs.add("Map Specific")

        # region Overview Tab

        current_status_frame = customtkinter.CTkFrame(overview_tab)
        current_status_frame.grid(row=0, column=0)

        current_status_label = customtkinter.CTkLabel(
            current_status_frame, text="Instalocker:", font=self.label_font
        )
        current_status_label.pack(padx=10, pady=(5, 0))

        self.current_status_button = customtkinter.CTkButton(
            current_status_frame,
            text=f"{'Running' if self.active is True else 'Stopped'}",
            hover=False,
            fg_color=f"{self.button_colors['enabled'] if self.active is True else self.button_colors['disabled']}",
            font=self.button_font,
            command=self.toggle_active,
        )
        self.current_status_button.pack(padx=10, pady=(0, 5))

        current_task_label = customtkinter.CTkLabel(
            current_status_frame, text=f"Current Task:", font=self.label_font
        )
        current_task_label.pack(padx=10, pady=(5, 0))

        self.current_task_button = customtkinter.CTkButton(
            current_status_frame,
            text=f"{'None' if self.active is False else 'Locking' if self.locking is True else 'In Game'}",
            hover=False,
            font=self.button_font,
            command=self.toggle_thread_mode,
        )
        self.current_task_button.pack(padx=10, pady=(0, 5))

        safe_mode_frame = customtkinter.CTkFrame(
            current_status_frame, width=140, height=70, fg_color="transparent"
        )
        safe_mode_frame.pack(padx=10, pady=(5, 0), ipadx=0)

        safe_mode_label = customtkinter.CTkLabel(
            safe_mode_frame, text=f"Safe Mode:", font=self.label_font
        )
        safe_mode_label.pack(anchor=tk.N, padx=10)

        self.safe_mode_enabled_button = customtkinter.CTkButton(
            safe_mode_frame,
            width=int(f"{141 if self.safe_mode is False else 70}"),
            hover=False,
            text=f"{'On' if self.safe_mode is True else 'Off'}",
            fg_color=f"{self.button_colors['enabled'] if self.active is True else self.button_colors['disabled']}",
            font=self.button_font,
            command=self.toggle_safe_mode,
        )
        self.safe_mode_enabled_button.pack(side=tk.LEFT, padx=(0, 1), pady=(0, 5))

        self.safe_mode_strength_button = customtkinter.CTkButton(
            safe_mode_frame,
            width=70,
            hover=False,
            text=f"{list(self.safe_mode_timing.keys())[self.safe_mode_strength]}",
            font=self.button_font,
            command=self.toggle_safe_mode_strength,
        )
        if self.safe_mode is True:
            self.safe_mode_strength_button.pack(side=tk.RIGHT, padx=0, pady=(0, 5))
        else:
            self.safe_mode_strength_button.pack_forget()

        current_save_label = customtkinter.CTkLabel(
            current_status_frame, text="Current Save:", font=self.label_font
        )
        current_save_label.pack(padx=10, pady=(5, 0))

        self.selected_save_file_combobox = customtkinter.CTkComboBox(
            current_status_frame,
            values=self.save_files,
            command=lambda x: self.change_current_save_file(x),
        )
        self.selected_save_file_combobox.set(f"{self.current_save_file}")
        self.selected_save_file_combobox.pack(padx=10, pady=(0, 5))
        self.selected_save_file_combobox.bind(
            "<Return>",
            lambda x: self.change_current_save_file(
                self.selected_save_file_combobox.get()
            ),
        )

        select_agent_frame = customtkinter.CTkFrame(overview_tab)
        select_agent_frame.grid(row=0, column=1)

        select_agent_label = customtkinter.CTkLabel(
            select_agent_frame, text="Selected Agent:", font=self.label_font
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
            select_agent_frame, text="Map Specific:", font=self.label_font
        )
        self.select_map_enabled_label.pack(padx=10, pady=(5, 0))

        self.select_map_specific_button = customtkinter.CTkButton(
            select_agent_frame,
            text=f"{'Enabled' if self.map_specific_mode is True else 'Disabled'}",
            hover=False,
            fg_color=f"{self.button_colors['enabled'] if self.map_specific_mode is True else self.button_colors['disabled']}",
            font=self.button_font,
            command=self.toggle_map_specific,
        )
        self.select_map_specific_button.pack(padx=10, pady=(0, 5))

        random_agent_label = customtkinter.CTkLabel(
            select_agent_frame, text="Random Agent:", font=self.label_font
        )
        random_agent_label.pack(padx=10, pady=(5, 0))

        self.random_agent_button = customtkinter.CTkButton(
            select_agent_frame,
            text=f"{'Enabled' if self.random_agent_mode is True else 'Disabled'}",
            hover=False,
            fg_color=f"{self.button_colors['enabled'] if self.random_agent_mode is True else self.button_colors['disabled']}",
            font=self.button_font,
            command=self.toggle_random_agent_mode,
        )
        self.random_agent_button.pack(padx=10, pady=(0, 5))

        hover_mode_label = customtkinter.CTkLabel(
            select_agent_frame, text="Hover Mode:", font=self.label_font
        )
        hover_mode_label.pack(padx=10, pady=(5, 0))
        self.hover_mode_button = customtkinter.CTkButton(
            select_agent_frame,
            text=f"{'Enabled' if self.hover_mode is True else 'Disabled'}",
            hover=False,
            fg_color=f"{self.button_colors['enabled'] if self.hover_mode is True else self.button_colors['disabled']}",
            font=self.button_font,
            command=self.toggle_hover_mode,
        )
        self.hover_mode_button.pack(padx=10, pady=(0, 5))

        stats_frame = customtkinter.CTkFrame(overview_tab)
        stats_frame.grid(row=0, column=2, sticky="n")

        stats_label = customtkinter.CTkLabel(
            stats_frame, text="Last Lock:", font=self.label_font
        )
        stats_label.pack(padx=10, pady=(5, 0))

        if self.safe_mode is False:
            time_to_lock_text = f"{self.time_to_lock_list[-1] if len(self.time_to_lock_list[-1]) != 0 else '-'}"
        else:
            time_to_lock_text = f"{self.time_to_lock_list[self.safe_mode_strength][-1] if len(self.time_to_lock_list[self.safe_mode_strength]) != 0 else '-'}"

        self.time_to_lock_label = customtkinter.CTkLabel(
            stats_frame,
            text=f"{time_to_lock_text} ms",
            font=self.button_font,
        )
        self.time_to_lock_label.pack(padx=10, pady=(0, 5))

        average_time_to_lock_label = customtkinter.CTkLabel(
            stats_frame, text=f"Average:", font=self.label_font
        )
        average_time_to_lock_label.pack(padx=10, pady=(5, 0))

        self.average_time_to_lock_value = customtkinter.CTkLabel(
            stats_frame,
            text=f"{'-' if len(self.time_to_lock_list[self.safe_mode_strength]) == 0 else round(sum(self.time_to_lock_list[self.safe_mode_strength])/len(self.time_to_lock_list[self.safe_mode_strength]),2)} ms",
            font=self.button_font,
        )
        self.average_time_to_lock_value.pack(padx=10, pady=(0, 5))

        total_games_locked_label = customtkinter.CTkLabel(
            stats_frame, text=f"Deployed:", font=self.label_font
        )
        total_games_locked_label.pack(padx=10, pady=(5, 0))

        self.total_games_locked_value = customtkinter.CTkLabel(
            stats_frame,
            text=f"{self.total_games_used} {'times' if self.total_games_used != 1 else 'time'}",
            font=self.button_font,
        )
        self.total_games_locked_value.pack(padx=10, pady=(0, 5))

        quit_button = customtkinter.CTkButton(
            overview_tab,
            text="Exit",
            fg_color=self.button_colors["disabled"],
            width=95,
            hover=False,
            command=self.exit,
        )
        quit_button.place(relx=0.79, rely=0.9)

        overview_tab.columnconfigure((0, 1, 2), weight=1)  # type: ignore

        # endregion

        # region Agent Toggle Tab

        mass_select_frame = customtkinter.CTkFrame(agent_toggle_tab)
        mass_select_frame.pack(padx=20, pady=(20, 10))

        self.toggle_all_agent_button = customtkinter.CTkCheckBox(
            mass_select_frame,
            text="All",
            command=lambda: self.toggle_unlocked_agent_status("all"),
        )
        self.toggle_all_agent_button.grid(row=0, column=0, padx=(20, 0), pady=10)

        self.toggle_none_agent_button = customtkinter.CTkCheckBox(
            mass_select_frame,
            text="None",
            command=lambda: self.toggle_unlocked_agent_status("none"),
        )
        self.toggle_none_agent_button.grid(row=0, column=1, pady=10)

        toggle_agent_checkbox_frame = customtkinter.CTkFrame(agent_toggle_tab)
        toggle_agent_checkbox_frame.pack()

        interior_toggle_agent_checkbox_frame = customtkinter.CTkFrame(
            toggle_agent_checkbox_frame, fg_color="transparent"
        )
        interior_toggle_agent_checkbox_frame.pack(padx=10, pady=10)

        unlockable_agents = [
            agent for agent in self.all_agents if agent not in self.default_agents
        ]

        self.agent_checkboxes = {}
        for index, agent in enumerate(unlockable_agents):
            column, row = index % 4, index // 4

            self.agent_checkboxes[f"self.{agent}_checkbox"] = customtkinter.CTkCheckBox(
                interior_toggle_agent_checkbox_frame,
                text=agent,
                command=lambda agent=agent: self.toggle_unlocked_agent_status(agent),
            )
            self.agent_checkboxes[f"self.{agent}_checkbox"].grid(
                row=row, column=column, padx=8, pady=8
            )

        # endregion

        # region Random Agent Tab
        random_agent_allnone_button_frame = customtkinter.CTkFrame(
            random_agent_tab, width=500, height=100, fg_color="transparent"
        )
        random_agent_allnone_button_frame.pack(padx=20, pady=5)

        self.random_agent_exclusiselect_button = customtkinter.CTkButton(
            random_agent_allnone_button_frame,
            width=60,
            text="ExclusiSelect",
            hover=False,
            fg_color=f"{self.button_colors['enabled'] if self.random_agent_exclusiselect is True else self.button_colors['disabled']}",
            command=self.toggle_random_agent_exclusiselect,
        )
        self.random_agent_exclusiselect_button.pack(
            side="left", padx=(20, 0), fill=tk.Y, pady=5
        )

        invisible_button = customtkinter.CTkButton(
            random_agent_allnone_button_frame,
            width=90,
            height=40,
            hover=False,
            text="",
            text_color="",
            bg_color="transparent",
            fg_color="transparent",
            state=tk.DISABLED,
            command=lambda: None,
        )
        invisible_button.pack(side="right", padx=(0, 20), fill=tk.Y, pady=5)

        random_agent_all_none_toggle_frame = customtkinter.CTkFrame(
            random_agent_allnone_button_frame, height=100, fg_color="#333333"
        )
        random_agent_all_none_toggle_frame.pack(padx=20, pady=5)

        self.all_random_agent_radio_button = customtkinter.CTkCheckBox(
            random_agent_all_none_toggle_frame,
            text="All",
            command=lambda: self.toggle_random_agent_status("all"),
        )
        self.all_random_agent_radio_button.pack(side="left", padx=(20, 0), pady=10)

        self.none_random_agent_radio_button = customtkinter.CTkCheckBox(
            random_agent_all_none_toggle_frame,
            text="None",
            command=lambda: self.toggle_random_agent_status("none"),
        )
        self.none_random_agent_radio_button.pack(side="right", padx=0, pady=10)

        random_agent_role_toggle_frame = customtkinter.CTkFrame(random_agent_tab)
        random_agent_role_toggle_frame.pack(padx=0, pady=5)

        # Creates the checkboxes for each role
        self.agent_role_checkboxes = dict()
        for index, role in enumerate(self.config_file_agents.keys()):
            role = role.lower()

            self.agent_role_checkboxes[role] = customtkinter.CTkCheckBox(
                random_agent_role_toggle_frame,
                text=role.capitalize(),
                text_color=self.role_colors[role],
                text_color_disabled=self.role_colors[f"{role}_disabled"],
                command=lambda role=role: self.toggle_random_agent_status(role),
            )
            self.agent_role_checkboxes[role].grid(row=0, column=index, padx=10, pady=10)

        # Creates frames for each role
        random_agent_individual_toggle_frame = customtkinter.CTkFrame(
            random_agent_tab, width=150, height=100, fg_color="transparent"
        )
        random_agent_individual_toggle_frame.pack(padx=0, pady=0)

        role_frames = dict()
        for index, role in enumerate(self.config_file_agents.keys()):
            role = role.lower()

            role_frames[role] = customtkinter.CTkFrame(
                random_agent_individual_toggle_frame,
                width=120,
                height=100,
                fg_color="#333333",
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
                command=lambda agent=agent: self.toggle_random_agent_status(agent),
            )
            self.random_agent_checkboxes[f"self.{agent}_random_checkbox"].pack(
                padx=5, pady=5
            )
        # endregion

        # region Map Specific Tab
        map_frames, map_labels, self.map_dropdowns = dict(), dict(), dict()
        for index, map_name in enumerate(self.map_names):
            row, column = index // 2, index % 2

            map_frames[f"{map_name}_frame"] = customtkinter.CTkFrame(
                map_specific_tab, width=230
            )
            map_frames[f"{map_name}_frame"].grid(
                row=row, column=column, padx=10, pady=10, sticky="nsew"
            )
            map_labels[f"{map_name}_label"] = customtkinter.CTkLabel(
                map_frames[f"{map_name}_frame"],
                text=f"{map_name}:",
                font=self.label_font,
            )
            map_labels[f"{map_name}_label"].pack(padx=10, pady=5, side=tk.LEFT)

            self.map_dropdowns[map_name] = customtkinter.CTkOptionMenu(
                map_frames[f"{map_name}_frame"],
                values=list(
                    agent
                    for agent, unlock_status in self.unlocked_agents_dict.items()
                    if unlock_status is True
                ),
                width=100,
                command=lambda agent_name, map_name=map_name: self.toggle_map_specific_agent(
                    agent_name=agent_name, map_name=map_name
                ),
            )

            self.map_dropdowns[map_name].pack(padx=(0, 10), pady=5, side=tk.RIGHT)

        map_specific_tab.columnconfigure((0, 1), weight=1)  # type: ignore

        # endregion

    def create_icon(self):
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

    # endregion

    # region GUI  Updates

    # Updates All GUI Elements
    def update_gui(self):
        try:
            self.update_overview_tab()
            self.update_agent_toggle_tab()
            self.update_random_agent_tab()
            self.update_map_specific_tab()
            self.update_icon()
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
            text=f"{'None' if self.active is False else 'Locking' if self.locking is True else 'In Game'}"
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

        self.selected_save_file_combobox.configure(values=self.save_files)

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

        self.random_agent_button.configure(
            text=f"{'Enabled' if self.random_agent_mode is True else 'Disabled'}",
            fg_color=f"{self.button_colors['enabled'] if self.random_agent_mode is True else self.button_colors['disabled']}",
        )

        # Disables random agent if map specific mode is enabled and vice versa
        match self.map_specific_mode, self.random_agent_mode:
            case False, False:
                self.select_agent_dropdown.configure(state=tk.NORMAL)
                if any(value is True for value in self.random_agents_dict.values()):
                    self.random_agent_button.configure(state=tk.NORMAL)
                else:
                    self.random_agent_button.configure(state=tk.DISABLED)
                if any(value is None for value in self.map_specific_agents_dict.values()):
                    self.select_map_specific_button.configure(state=tk.DISABLED)
                else:
                    self.select_map_specific_button.configure(state=tk.NORMAL)
            case True, False:
                self.random_agent_button.configure(state=tk.DISABLED)
                self.select_agent_dropdown.configure(state=tk.DISABLED)
            case False, True:
                self.select_map_specific_button.configure(state=tk.DISABLED)
                self.select_agent_dropdown.configure(state=tk.DISABLED)
            case True, True:
                self.map_specific_mode = False
                self.random_agent_mode = False
                self.update_overview_tab()


    # Updates agent toggle tab
    def update_agent_toggle_tab(self):
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

    # Updates random agent tab
    def update_random_agent_tab(self):
        # Selects enabled agents
        for agent, value in self.random_agents_dict.items():
            if value is True:
                self.random_agent_checkboxes[f"self.{agent}_random_checkbox"].select()
            else:
                self.random_agent_checkboxes[f"self.{agent}_random_checkbox"].deselect()

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

        # Selects enabled roles (controller/duelist/initiator/sentinel)
        for role in self.config_file_agents:
            if all(
                self.random_agents_dict[agent] is True
                for agent in self.config_file_agents[role]
                if self.unlocked_agents_dict[agent] is True
            ):
                self.agent_role_checkboxes[role.lower()].select()
            else:
                self.agent_role_checkboxes[role.lower()].deselect()

        # Disables agents that are not unlocked
        for agent in self.unlocked_agents_dict:
            if (
                agent not in self.default_agents
                and self.unlocked_agents_dict[agent] is False
            ):
                self.random_agent_checkboxes[f"self.{agent}_random_checkbox"].configure(
                    state=tk.DISABLED
                )
                self.random_agent_checkboxes[f"self.{agent}_random_checkbox"].deselect()
            else:
                self.random_agent_checkboxes[f"self.{agent}_random_checkbox"].configure(
                    state=tk.NORMAL
                )

    # Updates map specific tab
    def update_map_specific_tab(self):
        for map_name in self.map_names:
            if self.map_specific_agents_dict[map_name] is not None:
                self.map_dropdowns[map_name].set(
                    self.map_specific_agents_dict[map_name]
                )
            else:
                self.map_dropdowns[map_name].set("None")

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

        # Closes the window and runs the icon

    # Hides the window then the [X] is clicked
    def withdraw_window(self):
        self.withdraw()
        self.icon = pystray.Icon(
            "VALocker", PIL.Image.open(resource_path(self.current_icon)), "VALocker", self.icon_menu
        )
        self.icon.run()

    # endregion

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
        self.update_overview_tab()

    # Toggles the hover mode
    def toggle_hover_mode(self):
        self.hover_mode = not self.hover_mode
        self.update_overview_tab()

    def toggle_random_agent_exclusiselect(self):
        self.random_agent_exclusiselect = not self.random_agent_exclusiselect

        if self.random_agent_exclusiselect is True:
            self.random_agents_dict_backup = self.random_agents_dict.copy()
        else:
            self.random_agents_dict = self.random_agents_dict_backup.copy()

        self.random_agent_exclusiselect_button.configure(
            fg_color=f"{self.button_colors['enabled'] if self.random_agent_exclusiselect is True else self.button_colors['disabled']}",
        )
        self.update_random_agent_tab()

    # endregion

    # region Config and Save Reading and Writing

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
                with open(resource_path("data/user_settings.json"), "r") as user_settings_file:
                    user_settings = json.load(user_settings_file)
                    self.current_save_file = user_settings["ACTIVE_SAVE_FILE"]
                    self.minimize_to_tray = user_settings["MINIMIZE_TO_TRAY"]
                    self.start_minimized = user_settings["START_MINIMIZED"]
                    self.active = user_settings["INSTALOCK_ON_START"]
                    self.safe_mode = user_settings["SAFE_MODE_ENABLED_ON_START"]
                    self.safe_mode_strength = user_settings["SAFE_MODE_STRENGTH_ON_START"]
                    self.total_games_used = user_settings["TIMES_USED"]
                    self.time_to_lock_list = user_settings["TIME_TO_LOCK"]

                    if len(self.time_to_lock_list) != len(self.safe_mode_timing) + 1:
                        self.time_to_lock_list = list(
                            list() for _ in range(len(self.safe_mode_timing) + 1)
                        )

                with open(resource_path("data/user_settings.json"), "w") as us:
                    user_settings_file_json = {
                        "ACTIVE_SAVE_FILE": self.current_save_file,
                        "MINIMIZE_TO_TRAY": self.minimize_to_tray,
                        "START_MINIMIZED": self.start_minimized,
                        "INSTALOCK_ON_START": self.active,
                        "SAFE_MODE_ENABLED_ON_START": self.safe_mode,
                        "SAFE_MODE_STRENGTH_ON_START": self.safe_mode_strength,
                        "TIMES_USED": self.total_games_used,
                        "TIME_TO_LOCK": self.time_to_lock_list,
                    }
                    us.write(json.dumps(user_settings_file_json, indent=4))

            # Creates a new user_settings.json file if one does not exist
            except FileNotFoundError:
                self.minimize_to_tray = False
                self.start_minimized = False
                with open(resource_path("data/user_settings.json"), "w") as us:
                    user_settings_file_json = {
                        "ACTIVE_SAVE_FILE": self.current_save_file,
                        "MINIMIZE_TO_TRAY": self.minimize_to_tray,
                        "START_MINIMIZED": self.start_minimized,
                        "INSTALOCK_ON_START": self.active,
                        "SAFE_MODE_ENABLED_ON_START": self.safe_mode,
                        "SAFE_MODE_STRENGTH_ON_START": self.safe_mode_strength,
                        "TIMES_USED": self.total_games_used,
                        "TIME_TO_LOCK": self.time_to_lock_list,
                    }
                    us.write(json.dumps(user_settings_file_json, indent=4))

        # Loads the save file data
        with open(resource_path(f"data/save_files/{self.current_save_file}.json"), "r") as sf:
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
        with open(resource_path(f"data/save_files/{self.current_save_file}.json"), "w") as sf:
            save_file_json = {
                "SELECTED_AGENT": self.selected_agent,
                "UNLOCKED_AGENTS": self.unlocked_agents_dict,
                "RANDOM_AGENTS": self.random_agents_dict,
                "MAP_SPECIFIC_AGENTS": self.map_specific_agents_dict,
            }
            sf.write(json.dumps(save_file_json, indent=4))

    # Changes the current active save file
    def change_current_save_file(self, file_name):
        self.current_save_file = file_name

        if file_name not in self.save_files:
            for agent in self.map_specific_agents_dict.copy():
                self.map_specific_agents_dict[agent] = None
            self.save_current_data()

        with open(resource_path("data/user_settings.json"), "r") as config_file:
            config = json.load(config_file)
            config["ACTIVE_SAVE_FILE"] = file_name
        with open(resource_path("data/user_settings.json"), "w") as file:
            file.write(json.dumps(config, indent=4))

        self.find_save_files()

        self.load_data_from_files()

        self.update_gui()

    # Finds all save files in data/save_files
    def find_save_files(self):
        self.save_files = ["default"]
        for file in os.listdir(resource_path("./data/save_files")):
            if file.endswith(".json") and file.startswith("default") is False:
                self.save_files.append(file.removesuffix(".json"))

    # Updates the stats in config.json
    def update_stats_in_user_settings(self):
        with open(resource_path("data/user_settings.json"), "r") as config_file:
            config = json.load(config_file)
            config["TIMES_USED"] = self.total_games_used
            config["TIME_TO_LOCK"] = self.time_to_lock_list
        with open(resource_path("data/user_settings.json"), "w") as file:
            file.write(json.dumps(config, indent=4))

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
            case _:
                self.unlocked_agents_dict[agent_name] = not self.unlocked_agents_dict[
                    agent_name
                ]

        # Makes sure selected agent is unlocked
        if self.unlocked_agents_dict[self.selected_agent] is False:
            self.selected_agent = list(
                agent
                for agent, unlock_status in self.unlocked_agents_dict.items()
                if unlock_status is True
            )[0]

        for agent in self.all_agents:
            if self.unlocked_agents_dict[agent] is False:
                self.random_agents_dict[agent] = False

        self.update_gui()
        self.save_current_data()

    # Toggles the agent in the random agent tab
    def toggle_random_agent_status(self, agent_name, exclusiselect_toggle=False):
        if agent_name in [
            "all",
            "none",
            "controllers",
            "duelists",
            "initiators",
            "sentinels",
        ]:
            match agent_name:
                case "all":
                    for agent in self.all_agents:
                        if self.unlocked_agents_dict[agent] is True:
                            self.random_agents_dict[agent] = True
                case "none":
                    for agent in self.all_agents:
                        self.random_agents_dict[agent] = False
                case _:
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
        else:
            self.random_agents_dict[agent_name] = not self.random_agents_dict[
                agent_name
            ]

        # Only updates the list if a checkbox is selected, not when the ExclusiSelect mode is toggled
        if self.random_agent_exclusiselect is True and exclusiselect_toggle is False:
            self.random_agents_dict_backup = self.random_agents_dict.copy()

        self.update_random_agent_tab()
        self.update_overview_tab()
        self.save_current_data()

    # Toggles which agent is selected for a specific map
    def toggle_map_specific_agent(self, agent_name, map_name):
        self.map_specific_agents_dict[map_name] = agent_name
        self.update_map_specific_tab()
        self.update_overview_tab()
        self.save_current_data()

    # endregion

    # region Locking

    def locking_thread(self):
        time.sleep(1)
        while self.active_thread is True:
            time.sleep(0.3)
            if (
                self.locking is True
                and self.active is True
                and self.active_thread is True
            ):
                self.lock_button = (
                    self.box_info["LOCK_COORDS"][0]
                    + random.randint(0, self.box_info["LOCK_SIZE"][0]),
                    self.box_info["LOCK_COORDS"][1]
                    + random.randint(0, self.box_info["LOCK_SIZE"][1]),
                )
                if self.map_specific_mode is False:
                    self.locate_agent_screen()
                else:
                    self.locate_map_screen()

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
            current_map = PIL.ImageGrab.grab(bbox=(878, 437, 1047, 646)).tobytes()
            game_map = self.map_lookup.get(current_map)

        if game_map is not None:
            self.find_agent_coords(self.map_specific_agents_dict[game_map])
            self.locate_agent_screen(True)
        else:
            self.find_game_end()

    def locate_agent_screen(self, map_specific_toggle=False):
        total_confirmations = 0
        self.start_lock = float()
        while (
            self.active_thread is True
            and self.locking is True
            and self.active is True
            and self.map_specific_mode is map_specific_toggle
        ):
            agent_screen_section = PIL.ImageGrab.grab(
                bbox=(self.locking_coords)
            ).tobytes()

            if agent_screen_section == self.agent_select_image:
                total_confirmations += 1

                if total_confirmations >= self.locking_confirmations:
                    self.start_lock = time.time()
                    self.lock_agent()

            else:
                total_confirmations = 0
        self.find_game_end()

    def lock_agent(self):
        randomly_selected_agent = str()
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
            time.sleep(0.01)
            self.mouse.click(pynmouse.Button.left, 1)
            time.sleep(0.06)
            self.mouse.position = (self.lock_button[0], self.lock_button[1])
            time.sleep(0.01)

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

        time_to_lock = round((time.time() - self.start_lock) * 1000, 2)
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
        self.update_stats_in_user_settings()
        self.find_game_end()

    def find_game_end(self):
        while (
            self.active is True and self.active_thread is True and self.locking is False
        ):
            time.sleep(1)
            menu_screen_1 = PIL.ImageGrab.grab(bbox=(814, 243, 892, 244)).tobytes()
            menu_screen_2 = PIL.ImageGrab.grab(bbox=(1330, 330, 1455, 353)).tobytes()
            if (
                menu_screen_1 in self.in_menu_images
                or menu_screen_2 in self.in_menu_images
            ):
                self.locking = True
                self.update_overview_tab()
                try:
                    self.icon.update_menu()
                except AttributeError:
                    pass
                self.locking_thread()

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
            min_offset_x, max_offset_x = self.agent_coords_offset[0], self.box_info["SIZE"] - self.agent_coords_offset[0]
            min_offset_y, max_offset_y = self.agent_coords_offset[1], self.box_info["SIZE"] - self.agent_coords_offset[1]
            
            offset_x = random.randint(min_offset_x, max_offset_x)
            offset_y = random.randint(min_offset_y, max_offset_y)

            # Returns the coords of the agent with a random offset
            self.agent_coords = (
                corner_coords[0] + offset_x,
                corner_coords[1] + offset_y
            )

        # Disable instalocking if the agent trying to be selected is not unlocked
        except ValueError:
            self.active = False

    # endregion


if __name__ == "__main__":
    program = Program()
    program.mainloop()
