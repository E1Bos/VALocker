import customtkinter as ctk

from ProjectUtils import BRIGHTEN_COLOR

from GUI.CustomElements import (
    ThemedFrame,
    ThemedLabel,
    ThemedButton,
    ThemedDropdown,
    IndependentButton,
    DependentButton,
    SplitButton,
    DependentLabel,
    SideFrame,
)

class NavigationFrame(ctk.CTkFrame):
    def __init__(self, parent, width):
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

        buttons = [
            "Overview",
            "Save Files",
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

    def change_active_frame(self, button):
        self.parent.frames[button].tkraise()

    def quit_program(self):
        self.parent.exit()

class OverviewFrame(SideFrame):
    def __init__(self, parent: ctk.CTk):
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
            frame.configure(fg_color=self.theme["foreground"])
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

    def toggle_boolean(self, var: ctk.BooleanVar, value=None):
        if value is not None:
            var.set(value)
        else:
            var.set(not var.get())

    def toggle_safe_mode(self):
        self.toggle_boolean(self.parent.safe_mode_enabled)
        self.parent.update_stats()

    def increment_save_mode_strength(self):
        self.parent.safe_mode_strength.set(
            (self.parent.safe_mode_strength.get() + 1) % 3
        )
        self.parent.update_stats()

    def redirect_save_files_frame(self):
        self.parent.frames["Save Files"].tkraise()

    def redirect_tools_frame(self):
        self.parent.frames["Tools"].tkraise()

    def update_current_save_button(self, *_):
        self.save_button.configure(text=self.parent.current_save_name.get())

    def select_agent(self, *_):
        # TODO: Implement this method
        print(self.parent.selected_agent.get())

    def toggle_hover(self, *_):
        self.parent.instalocker.toggle_hover()

    def toggle_random_select(self, *_):
        self.parent.instalocker.toggle_random_select()

    def toggle_map_specific(self, *_):
        self.parent.instalocker.toggle_map_specific()

    def toggle_anti_afk(self, *_):
        self.parent.tools.toggle_anti_afk()

    def toggle_drop_spike(self, *_):
        self.parent.tools.toggle_drop_spike()
