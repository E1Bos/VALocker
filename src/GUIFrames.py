import customtkinter as ctk
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from VALocker import VALocker


from Constants import BRIGHTEN_COLOR, FILE, FRAME, profile
from CustomElements import *
import os

# region: Navigation Frame


class NavigationFrame(ctk.CTkFrame):
    parent: "VALocker"
    theme: dict[str, str]
    nav_buttons: dict[str, ctk.CTkButton] = dict()

    def __init__(self, parent: "VALocker", width: int):
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


# endregion

# region: Overview Frame


class OverviewFrame(SideFrame):
    agent_dropdown: ThemedDropdown

    def __init__(self, parent: "VALocker"):
        super().__init__(parent)

        # Make each frame take up equal space
        for frame in range(3):
            self.grid_columnconfigure(frame, weight=1)

        # Make the frames take up the entire vertical space
        self.grid_rowconfigure(0, weight=1)

        # Segmented Frames
        left_frame = ThemedFrame(self)
        middle_frame = ThemedFrame(self)
        right_frame = ThemedFrame(self)

        # Grid the frames
        for index, frame in enumerate([left_frame, middle_frame, right_frame]):
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
        program_status_label = ThemedLabel(
            left_frame,
            text="Instalocker",
        )
        program_status_label.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 0))

        program_status_button = IndependentButton(
            left_frame,
            text=["Running", "Stopped"],
            variable=self.parent.instalocker_thread_running,
            command=lambda: self.parent.toggle_boolean(
                self.parent.instalocker_thread_running
            ),
        )

        program_status_button.grid(
            row=1, column=0, sticky="nsew", padx=10, pady=(0, 10)
        )

        instalocker_status_label = ThemedLabel(left_frame, "Status")
        instalocker_status_label.grid(
            row=2, column=0, sticky="nsew", padx=10, pady=(10, 0)
        )

        instalocker_status_button = DependentButton(
            left_frame,
            variable=self.parent.instalocker_status,
            dependent_variable=self.parent.instalocker_thread_running,
            text=["Locking", "Waiting", "None"],
            command=lambda: self.parent.toggle_boolean(self.parent.instalocker_status),
        )

        instalocker_status_button.grid(
            row=3, column=0, sticky="nsew", padx=10, pady=(0, 10)
        )

        safe_mode_label = ThemedLabel(left_frame, "Safe Mode")
        safe_mode_label.grid(row=4, column=0, sticky="nsew", padx=10, pady=(10, 0))

        safe_mode_button = SplitButton(
            left_frame,
            text_left=["On", "Off"],
            text_right=["Low", "Medium", "High"],
            variable_left=self.parent.safe_mode_enabled,
            variable_right=self.parent.safe_mode_strength,
            command_left=lambda: self.parent.toggle_boolean(
                self.parent.safe_mode_enabled
            ),
            command_right=lambda: self.parent.increment_int(
                self.parent.safe_mode_strength, 3
            ),
        )
        safe_mode_button.grid(row=5, column=0, sticky="nsew", padx=10, pady=(0, 10))

        save_label = ThemedLabel(left_frame, "Current Save")
        save_label.grid(row=6, column=0, sticky="nsew", padx=10, pady=(10, 0))

        save_button = ThemedButton(
            left_frame,
            fg_color=self.theme["foreground-highlight"],
            hover_color=self.theme["foreground-highlight-hover"],
            textvariable=self.parent.current_save_name,
            command=self.redirect_save_files_frame,
        )
        save_button.grid(row=7, column=0, sticky="nsew", padx=10, pady=(0, 10))

        # endregion

        # region: Middle Frame

        agent_label = ThemedLabel(middle_frame, "Selected Agent")
        agent_label.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 0))

        self.agent_dropdown = ThemedDropdown(
            middle_frame,
            values=[],
            variable=self.parent.selected_agent,
            command=lambda agent: self.parent.selected_agent.set(agent),
        )
        self.agent_dropdown.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        options_label = ThemedLabel(middle_frame, "Options")
        options_label.grid(row=2, column=0, sticky="nsew", padx=10, pady=(10, 0))

        hover_button = IndependentButton(
            middle_frame,
            text="Hover",
            variable=self.parent.hover,
            command=lambda: self.parent.toggle_boolean(self.parent.hover),
        )
        hover_button.grid(row=3, column=0, sticky="nsew", padx=10)

        random_agent_button = IndependentButton(
            middle_frame,
            text="Random Agent",
            variable=self.parent.random_select,
            command=lambda: self.parent.toggle_boolean(self.parent.random_select),
        )
        random_agent_button.grid(row=4, column=0, sticky="nsew", padx=10, pady=10)

        map_specific_button = IndependentButton(
            middle_frame,
            text="Map Specific",
            variable=self.parent.map_specific,
            command=lambda: self.parent.toggle_boolean(self.parent.map_specific),
        )
        map_specific_button.grid(row=5, column=0, sticky="nsew", padx=10)

        tools_button = ThemedButton(
            middle_frame,
            text="Tools",
            height=20,
            fg_color=self.theme["foreground-highlight"],
            hover_color=self.theme["foreground-highlight-hover"],
            command=self.redirect_tools_frame,
        )
        tools_button.grid(row=6, column=0, sticky="nsew", padx=10, pady=(10, 5))

        anti_afk_button = IndependentButton(
            middle_frame,
            text="Anti-AFK",
            variable=self.parent.anti_afk,
            command=lambda: self.parent.toggle_boolean(self.parent.anti_afk),
        )
        anti_afk_button.grid(row=7, column=0, sticky="nsew", padx=10)

        # endregion

        # region: Right Frame
        last_lock_label = ThemedLabel(right_frame, "Last Lock")
        last_lock_label.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 0))

        last_lock_stat = ThemedLabel(
            right_frame,
            variable=self.parent.last_lock,
        )
        last_lock_stat.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

        average_lock_label = ThemedLabel(right_frame, "Average Lock")
        average_lock_label.grid(row=2, column=0, sticky="nsew", padx=10, pady=(10, 0))

        average_lock_stat = ThemedLabel(
            right_frame,
            variable=self.parent.average_lock,
        )
        average_lock_stat.grid(row=3, column=0, sticky="nsew", padx=10, pady=(0, 10))

        times_used_label = ThemedLabel(right_frame, "Times Used")
        times_used_label.grid(row=4, column=0, sticky="nsew", padx=10, pady=(10, 0))

        times_used_stat = ThemedLabel(
            right_frame,
            variable=self.parent.times_used,
        )
        times_used_stat.grid(row=5, column=0, sticky="nsew", padx=10, pady=(0, 10))

        # endregion

    def redirect_save_files_frame(self) -> None:
        """
        Redirects the user to the "Save Files" frame.

        This method raises the "Save Files" frame to the top, making it visible to the user.
        """
        self.parent.select_frame(FRAME.SAVE_FILES)

    def redirect_tools_frame(self) -> None:
        """
        Redirects the user to the 'Tools' frame.

        This method raises the 'Tools' frame to the top, making it visible to the user.
        """
        self.parent.select_frame(FRAME.TOOLS)

    def update_dropdown(self, unlocked_agents: list[str]) -> None:
        """
        Updates the options in the agent dropdown based on the unlocked agents.

        Args:
            unlocked_agents (list[str]): A list of unlocked agents.
        """

        # Code to calculate unlocked agents list
        # unlocked_agents = [
        #     agent[0].capitalize()
        #     for agent in self.parent.agent_status.items()
        #     if agent[1][0].get()
        # ]

        self.agent_dropdown.set_values(unlocked_agents)


