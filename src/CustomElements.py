"""
@author: [E1Bos](https://www.github.com/E1Bos)
"""

import customtkinter as ctk
from PIL import Image
import os
from typing import TYPE_CHECKING, Callable, List, Optional, Union, Dict, Any
from Constants import BRIGHTEN_COLOR, RESOURCE_PATH, ICON, FILE
from abc import abstractmethod

if TYPE_CHECKING:
    from VALocker import VALocker, SaveFilesFrame


# region: Labels


class ThemedLabel(ctk.CTkLabel):
    """
    A custom label themed according to the VALocker theme.

    Attributes:
        theme (dict[str, str]): The theme dictionary containing key-value pairs for theming.
        default_config (dict[str, str]): The default configuration for the label.

    Args:
        parent (SideFrame): The parent widget.
        text (str): The initial text for the label.
        variable (Union[ctk.StringVar, None]): The variable to associate with the label's text.
        **kwargs: Additional keyword arguments to configure the label.

    """

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
        use_same_color: bool = False,
        **kwargs,
    ) -> None:

        self.command = command
        self.variable = variable

        if isinstance(text, str):
            text = [text, text]

        super().__init__(parent, **kwargs)

        self.configure(
            command=self.command,
        )

        if use_same_color:
            self.button_colors = [self.theme["accent"], self.theme["accent"]]
            self.hover_colors = [self.theme["accent-hover"], self.theme["accent-hover"]]
        else:
            self.button_colors = [self.theme["button-enabled"], self.theme["button-disabled"]]
            self.hover_colors = [self.theme["button-enabled-hover"], self.theme["button-disabled-hover"]]

        self.text = text
        self.disabled = False
        self._update_button()

        self.variable.trace_add("write", self._variable_update)

    def _update_button(self) -> None:
        """
        Updates the button based on the variable value.
        """
        is_enabled = self.variable.get()
        self.configure(
            text=self.text[0] if is_enabled else self.text[1],
            fg_color=self.button_colors[0] if is_enabled else self.button_colors[1],
            hover_color=self.hover_colors[0] if is_enabled else self.hover_colors[1]
        )

    def _variable_update(self, *_):
        """
        Updates the button based on the variable value.
        Bound to the variable's trace.
        """
        self._update_button()

    def toggle_disable(self) -> None:
        """
        Toggles the disabled state of the button.
        """
        self.disabled = not self.disabled
        self.configure(state=ctk.NORMAL if not self.disabled else ctk.DISABLED)

class MultiTextIndependentButton(ThemedButton):
    """
    A button that is enabled, independent of any other variable.
    It changes its text and color based on the state of its own variable.
    """

    text: list[str]
    variable: ctk.BooleanVar

    def __init__(
        self,
        parent: "SideFrame",
        text: list[str],
        variable: ctk.IntVar,
        command: Callable,
        prefix: Union[str | None] = None,
        **kwargs,
    ) -> None:

        self.command = command
        self.variable = variable

        super().__init__(parent, **kwargs)

        self.configure(
            fg_color=self.theme["accent"],
            hover_color=self.theme[
                "accent-hover"
            ],
            command=self.command,
        )

        if prefix == None:
            self.text = text
        else:
            self.text = [f"{prefix}{text}" for text in text]
            
        self.disabled = False
        self._update_button()

        self.variable.trace_add("write", self._variable_update)

    def _update_button(self) -> None:
        """
        Updates the button based on the variable value.
        """
        if self.variable.get() >= len(self.text):
            raise ValueError("Issue occurred with the variable value.")
        
        text_value = self.text[self.variable.get()]
        self.configure(
            text=text_value,
        )

    def _variable_update(self, *_):
        """
        Updates the button based on the variable value.
        Bound to the variable's trace.
        """
        self._update_button()

    def toggle_disable(self) -> None:
        """
        Toggles the disabled state of the button.
        """
        self.disabled = not self.disabled
        self.configure(state=ctk.NORMAL if not self.disabled else ctk.DISABLED)

