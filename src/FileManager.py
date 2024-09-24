
from typing import Optional
import os
import requests
import json
from ruamel.yaml import YAML
import datetime

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
    ]

    _WORKING_DIR: str = GET_WORKING_DIR()

    _DOWNLOAD_URL: str = f"{URL.DOWNLOAD_URL.value}/{FOLDER.DEFAULTS.value}/"

    configs: dict[FILE | LOCKING_CONFIG, dict] = dict()
    locking_configs: dict[str, LOCKING_CONFIG] = dict()

    yaml: YAML = YAML(typ="rt")
    _logger: CustomLogger = CustomLogger.get_instance().get_logger("FileManager")

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

        if self.get_value(FILE.SETTINGS, "$alreadyMigrated", False) == False:
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
        url = file.download_url
        
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
                "$favoritedSaveFiles": stats_data.get("FAVORITED_SAVE_FILES"),
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
                "$activeSaveFile": f"{user_settings_data.get('ACTIVE_SAVE_FILE')}.yaml",
                "$enableOnStartup": user_settings_data.get("ENABLE_ON_STARTUP"),
                "$safeModeOnStartup": user_settings_data.get("SAFE_MODE_ON_STARTUP"),
                "$safeModeStrengthOnStartup": user_settings_data.get(
                    "SAFE_MODE_STRENGTH_ON_STARTUP"
                ),
                "$lockingConfirmations": user_settings_data.get("LOCKING_CONFIRMATIONS"),
                "$hideDefaultSave": user_settings_data.get("HIDE_DEFAULT_SAVE_FILE"),
                "$antiAfkMode": user_settings_data.get("ANTI_AFK_MODE"),
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
        self.set_value(FILE.SETTINGS, "$alreadyMigrated", value)

    # endregion

    def _read_all_files(self) -> None:
        """
        Reads all the files into memory.
        """
        for config in FILE:
            file_path = self._absolute_file_path(config.value)
            self._logger.debug(f"Reading file: {file_path}")
            with open(file_path, "r") as f:
                self.configs[config] = self.yaml.load(f)
                self._logger.debug(self.configs[config])
                
        for config in os.listdir(
            self._absolute_file_path(FOLDER.LOCKING_CONFIGS.value)
        ):
            try:
                config_enum = LOCKING_CONFIG(config)
                file_path = self._absolute_file_path(config_enum.value)
                
            except ValueError:
                self._logger.debug(f"Found custom config: {config}")
                config_enum = config
                file_path = self._absolute_file_path(FOLDER.LOCKING_CONFIGS.value, config)
            
            self._logger.debug(f"Reading file: {file_path}")
            with open(file_path, "r") as f:
                data: dict = self.yaml.load(f)

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
        # check if the key exists with a $
        if self.configs[file].get(f"${key}", None) is not None:
            self.configs[file][f"${key}"] = value
        else:
            self.configs[file][key] = value
        

        with open(self._absolute_file_path(file.value), "w") as f:
            self.yaml.dump(self.configs[file], f)

    def get_value(self, file: FILE | LOCKING_CONFIG, key: str, set_value: Optional[any] = None) -> any:
        """
        Returns the value of the specified key from the configuration dictionary of the specified file.

        If the value is not found, it can be set with the `set_value` parameter.

        Args:
            file (constants.Files): The file enum for which the configuration is required.
            key (str): The key for which the value is required.
            set_value (any, optional): The value to set for the key if it doesn't exist. Defaults to None.

        Returns:
            any: The value of the specified key.
        """
        value = self.configs[file].get(key, None)
        value = value or self.configs[file].get(f"${key}", None)

        if value is None and set_value is not None:
            self._logger.debug(f"Value for key '{key}' not found in {file.value}, setting to {set_value}")
            self.set_value(file, key, set_value)
            return set_value

        self._logger.debug(f"Value for key '{key}' in {file.value} is {value}")
        return value

    def get_locking_configs(self) -> dict[str, LOCKING_CONFIG]:
        """
        Returns a dictionary of locking configs with the title as the key.

        Returns:
            dict[str, LOCKING_CONFIG]: A dictionary of locking configs with the title as the key.
        """
        self._logger.debug("Getting locking configs")
        return self.locking_configs

    def get_locking_config(self, key: str) -> LOCKING_CONFIG | None:
        """
        Returns the locking config for the specified key.

        Args:
            key (str): The key of the locking config.

        Returns:
            LOCKING_CONFIG | None: The locking config if found, otherwise None.
        """
        self._logger.debug(f"Getting locking config for key {key}")
        return self.locking_configs.get(key)

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
            str | LOCKING_CONFIG | dict[str, any]: The locking config
        """
        self._logger.debug(f"Getting locking config by file name: {file_name}")

        if get_title and get_data:
            raise ValueError(
                "Only one of get_title and get_data can be True. "
                "Please specify which one to use."
            )

        locking_configs = self.get_locking_configs()

        for title, config in locking_configs.items():
            if type(config) is LOCKING_CONFIG:
                file = config.value
            else:
                file = config

            file = os.path.basename(file)

            if file == file_name:
                self._logger.debug(f"Found locking config: {title}")

                if get_title:
                    return title
                if get_data:
                    return self.configs[config]
                return config

        self._logger.warning(f"Locking config not found: {file_name}")
        return None

    # region:  Update files

    def update_file(self, file: FILE | LOCKING_CONFIG) -> None:
        """
        Update a file by downloading the latest version from the repository.

        Args:
            file (FILE | LOCKING_CONFIG): The file enum that needs to be updated.
        """
        self._logger.info(f"Updating {file.value} to the latest version")

        # Download the latest version of the file
        data = self._download_file(file)

        self._logger.debug(f"Downloaded data for {file.value}: {data}")

        # Update the configuration data in memory
        self.update_config_data(file, data)

        self._logger.info(f"Updated {file.value} to the latest version")

    def update_config_data(
        self, file: FILE | LOCKING_CONFIG, new_data: dict[str, any]
    ) -> None:
        """
        Update the configuration data in the specified file while preserving user-defined fields.

        This method loads the current configuration, prepares a copy of the current configuration
        for fields to preserve, merges the user-defined fields with the new data, saves the
        updated configuration, and reloads the configuration in memory if necessary.

        Args:
            file (FILE | LOCKING_CONFIG): The file enum that needs to be updated.
            new_data (dict[str, any]): The new configuration data to update with.
        """
        self._logger.debug(f"Updating {file.value} with new data: {new_data}")

        # Load current configuration
        current_data = self._load_config_data(file)

        self._logger.debug(f"Current configuration in {file.value}: {current_data}")

        # Prepare a copy of the current configuration for fields to preserve
        preserved_data = {
            key: value
            for key, value in current_data.items()
            if not key.startswith("$$") and key.startswith("$")
        }

        self._logger.debug(f"Preserved user-defined fields in {file.value}: {preserved_data}")

        # Preserve the user defined fields
        for key in preserved_data:
            new_data[key] = preserved_data[key]

        self._logger.debug(f"Updated configuration, preserved user-defined fields, in {file.value}. Fields: {new_data}")

        # Save updated configuration
        self._save_config_data(file, new_data)

        self._logger.info(f"Updated configuration, preserved user-defined fields, in {file.value}.")

        # Reload configuration in memory
        self.configs[file] = self._load_config_data(file)


    def _load_config_data(self, file: FILE | LOCKING_CONFIG) -> dict[str, any]:
        """
        Load the configuration data from the specified file.

        Args:
            file (FILE | LOCKING_CONFIG): The file enum that needs to be loaded.

        Returns:
            dict[str, any]: The configuration data.
        """
        with open(self._absolute_file_path(file.value), "r") as f:
            return self.yaml.load(f)


    def _save_config_data(self, file: FILE | LOCKING_CONFIG, data: dict[str, any]) -> None:
        """
        Save the configuration data to the specified file.

        Args:
            file (FILE | LOCKING_CONFIG): The file enum that needs to be saved.
            data (dict[str, any]): The configuration data to save.
        """
        with open(self._absolute_file_path(file.value), "w") as f:
            self.yaml.dump(data, f)

    # endregion

    def get_files_in_folder(self, folder: FOLDER, contains_field: Optional[str] = None) -> list[str]:
        """
        Get all the files in a specified folder.

        This method returns a list of file names in the specified folder. The folder
        path is obtained using the `absolute_file_path` method.

        Args:
            folder (FOLDER): The folder enum for which the files are required.
            contains_field (str): The field that the files must contain. Defaults to None.

        Returns:
            list[str]: A list of file names in the specified folder.
        """
        folder_path = self._absolute_file_path(folder.value)
        self._logger.debug(f"Getting files in folder: {folder_path}")
        if not os.path.exists(folder_path):
            self._logger.warning(f"Folder {folder_path} does not exist")
            return []

        file_list = [file for file in os.listdir(folder_path) if file.endswith(".yaml")]
        filtered_files = []

        for file in file_list:
            self._logger.debug(f"Checking file: {file}")
            try:
                with open(os.path.join(folder_path, file), "r") as f:
                    if contains_field is None or contains_field in f.read():
                        filtered_files.append(file)
            except Exception as e:
                self._logger.warning(f"Failed to check file: {file}. Exception: {e}")

        self._logger.info(f"Found {len(filtered_files)} files in folder: {folder_path}")
        return filtered_files

    def reset_configs(self) -> None:
        """
        Resets the configuration files to their default values. This method will backup the current configuration files in the "backups" folder before resetting them, in case the user wants to restore the previous configuration.

        This method will download the default configuration files from the GitHub repository and overwrite the current configuration files with the default ones.

        Args:
            None

        Returns:
            None
        """
        # List of files that require a backup before resetting
        REQUIRES_BACKUP: list[FILE] = [
            FILE.STATS,
            FILE.SETTINGS,
            FILE.DEFAULT_SAVE,
        ]
        
        self._logger.info("Resetting configuration files")
        
        # Backup the current configuration files if they exist
        for file in self._REQUIRED_FILES:
            if file in REQUIRES_BACKUP:
                if not os.path.exists(self._absolute_file_path("backups")):
                    os.mkdir(self._absolute_file_path("backups"))
                    
                self._logger.debug(f"Backing up {file.name}")
                
                with open(self._absolute_file_path(file.value), "r") as f:
                    file_content = self.yaml.load(f)
                
                now = datetime.datetime.now().strftime("-%d-%m-%Y--%H-%M")
                with open(self._absolute_file_path(f"backups/{file.file_name}-{now}.bak"), "w") as f:
                    self.yaml.dump(file_content, f)
                self._logger.info(f"Backed up {file.name}")
        
        # Fetch the default configuration files from the repository
        for file in self._REQUIRED_FILES:
            self._logger.debug(f"Fetching content for {file.name}")
            
            try:
                file_content = self._download_file(file)
            except Exception as e:
                self._logger.error(f"Failed to fetch content for {file.name}. Exception: {e}")
                continue
            
            # Save the default configuration file
            with open(self._absolute_file_path(file.value), "w") as f:
                self.yaml.dump(file_content, f)
            
            self._logger.info(f"Reset {file.name}")
        
            # Reload the configuration in memory
            self.configs[file] = file_content
            self._logger.debug(f"Reloaded {file.name} configuration in memory")
        
        self._logger.info("Configuration files reset")
        
        


if __name__ == "__main__":
    # Test FileManager class
    file_manager = FileManager()
    file_manager.setup()
