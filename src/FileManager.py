import os
import requests
import json
from ruamel.yaml import YAML

# Custom imports
from CustomLogger import CustomLogger
from Constants import URL, FOLDER, FILE, GET_WORKING_DIR


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
    """

    _REQUIRED_FOLDERS: dict = {
        FOLDER.SAVE_FILES,
        FOLDER.DATA,
        FOLDER.LOGS,
        FOLDER.SETTINGS,
        FOLDER.THEMES,
    }

    _REQUIRED_FILES: dict = {
        FILE.STATS,
        FILE.LOCKING_CONFIG,
        FILE.AGENT_CONFIG,
        FILE.SETTINGS,
        FILE.DEFAULT_SAVE,
        FILE.DEFAULT_THEME,
    }

    _WORKING_DIR: str = GET_WORKING_DIR()

    _DOWNLOAD_URL: str = f"{URL.DOWNLOAD_URL.value}/{FOLDER.DEFAULTS.value}/"

    configs: dict = dict()

    yaml: YAML = YAML(typ='rt')
    _logger: CustomLogger = CustomLogger("File Manager").get_logger()

    def __init__(self) -> None:
        self.yaml.indent(mapping=2, sequence=4, offset=2)

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

        settings_rel_path = FILE.SETTINGS.value
        with open(self._absolute_file_path(settings_rel_path), "r") as f:
            self._settings: dict = self.yaml.load(f)

        if self._settings.get("alreadyMigrated", False) == False:
            self._logger.info("Files may need to be migrated, checking for old files")
            self._migrate_old_files()

    def _download_file(self, file: FILE) -> dict:
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

        except requests.exceptions.RequestException as e:
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
            self._migrate_data(new_stats, FILE.STATS)
            self._migrate_data(new_settings, FILE.SETTINGS)

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
                "minimizeToTray": user_settings_data.get("MINIMIZE_TO_TRAY"),
                "startMinimized": user_settings_data.get("START_MINIMIZED"),
                "safeModeOnStartup": user_settings_data.get("SAFE_MODE_ON_STARTUP"),
                "safeModeStrengthOnStartup": user_settings_data.get(
                    "SAFE_MODE_STRENGTH_ON_STARTUP"
                ),
                "lockingConfirmations": user_settings_data.get("LOCKING_CONFIRMATIONS"),
                "menuConfirmations": user_settings_data.get("MENU_CONFIRMATIONS"),
                "fastModeTimings": user_settings_data.get("FAST_MODE_TIMINGS"),
                "grabKeybinds": user_settings_data.get("GRAB_KEYBINDS"),
                "persistentRandomAgents": user_settings_data.get(
                    "PERSISTENT_RANDOM_AGENTS"
                ),
                "hideDefaultSave": user_settings_data.get("HIDE_DEFAULT_SAVE_FILE"),
                "antiAfkMode": user_settings_data.get("ANTI_AFK_MODE"),
                "antiAfkTogglesDropSpike": user_settings_data.get(
                    "ANTIAFK_TOGGLES_AUTODROPSPIKE"
                ),
                "detectOpenChat": user_settings_data.get(
                    "DETECT_OPEN_CHAT_THROUGH_KEYBOARD"
                ),
                "startToolsThreadAutomatically": user_settings_data.get(
                    "START_TOOLS_THREAD_AUTOMATICALLY"
                ),
            }

            self._migrate_data(new_settings, FILE.SETTINGS)

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
        # self._set_migrated_flag(True)

    def _migrate_data(self, data_to_migrate: dict, file_to_migrate_to: FILE) -> None:
        """
        Migrates a file to a new directory.

        Args:
            data_to_migrate (dict): The data of the file to migrate.
            file_to_migrate_to (FILE): The file enum to migrate the file to.

        Returns:
            None
        """

        with open(self._absolute_file_path(file_to_migrate_to.value), "r") as f:
            new_file = self.yaml.load(f)

        for key in data_to_migrate:
            if key in new_file:
                new_file[key] = data_to_migrate[key]

        with open(self._absolute_file_path(file_to_migrate_to.value), "w") as f:
            self.yaml.dump(new_file, f)

        self._logger.info(
            f"Migrated old values to {self._absolute_file_path(file_to_migrate_to.value)}"
        )

    def _migrate_old_save_file(
        self, old_save_file_path: str, old_save_name: str
    ) -> None:

        with open(old_save_file_path, "r") as f:
            save_data: dict = json.load(f)

        current_active_agent: str = save_data.get("SELECTED_AGENT").lower()
        old_agent_unlock: dict[str, bool] = save_data.get("UNLOCKED_AGENTS")
        old_agent_random: dict[str, bool] = save_data.get("RANDOM_AGENTS")
        old_map_specific_agents: dict[str, str] = save_data.get("MAP_SPECIFIC_AGENTS")

        default_agents: list[str] = self.get_config(FILE.AGENT_CONFIG).get("defaultAgents")

        agent_status = {}
        for agent in old_agent_unlock:
            if agent.lower() in default_agents:
                agent_status[agent.lower()] = [old_agent_random[agent]]
                continue
            
            agent_status[agent.lower()] = [old_agent_unlock[agent], old_agent_random[agent]]

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
        self._settings["alreadyMigrated"] = value
        self.set_config(FILE.SETTINGS, self._settings)

    # endregion

    def _read_all_files(self) -> None:
        """
        Reads all the files into memory.
        """
        for file in FILE:
            with open(self._absolute_file_path(file.value), "r") as f:
                self.configs[file.name] = self.yaml.load(f)

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
            self.yaml.dump(config, f)

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
            self.yaml.dump(self.configs[file.name], f)

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

    # region:  Update files

    def update_file(self, file: FILE) -> None:
        """
        Update a file by downloading the latest version from the repository.
        # TODO: Make this method not override settings already present

        Args:
            file_path (FILE): The file enum that needs to be updated.
        """
        self._logger.info(f"Updating {file.value} to the latest version")

        # Store the path where the file will be saved
        save_path = os.path.join(self._absolute_file_path(file.value))

        # Download the latest version of the file
        data = self._download_file(file.value, save_path)

        self._migrate_data(data, file)

        self._logger.info(f"Updated {file.value} to the latest version")

    # endregion


if __name__ == "__main__":
    # Test FileManager class
    file_manager = FileManager()
    file_manager.setup()
    file_manager._migrate_old_files()