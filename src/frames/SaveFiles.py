"""
@author: [E1Bos](https://www.github.com/E1Bos)
"""

import customtkinter as ctk
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from VALocker import VALocker

# Custom Imports
from Constants import FILE
from CustomElements import *


class SaveFilesUI(SideFrame):
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
            try:
                for favorited_save in self.parent.file_manager.get_value(
                    FILE.SETTINGS, "$favoritedSaveFiles"
                ):
                    favorite_button_names.append(favorited_save)
            except TypeError as e:
                pass

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
            "$favoritedSaveFiles",
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
                self.parent.file_manager.get_value(FILE.SETTINGS, "$activeSaveFile")
                == old_name
            ):
                self.parent.file_manager.set_value(
                    FILE.SETTINGS, "$activeSaveFile", file_name_with_extension
                )

        if old_name in self.parent.file_manager.get_value(
            FILE.SETTINGS, "$favoritedSaveFiles"
        ):
            # Ensure the new file name has the .yaml extension
            self.parent.file_manager.set_value(
                FILE.SETTINGS,
                "$favoritedSaveFiles",
                [
                    file_name_with_extension if name == old_name else name
                    for name in self.parent.file_manager.get_value(
                        FILE.SETTINGS, "$favoritedSaveFiles"
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
