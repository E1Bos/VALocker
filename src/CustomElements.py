import customtkinter as ctk
from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from GUI import GUI


# region: Labels


class ThemedLabel(ctk.CTkLabel):
    def __init__(self, parent: "GUI", text, **kwargs):
        super().__init__(parent, **kwargs)
        self.theme = parent.theme
        self.configure(
            text=text if text else "",
            font=self.theme["label"],
            text_color=self.theme["text"],
        )


class DependentLabel(ctk.CTkLabel):
    def __init__(self, parent: "GUI", variable: ctk.StringVar, **kwargs):
        super().__init__(parent, **kwargs)
        self.theme = parent.theme
        self.configure(
            font=self.theme["label"],
            text_color=self.theme["text"],
            textvariable=variable,
        )


# endregion

# region: Buttons


class ThemedButton(ctk.CTkButton):
    def __init__(self, parent, command: callable, **kwargs):
        super().__init__(parent, command=command, **kwargs)
        self.theme = parent.theme
        height = kwargs.get("height", 40)

        self.configure(
            corner_radius=5,
            height=height,
            text_color=self.theme["text"],
            hover=True,
            font=self.theme["button"],
        )


class IndependentButton(ThemedButton):
    def __init__(
        self,
        parent,
        text: Union[str, list[str]],
        variable: ctk.BooleanVar,
        command: callable,
        **kwargs,
    ):
        super().__init__(parent, command=command, **kwargs)
        self.parent = parent
        self.theme = parent.theme
        self.variable = variable

        if isinstance(text, str):  # Inefficient solution but solves my problem
            text = [text, text]

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

    def variable_update(self, *_):
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

    def get_current_text(self):
        return (
            self.text[2]
            if not self.dependent_variable.get()
            else self.text[0] if self.variable.get() else self.text[1]
        )


class SplitButton:
    def __init__(
        self,
        parent,
        text_left: list[str],
        text_right: list[str],
        variable_left: ctk.BooleanVar,
        variable_right: ctk.IntVar,
        command_left: callable,
        command_right: callable,
        **kwargs,
    ):
        # Store Vars
        self.parent = parent
        self.theme = parent.theme
        self.text_left = text_left
        self.text_right = text_right
        self.variable_left = variable_left
        self.variable_right = variable_right

        # Create Frame, make each column take up equal space
        self.frame = ThemedFrame(parent, fg_color="transparent", corner_radius=0)
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)

        # Create the left button
        self.left_button = ctk.CTkButton(
            self.frame,
            text=text_left[0] if variable_left.get() else text_left[1],
            command=command_left,
            fg_color=(
                self.theme["button-enabled"]
                if variable_left.get()
                else self.theme["button-disabled"]
            ),
            hover_color=(
                self.theme["button-enabled-hover"]
                if variable_left.get()
                else self.theme["button-disabled-hover"]
            ),
            font=self.theme["button"],
            corner_radius=5,
            height=40,
            text_color=self.theme["text"],
            hover=True,
        )

        # Create the right button
        self.right_button = ctk.CTkButton(
            self.frame,
            text=self.text_right[self.variable_right.get()],
            command=command_right,
            fg_color=self.theme["accent"],
            hover_color=self.theme["accent-hover"],
            font=self.theme["button"],
            corner_radius=5,
            height=40,
            text_color=self.theme["text"],
            hover=True,
        )

        self.draw_buttons()

        # Add the trace to the variables
        self.variable_left.trace_add("write", self.left_variable_update)
        self.variable_right.trace_add("write", self.right_variable_update)

    def draw_buttons(self):
        # If on
        if self.variable_left.get():
            # Forget the left button
            self.left_button.grid_forget()
            # Draw the buttons
            self.left_button.grid(row=0, column=0, sticky="nsew")
            self.right_button.grid(row=0, column=1, sticky="nsew")
        else:
            # Forget the right button, redraw the left button
            self.right_button.grid_forget()
            self.left_button.grid(row=0, column=0, columnspan=2, sticky="nsew")

    def left_variable_update(self, *_):
        self.left_button.configure(
            fg_color=(
                self.theme["button-enabled"]
                if self.variable_left.get()
                else self.theme["button-disabled"]
            ),
            text=self.text_left[0] if self.variable_left.get() else self.text_left[1],
            hover_color=(
                self.theme["button-enabled-hover"]
                if self.variable_left.get()
                else self.theme["button-disabled-hover"]
            ),
        )
        # Redraw the buttons
        self.draw_buttons()

    def right_variable_update(self, *_):
        self.right_button.configure(
            text=self.text_right[self.variable_right.get()],
        )


# endregion


class ThemedDropdown(ctk.CTkOptionMenu):
    def __init__(
        self,
        parent: "GUI",
        variable: ctk.StringVar,
        values: list[str],
        command: callable,
        **kwargs,
    ):
        super().__init__(parent, values=values, command=command, height=40, **kwargs)
        self.theme = parent.theme
        self.configure(
            # dynamic_resizing=False,
            font=self.theme["button"],
            corner_radius=5,
            text_color=self.theme["text"],
            hover=True,
            variable=variable,
        )

    def set_values(self, values: list[str]):
        self.configure(values=values)


# region: Frames


class ThemedFrame(ctk.CTkFrame):
    def __init__(self, parent: "GUI", **kwargs):
        super().__init__(parent, **kwargs)
        self.theme = parent.theme


class SideFrame(ctk.CTkFrame):
    def __init__(self, parent: "GUI"):
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


# endregion