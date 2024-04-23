import customtkinter as ctk
from PIL import Image
import os
from typing import TYPE_CHECKING, Callable, List, Union, Dict, Any
from Constants import BRIGHTEN_COLOR, RESOURCE_PATH, ICON, FILE
from abc import abstractmethod

if TYPE_CHECKING:
    from VALocker import VALocker, SaveFilesFrame


# region: Labels


class ThemedLabel(ctk.CTkLabel):
    theme: dict[str, str]
    default_config: dict[str, str] = {
        "font": "label",
        "text_color": "text",
    }

    def __init__(
        self,
        parent: "SideFrame",
        text: str = "",
        variable: Union[ctk.StringVar, None] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(parent, **kwargs)
        self.theme = parent.theme

        config = {
            key: kwargs.get(key, parent.theme.get(value, value))
            for key, value in self.default_config.items()
        }
        config.update(kwargs)

        self.configure(**config)

        if variable:
            self.configure(textvariable=variable)
        else:
            self.configure(text=text if text else "")


# endregion

# region: Buttons


class ThemedButton(ctk.CTkButton):
    default_config = {
        "font": "button",
        "text_color": "text",
        "fg_color": "accent",
        "hover_color": "accent-hover",
        "corner_radius": 5,
        "height": 40,
        "hover": True,
    }

    theme: dict[str, str]

    def __init__(self, parent: "SideFrame", *args, **kwargs) -> None:
        self.theme = parent.theme

        config = {
            key: kwargs.get(key, parent.theme.get(value, value))
            for key, value in self.default_config.items()
        }
        config["text_color_disabled"] = BRIGHTEN_COLOR(config["text_color"], 0.5)
        config.update(kwargs)

        super().__init__(parent, *args, **config)


class IndependentButton(ThemedButton):
    text: list[str]
    variable: ctk.BooleanVar

    def __init__(
        self,
        parent: "SideFrame",
        text: Union[str, list[str]],
        variable: ctk.BooleanVar,
        command: Callable,
        **kwargs,
    ) -> None:

        self.command = command
        self.variable = variable

        if isinstance(text, str):
            text = [text, text]

        super().__init__(parent, **kwargs)

        self.text = text
        self.disabled = False
        self._update_button()

        self.variable.trace_add("write", self._variable_update)

    def _update_button(self) -> None:
        is_enabled = self.variable.get()
        self.configure(
            text=self.text[0] if is_enabled else self.text[1],
            fg_color=self.theme["button-enabled" if is_enabled else "button-disabled"],
            hover_color=self.theme[
                "button-enabled-hover" if is_enabled else "button-disabled-hover"
            ],
            command=self.command,
        )

    def _variable_update(self, *_):
        self._update_button()

    def toggle_disable(self) -> None:
        self.disabled = not self.disabled
        self.configure(state=ctk.NORMAL if not self.disabled else ctk.DISABLED)


class DependentButton(ThemedButton):
    dependent_variable: ctk.BooleanVar
    variable: ctk.BooleanVar
    text: list[str]

    def __init__(
        self,
        parent: "SideFrame",
        text: list[str],
        variable: ctk.BooleanVar,
        dependent_variable: ctk.BooleanVar,
        command: Callable[..., None],
        **kwargs,
    ):
        super().__init__(parent, command=command, **kwargs)
        self.dependent_variable = dependent_variable
        self.variable = variable
        self.text = text

        self.configure(
            text=self.get_current_text(),
            fg_color=self.theme["accent"],
            hover_color=self.theme["accent-hover"],
        )

        self.variable.trace_add("write", self.variable_update)
        self.dependent_variable.trace_add("write", self.dependent_variable_update)
        self.check_disable()

    def variable_update(self, *_):
        self.configure(text=self.get_current_text())

    def dependent_variable_update(self, *_):
        self.configure(text=self.get_current_text())
        self.check_disable()

    def check_disable(self):
        if self.dependent_variable.get():
            self.configure(state=ctk.NORMAL)
        else:
            self.configure(state=ctk.DISABLED)

    def get_current_text(self) -> str:
        return (
            self.text[2]
            if not self.dependent_variable.get()
            else self.text[0] if self.variable.get() else self.text[1]
        )


class SplitButton:
    parent: object
    theme: dict[str, str]

    def __init__(
        self,
        parent: "ThemedFrame",
        text_left: list[str],
        text_right: list[str],
        variable_left: ctk.BooleanVar,
        variable_right: ctk.IntVar,
        command_left: Callable,
        command_right: Callable,
        **kwargs,
    ) -> None:
        self.theme = parent.theme
        self.text_left = text_left
        self.text_right = text_right
        self.variable_left = variable_left
        self.variable_right = variable_right

        default_config = {
            "font": self.theme["button"],
            "text_color": self.theme["text"],
            "corner_radius": 5,
            "height": 40,
            "hover": True,
        }
        default_config.update(kwargs)

        self.frame = ThemedFrame(parent, fg_color="transparent", corner_radius=0)
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)

        self.left_button = ctk.CTkButton(
            self.frame,
            command=command_left,
            **default_config,
        )

        self.right_button = ctk.CTkButton(
            self.frame,
            command=command_right,
            **default_config,
        )

        self.left_variable_update()
        self.right_variable_update()
        self.draw_buttons()

        self.variable_left.trace_add("write", self.left_variable_update)
        self.variable_right.trace_add("write", self.right_variable_update)

    def draw_buttons(self) -> None:
        if self.variable_left.get():
            self.left_button.grid_forget()
            self.left_button.grid(row=0, column=0, sticky="nsew")
            self.right_button.grid(row=0, column=1, sticky="nsew")
        else:
            self.right_button.grid_forget()
            self.left_button.grid(row=0, column=0, columnspan=2, sticky="nsew")

    def left_variable_update(self, *_):
        self.left_button.configure(
            text=self.text_left[0] if self.variable_left.get() else self.text_left[1],
            fg_color=(
                self.theme["button-enabled"]
                if self.variable_left.get()
                else self.theme["button-disabled"]
            ),
            hover_color=(
                self.theme["button-enabled-hover"]
                if self.variable_left.get()
                else self.theme["button-disabled-hover"]
            ),
        )
        self.draw_buttons()

    def right_variable_update(self, *_):
        self.right_button.configure(
            text=self.text_right[self.variable_right.get()],
        )

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)

    def grid(self, **kwargs):
        self.frame.grid(**kwargs)


