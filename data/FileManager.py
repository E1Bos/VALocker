# Updates files including settings, user data, and other data files
import os
import requests
import json
import shutil
from CustomLogger import CustomLogger

class FileManager:
    """
    The FileManager class is responsible for managing the required files and directories for the VALocker application.
    It provides methods to ensure that the required files exist, download missing files, migrate old files to a new directory structure,
    and read all the files into memory. It also provides getters and setters for accessing and modifying the file data.

    Methods:
        setup_file_manager(): Sets up the FileManager by ensuring that the required files exist and reading them into memory.
        get_settings(): Returns the settings dictionary.
        get_user_settings(): Returns the user settings dictionary.
        get_stats(): Returns the stats dictionary.
        get_locking_info(): Returns the locking info dictionary.
        get_config(): Returns the config dictionary.
        set_settings(settings): Sets the settings dictionary.
        set_user_settings(user_settings): Sets the user settings dictionary.
        set_stats(stats): Sets the stats dictionary.
    """
    
    def __init__(self) -> None:
        # Dictionary to store the required files
        self._REQUIRED_FILES = {
            "data": ["config.json", "stats.json", "locking_info.json"],
            "settings": ["settings.json", "user_settings.json"],
            "save_files": ["default.json"],
            "logs": [],
        }
        
        # Main directory for the files
        self._MAIN_DIR = os.path.join(os.environ["APPDATA"], "VALocker")
        
        # URL to download the files from
        self._DOWNLOAD_URL = "https://raw.githubusercontent.com/E1Bos/VALocker/valocker-v2/default_templates/"
        
        # Dictionaries to store the data from the files
        self._settings = dict()
        self._user_settings = dict()
        self._stats = dict()
        self._locking_info = dict()
        self._config = dict()

        # Set up logging
        self._logger = CustomLogger("FileManager", "file_manager.log").get_logger()

    # Start Function
    def setup_file_manager(self) -> None:
        """
        Sets up the FileManager by ensuring that the required files exist and reading them into memory.
        """
        self._logger.info("Setting up file manager")
        self._ensure_files_exist()
        self._read_all_files()
        self._logger.info("File manager setup complete")

    #region: Creating directories and downloading files

    def _ensure_files_exist(self) -> None:
        """
        Ensures that the required directories and files exist.
        If any file is missing, it will be downloaded.
        """

        # Creates appdata/roaming/VALocker if it doesn't exist
        os.makedirs(self._MAIN_DIR, exist_ok=True)

        # Creates the required directories and files if they don't exist
        for sub_dir in self._REQUIRED_FILES.keys():
            # Creates subdirs
            os.makedirs(os.path.join(self._MAIN_DIR, sub_dir), exist_ok=True)

            # Checks files
            for file_name in self._REQUIRED_FILES[sub_dir]:
                file_path = os.path.join(self._MAIN_DIR, sub_dir, file_name)

                # If file is missing, download it
                if not os.path.isfile(file_path):
                    self._logger.info(f"{file_name} not found, downloading")
                    online_file_path = f"{sub_dir}/{file_name}"
                    self._download_file(online_file_path, file_path)
        
        settings = json.load(open(os.path.join(self._MAIN_DIR, "settings", "settings.json"), "r"))
        
        if settings["ALREADY_MIGRATED"] == False:
            self._logger.info("Files may need to be migrated, checking for old files")
            self._migrate_old_files()

    def _download_file(self, file_path: str, save_path: str) -> None:
        """
        Download a file from a public GitHub repository.

        Args:
            file_path (str): The path of the file in the repository.
            save_path (str): The path where the file should be saved.
        """
        url = f"{self._DOWNLOAD_URL}/{file_path}"

        response = requests.get(url)
        response.raise_for_status()  # Raise an exception if the request failed
        with open(save_path, "wb") as f:
            f.write(response.content)
        self._logger.info(f"Downloaded {file_path}")

    #endregion

    #region: Migrating old files

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
                return

            # Check for stats file
            stats_file = os.path.join(old_dir, "stats.json")
            if os.path.exists(stats_file):
                self._logger.info("Found old stats.json file, migrating to new directory")
                
                # Migrate the old stats.json file to the new directory
                self._override_json_file(stats_file, os.path.join("data", "stats.json"), delete_old=False)
                self._override_json_file(stats_file, os.path.join("settings", "user_settings.json"), delete_old=False)

            # Check for user_settings file
            user_settings_file = os.path.join(old_dir, "user_settings.json")
            if os.path.exists(user_settings_file):
                self._logger.info("Found old user_settings.json file, migrating to new directory")
                self._override_json_file(user_settings_file, os.path.join("settings", "settings.json"), delete_old=False)

            save_files_dir = os.path.join(old_dir, "save_files")
            if os.path.exists(save_files_dir):
                self._logger.info("Found old save_files directory, migrating to new directory")
                for file_name in os.listdir(save_files_dir):
                    save_file_location = os.path.join(save_files_dir, file_name)
                    new_save_file_location = os.path.join(self._MAIN_DIR, "save_files", file_name)
                    shutil.move(save_file_location, new_save_file_location)
                    self._logger.info(f"Migrated {file_name} to {new_save_file_location}")
                os.rmdir(save_files_dir)
                self._logger.info(f"Deleted {save_files_dir}")
            
            self._settings["ALREADY_MIGRATED"] = True
            self.set_settings(self._settings)

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
        new_stats_json = json.load(
            open(os.path.join(self._MAIN_DIR, new_file_path), "r")
        )

        # Update the new stats.json file
        for key, value in old_stats_json.items():
            if key in new_stats_json:
                new_stats_json[key] = value

        # Save the updated new_stats_json
        with open(os.path.join(self._MAIN_DIR, new_file_path), "w") as f:
            json.dump(new_stats_json, f, indent=4)
            
        self._logger.info(f"Migrated {old_file_path} to {os.path.join(self._MAIN_DIR, new_file_path)}")

        # Delete the old file
        if delete_old:
            os.remove(old_file_path)
            self._logger.info(f"Deleted {old_file_path}")

    #endregion

    def _read_all_files(self) -> None:
        """
        Reads all the files into memory.
        """
        self._settings = json.load(open(os.path.join(self._MAIN_DIR, "settings", "settings.json"), "r"))
        self._user_settings = json.load(open(os.path.join(self._MAIN_DIR, "settings", "user_settings.json"), "r"))
        self._stats = json.load(open(os.path.join(self._MAIN_DIR, "data", "stats.json"), "r"))
        self._locking_info = json.load(open(os.path.join(self._MAIN_DIR, "data", "locking_info.json"), "r"))
        self._config = json.load(open(os.path.join(self._MAIN_DIR, "data", "config.json"), "r"))
        self._logger.info("Read all files into memory")

    #region:  Getters

    def get_settings(self) -> dict:
        """
        Returns the settings dictionary.
        """
        return self._settings
    
    def get_user_settings(self) -> dict:
        """
        Returns the user settings dictionary.
        """
        return self._user_settings
    
    def get_stats(self) -> dict:
        """
        Returns the stats dictionary.
        """
        return self._stats
    
    def get_locking_info(self) -> dict:
        """
        Returns the locking info dictionary.
        """
        return self._locking_info
    
    def get_config(self) -> dict:
        """
        Returns the config dictionary.
        """
        return self._config
    
    #endregion
    
    #region: Setters
    
    def set_settings(self, settings: dict) -> None:
        """
        Sets the settings dictionary.
        """
        self._settings = settings
        with open(os.path.join(self._MAIN_DIR, "settings", "settings.json"), "w") as f:
            json.dump(settings, f, indent=4)
    
    def set_user_settings(self, user_settings: dict) -> None:
        """
        Sets the user settings dictionary.
        """
        self._user_settings = user_settings
        with open(os.path.join(self._MAIN_DIR, "settings", "user_settings.json"), "w") as f:
            json.dump(user_settings, f, indent=4)
    
    def set_stats(self, stats: dict) -> None:
        """
        Sets the stats dictionary.
        """
        self._stats = stats
        with open(os.path.join(self._MAIN_DIR, "data", "stats.json"), "w") as f:
            json.dump(stats, f, indent=4)

    def set_locking_info(self, locking_info: dict) -> None:
        """
        Sets the locking info dictionary.
        """
        self._locking_info = locking_info
        with open(os.path.join(self._MAIN_DIR, "data", "locking_info.json"), "w") as f:
            json.dump(locking_info, f, indent=4)

    def set_config(self, config: dict) -> None:
        """
        Sets the config dictionary.
        """
        self._config = config
        with open(os.path.join(self._MAIN_DIR, "data", "config.json"), "w") as f:
            json.dump(config, f, indent=4)

    #endregion
