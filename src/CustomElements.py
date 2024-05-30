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
    """
    A button that is styled according to the VALocker theme.
    """

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
    """
    A button that is enabled, independent of any other variable.
    It changes its text and color based on the state of its own variable.
    """

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
    """
    Button that is dependent on two variables,
    one that determines if the button is enabled,
    and the other that the button is responsable for.

    The button will change its text based on the state of the dependent variable and the variable.
    """

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
        self.dependent_variable = dependent_variable
        self.variable = variable
        self.text = text

        config = {"text": self.get_current_text()}
        config.update(kwargs)

        super().__init__(parent, command=command, **config)

        self.variable.trace_add("write", self.variable_update)
        self.dependent_variable.trace_add("write", self.dependent_variable_update)
        self.check_disable()

    def variable_update(self, *_):
        config = {"text": self.get_current_text()}
        self.configure(**config)

    def dependent_variable_update(self, *_):
        self.variable_update()
        self.check_disable()

    def check_disable(self):
        if self.dependent_variable.get():
            self.configure(state=ctk.NORMAL)
        else:
            self.configure(state=ctk.DISABLED)

    def get_current_text(self) -> str:
        if type(self.text) == str:
            return self.text

        return (
            self.text[2]
            if not self.dependent_variable.get()
            else self.text[0] if self.variable.get() else self.text[1]
        )


class ColorDependentButton(ThemedButton):
    """
    Button that is dependent on two variables,
    one that determines if the button is enabled,
    and the other that the button is responsable for.

    The button will change its color based on both the state of the dependent and independent variable.

    This is equivalent to the IndependentButton, but is dependent on a second variable.
    """

    dependent_variable: ctk.BooleanVar
    variable: ctk.BooleanVar
    text: list[str]

    def __init__(
        self,
        parent: "SideFrame",
        variable: ctk.BooleanVar,
        dependent_variable: ctk.BooleanVar,
        command: Callable[..., None],
        **kwargs,
    ):
        self.theme = parent.theme
        self.dependent_variable = dependent_variable
        self.variable = variable

        config = self.get_color()
        config.update(kwargs)

        super().__init__(parent, command=command, **config)

        self.variable.trace_add("write", self.variable_update)
        self.dependent_variable.trace_add("write", self.dependent_variable_update)
        self.check_disable()

    def get_color(self) -> str:
        config = {
            "fg_color": (
                self.theme["button-enabled"]
                if self.variable.get()
                else self.theme["button-disabled"]
            ),
            "hover_color": (
                self.theme["button-enabled-hover"]
                if self.variable.get()
                else self.theme["button-disabled-hover"]
            ),
        }

        return config

    def variable_update(self, *_):
        config = self.get_color()
        self.configure(**config)

    def dependent_variable_update(self, *_):
        config = self.get_color()
        self.configure(**config)
        self.check_disable()

    def check_disable(self):
        if self.dependent_variable.get():
            self.configure(state=ctk.NORMAL)
        else:
            self.configure(state=ctk.DISABLED)
            self.variable.set(False)