class DependentButton(ThemedButton):
    """
    Button that is dependent on two variables,
    one that determines if the button is enabled,
    and the other that the button is responsible for.

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
    ) -> None:
        self.dependent_variable = dependent_variable
        self.variable = variable
        self.text = text

        config = {"text": self.get_current_text()}
        config.update(kwargs)

        super().__init__(parent, command=command, **config)

        self.variable.trace_add("write", self.variable_update)
        self.dependent_variable.trace_add("write", self.dependent_variable_update)
        self.check_disable()

    def variable_update(self, *_) -> None:
        """
        Configures the element.
        """
        config = {"text": self.get_current_text()}
        self.configure(**config)

    def dependent_variable_update(self, *_) -> None:
        """
        This method is called every time the dependent variable is changed.
        It updates the text and then updates whether the button is enabled or disabled.
        """
        self.variable_update()
        self.check_disable()

    def check_disable(self) -> None:
        """
        Enable or disable the widget based on the value of the dependent variable.

        If the dependent variable is True, the widget will be enabled.
        If the dependent variable is False, the widget will be disabled.
        """
        if self.dependent_variable.get():
            self.configure(state=ctk.NORMAL)
        else:
            self.configure(state=ctk.DISABLED)

    def get_current_text(self) -> str:
        """
        Returns the current text based on the state of the variables.

        If the `text` attribute is already a string, it is returned as is.
        Otherwise, the text is determined based on the values of `dependent_variable`
        and `variable`.

        Returns:
            str: The current text.
        """
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
    and the other that the button is responsible for.

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
    ) -> None:
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
        """
        Returns the color configuration based on the current state of the variable.

        Returns:
            A dictionary containing the foreground color and hover color based on the state of the variable.
        """
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

    def variable_update(self, *_) -> None:
        """
        Update the variables of the custom element.

        This method retrieves the color configuration using the `get_color` method and applies it to the custom element
        using the `configure` method.
        """
        config = self.get_color()
        self.configure(**config)

    def dependent_variable_update(self, *_) -> None:
        """
        Updates the dependent variable and applies the corresponding configuration.
        """
        config = self.get_color()
        self.configure(**config)
        self.check_disable()

    def check_disable(self) -> None:
        """
        Enable or disable the widget based on the value of the dependent variable.

        If the dependent variable is True, the widget is enabled.
        If the dependent variable is False, the widget is disabled and the variable is set to False.
        """
        if self.dependent_variable.get():
            self.configure(state=ctk.NORMAL)
        else:
            self.configure(state=ctk.DISABLED)
            self.variable.set(False)


class SplitButton:
    """
    A custom button that can be split into two buttons when enabled.

    When disabled, the button is displayed as a single button.
    When enabled, the button splits into two buttons.

    The buttons can be customized with different text and commands.

    Args:
        parent (ThemedFrame): The parent frame that contains the SplitButton.
        text_left (list[str]): A list of two strings representing the text for the left button. The first string is used when the left button is enabled, and the second string is used when the left button is disabled.
        text_right (list[str]): A list of strings representing the text for the right button. Each string corresponds to a different value of the right variable.
        variable_left (ctk.BooleanVar): The variable that determines the state of the left button (enabled or disabled).
        variable_right (ctk.IntVar): The variable that determines the selected value of the right button.
        command_left (Callable): The command to be executed when the left button is clicked.
        command_right (Callable): The command to be executed when the right button is clicked.

    Attributes:
        parent (object): The parent object that contains the SplitButton.
        theme (dict[str, str]): A dictionary containing the theme colors for the buttons.

    Methods:
        draw_buttons: Draws the buttons based on the value of the 'variable_left' variable.
        left_variable_update: Updates the left button based on the value of the left variable.
        right_variable_update: Updates the right button's text based on the selected value of the right variable.
        pack: Packs the frame using the given keyword arguments.
        grid: Configures the grid layout for the frame.
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
        """
        Draws the buttons based on the value of the 'variable_left' variable.

        If 'variable_left' is True, the left button is displayed on the grid and the right button is hidden.
        If 'variable_left' is False, the right button is displayed on the grid and the left button is hidden.
        """
        if self.variable_left.get():
            self.left_button.grid_forget()
            self.left_button.grid(row=0, column=0, sticky="nsew")
            self.right_button.grid(row=0, column=1, sticky="nsew")
        else:
            self.right_button.grid_forget()
            self.left_button.grid(row=0, column=0, columnspan=2, sticky="nsew")

    def left_variable_update(self, *_) -> None:
        """
        Update the left button based on the value of the left variable.

        This method updates the text, foreground color, and hover color of the left button
        based on the value of the left variable. If the left variable is True, the button
        text is set to the first element of `self.text_left` and the colors are set to the
        enabled theme colors. If the left variable is False, the button text is set to the
        second element of `self.text_left` and the colors are set to the disabled theme colors.
        """
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

    def right_variable_update(self, *_) -> None:
        """
        Update the right button's text based on the selected value of the right variable.
        """
        self.right_button.configure(
            text=self.text_right[self.variable_right.get()],
        )

    def pack(self, **kwargs) -> None:
        """
        Packs the frame using the given keyword arguments.

        Args:
            **kwargs: Additional keyword arguments to be passed to the pack method.
        """
        self.frame.pack(**kwargs)

    def grid(self, **kwargs) -> None:
        """
        Configures the grid layout for the frame.

        Args:
            **kwargs: Additional keyword arguments to be passed to the grid method.
        """
        self.frame.grid(**kwargs)


