from customtkinter import BooleanVar, IntVar
from CustomLogger import CustomLogger
import time
import threading


class Instalocker:
    def __init__(self) -> None:
        self.logger = CustomLogger("Instalocker").get_logger()

        self.stop_flag = False

        self.in_locking_state = BooleanVar(value=True)
        self.hover = BooleanVar(value=False)
        self.random_select = BooleanVar(value=False)
        self.exclusiselect = BooleanVar(value=False)
        self.map_specific = BooleanVar(value=False)
        self.agent_index = IntVar(value=0)

        self.box_coords = list()

    # region: Toggles

    def toggle_locking(self):
        self.in_locking_state.set(not self.in_locking_state.get())

    def toggle_hover(self):
        self.hover.set(not self.hover.get())

    def toggle_random_select(self):
        self.random_select.set(not self.random_select.get())

    def toggle_map_specific(self):
        self.map_specific.set(not self.map_specific.get())

    def toggle_exclusiselect(self):
        self.exclusiselect.set(not self.exclusiselect.get())

    # endregion

    # region: Setters

    def set_agent_index(self, index: int):
        self.agent_index.set(index)
        self.logger.info(f"Agent index set to {index}")

    def set_box_coords(self, coords: list):
        self.box_coords = coords

    # endregion

    # region: Getters

    def get_locking(self):
        return self.in_locking_state.get()

    def get_hover(self):
        return self.hover.get()

    def get_random_select(self):
        return self.random_select.get()

    def get_map_specific(self):
        return self.map_specific.get()

    def get_exclusiselect(self):
        return self.exclusiselect.get()

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
