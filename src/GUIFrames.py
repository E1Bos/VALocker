import customtkinter as ctk
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from GUI import GUI

from ProjectUtils import BRIGHTEN_COLOR, FILE
from CustomElements import (
    ThemedFrame,
    ThemedLabel,
    ThemedButton,
    ThemedDropdown,
    IndependentButton,
    DependentButton,
    SplitButton,
    DependentLabel,
    SideFrame,
    ThemedCheckbox,
)

# region: Navigation Frame


class NavigationFrame(ctk.CTkFrame):
    def __init__(self, parent: "GUI", width):
        super().__init__(
            parent, width=width, corner_radius=0, fg_color=parent.theme["foreground"]
        )
        self.parent = parent
        self.theme = parent.theme

        self.title_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.title_frame.pack(pady=10)

        self.title_label_frame = ctk.CTkFrame(self.title_frame, fg_color="transparent")
        self.title_label_frame.pack()

        self.valocker_label_left = ctk.CTkLabel(
            self.title_label_frame,
            text="VAL",
            fg_color="transparent",
            text_color="#BD3944",
            font=(self.parent.theme["font"], 20),
        )
        self.valocker_label_left.pack(side=ctk.LEFT)

        self.valocker_label_right = ctk.CTkLabel(
            self.title_label_frame,
            text="ocker",
            fg_color="transparent",
            text_color=self.theme["text"],
            font=(self.parent.theme["font"], 20),
        )
        self.valocker_label_right.pack(side=ctk.LEFT)

        self.version_label = ctk.CTkLabel(
            self.title_frame,
            text=f"v{self.parent.VERSION}",
            fg_color="transparent",
            text_color=BRIGHTEN_COLOR(self.theme["text"], 0.5),
            font=(self.parent.theme["font"], 12),
        )
        self.version_label.pack(pady=0)

        # TODO: Uncomment map specific when better solution is implemented
        buttons = [
            "Overview",
            "Agent Toggle",
            "Random Select",
            # "Map Specific",
            "Save Files",
            "Tools",
            "Settings",
        ]

        for button_text in buttons:
            button = ctk.CTkButton(
                self,
                text=button_text,
                height=40,
                corner_radius=0,
                border_spacing=10,
                anchor=ctk.W,
                fg_color="transparent",
                text_color=self.theme["text"],
                hover_color=BRIGHTEN_COLOR(self.theme["foreground"], 1.5),
                font=self.parent.theme["button"],
                command=lambda button=button_text: self.change_active_frame(button),
            )
            button.pack(fill=ctk.X)

        self.exit_button = ctk.CTkButton(
            self,
            text="Exit",
            font=self.parent.theme["button"],
            fg_color=self.parent.theme["accent"],
            hover_color=self.parent.theme["accent-hover"],
            corner_radius=5,
            hover=True,
            command=self.quit_program,
        )
        self.exit_button.pack(side=ctk.BOTTOM, pady=10, padx=10, fill=ctk.X)

    def change_active_frame(self, button) -> None:
        """
        Raises the specified frame to the top of the stack of frames.

        Parameters:
        - button: The name of the frame to be raised.
        """
        self.parent.frames[button].tkraise()

    def quit_program(self) -> None:
        """
        Quit the program.

        This method is responsible for exiting the program gracefully.
        It calls the `exit` method of the parent object to terminate the application.
        """
        self.parent.exit()


# endregion

# region: Overview Frame


