import json
import threading
import time
import pystray
import customtkinter
import tkinter as tk
import pynput.mouse as pynmouse
import PIL.Image
import PIL.ImageGrab
import time
import random

class Program(customtkinter.CTk):
    #---------------INITIALIZATION---------------#
    
    def __init__(self):
        super().__init__()
        # Default values
        self.name = "VaLocker"

        # Default values
        self.active = False  # Instalocker Active
        self.map_specific_enabled = False  # Map Specific Agents Enabled by Default
        self.active_coords = None  # Coords of Agent
        self.lock_button = None  # Coords of Lock Button
        self.active_thread = True  # Thread Active
        self.in_valorant_menu = True  # In Valorant Menu
        
        # Safe Mode 
        self.safe_mode = False # Safe Mode
        self.safe_mode_strength = 0 # Affets safe mode timing (0 = disabled, 1 = low, 2 = medium, 3 = high)
        self.safe_mode_strength_saved = 1 # Saved safe mode strength
        self.safe_mode_timing = [(0.2, 0.4), (0.4, 0.7), (0.7, 1.0)] # + 0.1s for average lock time
        # 0.3 - 0.5s, 0.5 - 0.8s, 0.8 - 1.1s
        
        # Stats
        self.time_to_lock = "-" # Last lock time
        self.total_games_locked = 0 # Total games locked

        self.average_time_to_lock = [[] for x in range(4)] # Average lock time for each safe mode strength

        # Changed in agents.json
        self.box_dim = 0 # Box Dimension
        self.selected_agent = None  # Selected Agent

        with open('data/config.json', 'r') as f:
            config = json.load(f)
            self.start_minimized = config["START_MINIMIZED"]

        self.mouse = pynmouse.Controller()

        # Load all agents
        self.load_agents()

        # Load icons
        self.tray_icons = (PIL.Image.open("images/instalocker_enabled.ico"),
                           PIL.Image.open("images/instalocker_disabled.ico"))

        self.agent_select_image = PIL.Image.open("images/agent_screen/agent_screen_bar.png").tobytes()

        self.in_menu_images = [PIL.Image.open('images/in_menu/in_menu_1.png').tobytes(),
                               PIL.Image.open('images/in_menu/in_menu_2.png').tobytes()]

        # Load the map specific images to be searched
        maps_list = ['Ascent', 'Bind', 'Breeze', 'Fracture',
                     'Haven', 'Icebox', 'Lotus', 'Pearl', 'Split']
        self.maps_lookup = {}
        for map_name in maps_list:
            binary_of_map = PIL.Image.open(
                f"images/map_images/{map_name}.png").tobytes()
            self.maps_lookup[binary_of_map] = map_name
        self.selected_map = maps_list[0]

        # Create the icon
        self.icon_menu = pystray.Menu(
            pystray.MenuItem(
                lambda x: f'Show GUI',
                lambda x: self.show_window(),
                default=True
            ),
            pystray.MenuItem(
                lambda x: f'Status: {"Enabled" if self.active else "Disabled"}',
                lambda x: self.change_active_status(), checked=lambda x: self.active
            ),
            pystray.MenuItem(
                lambda x: f"Status: {'None' if self.active is False else 'Locking' if self.in_valorant_menu is True else 'In Game (Waiting)'}", lambda x: self.switch_mode()),
            pystray.MenuItem("Exit", lambda x: self.exit())
        )

        self.protocol('WM_DELETE_WINDOW', self.withdraw_window)

        self.agent_thread = threading.Thread(target=self.agent_lock).start()

        self.update_icon()
        self.create_gui()
        self.update_gui()

        if self.start_minimized == True:
            self.withdraw_window()


    #---------------EXIT---------------#

    def exit(self):
        self.active_thread = False
        try: self.icon.stop()
        except AttributeError: pass
        self.destroy()


    #---------------GUI---------------#

    # Create GUI elements
    def create_gui(self):
        customtkinter.set_appearance_mode("Dark")
        customtkinter.set_default_color_theme("blue")

        self.title("VaLocker")
        self.geometry("650x350")
        self.resizable(False, False)

        self.tabs = customtkinter.CTkTabview(self, corner_radius=10, width=650, height=350)
        self.tabs.pack(padx=10, pady=5, fill=tk.BOTH)

        self.overview_tab = self.tabs.add("Overview")
        self.agent_tab = self.tabs.add("Toggle Agents")
        self.map_specific_tab = self.tabs.add("Map Specific")

        # Overview Tab
        self.current_status = customtkinter.CTkFrame(self.overview_tab, width=202, height=200)
        self.current_status.pack(padx=(55,20), pady=10, side=tk.LEFT, anchor=tk.N)

        self.current_status_label = customtkinter.CTkLabel(self.current_status, text="Instalocker:", font=("Arial", 16))
        self.current_status_label.grid(row=0, column=0, padx=10, pady=(5,0))

        self.current_status_button = customtkinter.CTkButton(self.current_status, text=f"{'Running' if self.active is True else 'Stopped'}", hover=False, fg_color=f"{'#259969' if self.active is True else '#b52d3b'}", font=("Arial", 14), command=self.change_active_status)
        self.current_status_button.grid(row=1, column=0, padx=10, pady=(0,5))

        self.current_task_label = customtkinter.CTkLabel(self.current_status, text=f"Current Task:", font=("Arial", 16))
        self.current_task_label.grid(row=2, column=0, padx=10, pady=(5,0))

        self.current_task_button = customtkinter.CTkButton(self.current_status, text=f"{'None' if self.active is False else 'Locking' if self.in_valorant_menu is True else 'In Game'}", hover=False, font=("Arial", 14), command=self.switch_mode)
        self.current_task_button.grid(row=3, column=0, padx=10, pady=(0,5))

        self.safe_mode_frame = customtkinter.CTkFrame(self.current_status, width=140, height=70, fg_color='transparent')
        self.safe_mode_frame.grid(row=4, column=0, padx=10, pady=(5,0), ipadx=0)

        self.safe_mode_enabled_label = customtkinter.CTkLabel(self.safe_mode_frame, text=f"Safe Mode:", font=("Arial", 16))
        self.safe_mode_enabled_label.pack(anchor=tk.N, padx=10)

        self.safe_mode_enabled_button = customtkinter.CTkButton(self.safe_mode_frame, width=int(f"{141 if self.safe_mode is False else 70}"), hover=False, text=f"{'On' if self.safe_mode is True else 'Off'}", font=("Arial", 14), command=self.toggle_safe_mode)
        self.safe_mode_enabled_button.pack(side=tk.LEFT, padx=(0,1), pady=(0,5))

        self.safe_mode_strength_button = customtkinter.CTkButton(self.safe_mode_frame, width=70, hover=False, text=f"{'Low' if self.safe_mode_strength == 0 else 'Medium' if self.safe_mode_strength == 1 else 'High'}", font=("Arial", 14), command=self.change_safe_mode_strength)

        self.select_agent_frame = customtkinter.CTkFrame(self.overview_tab, width=150, height=100)
        self.select_agent_frame.pack(padx=20, pady=10, side=tk.LEFT, anchor=tk.N)

        self.select_agent_label = customtkinter.CTkLabel(self.select_agent_frame, text="Default Agent:", font=("Arial", 16))
        self.select_agent_label.grid(row=0, column=0, padx=10, pady=(5,0))

        self.select_agent_dropdown = customtkinter.CTkOptionMenu(self.select_agent_frame, dynamic_resizing=False,
                                                                values=self.unlocked_agents, command=lambda x: self.change_agent(x))
        self.select_agent_dropdown.set(f"{self.selected_agent}")
        self.select_agent_dropdown.grid(row=1, column=0, padx=10, pady=(0,5))

        self.select_map_enabled_label = customtkinter.CTkLabel(self.select_agent_frame, text="Map Specific:", font=("Arial", 16))
        self.select_map_enabled_label.grid(row=2, column=0, padx=10, pady=(5,0))

        self.select_map_specific_button = customtkinter.CTkButton(self.select_agent_frame, text=f"{'Enabled' if self.map_specific_enabled is True else 'Disabled'}", hover=False, fg_color=f"{'#259969' if self.map_specific_enabled is True else '#b52d3b'}", font=("Arial", 14), command=self.toggle_map_specific)
        self.select_map_specific_button.grid(row=3, column=0, padx=10, pady=(0,5))

        self.stats_frame = customtkinter.CTkFrame(self.overview_tab, width=300, height=100)
        self.stats_frame.pack(padx=20, pady=10, side=tk.LEFT, anchor=tk.N, fill='x')

        self.stats_label = customtkinter.CTkLabel(self.stats_frame, text="Last Lock:", font=("Arial", 16))
        self.stats_label.grid(row=0, column=0, padx=10, pady=(5,0))

        self.time_to_lock_label = customtkinter.CTkLabel(self.stats_frame, text=f"{self.time_to_lock} ms", font=("Arial", 14))
        self.time_to_lock_label.grid(row=1, column=0, padx=10, pady=(0,5))

        self.average_time_to_lock_label = customtkinter.CTkLabel(self.stats_frame, text=f"Average:", font=("Arial", 16))
        self.average_time_to_lock_label.grid(row=2, column=0, padx=10, pady=(5,0))

        self.average_time_to_lock_value = customtkinter.CTkLabel(self.stats_frame, text="-", font=("Arial", 14))
        self.average_time_to_lock_value.grid(row=3, column=0, padx=10, pady=(0,5))

        self.total_games_locked_label = customtkinter.CTkLabel(self.stats_frame, text=f"Deployed:", font=("Arial", 16))
        self.total_games_locked_label.grid(row=4, column=0, padx=10, pady=(5,0))

        self.total_games_locked_value = customtkinter.CTkLabel(self.stats_frame, text=f"{self.total_games_locked} {'times' if self.total_games_locked != 1 else 'time'}", font=("Arial", 14))
        self.total_games_locked_value.grid(row=5, column=0, padx=10, pady=(0,5))

        
        # Agent Toggle 
        self.all_none_frame = customtkinter.CTkFrame(self.agent_tab, width=150, height=100)
        self.all_none_frame.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.toggle_agent_checkbox_frame = customtkinter.CTkFrame(self.agent_tab, width=150, height=100)
        self.toggle_agent_checkbox_frame.grid(row=1, column=0, pady=(20, 20))

        self.all_radio_button = customtkinter.CTkCheckBox(self.all_none_frame, text="All", command=lambda: self.toggle_agent("All"))
        self.all_radio_button.grid(row=0, column=0, padx=(20,0), pady=10)

        self.none_radio_button = customtkinter.CTkCheckBox(self.all_none_frame, text="None", command=lambda: self.toggle_agent("None"))
        self.none_radio_button.grid(row=0, column=1, pady=10)

        for index, agent in enumerate(self.unlockable_agents):
            column = index//5
            row = index%5
            self.create_agent_checkbox(agent, row, column)

        # Map Specific Tab 
        self.map_specific_agent_dropdown = []

        self.ascent_frame = customtkinter.CTkFrame(self.map_specific_tab, width=230)
        self.ascent_frame.grid(row=0, column=0, padx=7, pady=20, sticky="nsew")
        self.ascent_label = customtkinter.CTkLabel(self.ascent_frame, text="Ascent:", font=("Arial", 16))
        self.ascent_label.pack(padx=10, pady=5, side=tk.LEFT)

        self.ascent_agent_dropdown = customtkinter.CTkOptionMenu(self.ascent_frame, values=self.unlocked_agents, width=100,command=lambda x: self.change_map_specific_agent(x,"Ascent"))
        self.ascent_agent_dropdown.pack(padx=(0,10), pady=5, side=tk.RIGHT)
        
        self.map_specific_agent_dropdown.append(self.ascent_agent_dropdown)

        self.bind_frame = customtkinter.CTkFrame(self.map_specific_tab, width=230)
        self.bind_frame.grid(row=0, column=1, padx=7, pady=20, sticky="nsew")
        self.bind_label = customtkinter.CTkLabel(self.bind_frame, text="Bind:", font=("Arial", 16))
        self.bind_label.pack(padx=10, pady=5, side=tk.LEFT)

        self.bind_agent_dropdown = customtkinter.CTkOptionMenu(self.bind_frame, values=self.unlocked_agents, width=100,command=lambda x: self.change_map_specific_agent(x,"Bind"))
        self.bind_agent_dropdown.pack(padx=(0,10), pady=5, side=tk.RIGHT)

        self.map_specific_agent_dropdown.append(self.bind_agent_dropdown)

        self.breeze_frame = customtkinter.CTkFrame(self.map_specific_tab, width=230)
        self.breeze_frame.grid(row=0, column=2, padx=7, pady=20, sticky="nsew")
        self.breeze_label = customtkinter.CTkLabel(self.breeze_frame, text="Breeze:", font=("Arial", 16))
        self.breeze_label.pack(padx=10, pady=5, side=tk.LEFT)

        self.breeze_agent_dropdown = customtkinter.CTkOptionMenu(self.breeze_frame, values=self.unlocked_agents, width=100,command=lambda x: self.change_map_specific_agent(x,"Breeze"))
        self.breeze_agent_dropdown.pack(padx=(0,10), pady=5, side=tk.RIGHT)

        self.map_specific_agent_dropdown.append(self.breeze_agent_dropdown)

        self.fracture_frame = customtkinter.CTkFrame(self.map_specific_tab, width=230)
        self.fracture_frame.grid(row=1, column=0, padx=7, pady=20, sticky="nsew")
        self.fracture_label = customtkinter.CTkLabel(self.fracture_frame, text="Fracture:", font=("Arial", 16))
        self.fracture_label.pack(padx=10, pady=5, side=tk.LEFT)

        self.fracture_agent_dropdown = customtkinter.CTkOptionMenu(self.fracture_frame, values=self.unlocked_agents, width=100,command=lambda x: self.change_map_specific_agent(x,"Fracture"))
        self.fracture_agent_dropdown.pack(padx=(0,10), pady=5, side=tk.RIGHT)

        self.map_specific_agent_dropdown.append(self.fracture_agent_dropdown)

        self.haven_frame = customtkinter.CTkFrame(self.map_specific_tab, width=230)
        self.haven_frame.grid(row=1, column=1, padx=7, pady=20, sticky="nsew")
        self.haven_label = customtkinter.CTkLabel(self.haven_frame, text="Haven:", font=("Arial", 16))
        self.haven_label.pack(padx=10, pady=5, side=tk.LEFT)

        self.haven_agent_dropdown = customtkinter.CTkOptionMenu(self.haven_frame, values=self.unlocked_agents, width=100,command=lambda x: self.change_map_specific_agent(x,"Haven"))
        self.haven_agent_dropdown.pack(padx=(0,10), pady=5, side=tk.RIGHT)

        self.map_specific_agent_dropdown.append(self.haven_agent_dropdown)

        self.icebox_frame = customtkinter.CTkFrame(self.map_specific_tab, width=230)
        self.icebox_frame.grid(row=1, column=2, padx=7, pady=20, sticky="nsew")
        self.icebox_label = customtkinter.CTkLabel(self.icebox_frame, text="Icebox:", font=("Arial", 16))
        self.icebox_label.pack(padx=10, pady=5, side=tk.LEFT)

        self.icebox_agent_dropdown = customtkinter.CTkOptionMenu(self.icebox_frame, values=self.unlocked_agents, width=100,command=lambda x: self.change_map_specific_agent(x,"Icebox"))
        self.icebox_agent_dropdown.pack(padx=(0,10), pady=5, side=tk.RIGHT)

        self.map_specific_agent_dropdown.append(self.icebox_agent_dropdown)

        self.lotus_frame = customtkinter.CTkFrame(self.map_specific_tab, width=230)
        self.lotus_frame.grid(row=2, column=0, padx=7, pady=20, sticky="nsew")
        self.lotus_label = customtkinter.CTkLabel(self.lotus_frame, text="Lotus:", font=("Arial", 16))
        self.lotus_label.pack(padx=10, pady=5, side=tk.LEFT)

        self.lotus_agent_dropdown = customtkinter.CTkOptionMenu(self.lotus_frame, values=self.unlocked_agents, width=100,command=lambda x: self.change_map_specific_agent(x,"Lotus"))
        self.lotus_agent_dropdown.pack(padx=(0,10), pady=5, side=tk.RIGHT)

        self.map_specific_agent_dropdown.append(self.lotus_agent_dropdown)

        self.pearl_frame = customtkinter.CTkFrame(self.map_specific_tab, width=230)
        self.pearl_frame.grid(row=2, column=1, padx=7, pady=20, sticky="nsew")
        self.pearl_label = customtkinter.CTkLabel(self.pearl_frame, text="Pearl:", font=("Arial", 16))
        self.pearl_label.pack(padx=10, pady=5, side=tk.LEFT)

        self.pearl_agent_dropdown = customtkinter.CTkOptionMenu(self.pearl_frame, values=self.unlocked_agents, width=100,command=lambda x: self.change_map_specific_agent(x,"Pearl"))
        self.pearl_agent_dropdown.pack(padx=(0,10), pady=5, side=tk.RIGHT)

        self.map_specific_agent_dropdown.append(self.pearl_agent_dropdown)

        self.split_frame = customtkinter.CTkFrame(self.map_specific_tab, width=230)
        self.split_frame.grid(row=2, column=2, padx=7, pady=20, sticky="nsew")
        self.split_label = customtkinter.CTkLabel(self.split_frame, text="Split:", font=("Arial", 16))
        self.split_label.pack(padx=10, pady=5, side=tk.LEFT)

        self.split_agent_dropdown = customtkinter.CTkOptionMenu(self.split_frame, values=self.unlocked_agents, width=100,command=lambda x: self.change_map_specific_agent(x,"Split"))
        self.split_agent_dropdown.pack(padx=(0,10), pady=5, side=tk.RIGHT)

        self.map_specific_agent_dropdown.append(self.split_agent_dropdown)

        # Quit button
        self.quit_button = customtkinter.CTkButton(self.overview_tab, text="Exit", fg_color='#b52d3b', width=95, hover=False, command=self.exit)
        self.quit_button.place(relx=0.76, rely=0.9)
    

    # Updates all GUI elements
    def update_gui(self):
        try:
            self.update_overview_tab()
            self.update_agent_tab()
            self.update_map_tab()
        except AttributeError:
            pass


    # Updates overview tab
    def update_overview_tab(self):
        try:
            if len(self.average_time_to_lock[self.safe_mode_strength]) > 0:
                average_time_to_lock = round(sum(self.average_time_to_lock[self.safe_mode_strength])/len(self.average_time_to_lock[self.safe_mode_strength]), 2)
                self.average_time_to_lock_value.configure(text=f"{average_time_to_lock} ms")
            else:
                self.average_time_to_lock_value.configure(text="- ms")

            self.current_status_button.configure(text=f"{'Running' if self.active is True else 'Stopped'}", fg_color=f"{'#259969' if self.active is True else '#b52d3b'}")
            self.current_task_button.configure(text=f"{'None' if self.active is False else 'Locking' if self.in_valorant_menu is True else 'In Game'}")
            self.safe_mode_enabled_button.configure(text=f"{'On' if self.safe_mode is True else 'Off'}", fg_color=f"{'#259969' if self.safe_mode is True else '#b52d3b'}", width=int(f"{141 if self.safe_mode is False else 70}"))
            self.safe_mode_strength_button.configure(text=f"{'Low' if self.safe_mode_strength == 1 else 'Medium' if self.safe_mode_strength == 2 else 'High'}")

            self.select_map_specific_button.configure(text=f"{'Enabled' if self.map_specific_enabled is True else 'Disabled'}", fg_color=f"{'#259969' if self.map_specific_enabled is True else '#b52d3b'}")
            self.time_to_lock_label.configure(text=f"{self.time_to_lock} ms")
            self.total_games_locked_value.configure(text=f"{self.total_games_locked} {'times' if self.total_games_locked != 1 else 'time'}")

            if self.safe_mode == True:
                self.safe_mode_strength_button.pack(side=tk.LEFT, padx=0, pady=(0,5))
            else:
                self.safe_mode_strength_button.pack_forget()

            if self.map_specific_enabled == False:
                self.select_agent_dropdown.configure(state="normal")
                self.select_agent_dropdown.configure(values=self.unlocked_agents)
                self.select_agent_dropdown.set(f"{self.selected_agent}")
            else:
                self.select_agent_dropdown.configure(state="disabled")

        except AttributeError:
            pass


    # Updates map tab
    def update_agent_tab(self):
        try:
            for agent in self.unlockable_agents:
                if agent in self.unlocked_agents:
                    globals()[f'self.{agent}_checkbox'].select()
                else:
                    globals()[f'self.{agent}_checkbox'].deselect()
            
            if len(self.unlockable_agents) == len(self.unlocked_agents)-5:
                self.all_radio_button.select()
                self.all_radio_button.configure(state=tk.DISABLED)
            else:
                self.all_radio_button.deselect()
                self.all_radio_button.configure(state=tk.NORMAL)

            if len(self.unlocked_agents) == 5:
                self.none_radio_button.select()
                self.none_radio_button.configure(state=tk.DISABLED)
            else:
                self.none_radio_button.deselect()
                self.none_radio_button.configure(state=tk.NORMAL)
        except AttributeError:
            pass


    # Updates map tab
    def update_map_tab(self):
        try:
            for dropdown in self.map_specific_agent_dropdown:
                dropdown.configure(state=f"{'disabled' if self.map_specific_enabled == False else 'normal'}", values=self.unlocked_agents)

            self.ascent_agent_dropdown.set(f"{self.maps['Ascent']}")
            self.bind_agent_dropdown.set(f"{self.maps['Bind']}")
            self.breeze_agent_dropdown.set(f"{self.maps['Breeze']}")
            self.fracture_agent_dropdown.set(f"{self.maps['Fracture']}")
            self.haven_agent_dropdown.set(f"{self.maps['Haven']}")
            self.icebox_agent_dropdown.set(f"{self.maps['Icebox']}")
            self.lotus_agent_dropdown.set(f"{self.maps['Lotus']}")
            self.pearl_agent_dropdown.set(f"{self.maps['Pearl']}")
            self.split_agent_dropdown.set(f"{self.maps['Split']}")
            
        except AttributeError:
            pass


    # Updates GUI or Icon Image
    def update_icon(self):
        self.current_icon = self.tray_icons[0] if self.active is True else self.tray_icons[1]
        try:
            self.icon.icon = self.current_icon
        except AttributeError:
            pass

        if self.active is True:
            self.wm_iconbitmap("images/instalocker_enabled.ico")
        else:
            self.wm_iconbitmap("images/instalocker_disabled.ico")


    # Shows window when icon is clicked
    def show_window(self):
        try: self.icon.stop()
        except AttributeError: pass
        self.protocol('WM_DELETE_WINDOW', self.withdraw_window)
        self.after(0, self.deiconify)


    # Creates agent checkboxes
    def create_agent_checkbox(self, agent, column, row):
        globals()[f'self.{agent}_checkbox'] = customtkinter.CTkCheckBox(self.toggle_agent_checkbox_frame, text=agent, command=lambda: self.toggle_agent(agent))
        globals()[f'self.{agent}_checkbox'].grid(row=row, column=column, padx=10, pady=10)



    #---------------ICON---------------#

    # Shows icon when window is closed.
    def withdraw_window(self):
        self.withdraw()
        self.icon = pystray.Icon(
            "Valocker", self.current_icon, "Valocker", self.icon_menu)
        self.icon.run()



    #---------------TOGGLING SETTINGS---------------#

    # Toggles whether or not the program is active
    def change_active_status(self):
        self.active = not self.active
        self.update_icon()
        self.update_overview_tab()


    # Switches between locking and waiting
    def switch_mode(self):
        self.in_valorant_menu = not self.in_valorant_menu
        self.update_overview_tab()


    # Toggles safe mode
    def toggle_safe_mode(self):
        self.safe_mode = not self.safe_mode
        if self.safe_mode == False:
            self.safe_mode_strength = 0
        else:
            self.safe_mode_strength = self.safe_mode_strength_saved
        self.update_overview_tab()


    # Changes safe mode strength
    def change_safe_mode_strength(self):
        if self.safe_mode_strength < 3:
            self.safe_mode_strength += 1
        else:
            self.safe_mode_strength = 1
        self.safe_mode_strength_saved = self.safe_mode_strength
        self.update_overview_tab()


    # Toggles map specific agents
    def toggle_map_specific(self):
        self.map_specific_enabled = not self.map_specific_enabled

        with open(f'data/agents.json', 'r') as file:
            json_file = json.load(file)
            if self.map_specific_enabled == False:
                self.selected_agent = json_file["DEFAULT"]
            else:
                self.selected_agent = self.maps[self.selected_map]
        
        self.update_overview_tab()
        self.update_map_tab()



    #---------------AGENT SELECTION---------------#

    # Loads agents from json file
    def load_agents(self):
        with open(f'data/agents.json', 'r') as f:
            json_file = json.load(f)

            # Get list of all agents
            self.all_agents = [agent for agent in json_file["AGENTS"].keys()]
            # List of all coords to click on
            self.box_info = json_file["BOX_INFO"]
            

            # dict of all coords for boxes and lock button using for loop. the top right box is "TOPRIGHT_COORDS", there are "COLUMNS" columns, and there are a total amount of boxes as the len(self.all_agents)
            self.box_coords = {}
            for i in range(len(self.all_agents)):
                self.box_coords[f"Box{i}"] = (self.box_info["TOPLEFT"][0] + (i%self.box_info["COLUMNS"])*self.box_info["SIZE"] + (i%self.box_info["COLUMNS"])*self.box_info["XDIST"],
                                                self.box_info["TOPLEFT"][1] + (i//(self.box_info["COLUMNS"]+1))*self.box_info["YDIST"])

            # Dict of map specific agents
            self.maps = json_file["MAP_SPECIFIC"]
            # Get the first map in the dict
            self.selected_map = next(iter(self.maps))

            # Get default agents, these cannot be disabled
            default_agents = json_file["DEFAULT_AGENTS"]
            
            self.unlockable_agents = []
            for agent in self.all_agents:  # Adds rest of agent names to unlockable agents
                if agent not in default_agents:
                    self.unlockable_agents.append(agent)

            # Get list of available agents (With True/False)
            list_of_available_agents = json_file["AGENTS"]

            # Adds unlocked agents to self.unlocked_agents which shows only agents that can be selected
            self.unlocked_agents = []
            for agent in list_of_available_agents:
                if list_of_available_agents[agent] == True:
                    self.unlocked_agents.append(agent)
            self.unlocked_agents.sort()

            # Get default agent
            try:
                if self.map_specific_enabled == False:
                    self.selected_agent = json_file["DEFAULT"]
                    if self.selected_agent not in self.unlocked_agents:
                        self.selected_agent = self.unlocked_agents[0]
                else:
                    self.selected_agent = self.maps[self.selected_map]
                    if self.selected_agent not in self.unlocked_agents:
                        self.selected_agent = self.unlocked_agents[0]
            except KeyError:
                pass


    # Toggles the unlock status of agent in the json file
    def toggle_agent(self, agent):
        if agent != "All" and agent != "None":
            with open(f'data/agents.json', 'r') as file:
                json_file = json.load(file)
                json_file["AGENTS"][agent] = not json_file["AGENTS"][agent]

        elif agent == "All":
            with open(f'data/agents.json', 'r') as file:
                json_file = json.load(file)
                for agent in self.unlockable_agents:
                    if agent != 'None' and agent != 'All':
                        json_file["AGENTS"][agent] = True

        elif agent == "None":
            with open(f'data/agents.json', 'r') as file:
                json_file = json.load(file)
                for agent in self.unlockable_agents:
                    if agent != 'None' and agent != 'All':
                        json_file["AGENTS"][agent] = False

        with open(f'data/agents.json', 'w') as file:
            file.write(json.dumps(json_file, indent=4))

        self.load_agents()
        self.update_gui()


    # Updates default or map agent in json file
    def change_agent(self, agent):
        self.selected_agent = agent

        with open(f'data/agents.json', 'r') as file:
            json_file = json.load(file)

            if self.map_specific_enabled == True:
                json_file["MAP_SPECIFIC"][self.selected_map] = agent
                self.maps = json_file["MAP_SPECIFIC"]
            else:
                json_file["DEFAULT"] = agent

        with open(f'data/agents.json', 'w') as file:
            file.write(json.dumps(json_file, indent=4))

        self.update_overview_tab()


    # Updates map specific agents in json file from GUI
    def change_map_specific_agent(self, agent, map):
        with open(f'data/agents.json', 'r') as file:
            json_file = json.load(file)
            json_file["MAP_SPECIFIC"][map] = agent
            self.maps = json_file["MAP_SPECIFIC"]

        with open(f'data/agents.json', 'w') as file:
            file.write(json.dumps(json_file, indent=4))

        self.update_map_tab()



    #---------------AGENT LOCKING---------------#
    
    # Thread that runs in background, detecting map/running agent lock/clicking on agent
    def agent_lock(self):
        time.sleep(1)
        while self.active_thread == True:
            time.sleep(0.2)
            if self.in_valorant_menu == True and self.active == True and self.active_thread == True:
                if self.map_specific_enabled == True:
                    game_map = None

                    while game_map == None and self.active_thread == True and self.in_valorant_menu == True and self.active == True and self.map_specific_enabled == True:
                        time.sleep(0.1)
                        current_map = PIL.ImageGrab.grab(
                            bbox=(878, 437, 1047, 646)).tobytes()

                        game_map = self.maps_lookup.get(current_map)

                    if self.map_specific_enabled == True:
                        self.active_coords = self.get_coords_of_agent(
                            self.selected_agent)

                        agent_screen = self.locate_agent_select(True)

                else:
                    self.active_coords = self.get_coords_of_agent(
                        self.selected_agent)
                    agent_screen = self.locate_agent_select()

                if agent_screen == True:
                    start_lock = time.time()
                    self.lock_button = (self.box_info["LOCK_COORDS"][0]+random.randint(0,self.box_info["LOCK_SIZE"][0]), self.box_info["LOCK_COORDS"][1]+random.randint(0,self.box_info["LOCK_SIZE"][1]))

                    if self.safe_mode == False:
                        self.mouse.position = (
                            self.active_coords[0], self.active_coords[1])
                        time.sleep(0.01)
                        self.mouse.click(pynmouse.Button.left, 1)
                        time.sleep(0.06)
                        self.mouse.position = (
                            self.lock_button[0], self.lock_button[1])
                        time.sleep(0.01)
                        self.mouse.click(pynmouse.Button.left, 1)

                    else:
                        low_timing = self.safe_mode_timing[self.safe_mode_strength-1][0]/4
                        high_timing = self.safe_mode_timing[self.safe_mode_strength-1][1]/4

                        time.sleep(round(random.uniform(low_timing, high_timing), 2))
                        self.mouse.position = (
                            self.active_coords[0], self.active_coords[1])
                        time.sleep(round(random.uniform(low_timing, high_timing), 2))
                        self.mouse.click(pynmouse.Button.left, 1)
                        time.sleep(round(random.uniform(low_timing, high_timing), 2))
                        self.mouse.position = (
                            self.lock_button[0], self.lock_button[1])
                        time.sleep(round(random.uniform(low_timing, high_timing), 2))
                        self.mouse.click(pynmouse.Button.left, 1)


                    end_lock = time.time()

                    self.time_to_lock = round(((end_lock - start_lock)*1000), 2)
                    self.average_time_to_lock[self.safe_mode_strength].append(self.time_to_lock)

                    self.in_valorant_menu = False
                    self.total_games_locked += 1
                    self.update_overview_tab()
                    time.sleep(1)

            while self.active == True and self.active_thread == True and self.in_valorant_menu == False:
                time.sleep(1)
                menu_screen_1 = PIL.ImageGrab.grab(
                    bbox=(814, 243, 892, 244)).tobytes()
                menu_screen_2 = PIL.ImageGrab.grab(
                    bbox=(1330, 330, 1455, 353)).tobytes()
                if menu_screen_1 in self.in_menu_images or menu_screen_2 in self.in_menu_images:
                    self.in_valorant_menu = True
                    self.update_overview_tab()
                    try:
                        self.icon.update_menu()
                    except AttributeError: pass


    # Locates when in the agent select screen
    def locate_agent_select(self, using_specific_agent=False):
        while self.active_thread == True and self.in_valorant_menu == True and self.active == True and self.map_specific_enabled == using_specific_agent:
            agent_screen_yellow_section = PIL.ImageGrab.grab(
                bbox=(945, 866, 955, 867)).tobytes()
            if agent_screen_yellow_section == self.agent_select_image:
                return True
        return False


    # Returns box coords of agent based on agent name
    def get_coords_of_agent(self, agent):
        agent_index = self.unlocked_agents.index(agent)
        corner_coords = self.box_coords[f'Box{agent_index}']

        return (corner_coords[0]+random.randint(0, self.box_info["SIZE"]), corner_coords[1]+random.randint(0, self.box_info["SIZE"]))


# Runs when the program is started as a window
if __name__ == "__main__":
    p = Program()
    p.mainloop()