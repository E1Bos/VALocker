from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from VALocker import VALocker


# Instalocker specific
import pynput.keyboard as pynkeyboard
import betterdxcam
from PIL import Image
import numpy as np
import cv2

# Custom Imports
from CustomLogger import CustomLogger

class LockingConfigGenerator:
    """
    Locking Config Generator is a class that generates the locking config for the VALocker
    It does this by analyzing a screenshot of the game and determining the important locations for the locking config
    
    THIS CLASS IS NOT YET IMPLEMENTED AND IS A WORK IN PROGRESS
    
    @author: [E1Bos](https://www.github.com/E1Bos)
    """
    parent: "VALocker"
    logger: CustomLogger
    cam: betterdxcam.betterDXCamera
    
    box_rgb = (236, 232, 225)
    
    def __init__(self, parent: "VALocker"):
        self.parent = parent
        self.logger = CustomLogger("LockingConfigGenerator")
        self.cam = betterdxcam.create()
    
    def start(self):
        """
        Starts the locking config generator
        """
        self.logger.info(f"Waiting for key press 'K'")
    
        # with pynkeyboard.Listener(on_press=self.on_press) as listener:
        #     listener.join()
        self.image = Image.open("screenshot.png")
        
        analysis = self.analyze_screenshot()
        
        del self.image
        
        output = self.generate_config(analysis)
        
        self.save_config(output)
    
    def analyze_screenshot(self):
        """
        Analyzes the screenshot to determine important locations for the locking config
        """
        pass
    
    def generate_config(self, analyzed_info: dict) -> dict:
        """
        Generates the locking config based on the analyzed screenshot
        """
        pass
    
    def save_config(self, config: dict):
        """
        Saves the config to the file system
        """
        pass
    
    # region Screenshot
    
    def take_screenshot(self) -> Image:
        """
        Takes a screenshot of the entire screen using the camera and stores it in the image attribute
        """
        
        self.logger.info("Taking screenshot")
        
        self.cam.start(video_mode=False)
        
        # Ensures that the latest frame is valid
        self.image = None
        while self.image is None:
            self.image = self.cam.get_latest_frame()
        
        image = Image.fromarray(self.image)
        image.save("screenshot-valorant.png")
        
        self.cam.stop()
    
    def on_press(self, key):
        """
        When a key is pressed, this function is called. If the key is 'k', the screenshot is taken
        """
        try:
            if key.char == 'k':
                self.logger.info("Detected key press")
                self.take_screenshot()
                return False  # Stop the listener
        except AttributeError:
            pass
        
    # endregion

if __name__ == "__main__":
    lcg = LockingConfigGenerator(None)
    lcg.start()