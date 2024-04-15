import customtkinter as ctk
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from GUI import GUI

class ThemedFrame(ctk.CTkFrame):
    def __init__(self, parent: 'GUI', **kwargs):
        super().__init__(parent, **kwargs)
        self.theme = parent.theme

class ThemedLabel(ctk.CTkLabel):
    def __init__(self, parent: 'GUI', text, **kwargs):
        super().__init__(parent, text=text, **kwargs)
        self.theme = parent.theme
        self.configure(
            font=self.theme["label"],
            text_color=self.theme["text"],
        )

class ThemedButton(ctk.CTkButton, ABC):
    def __init__(self, parent, command: callable, **kwargs):
        super().__init__(parent, command=command, **kwargs)
        self.theme = parent.theme

        self.configure(
            corner_radius=5,
            height=40,
            hover=True,
            font=self.theme["button"],
        )

    @abstractmethod
    def variable_update(self, *args):
        pass

class IndependentButton(ThemedButton):
    def __init__(
        self,
        parent,
        text: list[str],
        variable: ctk.BooleanVar,
        command: callable,
        **kwargs,
    ):
        super().__init__(parent, command=command, **kwargs)
        self.parent = parent
        self.theme = parent.theme
        self.variable = variable
        self.text = text
        self.disabled = False

        self.configure(
            text=self.text[0] if self.variable.get() else self.text[1],
            font=self.theme["button"],
            fg_color=(
                self.theme["button-enabled"]
                if self.variable.get()
                else self.theme["button-disabled"]
            ),
            hover_color=(
                self.theme["button-enabled-hover"]
                if self.variable.get()
                else self.theme["button-disabled-hover"]
            ),
        )

        self.variable.trace_add("write", self.variable_update)

    def variable_update(self, *args):
        self.configure(
            fg_color=(
                self.theme["button-enabled"]
                if self.variable.get()
                else self.theme["button-disabled"]
            ),
            text=self.text[0] if self.variable.get() else self.text[1],
            hover_color=(
                self.theme["button-enabled-hover"]
                if self.variable.get()
                else self.theme["button-disabled-hover"]
            ),
        )

    def toggle_disable(self):
        self.disabled = not self.disabled
        if not self.disabled:
            self.configure(state=ctk.NORMAL)
        else:
            self.configure(
                state=ctk.DISABLED,
            )

class DependentButton(ThemedButton):
    def __init__(
        self,
        parent,
        text: list[str],
        variable: ctk.BooleanVar,
        dependent_variable: ctk.BooleanVar,
        command: callable,
        **kwargs,
    ):
        super().__init__(parent, command=command, **kwargs)
        self.parent = parent
        self.variable = variable
        self.dependent_variable = dependent_variable
        self.text = text

        self.configure(
            text=self.get_current_text(),
            fg_color=self.theme["accent"],
            hover_color=self.theme["accent-hover"],
        )

        self.variable.trace_add("write", self.variable_update)
        self.dependent_variable.trace_add("write", self.dependent_variable_update)
        self.check_disable()

    def variable_update(self, *args):
        self.configure(text=self.get_current_text())

    def dependent_variable_update(self, *args):
        self.configure(text=self.get_current_text())
        self.check_disable()

    def check_disable(self):
        if self.dependent_variable.get():
            self.configure(state=ctk.NORMAL)
        else:
            self.configure(state=ctk.DISABLED)

    def get_current_text(self):
        return (
            self.text[2]
            if not self.dependent_variable.get()
            else self.text[0] if self.variable.get() else self.text[1]
        )

class SideFrame(ctk.CTkFrame):
    def __init__(self, parent: 'GUI'):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.parent = parent
        self.theme = parent.theme

    def get_button_color(self, var: ctk.BooleanVar) -> str:
        return (
            self.parent.theme["button-enabled"]
            if var.get()
            else self.parent.theme["button-disabled"]
        )

    def get_button_text(self, var: ctk.BooleanVar, text: list[str]) -> str:
        return text[0] if var.get() else text[1]