class SaveButton:
    """
    Represents a save button element in the user interface.

    Attributes:
        save_name (str): The name of the save file.
        save_file (str): The path to the save file.
        selected (bool): Indicates if the save button is selected.
        favorited (bool): Indicates if the save button is favorited.

    Methods:
        select_save: Selects the save and updates the side frame accordingly.
        set_selected: Sets the selected state of the element.
        toggle_favorite: Toggles the favorite status of the element.
        rename: Renames the element.
        change_text: Changes the text of the save label.
        delete: Deletes the current instance of the SaveButton.
        destroy: Destroys the frame associated with this custom element.
        grid: Configures the grid layout for the frame.
        grid_forget: Removes the widget from the grid layout manager.

    Each SaveButton instance represents a single save file in the user interface and has the following features:
    - A label displaying the name of the save file.
    - An icon to favorite the save file.
    - An icon to rename the save file.
    - An icon to delete the save file.
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
        
        frame_config["border_color"] = self.theme["accent"]

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

    def select_save(self, *_) -> None:
        """
        Selects the save and updates the side frame accordingly.
        This only runs when a button is clicked.

        If the save is already selected, the method does nothing.
        """
        if self.selected:
            return

        self.side_frame.change_save(self)
        self.set_selected(True)

    def set_selected(self, value: bool) -> None:
        """
        Sets the selected state of the element.
        This method is also run when the element is selected and when the button is first loaded.

        Args:
            value (bool): The value to set the selected state to.
        """
        self.selected = value
        self.configure_icons()
        self.on_exit_hover()

    # region: Icon Commands

    def toggle_favorite(self, value: Optional[bool] = None, reorderList: Optional[bool] = False) -> None:
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
        
        self.frame.configure(
            border_width=1 if self.favorited else 0
        )

        self.side_frame.favorite_button(self, reorderList=reorderList)

    def rename(self) -> None:
        """
        Renames the element by calling the `rename_save` method of the `side_frame` object.

        This method is responsible for renaming the element and saving the changes.

        Parameters:
            self (CustomElements): The current instance of the CustomElements class.
        """
        self.side_frame.rename_save(self)

    def change_text(self, text: str) -> None:
        """
        Change the text of the save label and update the save name and save file.
        This is called when it is renamed.

        Args:
            text (str): The new text for the save label.
        """
        self.save_label.configure(text=text)
        self.save_name = text
        self.save_file = text + ".yaml"

    def delete(self) -> None:
        """
        Deletes the current instance of the CustomElement.

        This method calls the `delete_save` method of the `side_frame` object, passing itself as an argument.
        """
        self.side_frame.delete_save(self)

    # endregion

    def configure_icons(self) -> None:
        """
        Configures the icons with the specified hover color based on the selected state.

        The `hover_color` is set to `self.theme["foreground-highlight-hover"]` by default.
        If the element is selected, the `hover_color` is set to `self.theme["accent-hover"]`.
        """
        config = {
            "hover_color": self.theme["foreground-highlight-hover"],
        }

        if self.selected:
            config["hover_color"] = self.theme["accent-hover"]

        for icon in self.icons:
            icon.configure(**config)

    # region: Hover Effects

    def on_hover(self, *_) -> None:
        """
        Change the foreground color of the frame based on the selected state.

        If the element is not selected, it changes the foreground color to the
        "foreground-highlight-hover" color defined in the theme. Otherwise, it
        changes the foreground color to the "accent-hover" color defined in the theme.
        """
        if not self.selected:
            self.frame.configure(fg_color=self.theme["foreground-highlight-hover"])
        else:
            self.frame.configure(fg_color=self.theme["accent-hover"])

    def on_exit_hover(self, *_) -> None:
        """
        Handles the hover event when the mouse exits the element.

        If the element is not selected, it changes the foreground color to the highlight color defined in the theme.
        If the element is selected, it changes the foreground color to the accent color defined in the theme.
        """
        if not self.selected:
            self.frame.configure(fg_color=self.theme["foreground-highlight"])
        else:
            self.frame.configure(fg_color=self.theme["accent"])

    # endregion

    def destroy(self) -> None:
        """
        Destroys the frame associated with this custom element.
        """
        self.frame.destroy()

    def grid(self, **kwargs) -> None:
        """
        Configures the grid layout for the frame.

        Args:
            **kwargs: Additional keyword arguments to be passed to the grid method.
        """
        self.frame.grid(**kwargs)

    def grid_forget(self):
        """
        Removes the widget from the grid layout manager.

        This method is used to remove the widget from the grid layout manager,
        effectively hiding it from the user interface.

        Note:
            The widget will still exist in memory and can be re-displayed using
            the `grid` method.
        """
        self.frame.grid_forget()


# endregion


class ThemedDropdown(ctk.CTkOptionMenu):
    """
    A custom themed dropdown menu widget.

    This class extends the `ctk.CTkOptionMenu` class to provide a dropdown menu
    with customizable theming options.

    Attributes:
        default_config (Dict[str, Union[str, int, bool]]): The default configuration
            options for the dropdown menu.
        parent (VALocker): The parent widget of the dropdown menu.
        theme (Dict[str, str]): The theme configuration for the dropdown menu.

    Methods:
        set_values(self, values): Sets the values of the dropdown menu.
        disable(self): Disables the dropdown menu.
        enable(self): Enables the dropdown menu.
    """

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
        """
        Configures the dropdown element with the given theme and keyword arguments.

        Returns:
            Dict[str, Union[str, int, bool]]: A dictionary containing the configured dropdown element.

        """
        config = {
            key: kwargs.get(key, theme.get(value, value))
            for key, value in self.default_config.items()
        }
        config["button_color"] = BRIGHTEN_COLOR(config["fg_color"], 0.8)
        config["button_hover_color"] = BRIGHTEN_COLOR(config["fg_color"], 0.75)
        config.update(kwargs)
        return config

    def set_values(self, values: List[str]) -> None:
        """
        Sets the values of the custom dropdown.

        Args:
            values (List[str]): The list of values to set.
        """
        self.configure(values=values)

    def disable(self) -> None:
        """
        Disables the custom element.
        """
        self.configure(state=ctk.DISABLED)

    def enable(self) -> None:
        """
        Enables the custom element.
        """
        self.configure(state=ctk.NORMAL)


# region: Checkboxes


class ThemedCheckbox(ctk.CTkCheckBox):
    """
    Checkbox that is styled according to the VALocker theme.
    """

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
    ) -> None:
        config = {
            key: kwargs.get(key, parent.theme.get(value, value))
            for key, value in self.default_config.items()
        }

        config.update(kwargs)

        super().__init__(parent, text=text, variable=variable, **config)

    def disable(self) -> None:
        """
        Disable the checkbox.
        """
        self.configure(state=ctk.DISABLED)

    def enable(self) -> None:
        """
        Enable the checkbox.
        """
        self.configure(state=ctk.NORMAL)


class DependentCheckbox(ThemedCheckbox):
    """
    A custom checkbox widget that depends on a variable.

    This checkbox widget is designed to be dependent on a variable. When the dependent variable is changed,
    the state of this checkbox can be enabled or disabled based on the configuration. If the dependent variable is
    false, this checkbox will be disabled and its value will be set to False.

    Attributes:
        variable (ctk.BooleanVar): The variable associated with this checkbox.
        dependent_variable (ctk.BooleanVar): The variable associated with the dependent checkbox.

    Args:
        parent (VALocker): The parent widget.
        text (str): The text to display next to the checkbox.
        variable (ctk.BooleanVar): The variable associated with this checkbox.
        dependent_variable (ctk.BooleanVar): The variable associated with the dependent checkbox.
        **kwargs: Additional keyword arguments to pass to the ThemedCheckbox constructor.
    """

    variable: ctk.BooleanVar
    dependent_variable: ctk.BooleanVar

    def __init__(
        self,
        parent: "VALocker",
        text: str,
        variable: ctk.BooleanVar,
        dependent_variable: ctk.BooleanVar,
        **kwargs,
    ) -> None:
        super().__init__(parent, text=text, variable=variable, **kwargs)
        self.variable = variable

        self.dependent_variable = dependent_variable
        self.dependent_variable.trace_add("write", self.dependent_variable_update)
        self._pending_config = None
        self.dependent_variable_update()

    def dependent_variable_update(self, *_) -> None:
        """
        Update the dependent variable and apply the pending configuration.

        This method is called when the dependent variable is updated. If the dependent variable is set to True,
        the pending configuration is set to ctk.NORMAL. Otherwise, the pending configuration is set to ctk.DISABLED
        and the variable is set to False. The pending configuration is then applied using the `apply_pending_config`
        method after the idle time.
        """
        if self.dependent_variable.get():
            self._pending_config = ctk.NORMAL
        else:
            self._pending_config = ctk.DISABLED
            self.variable.set(False)

        self.after_idle(self.apply_pending_config)

    def apply_pending_config(self) -> None:
        """
        Applies the pending configuration to the element.

        If there is a pending configuration, it sets the element's state to the pending configuration
        and clears the pending configuration afterwards.
        """
        if self._pending_config is not None:
            self.configure(state=self._pending_config)
            self._pending_config = None


# endregion

# region: Frames


class ThemedFrame(ctk.CTkFrame):
    """
    A frame that is styled according to the VALocker theme.
    """

    default_config = {
        "fg_color": "foreground",
        "corner_radius": 10,
    }

    def __init__(self, parent: "VALocker", **kwargs) -> None:

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
    """
    A frame used for the side panel of the VALocker application.
    i.e the frame that the navigation buttons point to.
    """

    parent: "VALocker"
    theme: dict[str, str]

    def __init__(self, parent: "VALocker") -> None:
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.parent = parent
        self.theme = parent.theme

    def get_button_color(self, var: ctk.BooleanVar) -> str:
        """
        Returns the button color based on the value of the given BooleanVar.

        Args:
            var (ctk.BooleanVar): The BooleanVar object representing the state of the button.

        Returns:
            str: The color value for the button, either the enabled color or the disabled color.
        """
        return (
            self.theme["button-enabled"] if var.get() else self.theme["button-disabled"]
        )

    def get_button_text(self, var: ctk.BooleanVar, text: list[str]) -> str:
        """
        Returns the button text based on the value of the BooleanVar.

        Args:
            var (ctk.BooleanVar): The BooleanVar object representing the button state.
            text (list[str]): A list of two strings representing the button text for different states.

        Returns:
            str: The button text based on the value of the BooleanVar.
        """
        return text[0] if var.get() else text[1]

    @abstractmethod
    def on_raise(self) -> None:
        """
        This method is called when the element is raised.
        It performs some actions related to the raising behavior.
        """
        raise NotImplementedError("The on_raise method must be implemented.")


class ThemedScrollableFrame(ctk.CTkScrollableFrame):
    """
    Scrollable frame that is styled according to the VALocker theme.
    """

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
    """
    A popup that is styled according to the VALocker theme.

    This class is an abstract class that should be inherited by other popup classes.
    """

    default_config = {
        "fg_color": "background",
    }

    def __init__(self, parent: "VALocker", title, geometry: str, **kwargs) -> None:
        self.parent = parent
        self.theme = parent.theme

        config = {
            key: kwargs.get(key, parent.theme.get(value, value))
            for key, value in self.default_config.items()
        }
        config.update(kwargs)

        super().__init__(**config)
        self.geometry(geometry)
        self.after(200, lambda: self.wm_iconbitmap(ICON.DEFAULT.value))
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
        self.after_idle(self.update)

    @abstractmethod
    def create_widgets(self) -> None:
        """
        Creates and initializes the widgets for the custom elements.
        This method must be implemented by subclasses.
        """
        raise NotImplementedError("The create_widgets method must be implemented.")

    def calculate_position(self) -> None:
        """
        Calculates the position of the popup window and centers it relative to the parent window.

        This method retrieves the geometry information of the parent window and the popup window,
        and then calculates the position to center the popup window relative to the parent window.
        """
        mw_size, mw_x_shift, mw_y_shift = self.parent.winfo_geometry().split("+")
        mw_size_x, mw_size_y = map(int, mw_size.split("x"))
        mw_x_shift, mw_y_shift = map(int, [mw_x_shift, mw_y_shift])

        popup_size, _, _ = self.geometry().split("+")
        popup_size_x, popup_size_y = map(int, popup_size.split("x"))

        self.geometry(
            "+%d+%d"
            % (
                mw_x_shift + (mw_size_x - popup_size_x) // 2,
                mw_y_shift + (mw_size_y - popup_size_y) // 2,
            )
        )

    def on_closing(self) -> None:
        """
        Method called when the window is closing.
        Releases the grab and destroys the window.
        """
        self.grab_release()
        self.destroy()

class InputDialog(ThemedPopup):
    """
    A popup that asks the user for a text input.

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
    ) -> None:

        self.theme = parent.theme

        super().__init__(parent, title, "300x170", **kwargs)

        self.user_input: Union[str, None] = None
        self.parent = parent
        self.label = label
        self.placeholder = placeholder if placeholder else ""
        self.prefill = prefill

    def create_widgets(self) -> None:
        """
        Create and configure the widgets for the custom element.

        This method sets up the label, entry, buttons, and event bindings for the custom element.
        """
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1, 2), weight=1)

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

    def ok_event(self, *_) -> None:
        """
        Handle the 'OK' event.

        This method is called when the user clicks the 'OK' button or presses the Enter key.
        It retrieves the user input from the entry widget, releases the grab, and destroys the window.
        """
        self.user_input = self.entry.get()
        self.grab_release()
        self.destroy()

    def cancel_event(self) -> None:
        """
        Cancels the event and releases the grab.

        This method releases the grab and destroys the element.
        """
        self.grab_release()
        self.destroy()

    def get_input(self) -> str | None:
        """
        Waits for the user to input something and returns the input value.

        This method waits for a window to be closed before returning the user's input value.

        Returns:
            str: The user's input value.
        """
        self.master.wait_window(self)
        return self.user_input


