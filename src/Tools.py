# Custom Imports
from CustomLogger import CustomLogger


class Tools():
    def __init__(self):
        self.logger = CustomLogger("Tools").get_logger()

        self.anti_afk = False
        self.drop_spike = False

    def toggle_anti_afk(self):
        self.anti_afk = not self.anti_afk

    def toggle_drop_spike(self):
        self.drop_spike = not self.drop_spike

    def get_anti_afk(self):
        return self.anti_afk

    def get_drop_spike(self):
        return self.drop_spike
