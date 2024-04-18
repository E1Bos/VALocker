import time
import threading

# Custom Imports
from CustomLogger import CustomLogger


class Instalocker():
    def __init__(self) -> None:
        self.logger = CustomLogger("Instalocker").get_logger()

        self.stop_flag = False

        self.in_locking_state = True
        self.hover = False
        self.random_select = False
        self.exclusiselect = False
        self.map_specific = False
        self.agent_index = 0

        self.box_coords = list()

    # region: Toggles

    def toggle_locking(self):
        self.in_locking_state = not self.in_locking_state

    def toggle_hover(self):
        self.hover = not self.hover

    def toggle_random_select(self):
        self.random_select = not self.random_select

    def toggle_map_specific(self):
        self.map_specific = not self.map_specific

    def toggle_exclusiselect(self):
        self.exclusiselect = not self.exclusiselect

    # endregion

    # region: Setters

    def set_agent_index(self, index: int):
        self.agent_index = index
        self.logger.info(f"Agent index set to {index}")

    def set_box_coords(self, coords: list):
        self.box_coords = coords

    # endregion

    # region: Getters

    def get_locking(self):
        return self.in_locking_state

    def get_hover(self):
        return self.hover

    def get_random_select(self):
        return self.random_select

    def get_map_specific(self):
        return self.map_specific

    def get_exclusiselect(self):
        return self.exclusiselect

    # endregion

    # region: Threading

    def main(self):
        while not self.stop_flag:
            time.sleep(1)
            # TODO: Implement logic

    def locking(self):
        while not self.stop_flag:
            time.sleep(1)
            # TODO: Implement locking

    def waiting(self):
        while not self.stop_flag:
            time.sleep(1)
            # TODO: Implement waiting

    def start(self):
        self.stop_flag = False
        self.logger.info("Thread started")
        self.thread = threading.Thread(target=self.main, daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_flag = True
        self.logger.info("Thread stopped")

    # endregion
