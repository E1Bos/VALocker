from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from VALocker import VALocker

import time
import threading
import random
from customtkinter import BooleanVar, IntVar

# Instalocker specific
import pynput.mouse as pynmouse
# import pynput.keyboard as pynkeyboard
import dxcam
import numpy as np

# Custom Imports
from CustomLogger import CustomLogger
from Constants import Region, LOCKING_CONFIG

class Instalocker:
    logger = CustomLogger("Instalocker").get_logger()

    # Parent
    parent: "VALocker"

    # Lock Confog
    locking_config: dict = dict()

    # Locking Variables
    lock_region: Region
    lock_button_location: tuple[int, int]

    # Wait Variables
    waiting_regions: list[Region]

    # States
    state: BooleanVar
    hover: BooleanVar
    agent_states: dict[str, list[BooleanVar]]
    safe_mode_enabled = BooleanVar
    safe_mode_strength = IntVar
    random_select: BooleanVar
    exclusiselect: BooleanVar
    map_specific: BooleanVar
    agent_index: IntVar
    box_coords: list = []

    # Timings
    fast_mode_timings: tuple[int, int, int]
    safe_mode_timings = list[tuple[int, int]]

    # Screen Recorder
    cam: dxcam.DXCamera

    # Controllers
    mouse: pynmouse.Controller = pynmouse.Controller()
    # keyboard: pynkeyboard.Controller = pynkeyboard.Controller()

    # Thread
    thread: Optional[threading.Thread] = None

    def __init__(self, parent: "VALocker") -> None:
        self.parent = parent
        self.file_manager = parent.file_manager

        # Instalocker state
        self.state = parent.instalocker_status

        # Unlock and random status of each agent
        self.agent_states = parent.agent_states

        # Timing settings (i.e. Safe Mode)
        self.fast_mode_timings = parent.fast_mode_timings
        
        self.safe_mode_enabled = parent.safe_mode_enabled
        self.safe_mode_strength = parent.safe_mode_strength
        self.safe_mode_timings = parent.safe_mode_timings

        # Additional options
        self.hover = parent.hover
        self.random_select = parent.random_select
        self.exclusiselect = parent.exclusiselect
        self.map_specific = parent.map_specific

        # Current Selected Agent
        self.agent_index = parent.agent_index
        
        # Screen Recorder
        self.cam = dxcam.create()
        
        # Threading
        self.stop_event = threading.Event()

    # region: Pre-Processing

    def set_locking_config(self, locking_config: LOCKING_CONFIG | str) -> None:
        self.locking_config = self.file_manager.get_config(locking_config)
        
        if type(locking_config) is LOCKING_CONFIG:
            config_name = locking_config.name
        else:
            config_name = self.locking_config.get('title')
        
        
        self.calculate_box_locations(self.parent.total_agents)
        self.load_config()
        
        self.logger.info(f"Locking config \"{config_name}\" loaded")

    def calculate_box_locations(self, total_agents: int) -> None:
        agent_buttons = self.locking_config["agentButtons"]

        for index in range(total_agents):
            x_position = (
                agent_buttons["start"][0]
                + (
                    (index % agent_buttons["columns"])
                    * (agent_buttons["size"] + agent_buttons["xDistance"])
                )
                + agent_buttons["size"] // 2
            )
            
            y_position = (
                agent_buttons["start"][1]
                + (
                    (index // agent_buttons["columns"])
                    * (agent_buttons["size"] + agent_buttons["yDistance"])
                )
                + agent_buttons["size"] // 2
            )
            self.box_coords.append((x_position, y_position))

    def load_config(self) -> None:

        # Lock Config
        lock_config = self.locking_config["lockRegion"]

        self.lock_region = Region(
            x=lock_config["xCoord"],
            y=lock_config["yCoord"],
            width=lock_config["width"],
            height=lock_config["height"],
            color=lock_config["color"],
        )

        # Wating Config
        self.waiting_regions = []
        for region in self.locking_config["waitingRegions"]:
            self.waiting_regions.append(
                Region(
                    x=region["xCoord"],
                    y=region["yCoord"],
                    width=region["width"],
                    height=region["height"],
                    color=region["color"],
                )
            )

        # Box Size
        self.box_size = self.locking_config["agentButtons"]["size"] // 2

        # Top left location
        lock_button_location = self.locking_config["lockButton"]["location"]
        self.lock_button_x = self.locking_config["lockButton"]["size"][0] // 2
        self.lock_button_y = self.locking_config["lockButton"]["size"][1] // 2

        # Center
        self.lock_button_center = (
            lock_button_location[0] + self.lock_button_x,
            lock_button_location[1] + self.lock_button_y,
        )

    # endregion

    def location_in_agent_button(self, center: tuple[int, int]) -> tuple[int, int]:
        """ """

        x = center[0] + random.randint(-(self.box_size - 5), (self.box_size - 5))
        y = center[1] + random.randint(-(self.box_size - 5), (self.box_size - 5))

        return x, y

    def location_in_lock_button(self) -> tuple[int, int]:
        """ """

        x = self.lock_button_center[0] + random.randint(
            -(self.lock_button_x - 5), (self.lock_button_x - 5)
        )
        y = self.lock_button_center[1] + random.randint(
            -(self.lock_button_y - 5), (self.lock_button_y - 5)
        )

        return x, y

    def frame_matches(self, frame, region: Region) -> bool:
        if frame is None:
            return False

        area = np.array(frame[region.y : region.y_end, region.x : region.x_end])

        return np.all(np.all(area == region.color, axis=2))

    def calculate_random_agent(self) -> int:
        unlocked_agents = []
        random_agents = []
        
        for agent, values in self.agent_states.items():
            if len(values) == 1:
                unlocked_agents.append(agent)
                
                if values[0].get():
                    random_agents.append(agent)
            
                continue
            
            if values[0].get():
                unlocked_agents.append(agent)
                
                if values[1].get():
                    random_agents.append(agent)
        
        if len(random_agents) == 0:
            self.logger.error("No random agents selected but random agent mode enabled")
            raise ValueError("No random agents selected but random agent mode enabled")
        
        selected_agent = random.choice(random_agents)
        
        if self.exclusiselect.get():
            agent_state = self.agent_states[selected_agent]
            if len(agent_state) == 1:
                agent_state[0].set(False)
            else:
                agent_state[1].set(False)
            
            if len(random_agents) == 1:
                self.logger.info(f"ExclusiSelect selected final agent, disabling exclusiselect")
                self.exclusiselect.set(False)
        
        self.parent.exclusiselect_update_gui()
        
        return unlocked_agents.index(selected_agent)

    def get_latest_frame(self) -> np.ndarray:
        try:
            return self.cam.get_latest_frame()
        except Exception as e:
            self.logger.error(f"Error getting frame: {e}")
            return None

    # region: Threading

    def main(self):
        self.cam.start(target_fps=144)
        self.logger.info("Thread started")
        while not self.stopped():
            if self.state.get():
                self.locking()
            else:
                self.waiting()
        self.cam.stop()
        self.logger.info("Thread stopped")

    def locking(self) -> None:
        while not self.stopped() and self.state.get():
            frame = self.get_latest_frame()
            if self.frame_matches(frame, self.lock_region):
                start = time.time()

                if self.random_select.get():
                    agent_index = self.calculate_random_agent()
                else:
                    agent_index = self.agent_index.get()

                self.lock_agent(agent_index)
                self.toggle_state(False)

                end = time.time()

                self.logger.info(f"Locked in {(end-start)*1000:.2f}ms")
                return

    def waiting(self) -> None:
        while not self.stopped() and not self.state.get():
            print("Waiting")
            frame = self.get_latest_frame()
            for region in self.waiting_regions:
                if self.frame_matches(frame, region):
                    self.toggle_state(True)
                    self.logger.info(f"Matched waiting region:\n{region}")
                    return
            self.stop_event.wait(3)

    def lock_agent(self, agent_index: int) -> None:
        # Sets timings based on safe mode
        if self.safe_mode_enabled.get():
            timing = self.safe_mode_timings[self.safe_mode_strength.get()]
            min_timing, max_timing = timing[0] / 4, timing[1] / 4
            timings = [random.uniform(min_timing, max_timing) for _ in range(4)]
            self.stop_event.wait(timings[-1])
        else:
            timings = self.fast_mode_timings

        self.mouse.position = self.location_in_agent_button(
            self.box_coords[agent_index]
        )
        self.stop_event.wait(timings[0])
        self.mouse.click(pynmouse.Button.left, 1)
        self.stop_event.wait(timings[1])
        self.mouse.position = self.location_in_lock_button()
        self.stop_event.wait(timings[2])
        self.mouse.click(pynmouse.Button.left, 1)

    def toggle_state(self, value: Optional[bool] = None):
        if value is None:
            value = not self.state.get()
        self.state.set(value)

    def start(self):
        # Start thread
        self.stop_event.clear()
        self.thread = threading.Thread(target=self.main, daemon=True)
        self.thread.start()

    def stop(self):
        # Ensure thread exists
        if self.thread is None:
            self.logger.info("Thread not started")
            return
        
        if threading.current_thread() is self.thread:
            self.logger.info("Cannot stop from within the thread itself")
            return
            
        # Stop thread
        self.stop_event.set()
        
    def stopped(self):
        return self.stop_event.is_set()

    # endregion


if __name__ == "__main__":
    from VALocker import VALocker

    main = VALocker()
    main.mainloop()
