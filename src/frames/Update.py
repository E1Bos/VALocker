"""
@author: [E1Bos](https://www.github.com/E1Bos)
"""

import customtkinter as ctk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from VALocker import VALocker

# Custom Imports
from Constants import FILE
from CustomElements import *


class UpdateUI(ctk.CTkFrame):
    default_config = {
        "fg_color": "background",
    }

    font_size: tuple[str, int]

    status_variables: dict[FILE, ctk.StringVar]
    version_variable: ctk.StringVar

    def __init__(self, parent: "VALocker", reset_configs=False, **kwargs) -> None:
        self.parent = parent
        self.theme = parent.theme

        config = {
            key: kwargs.get(key, parent.theme.get(value, value))
            for key, value in self.default_config.items()
        }
        config.update(kwargs)

        self.font_size = (self.theme["font"], 18)

        super().__init__(parent, **config)

        self.grid_columnconfigure(0, weight=1)

        self.update_label = ThemedLabel(
            self,
            text="Checking for Updates",
            font=(self.theme["font"], 20),
        )
        self.update_label.grid(row=0, column=0, sticky=ctk.NSEW, padx=10, pady=(20, 5))

        self.progress_bar = ctk.CTkProgressBar(
            self,
            fg_color=self.theme["foreground"],
            border_color=self.theme["foreground-highlight"],
            progress_color=self.theme["accent"],
            border_width=1,
            mode="indeterminate",
            indeterminate_speed=2,
            width=300,
            height=10,
        )
        self.progress_bar.grid(row=1, column=0, pady=(0, 10))
        self.progress_bar.start()

        self.status_variables = {}

        version_frame = ThemedFrame(self)
        version_frame.grid(row=2, column=0, sticky=ctk.NSEW, padx=50, pady=10)

        version_label = ThemedLabel(version_frame, text="Version", font=self.font_size)
        version_label.pack(side=ctk.LEFT, padx=10, pady=10)

        self.version_variable = ctk.StringVar(value="Waiting")
        version_status = ThemedLabel(
            version_frame, textvariable=self.version_variable, font=self.font_size
        )

        version_status.pack(side=ctk.RIGHT, padx=10, pady=10)

        for row, file_to_check in enumerate(self.parent.updater.ITEMS_TO_CHECK):
            row += 3

            file_frame = ThemedFrame(self)

            file_frame.grid(row=row, column=0, sticky=ctk.NSEW, padx=50, pady=10)

            file_name = file_to_check.name.split("_")
            file_name = " ".join([word.capitalize() for word in file_name])

            file_label = ThemedLabel(
                file_frame,
                text=file_name,
                font=self.font_size,
            )
            file_label.pack(side=ctk.LEFT, padx=10, pady=10)

            text_var = ctk.StringVar(value="Waiting")
            file_status = ThemedLabel(
                file_frame, textvariable=text_var, font=self.font_size
            )
            file_status.pack(side=ctk.RIGHT, padx=10, pady=10)

            self.status_variables[file_to_check] = text_var

    def resume_progress(self) -> None:
        self.progress_bar.start()

    def stop_progress(self) -> None:
        self.progress_bar.stop()

    def finished_checking_updates(self):
        self.update_label.configure(text="Loading VALocker")