class OverviewFrame(SideFrame):
    def __init__(self, parent: "GUI"):
        super().__init__(parent)
        self.parent = parent
        self.theme = parent.theme

        # Make each frame take up equal space
        for frame in range(3):
            self.grid_columnconfigure(frame, weight=1)

        # Make the frames take up the entire vertical space
        self.grid_rowconfigure(0, weight=1)

        # Segmented Frames
        self.left_frame = ThemedFrame(self, corner_radius=10)
        self.middle_frame = ThemedFrame(self, corner_radius=10)
        self.right_frame = ThemedFrame(self, corner_radius=10)

        # Grid the frames
        for index, frame in enumerate(
            [self.left_frame, self.middle_frame, self.right_frame]
        ):
            frame.grid(
                row=0,
                column=index,
                sticky="nsew",
                padx=10 if index == 1 else 0,
                pady=10,
            )
            frame.grid_propagate(False)
            frame.columnconfigure(0, weight=1)

        # region: Left Frame
        self.program_status_label = ThemedLabel(
            self.left_frame,
            text="Instalocker",
        )
        self.program_status_label.grid(
            row=0, column=0, sticky="nsew", padx=10, pady=(10, 0)
        )

        self.program_status_button = IndependentButton(
            self.left_frame,
            text=["Running", "Stopped"],
            variable=self.parent.is_thread_running,
            command=lambda variable=self.parent.is_thread_running: self.toggle_boolean(
                variable
            ),
        )

        self.program_status_button.grid(
            row=1, column=0, sticky="nsew", padx=10, pady=(0, 10)
        )

        self.instalocker_status_label = ThemedLabel(self.left_frame, "Status")
        self.instalocker_status_label.grid(
            row=2, column=0, sticky="nsew", padx=10, pady=(10, 0)
        )

        self.instalocker_status_button = DependentButton(
            self.left_frame,
            variable=self.parent.instalocker.locking,
            dependent_variable=self.parent.is_thread_running,
            text=["Locking", "Waiting", "None"],
            command=self.parent.instalocker.toggle_locking,
        )

        self.instalocker_status_button.grid(
            row=3, column=0, sticky="nsew", padx=10, pady=(0, 10)
        )

        self.save_mode_label = ThemedLabel(self.left_frame, "Safe Mode")
        self.save_mode_label.grid(row=4, column=0, sticky="nsew", padx=10, pady=(10, 0))

        self.safe_mode_button = SplitButton(
            self.left_frame,
            text_left=["On", "Off"],
            text_right=["Low", "Medium", "High"],
            variable_left=self.parent.safe_mode_enabled,
            variable_right=self.parent.safe_mode_strength,
            command_left=self.toggle_safe_mode,
            command_right=self.increment_save_mode_strength,
        )
        self.safe_mode_button.frame.grid(
            row=5, column=0, sticky="nsew", padx=10, pady=(0, 10)
        )

        self.save_label = ThemedLabel(self.left_frame, "Current Save")
        self.save_label.grid(row=6, column=0, sticky="nsew", padx=10, pady=(10, 0))

        self.save_button = ThemedButton(
            self.left_frame,
            text=self.parent.current_save_name.get(),
            fg_color=self.theme["foreground-highlight"],
            hover_color=self.theme["foreground-highlight-hover"],
            command=self.redirect_save_files_frame,
        )
        self.save_button.grid(row=7, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.parent.current_save_name.trace_add(
            "write", self.update_current_save_button
        )

        # endregion

        # region: Middle Frame

        self.agent_label = ThemedLabel(self.middle_frame, "Selected Agent")
        self.agent_label.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 0))

        self.agent_dropdown = ThemedDropdown(
            self.middle_frame,
            values=self.parent.save_manager.get_unlocked_agents(),
            variable=self.parent.selected_agent,
            # width=20,
            command=self.select_agent,
        )
        self.agent_dropdown.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        self.options_label = ThemedLabel(self.middle_frame, "Options")
        self.options_label.grid(row=2, column=0, sticky="nsew", padx=10, pady=(10, 0))

        self.hover_button = IndependentButton(
            self.middle_frame,
            text="Hover",
            fg_color=self.theme["foreground-highlight"],
            hover_color=self.theme["foreground-highlight-hover"],
            variable=self.parent.instalocker.hover,
            command=self.toggle_hover,
        )
        self.hover_button.grid(row=3, column=0, sticky="nsew", padx=10)

        self.random_agent_button = IndependentButton(
            self.middle_frame,
            text="Random Agent",
            fg_color=self.theme["foreground-highlight"],
            hover_color=self.theme["foreground-highlight-hover"],
            variable=self.parent.instalocker.random_select,
            command=self.toggle_random_select,
        )
        self.random_agent_button.grid(row=4, column=0, sticky="nsew", padx=10, pady=10)

        self.map_specific_button = IndependentButton(
            self.middle_frame,
            text="Map Specific",
            fg_color=self.theme["foreground-highlight"],
            hover_color=self.theme["foreground-highlight-hover"],
            variable=self.parent.instalocker.map_specific,
            command=self.toggle_map_specific,
        )
        self.map_specific_button.grid(row=5, column=0, sticky="nsew", padx=10)

        self.tools_button = ThemedButton(
            self.middle_frame,
            text="Tools",
            height=20,
            fg_color=self.theme["foreground-highlight"],
            hover_color=self.theme["foreground-highlight-hover"],
            command=self.redirect_tools_frame,
        )
        self.tools_button.grid(row=6, column=0, sticky="nsew", padx=10, pady=(10, 5))

        self.anti_afk_button = IndependentButton(
            self.middle_frame,
            text="Anti-AFK",
            fg_color=self.theme["foreground-highlight"],
            hover_color=self.theme["foreground-highlight-hover"],
            variable=self.parent.tools.anti_afk,
            command=self.toggle_anti_afk,
        )

        self.anti_afk_button.grid(row=7, column=0, sticky="nsew", padx=10)

        # endregion

        # region: Right Frame
        self.last_lock_label = ThemedLabel(self.right_frame, "Last Lock")
        self.last_lock_label.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 0))

        self.last_lock_time = DependentLabel(
            self.right_frame,
            variable=self.parent.last_lock,
        )
        self.last_lock_time.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        self.average_lock_label = ThemedLabel(self.right_frame, "Average Lock")
        self.average_lock_label.grid(
            row=2, column=0, sticky="nsew", padx=10, pady=(10, 0)
        )

        self.average_lock_time = DependentLabel(
            self.right_frame,
            variable=self.parent.average_lock,
        )
        self.average_lock_time.grid(
            row=3, column=0, sticky="nsew", padx=10, pady=(0, 10)
        )

        self.times_used_label = ThemedLabel(self.right_frame, "Times Used")
        self.times_used_label.grid(
            row=4, column=0, sticky="nsew", padx=10, pady=(10, 0)
        )

        self.times_used = DependentLabel(
            self.right_frame,
            variable=self.parent.times_used,
        )
        self.times_used.grid(row=5, column=0, sticky="nsew", padx=10, pady=(0, 10))

        # endregion

    def toggle_boolean(self, var: ctk.BooleanVar, value=None) -> None:
        """
        Toggles the value of a boolean variable.

        Args:
            var (ctk.BooleanVar): The boolean variable to toggle.
            value (bool, optional): The value to set the variable to. If not provided, the variable will be toggled.
        """
        if value is not None:
            var.set(value)
        else:
            var.set(not var.get())

    def toggle_safe_mode(self) -> None:
        """
        Toggles the safe mode enabled state and updates the statistics.
        """
        self.toggle_boolean(self.parent.safe_mode_enabled)
        self.parent.update_stats()

    def increment_save_mode_strength(self) -> None:
        """
        Increments the save mode strength by 1 and updates the stats.

        The save mode strength is incremented by 1 and wraps around to 0 when it reaches 3.
        After incrementing the save mode strength, the stats are updated.
        """
        self.parent.safe_mode_strength.set(
            (self.parent.safe_mode_strength.get() + 1) % 3
        )
        self.parent.update_stats()

    def redirect_save_files_frame(self) -> None:
        """
        Redirects the user to the "Save Files" frame.

        This method raises the "Save Files" frame to the top, making it visible to the user.
        """
        self.parent.frames["Save Files"].tkraise()

    def redirect_tools_frame(self) -> None:
        """
        Redirects the user to the 'Tools' frame.

        This method raises the 'Tools' frame to the top, making it visible to the user.
        """
        self.parent.frames["Tools"].tkraise()

    def update_current_save_button(self) -> None:
        """
        Updates the text of the save button with the value from the current_save_name variable.
        """
        self.save_button.configure(text=self.parent.current_save_name.get())

    def select_agent(self, *_) -> None:
        """
        Selects an agent based on the value of `selected_agent` attribute in the parent object.
        """
        # TODO: Implement this method
        print(self.parent.selected_agent.get())

    def toggle_hover(self) -> None:
        """
        Toggles the hover state of the parent's instalocker.
        """
        self.parent.instalocker.toggle_hover()

    def toggle_random_select(self) -> None:
        """
        Toggles the random select feature.

        This method calls the `toggle_random_select` method of the `instalocker` object
        belonging to the parent of this GUI frame.
        """
        self.parent.instalocker.toggle_random_select()

    def toggle_map_specific(self) -> None:
        """
        Toggles the map-specific functionality.

        This method calls the `toggle_map_specific` method of the `instalocker` object
        belonging to the parent object.
        """
        self.parent.instalocker.toggle_map_specific()

    def toggle_anti_afk(self) -> None:
        """
        Toggles the anti-AFK feature.

        This method calls the `toggle_anti_afk` method of the parent `tools` object.
        """
        self.parent.tools.toggle_anti_afk()

    def toggle_drop_spike(self) -> None:
        """
        Toggles the drop spike functionality.

        This method calls the `toggle_drop_spike` method of the parent's `tools` object.
        """
        self.parent.tools.toggle_drop_spike()


