# Updates files including settings, user data, and other data files
import os
import requests
import json
import shutil
from CustomLogger import CustomLogger
from constants import Urls, Folders, Files


class FileManager:
    """
    The FileManager class is responsible for managing the required files and directories for the VALocker application.
    It provides methods to ensure that the required files exist, download missing files, migrate old files to a new directory structure,
    and read all the files into memory. It also provides getters and setters for accessing and modifying the file data.

    Methods:
        setup_file_manager(): Sets up the FileManager by ensuring that the required files exist and reading them into memory.
        update_file(constants.Files): Update a file by downloading the latest version from the repository.
        get_config(constants.Files): Returns the configuration dictionary for the specified file.
        set_config(constants.Files, dict): Sets the configuration dictionary for the specified file.
        update_save_file(str, dict): Update a save file by saving the configuration to the specified file.
    """

    def __init__(self) -> None:
        # Stores the required file enums
        self._REQUIRED_FILES = {
            Files.STATS,
            Files.LOCKING_INFO,
            Files.AGENT_CONFIG,
            Files.USER_SETTINGS,
            Files.SETTINGS,
            Files.DEFAULT_SAVE,
        }

        # Main directory for the files
        self._MAIN_DIR = os.path.join(os.environ["APPDATA"], "VALocker")

        # URL to download the files from
        self._DOWNLOAD_URL = (
            f"{Urls.DOWNLOAD_URL.value}/{Folders.TEMPLATE_FOLDER_NAME.value}/"
        )

        # Dictionaries to store the data from the files
        self._settings = dict()
        self._user_settings = dict()
        self._stats = dict()
        self._locking_info = dict()
        self._agent_config = dict()

        # Set up logging
        self._logger = CustomLogger("FileManager").get_logger()

    # Start Function
    def setup_file_manager(self) -> None:
        """
        Sets up the FileManager by ensuring that the required files exist and reading them into memory.
        """
        self._logger.info("Setting up file manager")
        self._ensure_files_exist()
        self._read_all_files()
        self._logger.info("File manager setup complete")

    # region: Creating directories and downloading files

    def _ensure_files_exist(self) -> None:
        """
        Ensures that the required directories and files exist.
        If any file is missing, it will be downloaded.
        """

        # Creates appdata/roaming/VALocker if it doesn't exist
        os.makedirs(self._MAIN_DIR, exist_ok=True)

        # Creates the required directories and files if they don't exist
        for required_file in self._REQUIRED_FILES:
            required_file_relative_path = required_file.value
            parent_dir = os.path.dirname(required_file_relative_path)

            # Creates subdirs
            os.makedirs(self._absolute_file_path(parent_dir), exist_ok=True)

            # # Checks files
            file_path = self._absolute_file_path(required_file_relative_path)

            # # If file is missing, download it
            if not os.path.isfile(file_path):
                self._logger.info(
                    f"{required_file_relative_path} not found, downloading"
                )
                online_file_path = required_file_relative_path
                self._download_file(online_file_path, file_path)

        # if self._settings.

        settings_rel_path = Files.SETTINGS.value
        self._settings = json.load(
            open(self._absolute_file_path(settings_rel_path), "r")
        )

        if self._settings.get("ALREADY_MIGRATED", False) == False:
            self._logger.info("Files may need to be migrated, checking for old files")
            self._migrate_old_files()

    def _download_file(self, file_path: str, save_path: str) -> None:
        """
        Download a file from a public GitHub repository.

        Args:
            file_path (str): The path of the file in the repository.
            save_path (str): The path where the file should be saved.

        Raises:
            requests.exceptions.RequestException: If the request to download the file fails.
        """
        url = f"{self._DOWNLOAD_URL}{file_path}"

        self._logger.info(f"Downloading {file_path} from {url}")

        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception if the request failed
            with open(save_path, "wb") as f:
                f.write(response.content)
            self._logger.info(f"Downloaded {file_path}")
        except requests.exceptions.RequestException as e:
            self._logger.error(f"Error downloading {file_path}: {e}")
            raise e

    # endregion

    # region: Migrating old files

    def _migrate_old_files(self):
        """
        Check if the old VALocker directory exists and move the files to the new directory.

        This method is responsible for migrating the old VALocker files to the new directory structure.
        It checks for the existence of the old directory and performs the following actions:
        - Migrates the old `stats.json` file to the new directory.
        - Migrates the old `user_settings.json` file to the new directory.
        - Migrates the files in the `save_files` directory to the new directory.
        - Updates the settings to indicate that the migration has already been performed.

        Note: This method assumes that the new directory structure has already been set up.
        """

        # the old path was the ./data dir
        old_dir = os.path.join(os.getcwd(), "data")

        # If the old directory doesn't exist, return
        if not os.path.exists(old_dir):
            self._logger.info("Old directory not found, no migration required")
            self._set_migrated_flag(True)
            return

        # Check for stats file
        stats_file = os.path.join(old_dir, "stats.json")
        if os.path.exists(stats_file):
            self._logger.info("Found old stats.json file, migrating to new directory")

            # Migrate the old stats.json file to the new directory
            self._override_json_file(stats_file, Files.STATS.value, delete_old=False)
            self._override_json_file(
                stats_file, Files.USER_SETTINGS.value, delete_old=False
            )

        # Check for user_settings file
        user_settings_file = os.path.join(old_dir, "user_settings.json")
        if os.path.exists(user_settings_file):
            self._logger.info(
                "Found old user_settings.json file, migrating to new directory"
            )
            self._override_json_file(
                user_settings_file, Files.SETTINGS.value, delete_old=False
            )

        # Check for save_files directory
        save_files_dir = os.path.join(old_dir, "save_files")
        if os.path.exists(save_files_dir):
            self._logger.info(
                "Found old save_files directory, migrating to new directory"
            )
            # Iterate over the files in the save_files directory and move them to the new directory
            for file_name in os.listdir(save_files_dir):
                save_file_location = os.path.join(save_files_dir, file_name)
                new_save_file_location = os.path.join(
                    self._MAIN_DIR, "save_files", file_name
                )
                shutil.move(save_file_location, new_save_file_location)
                self._logger.info(f"Migrated {file_name} to {new_save_file_location}")
            # Remove the old save_files directory
            os.rmdir(save_files_dir)
            self._logger.info(f"Deleted {save_files_dir}")

        self._logger.info("Migration complete")
        self._set_migrated_flag(True)

    def _set_migrated_flag(self, value: bool) -> None:
        """
        Sets the value of the 'ALREADY_MIGRATED' flag in the settings dictionary.

        Args:
            value (bool): The value to set for the 'ALREADY_MIGRATED' flag.

        Returns:
            None
        """
        self._settings["ALREADY_MIGRATED"] = value
        self.set_config(Files.SETTINGS, self._settings)

    def _override_json_file(
        self, old_file_path, new_file_path, delete_old=False
    ) -> None:
        """
        Overrides the contents of a JSON file with the contents of another JSON file, only where keys match.

        Args:
            old_file_path (str): The path to the old JSON file.
            new_file_path (str): The path to the new JSON file.
            delete_old (bool, optional): Whether to delete the old file after overriding. Defaults to False.

        Returns:
            None
        """
        old_stats_json = json.load(open(old_file_path, "r"))
        new_stats_json = json.load(open(self._absolute_file_path(new_file_path), "r"))

        # Update the new stats.json file
        for key, value in old_stats_json.items():
            if key in new_stats_json:
                new_stats_json[key] = value

        # Save the updated new_stats_json
        with open(self._absolute_file_path(new_file_path), "w") as f:
            json.dump(new_stats_json, f, indent=4)

        self._logger.info(
            f"Migrated {old_file_path} to {self._absolute_file_path(new_file_path)}"
        )

        # Delete the old file
        if delete_old:
            os.remove(old_file_path)
            self._logger.info(f"Deleted {old_file_path}")

    # endregion

    def _read_all_files(self) -> None:
        """
        Reads all the files into memory.
        """
        self._settings = json.load(
            open(self._absolute_file_path(Files.SETTINGS.value), "r")
        )
        self._user_settings = json.load(
            open(self._absolute_file_path(Files.USER_SETTINGS.value), "r")
        )
        self._stats = json.load(open(self._absolute_file_path(Files.STATS.value), "r"))
        self._locking_info = json.load(
            open(self._absolute_file_path(Files.LOCKING_INFO.value), "r")
        )
        self._agent_config = json.load(
            open(self._absolute_file_path(Files.AGENT_CONFIG.value), "r")
        )
        self._logger.info("Read all files into memory")

    def _absolute_file_path(self, *args) -> str:
        """
        Returns the absolute file path by joining the main directory path with the provided arguments.

        Args:
            *args: Variable number of arguments representing the path components.

        Returns:
            str: The absolute file path.
        """
        return os.path.join(self._MAIN_DIR, *args)

    def get_config(self, file: Files) -> dict:
        """
        Returns the configuration dictionary for the specified file.

        Args:
            file (constants.Files): The file enum for which the configuration is required.

        Returns:
            dict: The configuration dictionary for the specified file.
        """
        match file:
            case Files.SETTINGS:
                return self._settings
            case Files.USER_SETTINGS:
                return self._user_settings
            case Files.STATS:
                return self._stats
            case Files.LOCKING_INFO:
                return self._locking_info
            case Files.AGENT_CONFIG:
                return self._agent_config
            case _:
                self._logger.error(f"Invalid file: {file}")
                return None

    def set_config(self, file: Files, config: dict) -> None:
        """
        Sets the configuration dictionary for the specified file.

        Args:
            file (constants.Files): The file enum for which the configuration is required.
            config (dict): The configuration dictionary to set.
        """
        match file:
            case Files.SETTINGS:
                self._settings = config
            case Files.USER_SETTINGS:
                self._user_settings = config
            case Files.STATS:
                self._stats = config
            case Files.LOCKING_INFO:
                self._locking_info = config
            case Files.AGENT_CONFIG:
                self._agent_config = config
            case _:
                self._logger.error(f"Invalid file: {file}")

        with open(self._absolute_file_path(file.value), "w") as f:
            json.dump(config, f, indent=4)

    # region:  Update files

    def update_file(self, file: Files) -> None:
        """
        Update a file by downloading the latest version from the repository.

        Args:
            file_path (constants.Files): The file enum that needs to be updated.
        """
        self._logger.info(f"Updating {file.value} to the latest version")

        # Store the path where the file will be saved
        save_path = os.path.join(self._absolute_file_path(file.value))

        # Download the latest version of the file
        self._download_file(file.value, save_path)

        self._logger.info(f"Updated {file.value} to the latest version")

    def update_save_file(self, save_name: str, config: dict) -> None:
        """
        Update a save file by saving the latest configuration to the specified file.

        Args:
            save_name (str): The name of the save file.
            config (dict): The configuration dictionary to save.
        """
        parent_dir = os.pardir(Files.DEFAULT_SAVE.value)
        save_path = os.path.join(self._absolute_file_path(parent_dir, save_name))

        with open(save_path, "w") as f:
            json.dump(config, f, indent=4)

        self._logger.info(f"Updated save file {save_name}")

    # endregion


if __name__ == "__main__":
    file_manager = FileManager()
    file_manager.setup_file_manager()