class ErrorPopup(ThemedPopup):
    """
    An error popup that displays an error message.
    """

    theme: dict[str, str]

    def __init__(self, parent: "VALocker", message: str, size: str = "300x100", **kwargs) -> None:
        self.theme = parent.theme
        self.message = message

        super().__init__(parent, "Error", size, **kwargs)

    def create_widgets(self) -> None:
        """
        Create and display the widgets for the custom element.

        This method creates and configures the label and button widgets for the custom element.
        It also binds the <Return> key to the destroy method and waits for the window to be closed.
        """
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
    """
    A popup that asks the user to confirm an action.
    Returns True if the user confirms, False if the user cancels.
    
    Args:
        parent (VALocker): The parent widget.
        title (str): The title of the popup.
        message (str): The message to display to the user.
        default_no (bool): Whether the default option is 'No'. Defaults to True.
        geometry (str): The geometry of the popup window. Defaults to "300x150".
        **kwargs: Additional keyword arguments to pass to the ThemedPopup constructor.
    """

    theme: dict[str, str]
    message: str
    confirm: bool
    default_no: bool

    def __init__(self, parent: "VALocker", title: str, message: str, default_no: bool = True, geometry: Optional[str] = None, **kwargs) -> None:
        self.theme = parent.theme
        self.message = message
        self.confirm = False
        self.default_no = default_no
        
        if geometry is None:
            geometry = "300x150"

        super().__init__(parent, title, geometry, **kwargs)

    def create_widgets(self) -> None:
        """
        Create and configure the widgets for the custom element.

        This method creates and configures the widgets required for the custom element.
        It sets up the grid layout, creates a label widget, and two button widgets.
        It also binds the Return and Escape keys to corresponding events.
        """
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1), weight=1)

        self.label = ThemedLabel(
            self,
            text=self.message,
        )
        self.label.grid(row=0, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        if self.default_no:
            ok_button_color = self.theme["button-disabled"]
            ok_button_hover_color = self.theme["button-disabled-hover"]
            
            no_button_color = self.theme["button-enabled"]
            no_button_hover_color = self.theme["button-enabled-hover"]
            
            column = (0, 1)
        else:
            ok_button_color = self.theme["button-enabled"]
            ok_button_hover_color = self.theme["button-enabled-hover"]
            
            no_button_color = self.theme["button-disabled"]
            no_button_hover_color = self.theme["button-disabled-hover"]
            
            column = (1, 0)

        self.ok_button = ThemedButton(
            self,
            text="Yes",
            height=30,
            command=self.ok_event,
            fg_color=ok_button_color,
            hover_color=ok_button_hover_color,
        )
        self.ok_button.grid(
            row=1, column=column[0], columnspan=1, padx=(10, 20), pady=(0, 10), sticky="ew"
        )

        self.no_button = ThemedButton(
            self,
            text="No",
            height=30,
            command=self.cancel_event,
            fg_color=no_button_color,
            hover_color=no_button_hover_color,
        )
        self.no_button.grid(
            row=1, column=column[1], columnspan=1, padx=(20, 10), pady=(0, 10), sticky="ew"
        )

        if self.default_no:
            self.bind("<Return>", lambda _: self.cancel_event())
            self.bind("<Escape>", lambda _: self.cancel_event())
        else:
            self.bind("<Return>", lambda _: self.ok_event())
            self.bind("<Escape>", lambda _: self.cancel_event())

    def ok_event(self) -> None:
        """
        Handles the OK event.

        This method sets the `confirm` attribute to True and destroys the element.

        """
        self.confirm = True
        self.destroy()

    def cancel_event(self) -> None:
        """
        Cancels the event and destroys the object.
        """
        self.confirm = False
        self.destroy()

    def get_input(self) -> bool:
        """
        Waits for the user to input something and returns the confirmation value.

        This method waits for a window to be closed before returning the confirmation value.
        The confirmation value is obtained from the `confirm` attribute of the object.

        Returns:
            bool: The confirmation value entered by the user.
        """
        
        if self.winfo_exists():
            self.master.wait_window(self)
        return self.confirm


# endregion
