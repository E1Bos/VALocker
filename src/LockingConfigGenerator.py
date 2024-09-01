from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from VALocker import VALocker

import pynput.keyboard as pynkeyboard
from pynput.keyboard import Key
import pynput.mouse as pynmouse
import betterdxcam
from PIL import Image
import numpy as np
import datetime
import time

import re

# import cv2

# Custom Imports
from CustomLogger import CustomLogger

def extract_resolution(res_string):
    match = re.search(r'Res:\((\d+), (\d+)\)', res_string)
    if match:
        width = int(match.group(1))
        height = int(match.group(2))
        return width, height
    else:
        raise ValueError("Resolution string is in an unexpected format.")



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

    def __init__(self, parent: "VALocker"):
        self.parent = parent
        self.logger = CustomLogger("LockingConfigGenerator")
        self.cam = betterdxcam.create()

    def start(self):
        """
        Starts the locking config generator
        """
        self.logger.info(f"Waiting for key press 'K'")

        with pynkeyboard.Listener(on_press=self.on_press) as listener:
            listener.join()

    def analyze_screen(self):
        """
        Analyzes the screen to determine important locations for the locking config
        """

        output_info = betterdxcam.output_info()
        screen_width, screen_height = extract_resolution(output_info)

        X_COORDINATE = 0
        Y_COORDINATE = 0

        X_STEP = 50
        Y_STEP = 50

        MAX_X = screen_width // 2
        MAX_Y = screen_height

        TIMING = 0.01

        self.cam.start()
        mouse = pynmouse.Controller()
        
        while Y_COORDINATE < MAX_Y:
            X_COORDINATE = 0
            while X_COORDINATE < MAX_X:
                mouse.position = (X_COORDINATE, Y_COORDINATE)
                X_COORDINATE += X_STEP
                screenshot = self.get_screenshot()
                print(np.count_nonzero(screenshot == (34, 255, 197)))
                time.sleep(TIMING)
            Y_COORDINATE += Y_STEP
            
            
            # Hover color rgb(34, 255, 197)s


        print("DONE")
        # t = self.get_screenshot()


        # mouse.position = (X_COORDINATE, Y_COORDINATE)

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

    def get_screenshot(self) -> np.ndarray:
        """
        Returns the screenshot
        """
        if not self.cam.is_capturing:
            return None

        image = self.cam.get_latest_frame()

        while image is None or np.all(image == 0):
            image = self.cam.get_latest_frame()

        return image

    def take_screenshot(self, save_image: bool = False) -> Image:
        """
        Takes a screenshot of the entire screen using the camera and stores it in the image attribute
        """

        self.logger.info("Taking screenshot")

        self.cam.start()

        image = self.get_screenshot()

        if save_image:
            now = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
            image = Image.fromarray(image)
            image.save(f"screenshot-{now}.png")
            self.logger.info(f"Screenshot saved as screenshot-{now}.png")

        self.cam.stop()

    def on_press(self, key):
        """
        When a key is pressed, this function is called. If the key is 'k', the screenshot is taken
        """
        try:
            if key == Key.esc:
                self.logger.info("Detected ESC key press, quitting")
                return False
            elif key.char == "k":
                self.logger.info("Detected K key press, taking screenshot")
                self.take_screenshot(save_image=True)
            elif key.char == "s":
                self.logger.info("Detected S key press, starting analysis")
                self.analyze_screen()
        except AttributeError:
            pass

    # endregion


if __name__ == "__main__":
    lcg = LockingConfigGenerator(None)
    lcg.start()
