"""
@author: [E1Bos](https://www.github.com/E1Bos)
"""

import traceback
import customtkinter as ctk

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from VALocker import VALocker

# Custom Imports
from Constants import FILE, FRAME, ANTI_AFK
from CustomElements import *


class SettingsUI(SideFrame):
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

        update_and_reset_frame = ThemedFrame(scrollable_frame, fg_color="transparent")
        update_and_reset_frame.pack(fill=ctk.X, pady=(0, 10), padx=0)

        update_and_reset_frame.grid_columnconfigure(0, weight=4)
        update_and_reset_frame.grid_columnconfigure(1, weight=1)

        self.update_button = ThemedButton(
            update_and_reset_frame,
            text="Check for Updates",
            command=self.manual_update,
            corner_radius=10,
        )
        self.update_button.pack(
            side=ctk.LEFT, fill=ctk.X, expand=True, padx=(0, 5), pady=0
        )

        self.reset_button = ThemedButton(
            update_and_reset_frame,
            text="Reset",
            command=self.reset_configs,
            corner_radius=10,
            fg_color=self.theme["button-disabled"],
            hover_color=self.theme["button-disabled-hover"],
            width=0,
        )
        self.reset_button.pack(side=ctk.LEFT, padx=0, pady=0)

        # endregion

        # region: Locking Config Section
        locking_configs = self.parent.file_manager.get_locking_configs()
        self.current_locking_config = ctk.StringVar(
            value=self.parent.file_manager.get_locking_config_by_file_name(
                self.parent.file_manager.get_value(FILE.SETTINGS, "$lockingConfig"),
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
        self.locking_config_dropdown.pack(
            fill=ctk.X, padx=10, pady=5, side=ctk.LEFT, expand=True
        )
        self.current_locking_config.trace_add("write", self.change_locking_config)

        self.generate_config_button = ThemedButton(
            locking_config_frame,
            image=ctk.CTkImage(Image.open(ICON.NEW_FILE.value), size=(20, 20)),
            text="",
            width=0,
            command=self.generate_config,
            corner_radius=10,
        )
        # TODO: GET CONFIG GENERATOR TO WORK
        # self.generate_config_button.pack(padx=(0,10), pady=5, side=ctk.LEFT)

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
            row=0, column=0, sticky=ctk.NSEW, columnspan=2, padx=10, pady=5
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
            row=0, column=0, sticky=ctk.NSEW, columnspan=2, padx=10, pady=5
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
        self.parent.file_manager.set_value(FILE.SETTINGS, "$antiAfkMode", new_mode.name)

    def manual_update(self) -> None:
        if not self.initUI_called:
            self.initUI_called = True
            self.update_button.configure(state=ctk.DISABLED)
            self.parent.init(force_check_update=True, set_frame=FRAME.SETTINGS)

            self.initUI_called = False
            self.after(1000, lambda: self.update_button.configure(state=ctk.NORMAL))

    def reset_configs(self) -> None:
        confirm = ConfirmPopup(
            self.parent,
            title="Reset Configurations",
            message="Are you sure you want to reset all configs?\nThis cannot be undone.\n\nYour save files will not be affected.\nThe default save file will be reset.\n\nYour current configs will be backed up.",
            geometry="400x200",
        ).get_input()

        if not confirm:
            return

        self.parent.file_manager.reset_configs()

        self.parent.init(reset_config=True, set_frame=FRAME.OVERVIEW)

    def generate_config(self) -> None:
        print("Generating config...")

    def on_raise(self) -> None:
        pass
