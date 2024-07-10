import os
import requests
import json
from ruamel.yaml import YAML

# Custom imports
from CustomLogger import CustomLogger
from Constants import URL, FOLDER, FILE, LOCKING_CONFIG, GET_WORKING_DIR


class FileManager:
    """
    The FileManager class is responsible for managing the required files and directories for the VALocker application.
    It provides methods to ensure that the required files exist, download missing files, migrate old files to a new directory structure,
    and read all the files into memory. It also provides getters and setters for accessing and modifying the file data.

    Methods:
        setup_file_manager(): Sets up the FileManager by ensuring that the required files exist and reading them into memory.
        update_file(FILE): Update a file by downloading the latest version from the repository.
        get_config(FILE): Returns the configuration dictionary for the specified file.
        set_config(FILE, dict): Sets the configuration dictionary for the specified file.

    @author: [E1Bos](https://www.github.com/E1Bos)
    """

    _REQUIRED_FOLDERS: list[FOLDER] = [
        FOLDER.SAVE_FILES,
        FOLDER.DATA,
        FOLDER.LOGS,
        FOLDER.SETTINGS,
        FOLDER.THEMES,
        FOLDER.LOCKING_CONFIGS,
    ]

    _REQUIRED_FILES: list[FILE | LOCKING_CONFIG] = [
        FILE.STATS,
        FILE.AGENT_CONFIG,
        FILE.SETTINGS,
        FILE.DEFAULT_SAVE,
        FILE.DEFAULT_THEME,
        # All locking configs
    ]

    _WORKING_DIR: str = GET_WORKING_DIR()

    _DOWNLOAD_URL: str = f"{URL.DOWNLOAD_URL.value}/{FOLDER.DEFAULTS.value}/"

    configs: dict[FILE | LOCKING_CONFIG, dict] = dict()
    locking_configs: dict[str, LOCKING_CONFIG] = dict()

    yaml: YAML = YAML(typ="rt")
    _logger: CustomLogger = CustomLogger("File Manager").get_logger()

    def __init__(self) -> None:
        self.yaml.indent(mapping=2, sequence=4, offset=2)

        for locking_config in LOCKING_CONFIG:
            self._REQUIRED_FILES.append(locking_config)

    # Start Function
    def setup(self) -> None:
        """
        Sets up the FileManager by ensuring that the required files exist and reading them into memory.
        """
        self._logger.info("Setting up file manager")

        self._ensure_files_exist()
        self._read_all_files()
        self._logger.info("File manager setup complete")

        if self.get_value(FILE.SETTINGS, "alreadyMigrated", False) == False:
            self._logger.info("Files may need to be migrated, checking for old files")
            self._migrate_old_files()

    # region: Creating directories and downloading files

    def _ensure_files_exist(self) -> None:
        """
        Ensures that the required directories and files exist.
        If any file is missing, it will be downloaded.
        """

        # Creates appdata/roaming/VALocker if it doesn't exist
        os.makedirs(self._WORKING_DIR, exist_ok=True)

        # Creates the required directories if they don't exist
        for folder in self._REQUIRED_FOLDERS:
            # Creates subdirs
            os.makedirs(self._absolute_file_path(folder.value), exist_ok=True)

        for file in self._REQUIRED_FILES:
            file_path = self._absolute_file_path(file.value)
            if not os.path.isfile(file_path):

                self._logger.info(f"{file_path} not found, downloading")

                file_data = self._download_file(file)

                with open(file_path, "w") as f:
                    self.yaml.dump(file_data, f)

    def _download_file(self, file: FILE | LOCKING_CONFIG) -> dict:
        """
        Download a file from a public GitHub repository and returns the content.

        Args:
            file (FILE): The enum of the file in the repository.

        Returns:
            dict: The content of the downloaded file.

        Raises:
            requests.exceptions.RequestException: If the request to download the file fails.
        """
        url = f"{self._DOWNLOAD_URL}{file.value}"

        self._logger.info(f"Downloading {file.value} from {url}")

        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception if the request failed
            self._logger.info(f"Downloaded {file.value}")
            return self.yaml.load(response.text)

        except (
            requests.exceptions.RequestException,
            requests.exceptions.HTTPError,
        ) as e:
            self._logger.error(f"Error downloading {file.value}: {e}")
            raise e

    # endregion

    # region: Migrating old files

    def _migrate_old_files(self) -> None:
        """
        Check if the old VALocker directory exists and move the files to the new directory.

        This method is responsible for migrating the old VALocker files to the new directory structure.
        It checks for the existence of the old directory and performs the following actions:
        - Migrates the old `stats.json` file to the new directory.
        - Migrates the old `user_settings.json` file to the new directory.
        - Migrates the files in the `save_files` directory to the new directory.
        - Updates the settings to indicate that the migration has already been performed.
        - Deletes `stats.json`, `user_settings.json`, and the `save_files` directory.

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

            with open(stats_file, "r") as f:
                stats_data: dict = json.load(f)

            new_stats = {
                "timesUsed": stats_data.get("TIMES_USED"),
                "timeToLock": stats_data.get("TIME_TO_LOCK")[-1],
                "timeToLockSafe": [
                    stats_data["TIME_TO_LOCK"][safe_strength]
                    for safe_strength in range(3)
                ],
            }

            new_settings = {
                "favoritedSaveFiles": stats_data.get("FAVORITED_SAVE_FILES"),
            }

            # Migrate the old stats data to the new file structure
            self._update_data(new_stats, FILE.STATS)
            self._update_data(new_settings, FILE.SETTINGS)

            os.remove(stats_file)
            self._logger.info(f"Deleted {stats_file}")

        # Check for user_settings file
        user_settings_file = os.path.join(old_dir, "user_settings.json")
        if os.path.exists(user_settings_file):
            self._logger.info(
                "Found old user_settings.json file, migrating to new directory"
            )

            with open(user_settings_file, "r") as f:
                user_settings_data: dict = json.load(f)

            new_settings = {
                "activeSaveFile": f"{user_settings_data.get('ACTIVE_SAVE_FILE')}.yaml",
                "enableOnStartup": user_settings_data.get("ENABLE_ON_STARTUP"),
                "safeModeOnStartup": user_settings_data.get("SAFE_MODE_ON_STARTUP"),
                "safeModeStrengthOnStartup": user_settings_data.get(
                    "SAFE_MODE_STRENGTH_ON_STARTUP"
                ),
                "lockingConfirmations": user_settings_data.get("LOCKING_CONFIRMATIONS"),
                "hideDefaultSave": user_settings_data.get("HIDE_DEFAULT_SAVE_FILE"),
                "antiAfkMode": user_settings_data.get("ANTI_AFK_MODE"),
            }

            self._update_data(new_settings, FILE.SETTINGS)

            os.remove(user_settings_file)
            self._logger.info(f"Deleted {user_settings_file}")

        # Check if config file exists
        config_file = os.path.join(old_dir, "config.json")
        if os.path.exists(config_file):
            self._logger.info("Found old config.json file, deleting")
            os.remove(config_file)

        # Check for save_files directory
        save_files_dir = os.path.join(old_dir, "save_files")
        if os.path.exists(save_files_dir):
            self._logger.info(
                "Found old save_files directory, migrating to new directory"
            )

            for file_name in os.listdir(save_files_dir):
                full_path = os.path.join(save_files_dir, file_name)
                self._migrate_old_save_file(full_path, file_name)

            self._logger.info(f"Migrated all save files in {save_files_dir}")

            # Remove the old save_files dir
            os.rmdir(save_files_dir)
            self._logger.info(f"Deleted {save_files_dir}")

        self._logger.info("Migration complete")
        self._set_migrated_flag(True)

    def _update_data(self, new_data: dict, file: FILE | LOCKING_CONFIG) -> None:
        """
        Updates a file with data and reloads the file into memory.

        Args:
            data (dict): The data of the file to migrate.
            file (FILE): The file enum to migrate the file to.
        """

        with open(self._absolute_file_path(file.value), "r") as f:
            current_data: dict = self.yaml.load(f)

        current_data.update(new_data)

        with open(self._absolute_file_path(file.value), "w") as f:
            self.yaml.dump(current_data, f)

        self._logger.info(
            f"Migrated old values to {self._absolute_file_path(file.value)}"
        )

        self.configs[file] = current_data

    def _migrate_old_save_file(
        self, old_save_file_path: str, old_save_name: str
    ) -> None:

        with open(old_save_file_path, "r") as f:
            save_data: dict = json.load(f)

        current_active_agent: str = save_data.get("SELECTED_AGENT").lower()
        old_agent_unlock: dict[str, bool] = save_data.get("UNLOCKED_AGENTS")
        old_agent_random: dict[str, bool] = save_data.get("RANDOM_AGENTS")
        old_map_specific_agents: dict[str, str] = save_data.get("MAP_SPECIFIC_AGENTS")

        default_agents: list[str] = self.get_config(FILE.AGENT_CONFIG).get(
            "defaultAgents"
        )

        agent_status = {}
        for agent in old_agent_unlock:
            if agent.lower() in default_agents:
                agent_status[agent.lower()] = [old_agent_random[agent]]
                continue

            agent_status[agent.lower()] = [
                old_agent_unlock[agent],
                old_agent_random[agent],
            ]

        maps = {}
        for map_name, value in old_map_specific_agents.items():
            maps[map_name.lower()] = value.lower() if value is not None else None

        new_save_data = {
            "selectedAgent": current_active_agent,
            "agents": agent_status,
            "mapSpecificAgents": maps,
        }

        new_save_name = old_save_name.replace(".json", ".yaml")

        new_save_file_location = os.path.join(
            self._WORKING_DIR, FOLDER.SAVE_FILES.value, new_save_name
        )

        with open(new_save_file_location, "w") as f:
            self.yaml.dump(new_save_data, f)

        os.remove(old_save_file_path)

        self._logger.info(f"Migrated {old_save_name} to {new_save_file_location}")

    def _set_migrated_flag(self, value: bool) -> None:
        """
        Sets the value of the 'ALREADY_MIGRATED' flag in the settings dictionary.

        Args:
            value (bool): The value to set for the 'ALREADY_MIGRATED' flag.

        """
        self.set_value(FILE.SETTINGS, "alreadyMigrated", value)

    # endregion

    def _read_all_files(self) -> None:
        """
        Reads all the files into memory.
        """
        for config in FILE:
            with open(self._absolute_file_path(config.value), "r") as f:
                self.configs[config] = self.yaml.load(f)

        for config in os.listdir(
            self._absolute_file_path(FOLDER.LOCKING_CONFIGS.value)
        ):
            try:
                config_enum = LOCKING_CONFIG(config)
                with open(self._absolute_file_path(config_enum.value), "r") as f:
                    data: dict = self.yaml.load(f)
            except ValueError:
                with open(
                    self._absolute_file_path(FOLDER.LOCKING_CONFIGS.value, config), "r"
                ) as f:
                    data: dict = self.yaml.load(f)

                    is_custom = data.get("custom", False)

                    config_enum = config
                    self._logger.info(
                        f"Found config: {config_enum} - custom: {is_custom}"
                    )

            self.configs[config_enum] = data

            title = data.get("title")
            self.locking_configs[title] = config_enum

        self._logger.info("Read all files into memory")

    def _absolute_file_path(self, *args) -> str:
        """
        Returns the absolute file path by joining the main directory path with the provided arguments.

        Args:
            *args: Variable number of arguments representing the path components.

        Returns:
            str: The absolute file path.
        """
        return os.path.join(self._WORKING_DIR, *args)

    def get_config(self, file: FILE | LOCKING_CONFIG | str) -> dict:
        """
        Returns the configuration dictionary for the specified file.

        Args:
            file (constants.Files | constants.LOCKING_CONFIG | str): The enum for which the configuration is required.
                If the file is custom, a string representing the file name is required.


        Returns:
            dict: The configuration dictionary for the specified file.
        """
        return self.configs.get(file, {})

    def set_config(self, file: FILE | LOCKING_CONFIG, config: dict) -> None:
        """
        Sets the configuration dictionary for the specified file.

        Args:
            file (constants.Files): The file enum for which the configuration is required.
            config (dict): The configuration dictionary to set.
        """
        self.configs[file] = config

        with open(self._absolute_file_path(file.value), "w") as f:
            self.yaml.dump(config, f)

    def set_value(self, file: FILE | LOCKING_CONFIG, key: str, value: any) -> None:
        """
        Sets the value of the specified key in the configuration dictionary of the specified file.

        Args:
            file (constants.Files): The file enum for which the configuration is required.
            key (str): The key to set the value for.
            value (any): The value to set for the key.
        """
        self.configs[file][key] = value

        with open(self._absolute_file_path(file.value), "w") as f:
            self.yaml.dump(self.configs[file], f)

    def get_value(self, file: FILE | LOCKING_CONFIG, key: str, set_value=None) -> any:
        """
        Returns the value of the specified key from the configuration dictionary of the specified file.

        Args:
            file (constants.Files): The file enum for which the configuration is required.
            key (str): The key for which the value is required.
            set_value (any): The value to set for the key if it doesn't exist.

        Returns:
            any: The value of the specified key.
        """
        value = self.configs[file].get(key, None)

        if value is None and set_value is not None:
            self.set_value(file, key, set_value)
            return set_value

        return value

    def get_locking_configs(self) -> dict[str, LOCKING_CONFIG]:
        """
        Returns a dictionary of locking configs with the title as the key.

        Returns:
            dict[str, LOCKING_CONFIG]: A dictionary of locking configs with the title as the key.
        """
        return self.locking_configs

    def get_locking_config_by_file_name(
        self, file_name: str, get_title: bool = False, get_data: bool = False
    ) -> str | LOCKING_CONFIG | dict[str, any]:
        """
        Returns the locking config value saved in self.configs.

        Args:
            file_name (str): The file name of the locking config.
            get_title (bool): If True, the title of the locking config is returned.
            get_data (bool): If True, the data of the locking config is returned.

        Returns:
            str | LOCKING_CONFIG: The locking config
        """

        if get_title and get_data:
            raise ValueError("Only one of get_title and get_data can be True")

        for config in self.get_locking_configs().items():
            if type(config[1]) is LOCKING_CONFIG:
                file = config[1].value
            else:
                file = config[1]

            file = os.path.basename(file)
            if file == file_name:
                if get_title:
                    return config[0]
                if get_data:
                    return self.configs[config[1]]
                return config[1]

    # region:  Update files

    def update_file(self, file: FILE | LOCKING_CONFIG) -> None:
        """
        Update a file by downloading the latest version from the repository.

        Args:
            file_path (FILE): The file enum that needs to be updated.
        """
        self._logger.info(f"Updating {file.value} to the latest version")

        # Download the latest version of the file
        data = self._download_file(file)

        self.update_config_data(file, data)

        self._logger.info(f"Updated {file.value} to the latest version")

    # endregion

    def update_config_data(
        self, file: FILE | LOCKING_CONFIG, new_data: dict[str, any]
    ) -> None:
        """
        Update the configuration data in the specified file while preserving user-defined fields.
        """
        
        # Load current configuration
        with open(self._absolute_file_path(file.value), "r") as f:
            current_data = self.yaml.load(f)

        # Identify user-defined fields to preserve
        user_defined_fields = ["field1", "field2"]  # Example fields to preserve

        # Prepare a copy of the current data for fields to preserve
        preserved_data = {}

        match file:
            case FILE.SETTINGS:
                user_defined_fields = [
                    "theme",
                    "lockingConfig",
                    "activeSaveFile",
                    "favoritedSaveFiles",
                    "enableOnStartup",
                    "safeModeOnStartup",
                    "safeModeStrengthOnStartup",
                    "alreadyMigrated",
                ]
                preserved_data = {
                    field: current_data[field]
                    for field in user_defined_fields
                    if field in current_data
                }
            case _:
                pass

        # Update current configuration with new data
        current_data.update(new_data)

        # Restore user-defined fields to ensure they are not overwritten
        current_data.update(preserved_data)

        # Save updated configuration
        with open(self._absolute_file_path(file.value), "w") as f:
            self.yaml.dump(current_data, f)

        # Log the update
        self._logger.info(
            f"Updated configuration, preserving user-defined fields, in {self._absolute_file_path(file.value)}"
        )

        # Reload the configuration in memory if necessary
        self.configs[file] = current_data

    def get_files_in_folder(self, folder: FOLDER) -> list[str]:
        """
        Get all the files in a specified folder.

        Args:
            folder (FOLDER): The folder enum for which the files are required.

        Returns:
            list[str]: A list of file names in the specified folder.
        """
        folder_path = self._absolute_file_path(folder.value)
        return os.listdir(folder_path)


if __name__ == "__main__":
    # Test FileManager class
    file_manager = FileManager()
    file_manager.setup()
