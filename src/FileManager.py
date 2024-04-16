import os
import requests
import json
import shutil

# Custom imports
from CustomLogger import CustomLogger
from ProjectUtils import URL, FOLDER, FILE, GET_WORKING_DIR


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

    # TODO: Replace "app_defaults/" with None when the app is ready for release
    def __init__(self) -> None:
        self._REQUIRED_FOLDERS = {
            FOLDER.SAVE_FILES,
            FOLDER.DATA,
            FOLDER.LOGS,
            FOLDER.SETTINGS,
            FOLDER.THEMES,
        }

        # Stores the required file enums
        self._REQUIRED_FILES = {
            FILE.STATS,
            FILE.LOCKING_INFO,
            FILE.AGENT_CONFIG,
            FILE.USER_SETTINGS,
            FILE.SETTINGS,
            FILE.DEFAULT_SAVE,
            FILE.DEFAULT_THEME,
        }

        # Main directory for the files
        self._MAIN_DIR = GET_WORKING_DIR()

        # URL to download the files from
        self._DOWNLOAD_URL = f"{URL.DOWNLOAD_URL.value}/{FOLDER.DEFAULTS.value}/"

        # Dictionary to store the data from the files in the form
        # {file_enum: config_dict}
        self.configs = dict()

        # Set up logging
        self._logger = CustomLogger("File Manager").get_logger()

    # Start Function
    def setup(self) -> None:
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

        # Creates the required directories if they don't exist
        for folder in self._REQUIRED_FOLDERS:
            # Creates subdirs
            os.makedirs(self._absolute_file_path(folder.value), exist_ok=True)

        for file in self._REQUIRED_FILES:
            file_path = self._absolute_file_path(file.value)
            if not os.path.isfile(file_path):
                self._logger.info(f"{file_path} not found, downloading")
                self._download_file(file.value, file_path)

        settings_rel_path = FILE.SETTINGS.value
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
            self._override_json_file(stats_file, FILE.STATS.value, delete_old=False)
            self._override_json_file(
                stats_file, FILE.USER_SETTINGS.value, delete_old=False
            )

        # Check for user_settings file
        user_settings_file = os.path.join(old_dir, "user_settings.json")
        if os.path.exists(user_settings_file):
            self._logger.info(
                "Found old user_settings.json file, migrating to new directory"
            )
            self._override_json_file(
                user_settings_file, FILE.SETTINGS.value, delete_old=False
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
        self.set_config(FILE.SETTINGS, self._settings)

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

    def _migrate_old_save_files(self):
        # TODO: Impletment migration in format agent: [unlocked, random]
        pass

    # endregion

    def _read_all_files(self) -> None:
        """
        Reads all the files into memory.
        """
        for file in FILE:
            self.configs[file.name] = json.load(
                open(self._absolute_file_path(file.value), "r")
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

    def get_config(self, file: FILE) -> dict:
        """
        Returns the configuration dictionary for the specified file.

        Args:
            file (constants.Files): The file enum for which the configuration is required.

        Returns:
            dict: The configuration dictionary for the specified file.
        """
        return self.configs.get(file.name, None)

    def set_config(self, file: FILE, config: dict) -> None:
        """
        Sets the configuration dictionary for the specified file.

        Args:
            file (constants.Files): The file enum for which the configuration is required.
            config (dict): The configuration dictionary to set.
        """
        self.configs[file.name] = config

        with open(self._absolute_file_path(file.value), "w") as f:
            json.dump(config, f, indent=4)

    def set_value(self, file: FILE, key: str, value: any) -> None:
        """
        Sets the value of the specified key in the configuration dictionary of the specified file.

        Args:
            file (constants.Files): The file enum for which the configuration is required.
            key (str): The key to set the value for.
            value (any): The value to set for the key.
        """
        self.configs[file.name][key] = value

        with open(self._absolute_file_path(file.value), "w") as f:
            json.dump(self.configs[file.name], f, indent=4)

    def get_value(self, file: FILE, key: str) -> any:
        """
        Returns the value of the specified key from the configuration dictionary of the specified file.

        Args:
            file (constants.Files): The file enum for which the configuration is required.
            key (str): The key for which the value is required.

        Returns:
            any: The value of the specified key.
        """
        return self.configs[file.name].get(key, None)

    def get_save_file(self, save_name: str) -> dict:
        """
        Returns the configuration dictionary for the specified save file.

        Args:
            save_name (str): The name of the save file.

        Returns:
            dict: The configuration dictionary for the specified save file.
        """
        save_path = os.path.join(self._absolute_file_path(FOLDER.SAVE_FILES.value, f"{save_name}.json"))
        return json.load(open(save_path, "r"))

    # region:  Update files

    def update_file(self, file: FILE) -> None:
        """
        Update a file by downloading the latest version from the repository.
        # TODO: Make this method not override settings already present

        Args:
            file_path (constants.Files): The file enum that needs to be updated.
        """
        self._logger.info(f"Updating {file.value} to the latest version")

        # Store the path where the file will be saved
        save_path = os.path.join(self._absolute_file_path(file.value))

        # Download the latest version of the file
        self._download_file(file.value, save_path)

        self._logger.info(f"Updated {file.value} to the latest version")


# TODO: FINISH SAVEMANAGER AND REMOVE SAVE RELATED METHODS
    def update_save_file(self, save_name: str, config: dict) -> None:
        """
        Update a save file by saving the latest configuration to the specified file.

        Args:
            save_name (str): The name of the save file.
            config (dict): The configuration dictionary to save.
        """
        parent_dir = os.pardir(FILE.DEFAULT_SAVE.value)
        save_path = os.path.join(self._absolute_file_path(parent_dir, save_name))

        with open(save_path, "w") as f:
            json.dump(config, f, indent=4)

        self._logger.info(f"Updated save file {save_name}")

    # endregion

    def get_theme(self, theme_name: str) -> dict:
        """
        Load a theme from the themes directory.

        Args:
            theme_name (str): The name of the theme to load.

        Returns:
            dict: The theme configuration dictionary.
        """
        
        if theme_name.rfind("-theme.json") == -1:
            theme_name += "-theme.json"
        
        theme_path = os.path.join(
            self._absolute_file_path(FOLDER.THEMES.value, theme_name)
        )
        return json.load(open(theme_path, "r"))


if __name__ == "__main__":
    # Test FileManager class
    file_manager = FileManager()
    file_manager.setup()
