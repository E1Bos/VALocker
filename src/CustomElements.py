import customtkinter as ctk
from typing import TYPE_CHECKING, Callable, List, Union, Dict, Any
from Constants import BRIGHTEN_COLOR
from abc import abstractmethod

if TYPE_CHECKING:
    from VALocker import VALocker


# region: Labels


class ThemedLabel(ctk.CTkLabel):
    theme: dict[str, str]
    default_config: dict[str, str] = {
        "font": "label",
        "text_color": "text",
    }

    def __init__(
        self,
        parent: "VALocker",
        text: str = None,
        variable: ctk.StringVar = None,
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
        parent: "ctk.CTkFrame",
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
        parent: "ctk.CTkFrame",
        text: list[str],
        variable: ctk.BooleanVar,
        dependent_variable: ctk.BooleanVar,
        command: callable,
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
        parent: "ctk.CTkFrame",
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
