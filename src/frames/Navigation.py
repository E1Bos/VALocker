"""
@author: [E1Bos](https://www.github.com/E1Bos)
"""

import customtkinter as ctk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from VALocker import VALocker

# Custom Imports
from Constants import BRIGHTEN_COLOR, FRAME
from CustomElements import *


class NavigationUI(ctk.CTkFrame):
    """
    The sidebar frame that contains the program label, navigation buttons and the exit button.
    """

    parent: "VALocker"
    theme: dict[str, str]
    nav_buttons: dict[str, ctk.CTkButton] = dict()

    def __init__(self, parent: "VALocker", width: int) -> None:
        super().__init__(
            parent, width=width, corner_radius=0, fg_color=parent.theme["foreground"]
        )
        self.parent = parent
        self.theme = parent.theme

        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(pady=10)

        title_label_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
        title_label_frame.pack()

        valocker_label_left = ctk.CTkLabel(
            title_label_frame,
            text="VAL",
            fg_color="transparent",
            text_color="#BD3944",
            font=(self.parent.theme["font"], 20),
        )
        valocker_label_left.pack(side=ctk.LEFT)

        valocker_label_right = ctk.CTkLabel(
            title_label_frame,
            text="ocker",
            fg_color="transparent",
            text_color=self.theme["text"],
            font=(self.parent.theme["font"], 20),
        )
        valocker_label_right.pack(side=ctk.LEFT)

        version_label = ctk.CTkLabel(
            title_frame,
            text=f"v{self.parent.VERSION}",
            fg_color="transparent",
            text_color=BRIGHTEN_COLOR(self.theme["text"], 0.5),
            font=(self.parent.theme["font"], 12),
        )
        version_label.pack(pady=0)

        exit_button = ctk.CTkButton(
            self,
            text="Exit",
            font=self.parent.theme["button"],
            fg_color=self.parent.theme["accent"],
            hover_color=self.parent.theme["accent-hover"],
            corner_radius=5,
            hover=True,
            command=self.quit_program,
        )
        exit_button.pack(side=ctk.BOTTOM, pady=10, padx=10, fill=ctk.X)

        normal_buttons = [
            frame for frame in self.parent.frames if frame != FRAME.SETTINGS
        ]

        for frame_enum in normal_buttons:
            self.nav_buttons[frame_enum] = self.create_button(frame_enum)
            self.nav_buttons[frame_enum].pack(fill=ctk.X, side=ctk.TOP)

        # Settings Button
        self.nav_buttons[FRAME.SETTINGS] = self.create_button(FRAME.SETTINGS)
        self.nav_buttons[FRAME.SETTINGS].pack(side=ctk.BOTTOM, fill=ctk.X)

    def create_button(self, frame: FRAME) -> ctk.CTkButton:
        button = ctk.CTkButton(
            self,
            text=frame.value,
            height=40,
            corner_radius=0,
            border_spacing=10,
            anchor=ctk.W,
            fg_color="transparent",
            text_color=self.theme["text"],
            hover_color=BRIGHTEN_COLOR(self.theme["foreground"], 1.5),
            font=self.parent.theme["button"],
            command=lambda frame=frame: self.parent.select_frame(frame),
        )
        return button

    def highlight_button(self, frame: FRAME) -> None:
        """
        Highlights the specified button.

        Parameters:
        - frame (FRAME): The enum of the button to be highlighted.
        """
        for button in self.nav_buttons:
            if frame == button:
                self.nav_buttons[frame].configure(
                    fg_color=BRIGHTEN_COLOR(self.theme["foreground"], 1.5)
                )
            else:
                self.nav_buttons[button].configure(fg_color="transparent")

    def quit_program(self) -> None:
        """
        Quit the program.

        This method is responsible for exiting the program gracefully.
        It calls the `exit` method of the parent object to terminate the application.
        """
        self.parent.exit()
