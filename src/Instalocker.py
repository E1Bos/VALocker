import time
import threading
from typing import TYPE_CHECKING

from customtkinter import BooleanVar, IntVar

if TYPE_CHECKING:
    from VALocker import VALocker

# Custom Imports
from CustomLogger import CustomLogger


class Instalocker:
    logger = CustomLogger("Instalocker").get_logger()

    stop_flag = False

    state: BooleanVar
    hover: BooleanVar
    random_select: BooleanVar
    exclusiselect: BooleanVar
    map_specific: BooleanVar
    agent_index: IntVar
    box_coords: list

    def __init__(self, parent: "VALocker") -> None:
        self.state = parent.instalocker_status
        self.hover = parent.hover
        self.random_select = parent.random_select
        self.exclusiselect = parent.exclusiselect
        self.map_specific = parent.map_specific
        self.agent_index = parent.agent_index
        self.box_coords = parent.box_coords

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