class SaveButton:
    icon_config = {
        "text_color": "text",
        "fg_color": "transparent",
        "hover_color": "foreground-highlight-hover",
        "corner_radius": 10,
        "text": "",
        "width": 40,
    }

    frame_config = {
        "fg_color": "foreground-highlight",
        "corner_radius": 10,
    }

    frame_colors = {"selected": "green", "unselected": "red"}

    icon_size = (20, 20)
    favorite_on_img = ctk.CTkImage(Image.open(ICON.FAVORITE_ON.value), size=icon_size)
    favorite_off_img = ctk.CTkImage(Image.open(ICON.FAVORITE_OFF.value), size=icon_size)
    rename_img = ctk.CTkImage(Image.open(ICON.RENAME.value), size=icon_size)
    delete_img = ctk.CTkImage(Image.open(ICON.DELETE.value), size=icon_size)

    parent: "ThemedScrollableFrame"
    side_frame: "SaveFilesFrame"
    theme: Dict[str, str]
    save_file: str

    selected: bool
    favorited: bool

    def __init__(
        self,
        parent: "ThemedScrollableFrame",
        save_file: str,
        **kwargs,
    ) -> None:
        self.parent = parent
        self.side_frame = parent.parent
        self.theme = parent.theme

        # Selected
        self.selected = False

        # File Name
        self.save_file = save_file
        self.save_name = save_file.removesuffix(".json")

        # If is favorited
        self.favorited = False

        frame_config = {
            key: kwargs.get(key, self.theme.get(value, value))
            for key, value in self.frame_config.items()
        }

        icon_config = {
            key: kwargs.get(key, self.theme.get(value, value))
            for key, value in self.icon_config.items()
        }

        self.frame = ThemedFrame(parent, **frame_config)

        self.save_label = ThemedLabel(
            self.frame, text=self.save_name, corner_radius=0, fg_color="transparent"
        )
        self.save_label.grid(row=0, column=0, sticky=ctk.W, pady=5, padx=10)

        self.frame.columnconfigure(0, weight=1)

        for element in [self.save_label, self.frame]:
            element.bind("<Button-1>", self.select_save)
            element.bind("<Enter>", self.on_hover)
            element.bind("<Leave>", self.on_exit_hover)

        self.favorite_icon = ThemedButton(
            self.frame,
            image=self.favorite_off_img,
            command=self.toggle_favorite,
            **icon_config,
        )

        self.rename_icon = ThemedButton(
            self.frame,
            image=self.rename_img,
            command=self.rename,
            **icon_config,
        )

        self.delete_icon = ThemedButton(
            self.frame,
            image=self.delete_img,
            command=self.delete,
            **icon_config,
        )

        self.icons = [self.favorite_icon]

        is_default = self.save_file != os.path.basename(FILE.DEFAULT_SAVE.value)

        if is_default:
            self.icons.extend([self.rename_icon, self.delete_icon])

        for col, icon in enumerate(self.icons):
            padx = (0, 5) if col == len(self.icons) - 1 else 0
            icon.grid(row=0, column=col + 1, sticky=ctk.E, pady=5, padx=padx)

    def select_save(self, *_):
        """
        Selects the save and updates the side frame accordingly.
        This only runs when a button is clicked.

        If the save is already selected, the method does nothing.

        Parameters:
        *_: Variable number of arguments (unused).

        Returns:
        None
        """
        if self.selected:
            return

        self.side_frame.change_save(self.save_name)
        self.set_selected(True)

    def set_selected(self, value: bool):
        """
        Sets the selected state of the element.
        This method is also run when the element is selected and when the button is first loaded.

        Args:
            value (bool): The value to set the selected state to.

        Returns:
            None
        """
        self.selected = value
        self.configure_icons()
        self.on_exit_hover()

    # region: Icon Commands

    def toggle_favorite(self):
        """
        Toggles the favorite status of the element.

        This method updates the `favorited` attribute of the element and
        changes the image of the favorite icon accordingly. It also calls
        the `favorite_button` method of the `side_frame` object, passing
        itself as an argument.

        """
        self.favorited = not self.favorited

        self.favorite_icon.configure(
            image=self.favorite_on_img if self.favorited else self.favorite_off_img
        )

        self.side_frame.favorite_button(self)

    def rename(self):
        # TODO: IMPLEMENT
        print(f"{self.save_file} renaming")

    def delete(self):
        # TODO: IMPLEMENT
        print(f"{self.save_file} deleted")

    # endregion

    def configure_icons(self):
        config = {
            "hover_color": self.theme["foreground-highlight-hover"],
        }

        if self.selected:
            config["hover_color"] = self.theme["accent-hover"]

        for icon in self.icons:
            icon.configure(**config)

    # region: Hover Effects

    def on_hover(self, *_):
        if not self.selected:
            self.frame.configure(fg_color=self.theme["foreground-highlight-hover"])
        else:
            self.frame.configure(fg_color=self.theme["accent-hover"])

    def on_exit_hover(self, *_):
        if not self.selected:
            self.frame.configure(fg_color=self.theme["foreground-highlight"])
        else:
            self.frame.configure(fg_color=self.theme["accent"])

    # endregion

    def grid(self, **kwargs):
        self.frame.grid(**kwargs)

    def grid_forget(self):
        self.frame.grid_forget()


