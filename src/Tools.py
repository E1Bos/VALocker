import time
import threading
from enum import Enum, auto

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from VALocker import VALocker

from customtkinter import BooleanVar, IntVar

# Custom Imports
from CustomLogger import CustomLogger

class ANTI_AFK(Enum):
    RANDOM = auto()
    RANDOM_CENTERED = auto()
    CIRCLE = auto()
    STRAFE = auto()

class Tools():
    logger = CustomLogger("Tools").get_logger()
    
    stop_flag = False
    
    anti_afk: BooleanVar
    drop_spike = BooleanVar
    
    # Thread
    thread: Optional[threading.Thread] = None
    
    def __init__(self, parent:"VALocker"):
        self.anti_afk = parent.anti_afk
        self.drop_spike = parent.drop_spike
    
    # region: Threading

    def main(self):
        while not self.stop_flag:
            time.sleep(1)
            
            if self.anti_afk.get():
                self.anti_afk_main()
            
            if self.drop_spike.get():
                self.drop_spike_main()
            # TODO: Implement logic

    def anti_afk_main(self):
        movement_type = ANTI_AFK.RANDOM
        
        match movement_type:
            case ANTI_AFK.RANDOM:
                self.logger.info("Random Movement")
            case ANTI_AFK.RANDOM_CENTERED:
                self.logger.info("Random Centered Movement")
            case ANTI_AFK.CIRCLE:
                self.logger.info("Circle Movement")
            case ANTI_AFK.STRAFE:
                self.logger.info("Strafe Movement")
            case _:
                self.logger.error(f"Unrecognized Movement Type {movement_type}")

        raise NotImplementedError("Anti-AFK not implemented")

    def drop_spike_main(self):
        raise NotImplementedError("Drop Spike not implemented")

    def start(self):
        # Check if thread is already running, if so return
        if self.thread is not None and self.thread.is_alive():
            self.logger.warning("Thread already running")
            return

        # Start thread
        self.stop_flag = False
        self.logger.info("Thread started")
        self.thread = threading.Thread(target=self.main, daemon=True)
        self.thread.start()

    def stop(self):
        # Ensure thread exists
        if self.thread is None:
            self.logger.info("Thread not started")
            return
        
        # If thread is not alive, thread is already stopped
        if not self.thread.is_alive():
            self.logger.warning("Thread already stopped")
            return

        # Stop thread
        self.stop_flag = True
        self.logger.info("Thread stopped")

    # endregion