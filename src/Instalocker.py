from customtkinter import BooleanVar
from CustomLogger import CustomLogger


class Instalocker:
    def __init__(self) -> None:
        self.logger = CustomLogger("Instalocker").get_logger()

        self.locking = BooleanVar(value=True)
        self.hover = BooleanVar(value=False)
        self.random_select = BooleanVar(value=False)
        self.exclusiselect = BooleanVar(value=False)
        self.map_specific = BooleanVar(value=False)
        # self.last_lock_time = str()

    def toggle_locking(self):
        self.locking.set(not self.locking.get())

    def toggle_hover(self):
        self.hover.set(not self.hover.get())

    def toggle_random_select(self):
        self.random_select.set(not self.random_select.get())

    def toggle_map_specific(self):
        self.map_specific.set(not self.map_specific.get())

    def toggle_exclusiselect(self):
        self.exclusiselect.set(not self.exclusiselect.get())

    def get_locking(self):
        return self.locking.get()

    def get_hover(self):
        return self.hover.get()

    def get_random_select(self):
        return self.random_select.get()

    def get_map_specific(self):
        return self.map_specific.get()

    def get_exclusiselect(self):
        return self.exclusiselect.get()
