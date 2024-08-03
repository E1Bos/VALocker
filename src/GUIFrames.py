"""
@author: [E1Bos](https://www.github.com/E1Bos)
"""

import customtkinter as ctk
import traceback
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from VALocker import VALocker

# Custom Imports
from Constants import BRIGHTEN_COLOR, FILE, FRAME
from Tools import ANTI_AFK
from CustomElements import *


# region: Navigation Frame


class NavigationFrame(ctk.CTkFrame):
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


# endregion


# region: Overview Frame


class OverviewFrame(SideFrame):
    """
    The main frame that displays the program status and the agent status.
    """

    agent_dropdown: ThemedDropdown

    def __init__(self, parent: "VALocker") -> None:
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
                sticky=ctk.NSEW,
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
        program_status_label.grid(
            row=0, column=0, sticky=ctk.NSEW, padx=10, pady=(10, 0)
        )

        program_status_button = IndependentButton(
            left_frame,
            text=["Running", "Stopped"],
            variable=self.parent.instalocker_thread_running,
            command=lambda: self.parent.toggle_boolean(
                self.parent.instalocker_thread_running
            ),
        )

        program_status_button.grid(
            row=1, column=0, sticky=ctk.NSEW, padx=10, pady=(0, 10)
        )

        instalocker_status_label = ThemedLabel(left_frame, "Status")
        instalocker_status_label.grid(
            row=2, column=0, sticky=ctk.NSEW, padx=10, pady=(10, 0)
        )

        instalocker_status_button = DependentButton(
            left_frame,
            variable=self.parent.instalocker_status,
            dependent_variable=self.parent.instalocker_thread_running,
            text=["Locking", "Waiting", "None"],
            command=lambda: self.parent.toggle_boolean(self.parent.instalocker_status),
        )

        instalocker_status_button.grid(
            row=3, column=0, sticky=ctk.NSEW, padx=10, pady=(0, 10)
        )

        safe_mode_label = ThemedLabel(left_frame, "Safe Mode")
        safe_mode_label.grid(row=4, column=0, sticky=ctk.NSEW, padx=10, pady=(10, 0))

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
        safe_mode_button.grid(row=5, column=0, sticky=ctk.NSEW, padx=10, pady=(0, 10))

        save_label = ThemedLabel(left_frame, "Current Save")
        save_label.grid(row=6, column=0, sticky=ctk.NSEW, padx=10, pady=(10, 0))

        save_button = ThemedButton(
            left_frame,
            fg_color=self.theme["foreground-highlight"],
            hover_color=self.theme["foreground-highlight-hover"],
            textvariable=self.parent.current_save_name,
            command=self.redirect_save_files_frame,
        )
        save_button.grid(row=7, column=0, sticky=ctk.NSEW, padx=10, pady=(0, 10))

        # endregion

        # region: Middle Frame

        agent_label = ThemedLabel(middle_frame, "Selected Agent")
        agent_label.grid(row=0, column=0, sticky=ctk.NSEW, padx=10, pady=(10, 0))

        self.agent_dropdown = ThemedDropdown(
            middle_frame,
            values=[],
            variable=self.parent.selected_agent,
        )
        self.agent_dropdown.grid(
            row=1, column=0, sticky=ctk.NSEW, padx=10, pady=(0, 10)
        )

        options_label = ThemedLabel(middle_frame, "Options")
        options_label.grid(row=2, column=0, sticky=ctk.NSEW, padx=10, pady=(10, 0))

        hover_button = IndependentButton(
            middle_frame,
            text="Hover",
            variable=self.parent.hover,
            command=lambda: self.parent.toggle_boolean(self.parent.hover),
        )
        hover_button.grid(row=3, column=0, sticky=ctk.NSEW, padx=10)

        random_agent_button = ColorDependentButton(
            middle_frame,
            text="Random Agent",
            variable=self.parent.random_select,
            dependent_variable=self.parent.random_select_available,
            command=lambda: self.parent.toggle_boolean(self.parent.random_select),
        )
        random_agent_button.grid(row=4, column=0, sticky=ctk.NSEW, padx=10, pady=10)

        # map_specific_button = IndependentButton(
        #     middle_frame,
        #     text="Map Specific",
        #     variable=self.parent.map_specific,
        #     command=lambda: self.parent.toggle_boolean(self.parent.map_specific),
        #     state=ctk.DISABLED,
        # )
        # map_specific_button.grid(row=5, column=0, sticky=ctk.NSEW, padx=10)

        tools_button = ThemedButton(
            middle_frame,
            text="Tools",
            height=20,
            fg_color=self.theme["foreground-highlight"],
            hover_color=self.theme["foreground-highlight-hover"],
            command=self.redirect_tools_frame,
        )
        tools_button.grid(row=5, column=0, sticky=ctk.NSEW, padx=10, pady=(10, 5))

        anti_afk_button = IndependentButton(
            middle_frame,
            text="Anti-AFK",
            variable=self.parent.anti_afk,
            command=lambda: self.parent.toggle_boolean_and_run_function(
                self.parent.anti_afk, self.parent.autostart_tools
            ),
        )
        anti_afk_button.grid(row=7, column=0, sticky=ctk.NSEW, padx=10)

        # endregion

        # region: Right Frame
        last_lock_label = ThemedLabel(right_frame, "Last Lock")
        last_lock_label.grid(row=0, column=0, sticky=ctk.NSEW, padx=10, pady=(10, 0))

        last_lock_stat = ThemedLabel(
            right_frame,
            variable=self.parent.last_lock,
        )
        last_lock_stat.grid(row=1, column=0, sticky=ctk.NSEW, padx=10, pady=(0, 10))

        average_lock_label = ThemedLabel(right_frame, "Average Lock")
        average_lock_label.grid(row=2, column=0, sticky=ctk.NSEW, padx=10, pady=(10, 0))

        average_lock_stat = ThemedLabel(
            right_frame,
            variable=self.parent.average_lock,
        )
        average_lock_stat.grid(row=3, column=0, sticky=ctk.NSEW, padx=10, pady=(0, 10))

        times_used_label = ThemedLabel(right_frame, "Times Used")
        times_used_label.grid(row=4, column=0, sticky=ctk.NSEW, padx=10, pady=(10, 0))

        times_used_stat = ThemedLabel(
            right_frame,
            variable=self.parent.times_used,
        )
        times_used_stat.grid(row=5, column=0, sticky=ctk.NSEW, padx=10, pady=(0, 10))

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

        self.agent_dropdown.set_values(unlocked_agents)

    def on_raise(self) -> None:
        pass


