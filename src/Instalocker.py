from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from VALocker import VALocker

import time
import threading
import random
from customtkinter import BooleanVar, IntVar


# Instalocker specific
import pynput.mouse as pynmouse
import pynput.keyboard as pynkeyboard
import dxcam

# Custom Imports
from CustomLogger import CustomLogger


class Instalocker:
    logger = CustomLogger("Instalocker").get_logger()

    stop_flag = False

    # Lock Confog
    locking_config: dict

    # Locking Variables
    lock_region: tuple[int, int, int, int]
    lock_colors: tuple[int, int, int]
    lock_button_location: tuple[int, int]

    state: BooleanVar
    hover: BooleanVar
    random_select: BooleanVar
    exclusiselect: BooleanVar
    map_specific: BooleanVar
    agent_index: IntVar
    box_coords: list = []

    cam: dxcam.DXCamera

    mouse: pynmouse.Controller = pynmouse.Controller()
    keyboard: pynkeyboard.Controller = pynkeyboard.Controller()

    def __init__(self, parent: "VALocker") -> None:
        self.locking_config = parent.locking_config

        self.state = parent.instalocker_status
        self.hover = parent.hover
        self.random_select = parent.random_select
        self.exclusiselect = parent.exclusiselect
        self.map_specific = parent.map_specific
        self.agent_index = parent.agent_index

        self.cam = dxcam.create(output_color="RGB")

        self.calculate_box_locations(parent.total_agents)
        self.calculate_lock_variables()

    # region: Pre-Processing

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

        self.logger.info("Locking box locations calculated")

    def calculate_lock_variables(self) -> None:
        lock_location = self.locking_config["lockLocation"]

        self.lock_region = lock_location[0]
        self.lock_colors = lock_location[1]

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

    # region: Threading

    def main(self):
        while not self.stop_flag:
            if self.state.get():
                self.locking()
            else:
                self.waiting()

    def locking(self):
        self.cam.start(region=self.lock_region)
        while not self.stop_flag and self.state.get():
            next_frame = self.cam.get_latest_frame()

            next_frame = list(next_frame[0][0])

            if next_frame == self.lock_colors:
                start = time.time()

                self.lock_agent(self.agent_index.get())
                self.toggle_state()

                end = time.time()

                self.logger.info(f"Locked in {(end-start)*1000:.2f}ms")
                return

    def waiting(self):
        while not self.stop_flag and not self.state.get():
            print("waiting")
            time.sleep(1)

    def lock_agent(self, agent_index: int):
        self.mouse.position = self.location_in_agent_button(
            self.box_coords[agent_index]
        )
        time.sleep(0.02)
        self.mouse.click(pynmouse.Button.left, 1)
        time.sleep(0.02)
        self.mouse.position = self.location_in_lock_button()
        time.sleep(0.02)
        self.mouse.click(pynmouse.Button.left, 1)

    def toggle_state(self):
        self.state.set(not self.state.get())

    def start(self):
        self.stop_flag = False
        self.logger.info("Thread started")
        self.thread = threading.Thread(target=self.main, daemon=True)
        self.thread.start()

    def stop(self):
        self.cam.stop()
        self.stop_flag = True
        self.logger.info("Thread stopped")

    # endregion


if __name__ == "__main__":
    from VALocker import VALocker

    main = VALocker()
    main.mainloop()