# endregion

# region: Agent Toggle Frame


class AgentToggleFrame(SideFrame):
    def __init__(self, parent: "GUI"):
        super().__init__(parent)
        self.parent = parent
        self.theme = parent.theme

        self.top_frame = ThemedFrame(self, corner_radius=10)
        self.top_frame.pack(fill=ctk.X, pady=10)
        self.top_frame.grid_columnconfigure(0, weight=1)
        self.top_frame.grid_columnconfigure(1, weight=1)

        self.all_variable = ctk.BooleanVar(value=False)
        self.none_variable = ctk.BooleanVar(value=False)

        self.all_checkbox = ThemedCheckbox(
            self.top_frame,
            text="All",
            variable=self.all_variable,
            command=self.toggle_all,
        )
        self.all_checkbox.grid(row=0, column=0, padx=10, pady=10)

        self.none_checkbox = ThemedCheckbox(
            self.top_frame,
            text="None",
            variable=self.none_variable,
            command=self.toggle_none,
        )
        self.none_checkbox.grid(row=0, column=1, padx=10, pady=10)

        self.specific_agent_frame = ThemedFrame(self, corner_radius=10)
        self.specific_agent_frame.pack(pady=10, padx=0, fill=ctk.X)

        self.toggleable_agent_vars = {
            agent: var
            for agent, var in self.parent.agent_unlock_status.items()
            if agent
            not in self.parent.file_manager.get_value(
                FILE.AGENT_CONFIG, "DEFAULT_AGENTS"
            )
        }

        NUMBER_OF_COLS = 4

        self.agent_buttons = dict()
        for i, (agent_name, variable) in enumerate(self.toggleable_agent_vars.items()):
            row = i // NUMBER_OF_COLS
            col = i % NUMBER_OF_COLS
            self.agent_buttons[agent_name] = ThemedCheckbox(
                self.specific_agent_frame,
                text=agent_name,
                variable=variable,
                command=lambda agent=agent_name: self.toggle_single_agent(agent),
            )

            xpadding = (
                (40, 10) if col == 0 else (10, 40) if col == NUMBER_OF_COLS - 1 else 10
            )
            ypadding = (
                (20, 5)
                if row == 0
                else (
                    (5, 20)
                    if row == len(self.toggleable_agent_vars) // NUMBER_OF_COLS
                    else 5
                )
            )

            self.agent_buttons[agent_name].grid(
                row=row, column=col, padx=xpadding, pady=ypadding, sticky="nsew"
            )

        self.manage_super_checkboxes()

    def toggle_all(self) -> None:
        """
        Toggles all the agent variables to True if the 'all_variable' is True.
        """
        if not self.all_variable.get():
            return

        for agent in self.toggleable_agent_vars:
            self.toggleable_agent_vars[agent].set(True)
            self.parent.save_manager.set_agent_status(agent, True)

        self.manage_super_checkboxes()
        self.parent.save_manager.save_file()

    def toggle_none(self) -> None:
        """
        Toggles the 'none' variable and sets all toggleable agent variables to False.
        """
        if not self.none_variable.get():
            return

        for agent in self.toggleable_agent_vars:
            self.toggleable_agent_vars[agent].set(False)
            self.parent.save_manager.set_agent_status(agent, False)

        self.manage_super_checkboxes()
        self.parent.save_manager.save_file()

    def manage_super_checkboxes(self) -> None:
        """
        Manages the state of the super checkboxes.

        This method checks if all the toggleable agent variables are checked or unchecked,
        and sets the state of the super checkboxes accordingly. It also enables or disables
        the checkboxes based on the state of the toggleable agent variables.
        """
        # Check if all are checked
        all_checked = all(
            self.toggleable_agent_vars[agent].get()
            for agent in self.toggleable_agent_vars
        )

        # Check if all are unchecked
        none_checked = all(
            not self.toggleable_agent_vars[agent].get()
            for agent in self.toggleable_agent_vars
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

    def toggle_single_agent(self, agent: str) -> None:
        """
        Toggles the state of a single agent.
        """
        self.manage_super_checkboxes()
        self.parent.save_manager.set_agent_status(agent, self.toggleable_agent_vars[agent].get())
        self.parent.save_manager.save_file()


# endregion