# endregion


# region: Agent Toggle Frame


class AgentToggleFrame(SideFrame):
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

        roles_list: list[str] = self.parent.file_manager.get_value(
            FILE.AGENT_CONFIG, "roles"
        )

        super_role_checkboxes_frame = ThemedFrame(self)
        super_role_checkboxes_frame.pack(fill=ctk.X, pady=(0, 10))

        self.role_variables = {role: ctk.BooleanVar(value=False) for role in roles_list}

        for col, role in enumerate(roles_list):
            super_role_checkboxes_frame.grid_columnconfigure(col, weight=1)

            role_color = self.theme[role]

            self.super_role_checkboxes[role] = ThemedCheckbox(
                super_role_checkboxes_frame,
                text=f"{role.capitalize()}s",
                text_color=BRIGHTEN_COLOR(role_color, 1.3),
                fg_color=role_color,
                hover_color=BRIGHTEN_COLOR(role_color, 1.1),
                variable=self.role_variables[role],
                command=lambda role=role: self.super_toggle_role(role, True),
            )
            self.super_role_checkboxes[role].grid(row=0, column=col, pady=10)

        agents_frame = ThemedFrame(self, fg_color="transparent")
        agents_frame.pack(fill=ctk.BOTH, expand=True, pady=(0, 10))

        always_true = ctk.BooleanVar(value=True)
        self.agent_checkboxes = {role: dict() for role in roles_list}
        for col, role in enumerate(roles_list):
            role_agents: list[str] = self.parent.file_manager.get_value(
                FILE.AGENT_CONFIG, role
            )
            agents_frame.grid_columnconfigure(col, weight=1)

            role_frame = ThemedFrame(agents_frame)
            padx = 0 if col == 0 else (5, 0)
            role_frame.grid(row=0, column=col, sticky=ctk.NSEW, padx=padx)
            role_color = self.theme[role]

            for row, agent_name in enumerate(role_agents):

                dependent_var = (
                    self.parent.agent_states[agent_name][0]
                    if len(self.parent.agent_states[agent_name]) != 1
                    else always_true
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

        agent_values = {}
        for role in self.agent_checkboxes:
            agent_values[role] = [
                self.agent_checkboxes[role][agent].variable.get()
                for agent in self.agent_checkboxes[role]
                if self.agent_checkboxes[role][agent].dependent_variable.get()
            ]

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


# endregion


# region: Save Files Frame


class SaveFilesFrame(SideFrame):
    """
    Frame that displays the save files.
    """

    parent: "VALocker"

    buttons: list[SaveButton]
    favorite_buttons: list[SaveButton] = None

    new_file_icon = ctk.CTkImage(Image.open(ICON.NEW_FILE.value), size=(20, 20))

    invalid_chars: list[str] = ["/", "\\", ":", "*", "?", '"', "<", ">", "|"]

    def __init__(self, parent: "VALocker") -> None:
        super().__init__(parent)

        self.scrollable_frame = ThemedScrollableFrame(self, label_text="Save Files")
        self.scrollable_frame.pack(fill=ctk.BOTH, expand=True, pady=(10, 0))
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        if self.favorite_buttons is None:
            self.favorite_buttons = []

        self.generate_save_button_list(first_time=True)

        self.new_save_button = ThemedButton(
            self,
            text="",
            image=self.new_file_icon,
            width=40,
            command=self.new_save,
            fg_color=self.theme["foreground"],
            hover_color=self.theme["foreground-hover"],
        )
        self.new_save_button.pack(side=ctk.RIGHT, pady=(5, 10), padx=0)

    def generate_save_button_list(self, first_time: Optional[bool] = False) -> None:
        """
        Generates the list of save buttons, which is rendered to the user
        as a list of buttons that represent the save files.

        Args:
            first_time (bool, optional): Only set to true when "SaveFilesFrame" is initiated, since it reads from disk.
            Defaults to False.
        """
        
        favorite_button_names = [button.save_file for button in self.favorite_buttons]
        
        if not first_time:
            for button in self.buttons:
                button.destroy()
            self.favorite_buttons = []
        else:
            for favorited_save in self.parent.file_manager.get_value(
                FILE.SETTINGS, "favoritedSaveFiles"
            ):
                favorite_button_names.append(favorited_save)

        self.buttons = []
        for save_file in self.parent.save_manager.get_all_save_files():
            button = SaveButton(self.scrollable_frame, save_file=save_file)
            self.buttons.append(button)

        for fav_button_name in favorite_button_names:
            for button in self.buttons:
                if button.save_file == fav_button_name:
                    button.toggle_favorite(value=True)

        self.reorder_buttons()
        self.change_selected_button(self.parent.current_save_name.get())

    def validate_file_name(self, file_name: str) -> bool | None:
        """
        Validates the file name.

        Raises an exception if the file name is invalid.
        Returns True if the file name is valid.
        """
        if file_name == "":
            raise Exception("File name cannot be empty")

        for char in self.invalid_chars:
            if char in file_name:
                raise Exception(f'Invalid character: "{char}".')

        if f"{file_name}.yaml" in self.parent.save_manager.get_all_save_files():
            raise Exception(f'Save file "{file_name}" already exists')

        return True

    def change_save(self, save: SaveButton) -> None:
        """
        Loads the specified save file.
        """
        self.change_selected_button(save.save_name)
        self.parent.load_save(save.save_file, save_current_config=True)

    def change_selected_button(self, save: str | SaveButton) -> None:
        """
        Changes the selected button based on the save name.

        Args:
            save (str | SaveButton): The save name or the button to be selected.
        """

        if isinstance(save, SaveButton):
            for button in self.buttons:
                if button == save:
                    button.set_selected(True)
                else:
                    button.set_selected(False)
            return

        if save.endswith(".yaml"):
            save = save.removesuffix(".yaml")

        for button in self.buttons:
            if button.save_name == save:
                button.set_selected(True)
            else:
                button.set_selected(False)

    def get_button_order(self) -> list[SaveButton]:
        """
        Returns the buttons in the order they should be displayed.

        Returns:
            list[SaveButton]: The buttons in the order they should be displayed.
        """
        other_buttons = sorted(
            [button for button in self.buttons if not button.favorited],
            key=lambda button: button.save_name.lower(),
        )

        return self.favorite_buttons + other_buttons

    def reorder_buttons(self) -> None:
        """
        Reorders the buttons based on the favorited status and the save name.
        """
        for index, button in enumerate(self.get_button_order()):
            button.grid(row=index, column=0, pady=5, padx=5, sticky="EW")

    # Button functionality

    def favorite_button(self, button: SaveButton, reorderList: bool = True) -> None:
        """
        Favorites or unfavorites a save file.

        Args:
            button (SaveButton): The button to be favorited or unfavorited.
            reorderList (bool, optional): Whether to reorder the buttons after the change. Defaults to True.
        """

        if button.favorited:
            self.favorite_buttons.append(button)
        else:
            self.favorite_buttons.remove(button)

        if reorderList:
            self.reorder_buttons()

        self.parent.file_manager.set_value(
            FILE.SETTINGS,
            "favoritedSaveFiles",
            [button.save_file for button in self.favorite_buttons],
        )

    def new_save(self) -> None:
        """
        Creates a new save file.

        This method prompts the user to enter a name for the new save file.
        """
        valid_input = False
        prefill = ""
        while not valid_input:
            file_name = InputDialog(
                self.parent,
                title="New Save",
                label="Enter new save name:",
                placeholder="Save Name",
                prefill=None if prefill == "" else prefill,
            ).get_input()
            prefill = file_name
            if file_name is None:
                self.parent.logger.info("New Save Cancelled")
                return

            try:
                valid_input = self.validate_file_name(file_name)
            except Exception as e:
                self.parent.logger.warning(f"Error creating new file: {e}")
                ErrorPopup(self.parent, message=str(e))

        file_name = file_name.strip() + ".yaml"

        self.parent.save_manager.create_new_save(file_name)
        self.parent.load_save(file_name, save_current_config=True)
        self.generate_save_button_list()

    def rename_save(self, save_button: SaveButton) -> None:
        """
        Renames the specified save file.

        Args:
            save_button (SaveButton): The save button that requested the rename.
        """

        valid_input = False
        save_name = save_button.save_name
        while not valid_input:
            file_name = InputDialog(
                self.parent,
                title="Rename Save",
                label=f'Rename save file \n"{save_name}"',
                prefill=save_name,
            ).get_input()
            if file_name is None:
                self.parent.logger.info("Rename Save Cancelled")
                return

            try:
                valid_input = self.validate_file_name(file_name)
            except Exception as e:
                self.parent.logger.warning(f"Error renaming file: {e}")
                ErrorPopup(self.parent, message=str(e))

        file_name = file_name.strip()

        old_name = save_button.save_file
        save_button.change_text(file_name)

        self.parent.save_manager.rename_save(old_name, save_button.save_file)

        file_name_with_extension = (
            file_name if file_name.endswith(".yaml") else f"{file_name}.yaml"
        )

        if old_name.removesuffix(".yaml") == self.parent.current_save_name.get():
            self.parent.current_save_name.set(file_name)
            if (
                self.parent.file_manager.get_value(FILE.SETTINGS, "activeSaveFile")
                == old_name
            ):
                self.parent.file_manager.set_value(
                    FILE.SETTINGS, "activeSaveFile", file_name_with_extension
                )

        if old_name in self.parent.file_manager.get_value(
            FILE.SETTINGS, "favoritedSaveFiles"
        ):
            # Ensure the new file name has the .yaml extension
            self.parent.file_manager.set_value(
                FILE.SETTINGS,
                "favoritedSaveFiles",
                [
                    file_name_with_extension if name == old_name else name
                    for name in self.parent.file_manager.get_value(
                        FILE.SETTINGS, "favoritedSaveFiles"
                    )
                ],
            )

    def delete_save(self, save_button: SaveButton) -> None:
        """
        Deletes the specified save file.

        Args:
            save_button (SaveButton): The save button that requested the deletion.
        """
        confirm = ConfirmPopup(
            self.parent,
            title="Delete Save",
            message=f'Are you sure you want to delete\n"{save_button.save_name}"?',
        ).get_input()

        if not confirm:
            return

        self.parent.save_manager.delete_save(save_button.save_file)
        self.generate_save_button_list()

        if save_button.save_name == self.parent.current_save_name.get():
            first_save = self.get_button_order()[0]
            self.parent.load_save(first_save.save_file, save_current_config=False)
            self.change_selected_button(first_save)

    def on_raise(self) -> None:
        pass


# endregion


# region: Tools Frame


class ToolsFrame(SideFrame):
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
            command=lambda: self.parent.manual_toggle_tools(self.tool_status),
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
                command=lambda tool_var=var: self.toggle_tool(tool_var),
            )
            button.grid(row=index, column=0, padx=10, pady=10, sticky=ctk.NSEW)

            self.tool_buttons[tool] = button

    def toggle_tool(self, tool_var: ctk.BooleanVar) -> None:
        """
        Toggles the state of the specified tool.

        Args:
            tool_var (ctk.BooleanVar): The tool to be toggled.
        """
        self.parent.toggle_boolean(tool_var)

        if tool_var.get():
            self.parent.num_running_tools += 1
        else:
            self.parent.num_running_tools -= 1

        self.parent.autostart_tools()

    def on_raise(self) -> None:
        pass


