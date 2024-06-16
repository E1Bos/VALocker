import time
import threading
from enum import Enum, auto
import random

from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from VALocker import VALocker

from customtkinter import BooleanVar
# import pynput.mouse as pynmouse
import pynput.keyboard as pynkeyboard

# Custom Imports
from CustomLogger import CustomLogger

class ANTI_AFK(Enum):
    RANDOM = auto()
    RANDOM_CENTERED = auto()
    CIRCLE = auto()
    STRAFE = auto()

class Tools():
    """
    This class manages the tools thread that can run alongside the instalocker.
    @author: [E1Bos](https://www.github.com/E1Bos)
    """
    logger = CustomLogger("Tools").get_logger()
    
    stop_flag = False
    
    tools_input: bool = False
    
    keybinds = {
            "MoveForward": "w",
            "MoveBackward": "s",
            "MoveRight": "d",
            "MoveLeft": "a",
        }
    
    movement_type: ANTI_AFK = ANTI_AFK.RANDOM_CENTERED
    anti_afk: BooleanVar
    drop_spike = BooleanVar
    
    keyboard: pynkeyboard.Controller = pynkeyboard.Controller()
    keyboard_listener: pynkeyboard.Listener = None
    
    # Thread
    thread: Optional[threading.Thread] = None
    stop_event: threading.Event
    
    
    def __init__(self, parent:"VALocker"):
        self.anti_afk = parent.anti_afk
        self.keyboard_listener = None
        self.stop_event = threading.Event()
        
    def keyboard_on_press(self, key) -> None:
        if (
            hasattr(key, "char")
            and not self.tools_input
            and not self.stop_flag
            and self.anti_afk.get()
        ):
            self.anti_afk.set(False)
    
    # region: Threading

    def main(self) -> None:
        self.keyboard_listener = pynkeyboard.Listener(
            on_press=self.keyboard_on_press
        )
        self.keyboard_listener.start()
        
        self.logger.info("Thread started")
        
        before = 0
        while not self.stopped():
            now = time.time()
            
            if self.anti_afk.get():
                if now - before >= 7.5:
                    self.anti_afk_main(self.movement_type)
                    before = now
            
            self.stop_event.wait(3)
        
        self.logger.info("Thread stopped")
        self.keyboard_listener.stop()        

    def anti_afk_main(self, movement_type: ANTI_AFK = ANTI_AFK.RANDOM_CENTERED) -> None:
        
        queue = []
        
        match movement_type:
            case ANTI_AFK.RANDOM_CENTERED:
                # Random key presses but end up back in the center
                direction = random.choice(
                    ["forward", "right", "backward", "left"]
                )
                match direction:
                    case "forward":
                        keybind_order = [
                            self.keybinds["MoveForward"],
                            self.keybinds["MoveBackward"],
                        ]
                    case "backward":
                        keybind_order = [
                            self.keybinds["MoveBackward"],
                            self.keybinds["MoveForward"],
                        ]
                    case "right":
                        keybind_order = [
                            self.keybinds["MoveRight"],
                            self.keybinds["MoveLeft"],
                        ]
                    case "left":
                        keybind_order = [
                            self.keybinds["MoveLeft"],
                            self.keybinds["MoveRight"],
                        ]
                
            case ANTI_AFK.RANDOM:
                # Random key presses
                possible_directions = [
                    self.keybinds["MoveForward"],
                    self.keybinds["MoveRight"],
                    self.keybinds["MoveBackward"],
                    self.keybinds["MoveLeft"],
                ]
                keybind_order = [random.choice(possible_directions),]
                
            case ANTI_AFK.CIRCLE:
                # Go in a circle
                keybind_order = [
                    self.keybinds["MoveForward"],
                    self.keybinds["MoveRight"],
                    self.keybinds["MoveBackward"],
                    self.keybinds["MoveLeft"],
                ]
                    
            case ANTI_AFK.STRAFE:
                # Go right to left
                keybind_order = [
                    self.keybinds["MoveRight"],
                    self.keybinds["MoveLeft"],
                ]
            case _:
                self.logger.error(f"Unrecognized Movement Type {movement_type}")
                self.anti_afk_main(ANTI_AFK.RANDOM_CENTERED)

        queue.extend(keybind_order)

        for key in queue:
            self.tools_input = True
            
            self.keyboard.press(key)
            self.stop_event.wait(random.uniform(0.1, 0.3))
            
            self.keyboard.release(key)
            self.tools_input = False
            self.stop_event.wait(random.uniform(0.1, 0.3))

    def start(self) -> None:
        # Check if thread is already running, if so return
        if self.thread is not None and self.thread.is_alive():
            self.logger.warning("Thread already running")

        # Start thread
        self.stop_event.clear()
        self.thread = threading.Thread(target=self.main, daemon=True)
        self.thread.start()

    def stop(self) -> None:
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