# endregion

# region: Agent Toggle Frame


class AgentToggleFrame(SideFrame):
    all_variable: ctk.BooleanVar
    none_variable: ctk.BooleanVar

    all_checkbox: ThemedCheckbox
    none_checkbox: ThemedCheckbox

    toggleable_agents: dict[str, ctk.BooleanVar]
    agent_checkboxes: dict[str, ThemedCheckbox]

    def __init__(self, parent: "VALocker"):
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
            command=self.toggle_all,
        )
        self.all_checkbox.grid(row=0, column=0, padx=10, pady=10)

        self.none_checkbox = ThemedCheckbox(
            top_frame,
            text="None",
            variable=self.none_variable,
            command=self.toggle_none,
        )
        self.none_checkbox.grid(row=0, column=1, padx=10, pady=10)

        self.outer_agent_frame = ThemedFrame(self)
        self.outer_agent_frame.pack(expand=True, fill=ctk.BOTH, pady=(0, 10), padx=0)

        self.specific_agent_frame = ThemedFrame(self.outer_agent_frame)
        self.specific_agent_frame.pack(anchor=ctk.CENTER, pady=10, padx=0)

        default_agents = self.parent.file_manager.get_value(
            FILE.AGENT_CONFIG, "defaultAgents"
        )
        self.toggleable_agents: dict[str, ctk.BooleanVar] = {
            agent_item[0]: agent_item[1][0]
            for agent_item in self.parent.agent_status.items()
            if agent_item[0] not in default_agents
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

            xpadding = (
                (30, 10) if col == 0 else (10, 30) if col == NUMBER_OF_COLS - 1 else 10
            )
            ypadding = (
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
                row=row, column=col, sticky="nsew", padx=xpadding, pady=ypadding
            )

    def toggle_all(self) -> None:
        """
        Toggles all the agent variables to True if the 'all_variable' is True.
        """
        if not self.all_variable.get():
            return

        for variable in self.toggleable_agents.values():
            variable.set(True)

        self.update_super_checkboxes()

    def toggle_none(self) -> None:
        """
        Toggles the 'none' variable and sets all toggleable agent variables to False.
        """
        if not self.none_variable.get():
            return

        for variable in self.toggleable_agents.values():
            variable.set(False)

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


# endregion

# region: Random Select Frame


class RandomSelectFrame(SideFrame):
    all_variable: ctk.BooleanVar
    none_variable: ctk.BooleanVar

    all_checkbox: ThemedCheckbox
    none_checkbox: ThemedCheckbox

    super_role_checkboxes: dict[str, ThemedCheckbox] = dict()
    role_variables: dict[str, ctk.BooleanVar]

    agent_checkboxes: dict[str, dict[str, DependentCheckbox]]

    def __init__(self, parent: "VALocker"):
        super().__init__(parent)

        super_frame = ThemedFrame(self)
        super_frame.pack(fill=ctk.X, pady=10)

        self.exclusiselect_button = IndependentButton(
            super_frame,
            text="ExclusiSelect",
            width=100,  # should be ~120 pixels but when set to 120 it becomes 150 (???)
            variable=self.parent.exclusiselect,
            command=lambda: self.parent.toggle_boolean(self.parent.exclusiselect),
        )
        self.exclusiselect_button.pack(
            side=ctk.LEFT,
            padx=(20, 0),
            pady=10,
        )

        super_checkboxes_frame = ThemedFrame(super_frame, fg_color="transparent")
        super_checkboxes_frame.pack(anchor=ctk.CENTER, fill=ctk.Y, expand=True)

        super_checkboxes_frame.grid_rowconfigure(0, weight=1)

        self.all_variable = ctk.BooleanVar(value=False)
        self.all_checkbox = ThemedCheckbox(
            super_checkboxes_frame,
            text="All",
            variable=self.all_variable,
            command=lambda: self.super_toggle_all(True),
        )
        self.all_checkbox.grid(row=0, column=0)

        self.none_variable = ctk.BooleanVar(value=False)
        self.none_checkbox = ThemedCheckbox(
            super_checkboxes_frame,
            text="None",
            variable=self.none_variable,
            command=lambda: self.super_toggle_none(True),
        )
        self.none_checkbox.grid(row=0, column=1)

        roles_dict = self.parent.file_manager.get_value(FILE.AGENT_CONFIG, "allAgents")

        super_role_checkboxes_frame = ThemedFrame(self)
        super_role_checkboxes_frame.pack(fill=ctk.X, pady=(0, 10))

        self.role_variables = {
            role: ctk.BooleanVar(value=False) for role in roles_dict.keys()
        }

        for col, role in enumerate(roles_dict.keys()):
            super_role_checkboxes_frame.grid_columnconfigure(col, weight=1)

            role_color = self.theme[role]

            self.super_role_checkboxes[role] = ThemedCheckbox(
                super_role_checkboxes_frame,
                text=role.capitalize(),
                text_color=BRIGHTEN_COLOR(role_color, 1.3),
                fg_color=role_color,
                hover_color=BRIGHTEN_COLOR(role_color, 1.1),
                variable=self.role_variables[role],
                command=lambda role=role: self.super_toggle_role(role, True),
            )
            self.super_role_checkboxes[role].grid(row=0, column=col, pady=10)

        agents_frame = ThemedFrame(self, fg_color="transparent")
        agents_frame.pack(fill=ctk.BOTH, expand=True, pady=(0, 10))

        self.agent_checkboxes = {role: dict() for role in roles_dict.keys()}
        for col, (role_name, agents) in enumerate(roles_dict.items()):
            agents_frame.grid_columnconfigure(col, weight=1)

            role_frame = ThemedFrame(agents_frame)
            padx = 0 if col == 0 else (5, 0)
            role_frame.grid(row=0, column=col, sticky=ctk.NSEW, padx=padx)
            role_color = self.theme[role_name]

            for i, agent in enumerate(agents):
                self.agent_checkboxes[role_name][agent] = DependentCheckbox(
                    role_frame,
                    text=agent.capitalize(),
                    text_color=BRIGHTEN_COLOR(role_color, 1.3),
                    fg_color=role_color,
                    hover_color=BRIGHTEN_COLOR(role_color, 1.1),
                    variable=self.parent.agent_status[agent][1],
                    dependent_variable=self.parent.agent_status[agent][0],
                    command=lambda: self.toggle_agent(True),
                )

                ypad = 5 if i == 0 else (0, 5)
                self.agent_checkboxes[role_name][agent].pack(pady=ypad)

    def on_raise(self):
        self.update_super_checkboxes()

    def super_toggle_all(self, update_super=False):
        for role in self.role_variables:
            self.role_variables[role].set(True)
            self.super_toggle_role(role)

        if update_super:
            self.update_super_checkboxes()

    def super_toggle_none(self, update_super=False):
        for role in self.role_variables:
            self.role_variables[role].set(False)
            self.super_toggle_role(role)

        if update_super:
            self.update_super_checkboxes()

    def super_toggle_role(self, role: str, update_super=False):
        value = self.role_variables[role].get()

        for agent in self.parent.file_manager.get_value(FILE.AGENT_CONFIG, "allAgents")[
            role
        ]:
            if self.agent_checkboxes[role][agent].cget("state") == ctk.NORMAL:
                self.parent.agent_status[agent][1].set(value)

        if update_super:
            self.update_super_checkboxes()

    def toggle_agent(self, update_super=False):
        if update_super:
            self.update_super_checkboxes()

    def update_super_checkboxes(self):

        for role in self.role_variables:
            if all(
                [
                    self.parent.agent_status[agent][1].get()
                    for agent in self.parent.file_manager.get_value(
                        FILE.AGENT_CONFIG, "allAgents"
                    )[role]
                    if self.parent.agent_status[agent][0].get()
                ]
            ):
                self.role_variables[role].set(True)
            else:
                self.role_variables[role].set(False)

        all_selected = all(
            [self.role_variables[role].get() for role in self.role_variables]
        )

        none_selected = all(
            [not agent_var[1].get() for agent_var in self.parent.agent_status.values()]
        )

        self.all_variable.set(all_selected)
        self.none_variable.set(none_selected)

        self.none_checkbox.enable()
        self.all_checkbox.enable()
        if all_selected:
            self.all_checkbox.disable()
        elif none_selected:
            self.none_checkbox.disable()

# endregion

# region: Save Files Frame


class SaveFilesFrame(SideFrame):
    parent: "VALocker"

    favorite_buttons: list[SaveButton] = []

    new_file_icon = ctk.CTkImage(Image.open(ICON.NEW_FILE.value), size=(20, 20))

    def __init__(self, parent: "VALocker"):
        super().__init__(parent)

        scrollable_frame = ThemedScrollableFrame(self, label_text="Save Files")
        scrollable_frame.pack(fill=ctk.BOTH, expand=True, pady=(10, 0))
        scrollable_frame.grid_columnconfigure(0, weight=1)

        self.buttons: list[SaveButton] = []

        for save_name in parent.save_manager.get_all_save_files():
            button = SaveButton(
                scrollable_frame, save_file=save_name
            )
            self.buttons.append(button)

        self.new_save_button = ThemedButton(
            self, text="", image=self.new_file_icon, width=40, command=self.new_save,
            fg_color=self.theme["foreground"],
            hover_color=self.theme["foreground-hover"],
        )
        self.new_save_button.pack(side=ctk.RIGHT, pady=(5, 10), padx=0)

        self.change_selected(self.parent.current_save_name.get())
        self.reorder_buttons()

    def new_save(self) -> None:
        raise NotImplementedError("New Save functionality not implemented")

    def change_save(self, save_name: str) -> None:
        self.parent.load_save(f"{save_name}.json", save_current_config=True)
        self.change_selected(save_name)

    def change_selected(self, save_name: str) -> None:
        for button in self.buttons:
            if button.save_name == save_name:
                button.set_selected(True)
            else:
                button.set_selected(False)

    def favorite_button(self, button: SaveButton) -> None:
        if button.favorited:
            self.favorite_buttons.append(button)
        else:
            self.favorite_buttons.remove(button)

        self.reorder_buttons()

    def reorder_buttons(self) -> None:
        other_buttons = sorted(
            [button for button in self.buttons if not button.favorited],
            key=lambda button: button.save_name,
        )

        for index, button in enumerate(self.favorite_buttons + other_buttons):
            button.grid(row=index, column=0, pady=5, padx=5, sticky=ctk.EW)


# endregion