# endregion


# region: Settings Frame


class SettingsFrame(SideFrame):
    # TODO: Add more settings
    current_locking_config: ctk.StringVar
    backup_locking_config: str = None
    
    initUI_called: bool

    def __init__(self, parent: "VALocker"):
        super().__init__(parent)

        self.initUI_called = False

        scrollable_frame = ThemedScrollableFrame(self, label_text="Settings")
        scrollable_frame.pack(fill="both", expand=True, pady=10)

        # region: Variables

        settings_file: dict[str, any] = self.parent.file_manager.get_config(
            FILE.SETTINGS
        )

        self.enable_on_startup = ctk.BooleanVar(
            value=settings_file.get("enableOnStartup")
        )
        self.safe_mode_on_startup = ctk.BooleanVar(
            value=settings_file.get("safeModeOnStartup")
        )
        self.safe_mode_strength_on_startup = ctk.IntVar(
            value=settings_file.get("safeModeStrengthOnStartup")
        )

        self.start_tools_automatically = parent.start_tools_automatically

        self.anti_afk_mode: ANTI_AFK = parent.anti_afk_mode
        self.anti_afk_mode_intvar = ctk.IntVar(value=self.anti_afk_mode.index)

        # endregion

        # region: Update Section

        self.update_button = ThemedButton(
            scrollable_frame,
            text="Check for Updates",
            command=self.manual_update,
            corner_radius=10,
        )
        self.update_button.pack(padx=5, pady=5, fill=ctk.X)

        # endregion

        # region: Locking Config Section
        locking_configs = self.parent.file_manager.get_locking_configs()
        self.current_locking_config = ctk.StringVar(
            value=self.parent.file_manager.get_locking_config_by_file_name(
                self.parent.file_manager.get_value(FILE.SETTINGS, "lockingConfig"),
                get_title=True,
            )
        )
        self.backup_locking_config = self.current_locking_config.get()

        locking_config_frame = ThemedFrame(
            scrollable_frame, fg_color=self.parent.theme["foreground-highlight"]
        )
        locking_config_frame.pack(fill=ctk.X, pady=10)

        locking_config_label = ThemedLabel(locking_config_frame, text="Locking Config:")
        locking_config_label.pack(padx=10, pady=5, side=ctk.LEFT)

        self.locking_config_dropdown = ThemedDropdown(
            locking_config_frame,
            corner_radius=10,
            variable=self.current_locking_config,
            values=list(locking_configs.keys()),
        )
        self.locking_config_dropdown.pack(fill=ctk.X, padx=10, pady=5)
        self.current_locking_config.trace_add("write", self.change_locking_config)

        # endregion

        # region: General Settings Section

        general_settings_frame = ThemedFrame(
            scrollable_frame, fg_color=self.parent.theme["foreground-highlight"]
        )
        general_settings_frame.pack(fill=ctk.X, pady=10, ipady=5)

        general_settings_frame.grid_columnconfigure((0, 1), weight=1, uniform="group1")

        general_settings_label = ThemedLabel(
            general_settings_frame, text="General Settings:"
        )
        general_settings_label.grid(
            row=0, column=0, sticky=ctk.NSEW, columnspan=2, padx=10, pady=(10, 5)
        )

        self.start_tools_automatically_button = IndependentButton(
            general_settings_frame,
            text=["Tools Start Automatically", "Tools Start Manually"],
            variable=self.start_tools_automatically,
            command=lambda: self.change_setting(
                "startToolsAutomatically", self.start_tools_automatically
            ),
        )
        self.start_tools_automatically_button.grid(
            row=1, column=0, sticky=ctk.NSEW, padx=10, pady=5
        )

        self.anti_afk_mode_button = MultiTextIndependentButton(
            general_settings_frame,
            prefix="Anti-AFK Mode: ",
            text=[enum.value for enum in ANTI_AFK],
            variable=self.anti_afk_mode_intvar,
            command=self.next_anti_afk_mode,
        )
        self.anti_afk_mode_button.grid(
            row=1, column=1, padx=10, pady=5, sticky=ctk.NSEW
        )

        # endregion

        # region: On Startup Section

        on_startup_frame = ThemedFrame(
            scrollable_frame, fg_color=self.parent.theme["foreground-highlight"]
        )
        on_startup_frame.pack(fill=ctk.X, pady=10, ipady=5)

        on_startup_frame.grid_columnconfigure((0, 1), weight=1, uniform="group1")

        on_startup_label = ThemedLabel(on_startup_frame, text="On Startup:")
        on_startup_label.grid(
            row=0, column=0, sticky=ctk.NSEW, columnspan=2, padx=10, pady=(10, 5)
        )

        self.enable_on_startup_button = IndependentButton(
            on_startup_frame,
            text=["Instalocker Enabled", "Instalocker Disabled"],
            variable=self.enable_on_startup,
            command=lambda: self.change_setting(
                "enableOnStartup", self.enable_on_startup
            ),
        )
        self.enable_on_startup_button.grid(
            row=1, column=0, sticky=ctk.NSEW, padx=10, pady=5
        )

        self.safe_mode_on_startup_button = IndependentButton(
            on_startup_frame,
            text=["Safe Mode Enabled", "Safe Mode Disabled"],
            variable=self.safe_mode_on_startup,
            command=lambda: self.change_setting(
                "safeModeOnStartup", self.safe_mode_on_startup
            ),
        )
        self.safe_mode_on_startup_button.grid(
            row=1, column=1, sticky=ctk.NSEW, padx=10, pady=5
        )

        self.safe_mode_strength_on_startup_button = MultiTextIndependentButton(
            on_startup_frame,
            prefix="Safe Mode Strength: ",
            text=["Low", "Medium", "High"],
            variable=self.safe_mode_strength_on_startup,
            command=lambda: self.increment_setting(
                "safeModeStrengthOnStartup", self.safe_mode_strength_on_startup, 3
            ),
        )
        self.safe_mode_strength_on_startup_button.grid(
            row=2, column=0, padx=10, pady=5, sticky=ctk.NSEW
        )

        # endregion

    def change_locking_config(self, *_, backup: bool = False) -> None:
        if backup:
            config_title = self.backup_locking_config
        else:
            config_title = self.locking_config_dropdown.get()

        locking_configs = self.parent.file_manager.get_locking_configs()
        config_file = locking_configs.get(config_title)

        self.parent.logger.info(f'Changing locking config to "{config_title}"')

        try:
            self.parent.change_locking_config(config_file)
            self.backup_locking_config = config_title
        except Exception:
            self.parent.logger.error(
                f'Error loading locking config "{config_title}":\n{traceback.format_exc()}'
            )
            self.change_locking_config(backup=True)
            self.locking_config_dropdown.set(self.backup_locking_config)
            ErrorPopup(
                self.parent,
                message=f'Error loading config "{config_title}"\nCheck the logs for more information',
                size="400x100",
            )

    def change_setting(self, setting: str, variable: ctk.BooleanVar) -> None:
        variable.set(not variable.get())
        self.parent.file_manager.set_value(FILE.SETTINGS, setting, variable.get())

    def increment_setting(
        self, setting: str, variable: ctk.IntVar, max_value: int
    ) -> None:
        next_value = variable.get() + 1

        if next_value == max_value:
            variable.set(0)
        else:
            variable.set(next_value)

        self.parent.file_manager.set_value(FILE.SETTINGS, setting, variable.get())

    def next_anti_afk_mode(self) -> None:
        new_mode = self.parent.next_anti_afk_mode()
        self.anti_afk_mode = new_mode
        self.anti_afk_mode_intvar.set(new_mode.index)
        self.parent.file_manager.set_value(FILE.SETTINGS, "antiAfkMode", new_mode.name)

    def manual_update(self) -> None:
        if not self.initUI_called:
            self.initUI_called = True
            self.update_button.configure(
                state=ctk.DISABLED
            )
            self.parent.initUI(force_check_update=True)
            
            self.initUI_called = False
            self.after(1000, lambda: self.update_button.configure(
                state=ctk.NORMAL
            ))

    def on_raise(self) -> None:
        pass


# endregion


# region: Update Frame


class UpdateFrame(ctk.CTkFrame):
    default_config = {
        "fg_color": "background",
    }

    font_size: tuple[str, int]

    status_variables: dict[FILE, ctk.StringVar]
    version_variable: ctk.StringVar

    def __init__(self, parent: "VALocker", **kwargs) -> None:
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


# endregion
