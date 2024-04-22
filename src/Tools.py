import time
import threading

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from VALocker import VALocker

from customtkinter import BooleanVar, IntVar

# Custom Imports
from CustomLogger import CustomLogger


class Tools():
    logger = CustomLogger("Tools").get_logger()
    
    stop_flag = False
    
    anti_afk: BooleanVar
    drop_spike = BooleanVar
    
    def __init__(self, parent:"VALocker"):
        self.anti_afk = parent.anti_afk
        self.drop_spike = parent.drop_spike
    
    # region: Threading

    def main(self):
        while not self.stop_flag:
            time.sleep(1)
            # TODO: Implement logic

    def start(self):
        self.stop_flag = False
        self.logger.info("Thread started")
        self.thread = threading.Thread(target=self.main, daemon=True)
        self.thread.start()

    def stop(self):
        self.stop_flag = True
        self.logger.info("Thread stopped")

    # endregion