# endregion


class ThemedDropdown(ctk.CTkOptionMenu):
    default_config: Dict[str, Union[str, int, bool]] = {
        "font": "button",
        "text_color": "text",
        "fg_color": "accent",
        "corner_radius": 5,
        "height": 40,
        "hover": True,
    }

    parent: "VALocker"
    theme: Dict[str, str]

    def __init__(
        self,
        parent: "VALocker",
        variable: ctk.StringVar,
        values: List[str],
        command: Callable,
        **kwargs: Union[str, int, bool],
    ) -> None:
        self.parent = parent
        super().__init__(
            parent,
            variable=variable,
            values=values,
            command=command,
            **self._configure_dropdown(parent.theme, kwargs),
        )

    def _configure_dropdown(
        self, theme: Dict[str, str], kwargs: Dict[str, Union[str, int, bool]]
    ) -> Dict[str, Union[str, int, bool]]:
        config = {
            key: kwargs.get(key, theme.get(value, value))
            for key, value in self.default_config.items()
        }
        config["button_color"] = BRIGHTEN_COLOR(config["fg_color"], 0.8)
        config["button_hover_color"] = BRIGHTEN_COLOR(config["fg_color"], 0.75)
        config.update(kwargs)
        return config

    def set_values(self, values: List[str]) -> None:
        self.configure(values=values)

    def disable(self) -> None:
        self.configure(state=ctk.DISABLED)

    def enable(self) -> None:
        self.configure(state=ctk.NORMAL)