class SplitButton:
    """
    When disabled, the button is a single button.
    When enabled, the button splits into two buttons.

    The buttons can be customized with different text and commands.
    """

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
    """
    Button that represents a save file.

    The button has a label with the name of the save file and three icons:
    - A favorite icon that toggles the favorite status of the save.
    - A rename icon that renames the save file.
    - A delete icon that deletes the save file.

    The button is styled according to the VALocker theme.

    """

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
        self.save_name = save_file.removesuffix(".yaml")

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
            command=lambda: self.toggle_favorite(reorderList=True),
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

        self.side_frame.change_save(self)
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

    def toggle_favorite(self, value: bool = None, reorderList: bool = False):
        """
        Toggles the favorite status of the element.

        This method updates the `favorited` attribute of the element and
        changes the image of the favorite icon accordingly. It also calls
        the `favorite_button` method of the `side_frame` object, passing
        itself as an argument.

        """
        if value is not None:
            self.favorited = value
        else:
            self.favorited = not self.favorited

        self.favorite_icon.configure(
            image=self.favorite_on_img if self.favorited else self.favorite_off_img
        )

        self.side_frame.favorite_button(self, reorderList=reorderList)

    def rename(self):
        self.side_frame.rename_save(self)

    def change_text(self, text: str):
        self.save_label.configure(text=text)
        self.save_name = text
        self.save_file = text + ".yaml"

    def delete(self):
        self.side_frame.delete_save(self)

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

    def destroy(self):
        self.frame.destroy()

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
        **kwargs: Union[str, int, bool],
    ) -> None:
        self.parent = parent
        super().__init__(
            parent,
            variable=variable,
            values=values,
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

# region: Popups


class ThemedPopup(ctk.CTkToplevel):
    default_config = {
        "fg_color": "background",
    }

    def __init__(self, parent: "VALocker", title, geometry: str, **kwargs):
        self.parent = parent
        self.theme = parent.theme

        config = {
            key: kwargs.get(key, parent.theme.get(value, value))
            for key, value in self.default_config.items()
        }
        config.update(kwargs)

        super().__init__(**config)
        self.geometry(geometry)

        self.title(title)
        self.lift()  # lift window on top
        self.attributes("-topmost", True)  # stay on top
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.after(
            10, self.create_widgets
        )  # create widgets with slight delay, to avoid white flickering of background
        self.resizable(False, False)
        self.grab_set()  # make other windows not clickable
        self.calculate_position()

    @abstractmethod
    def create_widgets(self):
        pass

    def calculate_position(self):
        mw_size, mw_x_shift, mw_y_shift = self.parent.winfo_geometry().split("+")
        mw_size_x, mw_size_y = map(int, mw_size.split("x"))
        mw_x_shift, mw_y_shift = map(int, [mw_x_shift, mw_y_shift])

        popup_size, _, _ = self.geometry().split("+")
        popup_size_x, popup_size_y = map(int, popup_size.split("x"))

        # center the window
        self.geometry(
            "+%d+%d"
            % (
                mw_x_shift + (mw_size_x - popup_size_x) // 2,
                mw_y_shift + (mw_size_y - popup_size_y) // 2,
            )
        )

    def on_closing(self):
        self.grab_release()
        self.destroy()


class InputDialog(ThemedPopup):
    """
    Modified version of the InputDialog class from the customtkinter library to use the active theme.
    See https://github.com/TomSchimansky/CustomTkinter for the original class.
    """

    theme: dict[str, str]

    def __init__(
        self,
        parent: "VALocker",
        title: str,
        label: str,
        placeholder: str = None,
        prefill: str = None,
        **kwargs,
    ):

        self.theme = parent.theme

        super().__init__(parent, title, "300x170", **kwargs)

        self.user_input: Union[str, None] = None
        self.parent = parent
        self.label = label
        self.placeholder = placeholder if placeholder else ""
        self.prefill = prefill

    def create_widgets(self):
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0,1,2), weight=1)

        self.label = ThemedLabel(
            self, width=300, wraplength=300, fg_color="transparent", text=self.label
        )
        self.label.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.entry = ctk.CTkEntry(
            self,
            width=230,
            height=40,
            fg_color=self.theme["foreground"],
            text_color=self.theme["text"],
            font=self.theme["label"],
        )
        self.entry.grid(
            row=1, column=0, columnspan=2, padx=10, pady=(0, 10), sticky="ew"
        )

        if self.prefill:
            self.entry.insert(0, self.prefill)

        self.ok_button = ThemedButton(
            self,
            fg_color=self.theme["button-enabled"],
            hover_color=self.theme["button-enabled-hover"],
            text="Ok",
            height=30,
            command=self.ok_event,
        )
        self.ok_button.grid(
            row=2, column=1, columnspan=1, padx=(20, 10), pady=(0, 10), sticky="ew"
        )

        self.cancel_button = ThemedButton(
            self,
            fg_color=self.theme["button-disabled"],
            hover_color=self.theme["button-disabled-hover"],
            text="Cancel",
            height=30,
            command=self.cancel_event,
        )
        self.cancel_button.grid(
            row=2, column=0, columnspan=1, padx=(10, 20), pady=(0, 10), sticky="ew"
        )

        self.after(
            150, lambda: self.entry.focus()
        )  # set focus to entry with slight delay, otherwise it won't work
        self.entry.bind("<Return>", self.ok_event)
        self.entry.bind("<Escape>", self.cancel_event)

    def ok_event(self, event=None):
        self.user_input = self.entry.get()
        self.grab_release()
        self.destroy()

    def cancel_event(self):
        self.grab_release()
        self.destroy()

    def get_input(self):
        self.master.wait_window(self)
        return self.user_input


class ErrorPopup(ThemedPopup):
    theme: dict[str, str]

    def __init__(self, parent: "VALocker", message: str, **kwargs):
        self.theme = parent.theme
        self.message = message

        super().__init__(parent, "Error", "300x100", **kwargs)

    def create_widgets(self):
        self.label = ThemedLabel(
            self,
            text=self.message,
        )
        self.label.pack(side=ctk.TOP, padx=10, pady=10)

        self.ok_button = ThemedButton(self, text="Ok", height=30, command=self.destroy)
        self.ok_button.pack(side=ctk.BOTTOM, padx=10, pady=10)

        self.bind("<Return>", lambda e: self.destroy())
        self.master.wait_window(self)


class ConfirmPopup(ThemedPopup):
    theme: dict[str, str]

    def __init__(self, parent: "VALocker", title: str, message: str, **kwargs):
        self.theme = parent.theme
        self.message = message
        self.confirm = False

        super().__init__(parent, title, "300x150", **kwargs)

    def create_widgets(self):
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1), weight=1)
        
        self.label = ThemedLabel(
            self,
            text=self.message,
        )
        self.label.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        self.ok_button = ThemedButton(
            self,
            text="Yes",
            height=30,
            command=self.ok_event,
            fg_color=self.theme["button-disabled"],
            hover_color=self.theme["button-disabled-hover"],
        )
        self.ok_button.grid(
            row=1, column=1, columnspan=1, padx=(10, 20), pady=(0, 10), sticky="ew"
        )

        self.no_button = ThemedButton(
            self,
            text="No",
            height=30,
            command=self.cancel_event,
            fg_color=self.theme["button-enabled"],
            hover_color=self.theme["button-enabled-hover"],
        )
        self.no_button.grid(
            row=1, column=0, columnspan=1, padx=(20, 10), pady=(0, 10), sticky="ew"
        )
        
        self.bind("<Return>", lambda e: self.ok_event())
        self.bind("<Escape>", lambda e: self.cancel_event())

    def ok_event(self):
        self.confirm = True
        self.destroy()

    def cancel_event(self):
        self.confirm = False
        self.destroy()

    def get_input(self):
        self.master.wait_window(self)
        return self.confirm


# endregion
