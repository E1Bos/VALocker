"""
@author: [E1Bos](https://www.github.com/E1Bos)
"""

import customtkinter as ctk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from VALocker import VALocker

# Custom Imports
from CustomElements import *


class AgentToggleUI(SideFrame):
    """
    Frame that allows the user to toggle the agents unlocked status.
    """

    all_variable: ctk.BooleanVar
    none_variable: ctk.BooleanVar

    all_checkbox: ThemedCheckbox
    none_checkbox: ThemedCheckbox

    toggleable_agents: dict[str, ctk.BooleanVar]
    agent_checkboxes: dict[str, ThemedCheckbox]

    def __init__(self, parent: "VALocker") -> None:
        super().__init__(parent)

        top_frame = ThemedFrame(self)
        top_frame.pack(fill=ctk.X, pady=10)
        top_frame.grid_columnconfigure(0, weight=1)
        top_frame.grid_columnconfigure(1, weight=1)

        self.all_variable = ctk.BooleanVar(value=False)
        self.none_variable = ctk.BooleanVar(value=False)

        self.all_checkbox = ThemedCheckbox(
            top_frame,
            text="All",
            variable=self.all_variable,
            command=lambda: self.toggle_all_agents(True),
        )
        self.all_checkbox.grid(row=0, column=0, padx=10, pady=10)

        self.none_checkbox = ThemedCheckbox(
            top_frame,
            text="None",
            variable=self.none_variable,
            command=lambda: self.toggle_all_agents(False),
        )
        self.none_checkbox.grid(row=0, column=1, padx=10, pady=10)

        self.outer_agent_frame = ThemedFrame(self)
        self.outer_agent_frame.pack(expand=True, fill=ctk.BOTH, pady=10, padx=0)

        self.specific_agent_frame = ThemedFrame(self.outer_agent_frame)
        self.specific_agent_frame.pack(anchor=ctk.CENTER, pady=10, padx=0)

        self.toggleable_agents: dict[str, ctk.BooleanVar] = {
            agent_name: values[0]
            for agent_name, values in self.parent.agent_states.items()
            if len(values) != 1
        }

        NUMBER_OF_COLS = 4

        self.agent_checkboxes = dict()
        for i, (agent_name, variable) in enumerate(self.toggleable_agents.items()):
            row = i // NUMBER_OF_COLS
            col = i % NUMBER_OF_COLS

            self.agent_checkboxes[agent_name] = ThemedCheckbox(
                self.specific_agent_frame,
                text=agent_name.capitalize(),
                variable=variable,
                command=self.toggle_single_agent,
            )

            padx = (
                (30, 10) if col == 0 else (10, 30) if col == NUMBER_OF_COLS - 1 else 10
            )
            pady = (
                (20, 5)
                if row == 0
                else (
                    (5, 20)
                    if row == len(self.toggleable_agents) // NUMBER_OF_COLS
                    else 5
                )
            )

            self.specific_agent_frame.grid_rowconfigure(row, weight=1)
            self.specific_agent_frame.grid_columnconfigure(col, weight=1)

            self.agent_checkboxes[agent_name].grid(
                row=row, column=col, sticky=ctk.NSEW, padx=padx, pady=pady
            )

    def toggle_all_agents(self, value: bool) -> None:
        self.parent.update_idletasks()
        self.parent.after(0)        
        
        for var in self.toggleable_agents.values():
            var.set(value)

        self.update_super_checkboxes()

    def update_super_checkboxes(self) -> None:
        """
        Manages the state of the super checkboxes.

        This method checks if all the toggleable agent variables are checked or unchecked,
        and sets the state of the super checkboxes accordingly. It also enables or disables
        the checkboxes based on the state of the toggleable agent variables.
        """
        # Check if all are checked
        all_checked = all(
            self.toggleable_agents[agent].get() for agent in self.toggleable_agents
        )

        # Check if all are unchecked
        none_checked = all(
            not self.toggleable_agents[agent].get() for agent in self.toggleable_agents
        )

        # Set super checkboxes
        self.all_variable.set(all_checked)
        self.none_variable.set(none_checked)

        # Disable and enable checkboxes
        self.none_checkbox.enable()
        self.all_checkbox.enable()
        if all_checked:
            self.all_checkbox.disable()
        elif none_checked:
            self.none_checkbox.disable()

        self.parent.agent_unlock_status_changed()

    def toggle_single_agent(self) -> None:
        """
        Toggles the state of a single agent.
        """
        self.update_super_checkboxes()

    def on_raise(self) -> None:
        """
        Updates the state of the super checkboxes when the frame is raised.
        """
        self.update_super_checkboxes()
