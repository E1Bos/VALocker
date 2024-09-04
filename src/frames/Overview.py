"""
@author: [E1Bos](https://www.github.com/E1Bos)
"""

import customtkinter as ctk

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from VALocker import VALocker

# Custom Imports
from Constants import FILE, FRAME
from CustomElements import *


class OverviewUI(SideFrame):
    """
    The main frame that displays the program status and the agent status.
    """

    agent_dropdown: ThemedDropdown

    def __init__(self, parent: "VALocker") -> None:
        super().__init__(parent)

        self.main_overview_items = ThemedFrame(self, fg_color="transparent")

        # Make each frame take up equal space
        for frame in range(3):
            self.main_overview_items.grid_columnconfigure(frame, weight=1)

        # Make the frames take up the entire vertical space
        self.main_overview_items.grid_rowconfigure(0, weight=1)

        # Segmented Frames

        left_frame = ThemedFrame(self.main_overview_items)
        middle_frame = ThemedFrame(self.main_overview_items)
        right_frame = ThemedFrame(self.main_overview_items)

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

        self.agent_button = ThemedButton(
            middle_frame,
            textvariable=self.parent.selected_agent,
            command=self.show_agent_select_buttons,
        )
        self.agent_button.grid(row=1, column=0, sticky=ctk.NSEW, padx=10, pady=(0, 10))

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
            command=lambda: self.parent.toggle_tool(self.parent.anti_afk),
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

        # region: Agent Select Buttons
        self.select_agent_frame = ThemedFrame(self, fg_color="transparent")

        self.toggle_buttons: dict[str, ThemedButton] = {}

        # TODO: Implement fuzzy search
        # TODO: Implement keybinds to select (maybe smth with arrow keys)

        roles = self.parent.file_manager.get_value(FILE.AGENT_CONFIG, "roles")

        for index, role in enumerate(roles):

            self.select_agent_frame.grid_columnconfigure(index, weight=1)

            role_frame = ThemedFrame(self.select_agent_frame)

            role_label = ThemedLabel(
                role_frame,
                text=f"{role.capitalize()}s",
            )
            role_label.pack(side=ctk.TOP, pady=3, padx=5)

            for agent in self.parent.file_manager.get_value(FILE.AGENT_CONFIG, role):

                agent_button = ThemedButton(
                    role_frame,
                    text=agent.capitalize(),
                    fg_color=self.theme["foreground-highlight"],
                    hover_color=self.theme["foreground-highlight-hover"],
                    border_color=self.theme[role],
                    border_width=1,
                    command=lambda agent=agent: self.select_agent(agent),
                )
                self.toggle_buttons[agent] = agent_button

            role_frame.grid(
                row=0, column=index, sticky=ctk.NSEW, padx=5, pady=10, ipady=5
            )

        self.pack_unlocked_agents()
        self.select_agent(self.parent.selected_agent.get())

    def pack_unlocked_agents(self, loaded_save: bool = False) -> None:
        all_agents = self.parent.all_agents
        unlocked_agents = self.parent.get_unlocked_agents()

        for agent in all_agents:
            self.toggle_buttons[agent].pack_forget()

        for agent in unlocked_agents:
            self.toggle_buttons[agent].pack(side=ctk.TOP, padx=5, pady=2)

        if self.parent.selected_agent.get().lower() not in unlocked_agents:
            self.select_agent(unlocked_agents[0].capitalize())

        if loaded_save:
            self.select_agent()

    def select_agent(self, agent: str = None) -> None:
        if not agent:
            previous_agent = self.parent.get_unlocked_agents()
            agent = self.parent.selected_agent.get()
        else:
            previous_agent = [self.parent.selected_agent.get()]

        for prev_agent in previous_agent:
            self.toggle_buttons[prev_agent.lower()].configure(
                fg_color=self.theme["foreground-highlight"],
                hover_color=self.theme["foreground-highlight-hover"],
            )

        role = self.parent.get_agent_role_and_index(agent.lower(), efficient=False)[
            0
        ].value

        self.toggle_buttons[agent.lower()].configure(
            fg_color=self.theme[role],
            hover_color=self.theme[f"{role}-hover"],
        )

        self.agent_button.configure(
            fg_color=self.theme[role],
            hover_color=self.theme[f"{role}-hover"],
        )

        if previous_agent != agent:
            self.parent.selected_agent.set(agent.capitalize())

        self.on_raise()

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

    def show_agent_select_buttons(self) -> None:
        self.main_overview_items.pack_forget()
        self.select_agent_frame.pack(fill=ctk.BOTH, expand=True)
        self.select_agent_frame.bind("<Button-1>", lambda _: self.on_raise())
        self.parent.bind("<Button-3>", lambda _: self.on_raise())
        self.parent.bind("<Return>", lambda _: self.on_raise())
        self.parent.bind("<Escape>", lambda _: self.on_raise())
        self.parent.bind("<space>", lambda _: self.on_raise())

    def on_raise(self) -> None:
        self.select_agent_frame.pack_forget()
        self.main_overview_items.pack(fill=ctk.BOTH, expand=True)

        self.select_agent_frame.unbind("<Button-1>")
        self.parent.unbind("<Button-3>")
        self.parent.unbind("<Return>")
        self.parent.unbind("<Escape>")
        self.parent.unbind("<space>")
