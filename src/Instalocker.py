from typing import TYPE_CHECKING, Optional

import mss.windows

if TYPE_CHECKING:
    from VALocker import VALocker

from time import time
from random import randint, choice, uniform
import threading
from traceback import format_exc
from customtkinter import BooleanVar, IntVar

# Instalocker specific
import pynput.mouse as pynmouse

# import pynput.keyboard as pynkeyboard
import mss
import numpy as np

# Custom Imports
from CustomLogger import CustomLogger
from Constants import Region, LOCKING_CONFIG, ROLE, AgentIndex, AgentGrid

# from GUIFrames import ErrorPopup


class Instalocker:
    """
    Responsible for instalocking agents
    @author: [E1Bos](https://www.github.com/E1Bos)
    """

    logger: CustomLogger = CustomLogger.get_instance().get_logger("Instalocker")

    # Parent
    parent: "VALocker"

    # Lock Config
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
    agent_index: AgentIndex
    agent_grid: AgentGrid
    role_coords: dict[ROLE] = {}
    agent_coords: list = []

    # Timings
    fast_mode_timings: tuple[int, int, int]
    safe_mode_timings = list[tuple[int, int]]

    # Screen Recorder
    cam: mss.windows.MSS

    # Controllers
    mouse: pynmouse.Controller = pynmouse.Controller()
    # keyboard: pynkeyboard.Controller = pynkeyboard.Controller()

    # Thread
    thread: Optional[threading.Thread] = None

    def __init__(self, parent: "VALocker") -> None:
        self.parent = parent
        self.file_manager = parent.file_manager

        # Instalocker state
        self.running = parent.instalocker_thread_running
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

        # Agent Grid
        self.agent_grid = parent.agent_grid

        # Threading
        self.stop_event = threading.Event()

    # region: Pre-Processing

    def set_locking_config(self, locking_config: LOCKING_CONFIG | str) -> None:
        self.locking_config = self.file_manager.get_config(locking_config)

        if type(locking_config) is LOCKING_CONFIG:
            config_name = locking_config.name
        else:
            config_name = self.locking_config.get("title")

        self.calculate_box_locations()
        self.load_config()
        self.parent.set_locking_agent()

        self.logger.info(f'Locking config "{config_name}" loaded')

    def calculate_box_locations(self) -> None:
        """
        Calculates the locations of the role and agent buttons based on the locking config
        """

        role_buttons = self.locking_config["roleButtons"]
        roles_order = [
            ROLE.DEFAULT,
            ROLE.INITIATOR,
            ROLE.DUELIST,
            ROLE.SENTINEL,
            ROLE.CONTROLLER,
        ]

        self.role_coords.clear()
        for index, role in enumerate(roles_order):
            x_position = role_buttons["location"][0] + (
                index * (role_buttons["size"][0] + role_buttons["spacing"][0])
            )

            self.role_coords[role] = (x_position, role_buttons["location"][1])

        agent_buttons = self.locking_config["agentButtons"]

        self.agent_grid.set_grid(agent_buttons["grid"][0], agent_buttons["grid"][1])

        for index in range(self.agent_grid.columns * self.agent_grid.rows):
            x_position = agent_buttons["location"][0] + (
                (index % self.agent_grid.columns)
                * (agent_buttons["size"][0] + agent_buttons["spacing"][0])
            )

            y_position = agent_buttons["location"][1] + (
                (index // self.agent_grid.columns)
                * (agent_buttons["size"][1] + agent_buttons["spacing"][1])
            )

            self.agent_coords.append((x_position, y_position))

    def load_config(self) -> None:

        # Lock Config
        lock_config = self.locking_config["lockRegion"]

        self.lock_region = Region(
            location=lock_config["location"],
            size=lock_config["size"],
            color=lock_config["color"],
        )

        # Waiting Config
        self.waiting_regions = []
        if self.locking_config["waitingRegions"] is not None:
            for region in self.locking_config["waitingRegions"]:
                self.waiting_regions.append(
                    Region(
                        location=region["location"],
                        size=region["size"],
                        color=region["color"],
                    )
                )

        # Box Size
        self.role_box_size = self.locking_config["roleButtons"]["size"]
        self.agent_box_size = self.locking_config["agentButtons"]["size"]

        # Lock button sizes
        self.lock_button_location = self.locking_config["lockButton"]["location"]
        self.lock_button_size = (
            self.locking_config["lockButton"]["size"][0],
            self.locking_config["lockButton"]["size"][1],
        )

    # endregion

    def location_in_role_button(self, agent_index: AgentIndex) -> tuple[int, int]:
        role = agent_index.role

        x = self.role_coords[role][0] + randint(5, (self.role_box_size[0] - 5))
        y = self.role_coords[role][1] + randint(5, (self.role_box_size[1] - 5))

        return (x, y)

    def location_in_agent_button(self, agent_index: AgentIndex) -> tuple[int, int]:
        top_left = self.agent_coords[agent_index.index]

        x = top_left[0] + randint(5, (self.agent_box_size[0] - 5))
        y = top_left[1] + randint(5, (self.agent_box_size[1] - 5))

        return (x, y)

    def location_in_lock_button(self) -> tuple[int, int]:
        x = self.lock_button_location[0] + randint(5, (self.lock_button_size[0] - 5))
        y = self.lock_button_location[1] + randint(5, (self.lock_button_size[1] - 5))

        return x, y

    def frame_matches(self, area: np.array, region: Region) -> bool:
        if area is None:
            return False

        # Compare the screenshot array with the target RGB value
        return np.all(np.all(area == region.color, axis=2))

    def calculate_random_agent(self) -> tuple[ROLE, int]:
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

        selected_agent = choice(random_agents)

        if self.exclusiselect.get():
            agent_state = self.agent_states[selected_agent]
            if len(agent_state) == 1:
                agent_state[0].set(False)
            else:
                agent_state[1].set(False)

            if len(random_agents) == 1:
                self.logger.info(
                    f"ExclusiSelect selected final agent, disabling exclusiselect"
                )
                self.exclusiselect.set(False)

        self.parent.exclusiselect_update_gui()

        role, index = self.parent.get_agent_role_and_index(selected_agent)

        return AgentIndex(role, index)

    def get_latest_frame(self, region: Region) -> np.ndarray:
        try:
            # Get the frame from the camera
            frame = np.array(self.cam.grab(region.as_tuple))

            # Convert the frame from BGRA to RGB
            rgb_frame = frame[:, :, :3]
            rgb_frame = np.flip(rgb_frame, axis=2)

            return rgb_frame
        except Exception as e:
            self.logger.error(f"Error getting frame: {e}")
            return None

    # region: Threading

    def main(self):
        try:
            self.logger.info("Thread started")
            self.cam = mss.mss()
            while not self.stopped():
                if self.state.get():
                    self.locking()
                else:
                    self.waiting()
        except OSError:
            self.logger.error(f"Error in thread: {format_exc()}")
            self.running.set(False)
            self.stop_event.set()
        finally:
            self.logger.info("Thread stopped")

    def locking(self) -> None:
        start_time = time()
        while not self.stopped() and self.state.get():
            frame = self.get_latest_frame(self.lock_region)
            if self.frame_matches(frame, self.lock_region):
                break

        if self.stopped():
            return

        agent_index = self.calculate_random_agent() if self.random_select.get() else self.agent_index

        self.lock_agent(agent_index)

        end_time = time()
        self.parent.add_stat(end_time - start_time)

        self.toggle_state(False)

        locking_time_ms = (end_time - start_time) * 1000
        self.logger.info(
            f"Locked agent in {locking_time_ms:.2f}ms\n"
            f"Role: {self.agent_index.role} | Index: {self.agent_index.index}\n"
            f"Safe Mode: {self.safe_mode_enabled.get()} | Strength: {self.safe_mode_strength.get()}\n"
            f"Random Select: {self.random_select.get()}"
        )

    def waiting(self) -> None:
        regions = iter(self.waiting_regions)
        while not self.stopped() and not self.state.get():
            try:
                region = next(regions)
            except StopIteration:
                regions = iter(self.waiting_regions)
                region = next(regions)

            frame = self.get_latest_frame(region)
            if self.frame_matches(frame, region):
                self.toggle_state(True)
                self.logger.info(f"Matched waiting region:\n{region}")
                return

            self.stop_event.wait(1.5)

    def lock_agent(self, agent_index: AgentIndex) -> None:
        # Sets timings based on safe mode
        if self.safe_mode_enabled.get():
            timing = self.safe_mode_timings[self.safe_mode_strength.get()]
            min_timing, max_timing = timing[0] / 6, timing[1] / 6
            timings = [uniform(min_timing, max_timing) for _ in range(6)]
            self.stop_event.wait(timings[-1])
        else:
            timings = self.fast_mode_timings

        # Select correct role
        if agent_index.role != ROLE.DEFAULT:
            self.mouse.position = self.location_in_role_button(agent_index)
            self.stop_event.wait(timings[0])
            self.mouse.click(pynmouse.Button.left, 1)
            self.stop_event.wait(timings[1])

        # Select correct agent
        self.mouse.position = self.location_in_agent_button(agent_index)
        self.stop_event.wait(timings[2])
        self.mouse.click(pynmouse.Button.left, 1)
        self.stop_event.wait(timings[3])

        # Lock in
        if not self.hover.get():
            self.mouse.position = self.location_in_lock_button()
            self.stop_event.wait(timings[4])
            self.mouse.click(pynmouse.Button.left, 1)

    def toggle_state(self, value: Optional[bool] = None) -> None:
        """
        Set the state of the instalocker.

        Args:
            value (bool, optional): The state to set the instalocker to. If None, the state will be toggled.
        """
        if value is None:
            value = not self.state.get()
        self.state.set(value)

    def start(self) -> None:
        """
        Starts the instalocker thread.

        This method starts the instalocker thread if it is not already running.
        It sets the `stop_event` to False and starts the thread.
        """
        self.stop_event.clear()
        self.thread = threading.Thread(target=self.main, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        """
        Stops the instalocker thread.

        If the thread is not running, this method will log a message and return.
        If the method is called from within the thread itself, this method will log a message and return.
        Otherwise, this method will set the `stop_event` to True, which will cause the thread to stop.
        """
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
