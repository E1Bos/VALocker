from customtkinter import BooleanVar
from CustomLogger import CustomLogger


class Tools:
    def __init__(self):
        self.logger = CustomLogger("Tools").get_logger()

        self.anti_afk = BooleanVar(value=False)
        self.drop_spike = BooleanVar(value=False)

    def toggle_anti_afk(self):
        self.anti_afk.set(not self.anti_afk.get())

    def toggle_drop_spike(self):
        self.drop_spike.set(not self.drop_spike.get())

    def get_anti_afk(self):
        return self.anti_afk.get()

    def get_drop_spike(self):
        return self.drop_spike.get()