# region: Checkboxes


class ThemedCheckbox(ctk.CTkCheckBox):
    default_config = {
        "font": "button",
        "text_color": "text",
        "fg_color": "accent",
        "hover_color": "accent-hover",
        "corner_radius": 5,
        "hover": True,
    }

    def __init__(
        self,
        parent: "VALocker",
        text: str,
        variable: ctk.BooleanVar,
        **kwargs,
    ):
        config = {
            key: kwargs.get(key, parent.theme.get(value, value))
            for key, value in self.default_config.items()
        }

        config.update(kwargs)

        super().__init__(parent, text=text, variable=variable, **config)

    def disable(self):
        self.configure(state=ctk.DISABLED)

    def enable(self):
        self.configure(state=ctk.NORMAL)


class DependentCheckbox(ThemedCheckbox):
    variable: ctk.BooleanVar
    dependent_variable: ctk.BooleanVar

    def __init__(
        self,
        parent: "VALocker",
        text: str,
        variable: ctk.BooleanVar,
        dependent_variable: ctk.BooleanVar,
        **kwargs,
    ):
        super().__init__(parent, text=text, variable=variable, **kwargs)
        self.variable = variable
        self.dependent_variable = dependent_variable
        self.dependent_variable.trace_add("write", self.dependent_variable_update)
        self._pending_config = None
        self.dependent_variable_update()

    def dependent_variable_update(self, *_):
        if self.dependent_variable.get():
            self._pending_config = ctk.NORMAL
        else:
            self._pending_config = ctk.DISABLED
            self.variable.set(False)

        self.after_idle(self.apply_pending_config)

    def apply_pending_config(self):
        if self._pending_config is not None:
            self.configure(state=self._pending_config)
            self._pending_config = None


# endregion

# region: Frames


class ThemedFrame(ctk.CTkFrame):
    default_config = {
        "fg_color": "foreground",
        "corner_radius": 10,
    }

    def __init__(self, parent: "VALocker", **kwargs):

        self.theme = parent.theme

        config = {
            key: kwargs.get(key, parent.theme.get(value, value))
            for key, value in self.default_config.items()
        }
        config.update(kwargs)

        super().__init__(
            parent,
            **config,
        )


class SideFrame(ctk.CTkFrame):
    parent: "VALocker"
    theme: dict[str, str]

    def __init__(self, parent: "VALocker") -> None:
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.parent = parent
        self.theme = parent.theme

    def get_button_color(self, var: ctk.BooleanVar) -> str:
        return (
            self.theme["button-enabled"] if var.get() else self.theme["button-disabled"]
        )

    def get_button_text(self, var: ctk.BooleanVar, text: list[str]) -> str:
        return text[0] if var.get() else text[1]

    @abstractmethod
    def on_raise(self) -> None:
        """
        This method is called when the element is raised.
        It performs some actions related to the raising behavior.
        """
        pass


class ThemedScrollableFrame(ctk.CTkScrollableFrame):
    default_config = {
        "fg_color": "foreground",
        "label_fg_color": "foreground-highlight",
        "scrollbar_button_color": "accent",
        "scrollbar_button_hover_color": "accent-hover",
        "corner_radius": 10,
        "label_font": "label",
        "label_text_color": "text",
        "label_anchor": ctk.CENTER,
    }
    parent: "SideFrame"
    theme: dict[str, str]

    def __init__(self, parent: "SideFrame", **kwargs) -> None:
        self.parent = parent
        self.theme = parent.theme

        config = {
            key: kwargs.get(key, parent.theme.get(value, value))
            for key, value in self.default_config.items()
        }
        config.update(kwargs)

        super().__init__(parent, **config)


# endregion
