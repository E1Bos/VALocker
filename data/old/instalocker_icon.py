import json, threading, time, pystray
import pynput.mouse as pynmouse
import PIL.Image, PIL.ImageGrab
import time



class Program:
    def __init__(self):
        # Default values
        self.name = "VaLocker"

        with open('data/config.json', 'r') as f:
            config = json.load(f)
            self.display_scale = config["DISPLAY_SCALE"] # Scale of the display (1.25 for 125%, 1.0 for 100% etc.)
            self.show_notifications = config["NOTIFICATIONS"] # Show notifications or not
        
        self.map_specific_enabled = False # Map Specific Agents Enabled by Default
        self.active = True # Instalocker Active
        self.active_coords = None # Coords of Agent
        self.lock_button = None # Coords of Lock Button
        self.selected_agent = None # Selected Agent
        self.active_thread = True # Thread Active
        self.in_valorant_menu = True # In Valorant Menu
        self.mouse = pynmouse.Controller()

        # Load all agents
        self.load_agents()

        # Load icons
        self.tray_icons = (PIL.Image.open("images/instalocker_enabled.ico"), PIL.Image.open("images/instalocker_disabled.ico"))

        # Load the general images to be searched
        self.agent_select_images = [
        PIL.Image.open('images/agent_screen/agent_screen_y_0.png').tobytes(),
        PIL.Image.open('images/agent_screen/agent_screen_y_1.png').tobytes(),
        ]

        self.in_menu_images = [PIL.Image.open('images/in_menu/in_menu_1.png').tobytes(),
        PIL.Image.open('images/in_menu/in_menu_2.png').tobytes()]

        # Load the map specific images to be searched
        maps_list = ['Ascent', 'Bind', 'Breeze', 'Fracture', 'Haven', 'Icebox', 'Lotus', 'Pearl', 'Split']
        self.maps_lookup = {}
        for map_name in maps_list:
            binary_of_map = PIL.Image.open(f"images/map_images/{map_name}.png").tobytes()
            self.maps_lookup[binary_of_map] = map_name

    # Closes the program
    def exit(self):
        self.active_thread = False
        self.icon.stop()


    # Get the coords of the agent based on the agent name, and using the box coords for that agent
    def get_coords_of_agent(self, agent):
        agent_index = self.unlocked_agents.index(agent)
        return self.box_coords[f'Box{agent_index}']


    # Load agents.json into the program 
    def load_agents(self):
        with open(f'data/agents.json', 'r') as f:
            json_file = json.load(f)

            # Get list of all agents
            self.all_agents = [agent for agent in json_file["AGENTS"].keys()] # List of all agent names
            self.box_coords = json_file["BOX_COORDS"] # List of all coords to click on
            self.lock_button = self.box_coords["lock_button"] # Coords of lock button
            self.maps = json_file["MAP_SPECIFIC"] # Dict of map specific agents
            self.selected_map = next(iter(self.maps)) # Get the first map in the dict
            
            default_agents = json_file["DEFAULT_AGENTS"] # Get default agents, these cannot be disabled
            self.unlockable_agents = ["All", "None"] # Adds "All" and "None" to the list of unlockable agents
            for agent in self.all_agents: # Adds rest of agent names to unlockable agents
                if agent not in default_agents:
                    self.unlockable_agents.append(agent)

            list_of_available_agents = json_file["AGENTS"] # Get list of available agents (With True/False)
            
            self.unlocked_agents = [] # Adds unlocked agents to self.unlocked_agents which shows only agents that can be selected
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
                    self.active_coords = self.get_coords_of_agent(self.selected_agent)
                else:
                    self.selected_agent = self.maps[self.selected_map]
                    if self.selected_agent not in self.unlocked_agents:
                        self.selected_agent = self.unlocked_agents[0]
            except KeyError: pass


    # Change self.active from True to False and vice versa
    def change_active_status(self):
        self.active = not self.active
        self.change_icon()


    # Change the taskbar icon depending on self.active
    def change_icon(self):
        if self.active == True:
            self.icon.icon = self.tray_icons[0]
        else:
            self.icon.icon = self.tray_icons[1]


    # Change the default agent in data/agents.json and self.active_coords
    def change_agent(self, agent):
        self.selected_agent = agent

        with open(f'data/agents.json', 'r') as file:
            json_file = json.load(file)
            
            if self.map_specific_enabled == True:
                json_file["MAP_SPECIFIC"][self.selected_map] = agent
                self.maps = json_file["MAP_SPECIFIC"]
            else:
                json_file["DEFAULT"] = agent
                self.active_coords = self.get_coords_of_agent(agent)

        with open(f'data/agents.json', 'w') as file:
            file.write(json.dumps(json_file, indent=4))


    # Change the map for map specific agents (and select the previously selected agent for that map)
    def change_map(self, map):
        try:
            self.selected_map = map
            self.selected_agent = self.maps[self.selected_map]
        except KeyError:
            pass


    # Enable map specific agents
    def toggle_map_specific(self):
        self.map_specific_enabled = not self.map_specific_enabled

        with open(f'data/agents.json', 'r') as file:
            json_file = json.load(file)
            if self.map_specific_enabled == False:
                self.selected_agent = json_file["DEFAULT"]
            else:
                self.selected_agent = self.maps[self.selected_map]


    # Toggle the unlocked/locked status of an agent
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


    def send_notification(self, message):
        if self.active == True and self.show_notifications == True:
            self.icon.notify(message, title=self.name)


    def switch_mode(self):
        self.in_valorant_menu = not self.in_valorant_menu


    # Create "select agent" icons
    def create_menu_item(self, agent, hide=True):
        if agent in self.all_agents or agent == 'None' or agent == 'All': 
            if hide == True: # For selecting unlocked agents
                item = pystray.MenuItem(
                    agent, 
                    lambda x: self.change_agent(agent), 
                    checked=lambda x: self.selected_agent == agent, 
                    visible=lambda x: (agent in self.unlocked_agents)
                )
            else:
                if agent != 'None' and agent != 'All':
                    item = pystray.MenuItem(
                        agent, 
                        lambda x: self.toggle_agent(agent), 
                        checked=lambda x: agent in self.unlocked_agents, 
                        visible=lambda x: (agent in self.unlockable_agents),
                        radio=True
                    )
                elif agent == 'All':
                    item = pystray.MenuItem(
                        agent, 
                        lambda x: self.toggle_agent(agent), 
                        checked= lambda x: len(self.unlockable_agents[3:]) == len(self.unlocked_agents)-6, 
                        visible=True,
                        radio=False
                    )
                elif agent == 'None':
                    item = pystray.MenuItem(
                        agent, 
                        lambda x: self.toggle_agent(agent), 
                        checked=lambda x: len(self.unlocked_agents) == 5, 
                        visible=True,
                        radio=False
                    )
        else: # For selecting map
            item = pystray.MenuItem(
                    lambda x: f"{agent}\t{self.maps[agent]}", 
                    lambda x: self.change_map(agent.split('\t')[0]), 
                    checked=lambda x: self.selected_map == agent, 
                    visible=lambda x: self.map_specific_enabled == True,
                    radio=True
                )
        return item


    # Figures out when you're in the agent select screen
    def locate_agent_select(self, using_specific_agent=False):
        self.send_notification("Looking for agent select screen")
        while self.active_thread == True and self.in_valorant_menu == True and self.active == True and self.map_specific_enabled == using_specific_agent:
            agent_screen_yellow_section = PIL.ImageGrab.grab(bbox=(959,867,960,868)).tobytes()
            if agent_screen_yellow_section in self.agent_select_images:
                return True
        return False
                

    # Thread to run the agent locker
    def agent_lock(self):
        time.sleep(1)

        while self.active_thread == True:
            if self.in_valorant_menu == True and self.active == True and self.active_thread == True:
                self.icon.update_menu()
                if self.map_specific_enabled == True:
                    game_map = None

                    self.send_notification("Looking for map")

                    while game_map == None and self.active_thread == True and self.in_valorant_menu == True and self.active == True and self.map_specific_enabled == True:
                        current_map = PIL.ImageGrab.grab(bbox=(878, 437, 1047, 646)).tobytes()
                    
                        game_map = self.maps_lookup.get(current_map)

                if self.map_specific_enabled == True:
                    self.change_map(game_map)
                    self.active_coords = self.get_coords_of_agent(self.selected_agent)

                    self.send_notification(f"Loaded into {self.selected_map}, switched to {self.selected_agent}")
                    
                    agent_screen = self.locate_agent_select(True)

                else:
                    self.active_coords = self.get_coords_of_agent(self.selected_agent)
                    agent_screen = self.locate_agent_select()
                
                if agent_screen == True:
                    start_lock = time.time()

                    self.mouse.position = (self.active_coords[0]/self.display_scale, self.active_coords[1]/self.display_scale)
                    time.sleep(0.01)
                    self.mouse.click(pynmouse.Button.left, 1)
                    time.sleep(0.06)
                    self.mouse.position = (self.lock_button[0]/self.display_scale, self.lock_button[1]/self.display_scale)
                    time.sleep(0.01)
                    self.mouse.click(pynmouse.Button.left, 1)

                    end_lock = time.time()
                    self.send_notification(f'{self.selected_agent} was locked in {(end_lock - start_lock)* 1000:.2f} ms')

                    self.in_valorant_menu = not self.in_valorant_menu

            while self.active == True and self.active_thread == True and self.in_valorant_menu == False:
                time.sleep(1)           
                menu_screen_1 = PIL.ImageGrab.grab(bbox=(814, 243, 892, 244)).tobytes()
                menu_screen_2 = PIL.ImageGrab.grab(bbox=(1330, 330, 1455, 353)).tobytes()
                if menu_screen_1 in self.in_menu_images or menu_screen_2 in self.in_menu_images:
                    self.in_valorant_menu = not self.in_valorant_menu
                    self.icon.update_menu()


    # Start the task icon                
    def start(self):
        
        self.agent_thread = threading.Thread(target=self.agent_lock).start()
        
        menu = pystray.Menu(
            pystray.MenuItem(
                lambda x: f'Status: {"Enabled" if self.active else "Disabled"}', 
                lambda x: self.change_active_status(), checked = lambda x: self.active, 
                default=True
            ),
            pystray.MenuItem(lambda x: f"Status: {'None' if self.active is False else 'Locking' if self.in_valorant_menu is True else 'In Game (Waiting)'}", lambda x: self.switch_mode()),
            pystray.MenuItem(lambda x: f"Agent: {self.selected_agent}", pystray.Menu(*[self.create_menu_item(agent) for agent in self.all_agents])),
            pystray.MenuItem(lambda x: f"Map: {self.selected_map}", pystray.Menu(*[self.create_menu_item(agent, False) for agent in self.maps]), visible= lambda x: self.map_specific_enabled),
            pystray.MenuItem(lambda x: f"Enable/Disable Agents", pystray.Menu(*[self.create_menu_item(agent, False) for agent in self.unlockable_agents])),
            pystray.MenuItem(lambda x: f"{'Enable' if self.map_specific_enabled == False else 'Disable'} Map Specific Agents", self.toggle_map_specific),
            pystray.MenuItem("Exit", lambda x: self.exit())
        )

        self.icon = pystray.Icon("Valocker", self.tray_icons[0], "Valocker", menu)
        self.icon.run()


# Runs when the program is started as a window
if __name__ == "__main__":
    p = Program()
    p.start()