"""
@author: [E1Bos](https://www.github.com/E1Bos)
"""

import customtkinter as ctk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from VALocker import VALocker

# Custom Imports
from CustomElements import *


class ToolsUI(SideFrame):
    parent: "VALocker"

    # Status of tools thread
    tool_status: ctk.BooleanVar

    # Dict of tool button names and their corresponding button
    tool_buttons: dict[str, ThemedButton] = dict()

    def __init__(self, parent: "VALocker") -> None:
        super().__init__(parent)

        tools: dict[str, ctk.BooleanVar] = {"Anti-AFK": self.parent.anti_afk}

        self.tool_status = self.parent.tools_thread_running

        toggle_tool_status = IndependentButton(
            self,
            text=["Tools: Enabled", "Tools: Disabled"],
            variable=self.tool_status,
            command=lambda: self.parent.toggle_boolean(self.tool_status),
            corner_radius=10,
        )
        toggle_tool_status.pack(side=ctk.TOP, fill=ctk.X, pady=(10, 0), padx=0)

        scrollable_tools_frame = ThemedScrollableFrame(self)
        scrollable_tools_frame.pack(fill=ctk.BOTH, expand=True, pady=10)

        scrollable_tools_frame.columnconfigure(0, weight=1)

        # Scrollable frame items
        for index, tool in enumerate(tools):
            var = tools[tool]

            button = IndependentButton(
                scrollable_tools_frame,
                text=tool,
                variable=var,
                corner_radius=10,
                command=lambda tool_var=var: self.parent.toggle_tool(tool_var),
            )
            button.grid(row=index, column=0, padx=10, pady=10, sticky=ctk.NSEW)

            self.tool_buttons[tool] = button

    def on_raise(self) -> None:
        pass
