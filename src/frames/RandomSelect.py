"""
@author: [E1Bos](https://www.github.com/E1Bos)
"""

import customtkinter as ctk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from VALocker import VALocker

# Custom Imports
from Constants import BRIGHTEN_COLOR, FILE
from CustomElements import *


class RandomSelectUI(SideFrame):
    """
    Frame that allows the user to select the random select options.
    """

    all_variable: ctk.BooleanVar
    none_variable: ctk.BooleanVar

    all_checkbox: ThemedCheckbox
    none_checkbox: ThemedCheckbox

    super_role_checkboxes: dict[str, ThemedCheckbox] = dict()
    role_variables: dict[str, ctk.BooleanVar]

    agent_checkboxes: dict[str, dict[str, DependentCheckbox]]

    def __init__(self, parent: "VALocker") -> None:
        super().__init__(parent)

        self.super_frame = ThemedFrame(self)
        self.super_frame.pack(fill=ctk.X, pady=10)

        self.exclusiselect_button = IndependentButton(
            self.super_frame,
            text="ExclusiSelect",
            width=100,
            variable=self.parent.exclusiselect,
            command=lambda: self.parent.toggle_boolean(self.parent.exclusiselect),
        )
        self.exclusiselect_button.pack(side=ctk.LEFT, padx=(20, 0), pady=10)

        self.super_checkboxes_frame = ThemedFrame(self.super_frame, fg_color="transparent")
        self.super_checkboxes_frame.pack(anchor=ctk.CENTER, fill=ctk.Y, expand=True)

        self.super_checkboxes_frame.grid_rowconfigure(0, weight=1)

        self.all_variable = ctk.BooleanVar(value=False)
        self.all_checkbox = ThemedCheckbox(
            self.super_checkboxes_frame,
            text="All",
            variable=self.all_variable,
            command=lambda: self.super_toggle_all(True),
        )
        self.all_checkbox.grid(row=0, column=0)

        self.none_variable = ctk.BooleanVar(value=False)
        self.none_checkbox = ThemedCheckbox(
            self.super_checkboxes_frame,
            text="None",
            variable=self.none_variable,
            command=lambda: self.super_toggle_none(True),
        )
        self.none_checkbox.grid(row=0, column=1)

        self.roles_list = self.parent.file_manager.get_value(FILE.AGENT_CONFIG, "roles")

        self.super_role_checkboxes_frame = ThemedFrame(self)
        self.super_role_checkboxes_frame.pack(fill=ctk.X, pady=(0, 10))

        self.role_variables = {role: ctk.BooleanVar(value=False) for role in self.roles_list}

        for col, role in enumerate(self.roles_list):
            self.super_role_checkboxes_frame.grid_columnconfigure(col, weight=1)

            role_color = self.theme[role]

            self.super_role_checkboxes[role] = ThemedCheckbox(
                self.super_role_checkboxes_frame,
                text=f"{role.capitalize()}s",
                text_color=BRIGHTEN_COLOR(role_color, 1.3),
                fg_color=role_color,
                hover_color=BRIGHTEN_COLOR(role_color, 1.1),
                variable=self.role_variables[role],
                command=lambda role=role: self.super_toggle_role(role, True),
            )
            self.super_role_checkboxes[role].grid(row=0, column=col, pady=10)

        self.agents_frame = ThemedFrame(self, fg_color="transparent")
        self.agents_frame.pack(fill=ctk.BOTH, expand=True, pady=(0, 10))

        self.always_true = ctk.BooleanVar(value=True)
        self.agent_checkboxes = {role: dict() for role in self.roles_list}
        for col, role in enumerate(self.roles_list):
            role_agents = self.parent.file_manager.get_value(FILE.AGENT_CONFIG, role)
            self.agents_frame.grid_columnconfigure(col, weight=1)

            role_frame = ThemedFrame(self.agents_frame)
            padx = 0 if col == 0 else (5, 0)
            role_frame.grid(row=0, column=col, sticky=ctk.NSEW, padx=padx)
            role_color = self.theme[role]

            for row, agent_name in enumerate(role_agents):
                dependent_var = (
                    self.parent.agent_states[agent_name][0]
                    if len(self.parent.agent_states[agent_name]) != 1
                    else self.always_true
                )

                variable = (
                    self.parent.agent_states[agent_name][1]
                    if len(self.parent.agent_states[agent_name]) != 1
                    else self.parent.agent_states[agent_name][0]
                )

                self.agent_checkboxes[role][agent_name] = DependentCheckbox(
                    role_frame,
                    text=agent_name.capitalize(),
                    text_color=BRIGHTEN_COLOR(role_color, 1.3),
                    fg_color=role_color,
                    hover_color=BRIGHTEN_COLOR(role_color, 1.1),
                    variable=variable,
                    dependent_variable=dependent_var,
                    command=lambda: self.toggle_agent(True),
                )

                pady = 5 if row == 0 else (0, 5)
                self.agent_checkboxes[role][agent_name].pack(pady=pady)

        self.update_super_checkboxes()

    def on_raise(self) -> None:
        """
        Called when the frame is raised.
        """
        self.update_super_checkboxes()

    def super_toggle_all(self, update_super: bool = False) -> None:
        """
        Called when the 'All' checkbox is toggled.
        """
        for role in self.role_variables:
            self.role_variables[role].set(True)
            self.super_toggle_role(role)

        if update_super:
            self.update_super_checkboxes()

    def super_toggle_none(self, update_super: bool = False) -> None:
        """
        Called when the 'None' checkbox is toggled.
        """
        for role in self.role_variables:
            self.role_variables[role].set(False)
            self.super_toggle_role(role)

        if update_super:
            self.update_super_checkboxes()

    def super_toggle_role(self, role: str, update_super: bool = False) -> None:
        """
        Called when a role checkbox is toggled.
        """
        value = self.role_variables[role].get()

        for agent in self.agent_checkboxes[role]:
            if not self.agent_checkboxes[role][agent].dependent_variable.get():
                continue

            self.agent_checkboxes[role][agent].variable.set(value)

        if update_super:
            self.update_super_checkboxes()

    def toggle_agent(self, update_super: bool = False) -> None:
        """
        Toggles a single agent checkbox.
        """
        if update_super:
            self.update_super_checkboxes()

    def update_super_checkboxes(self) -> None:
        """
        Updates the state of all the super checkboxes.
        """
        agent_values = {role: [agent.variable.get() for agent in self.agent_checkboxes[role].values() if agent.dependent_variable.get()] for role in self.roles_list}

        for role, values in agent_values.items():
            if all(values):
                self.role_variables[role].set(True)
            else:
                self.role_variables[role].set(False)

        all_selected = all([all(role) for role in agent_values.values()])

        none_selected = all([not any(role) for role in agent_values.values()])

        self.all_variable.set(all_selected)
        self.none_variable.set(none_selected)

        match self.all_variable.get(), self.none_variable.get():
            case (True, False):
                self.all_checkbox.disable()
                self.none_checkbox.enable()
            case (False, True):
                self.all_checkbox.enable()
                self.none_checkbox.disable()
            case _:
                self.all_checkbox.enable()
                self.none_checkbox.enable()

        if not none_selected:
            self.parent.random_select_available.set(True)
        else:
            self.parent.random_select_available.set(False)
