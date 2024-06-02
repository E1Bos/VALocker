from typing import Optional, Tuple
import requests
import time

from customtkinter import StringVar

# Custom imports
from Constants import URL, FOLDER, FILE, LOCKING_CONFIG
from CustomLogger import CustomLogger
from FileManager import FileManager


class DummyStringVar:
    def __init__(self, *args, **kwargs):
        pass

    def set(self, value: str):
        pass

    def get(self):
        pass


class Updater:
    _logger: CustomLogger = CustomLogger("Updater").get_logger()
    _file_manager: FileManager
    release_version: str
    check_frequency: int
    ITEMS_TO_CHECK: list[FILE | FOLDER] = [
        FILE.AGENT_CONFIG,
        FILE.SETTINGS,
        FOLDER.LOCKING_CONFIGS,
    ]

    def __init__(
        self, release_version, file_manager: FileManager, check_frequency=3600
    ) -> None:
        """
        The Updater class is responsible for comparing versions and determining if an update is required.

        Args:
            release_version (str): The current release version of the agent.
            file_manager (FileManager): The file manager instance to use for updating files.
            check_frequency (int): How often the agent should check for updates. Default is 1 hour.

        Attributes:
            release_version (str): The current release version of the agent.
            check_frequency (int): The frequency in seconds to check for updates.

        Methods:
            check_frequency_met: Checks if the check frequency has been met for the agent.
            check_for_version_update: Checks if an update is available for the agent.
            check_for_config_updates: Checks for updates and updates the agent if necessary.
            compare_yaml_configs: Compares the version of the current agent configuration with the latest version available.
            compare_release_versions: Compares the version of the current agent with the latest version available.
            compare_versions: Compare two version numbers and determine if an update is required.
            update_last_checked: Updates the last checked time in the settings file.
        """
        self.release_version = release_version
        self.check_frequency = check_frequency
        self._file_manager = file_manager

    def check_frequency_met(self) -> bool:
        """
        Checks if the check frequency has been met for the agent.

        Returns:
            bool: True if the check frequency has been met, False otherwise.
        """
        last_checked_release = int(
            self._file_manager.get_value(FILE.SETTINGS, "lastChecked")
        )

        time_since_last_check = int(time.time()) - last_checked_release

        if time_since_last_check < self.check_frequency:
            self._logger.info(
                f"Check frequency not met, checked {round(time_since_last_check / 60, 1)} minutes ago"
            )
            return False

        return True

    def check_for_version_update(
        self, stringVar: Optional[StringVar] = None
    ) -> str | None:
        """
        Checks if an update is available for the agent.

        Returns:
            str: The latest version if an update is available, None otherwise.
        """
        if stringVar is None:
            stringVar = StringVar()

        self._logger.info("Checking for version update")
        stringVar.set("Checking")

        update_available, latest_version = self.compare_release_versions()

        if update_available:
            self._logger.info("New version available, agent needs updating")
            stringVar.set(f"Update Available: {latest_version}")
            return latest_version

        stringVar.set("Up to date")
        return None

    def check_for_config_update(
        self,
        item: FILE | FOLDER | LOCKING_CONFIG,
        stringVar: Optional[StringVar] = None,
    ) -> None:
        if stringVar is None:
            stringVar = DummyStringVar()

        # If checking a single file
        if type(item) is FILE or type(item) is LOCKING_CONFIG:
            # Use a dummy stringvar if the type is LOCKING_CONFIG so that it doesn't
            # override the FOLDER stringvar text
            innerStringVar = stringVar if type(item) is FILE else DummyStringVar()
            
            self._logger.info(f"Checking {item.name} for updates")
            innerStringVar.set("Checking")
            update_available = self.compare_yaml_configs(item)

            if update_available:
                self._logger.info(f"{item.name} configuration needs updating")
                innerStringVar.set("Downloading update...")
                self._file_manager.update_file(item)
                innerStringVar.set("Updated")
            else:
                self._logger.info(f"{item.name} is up to date")
                innerStringVar.set("Up to date")
        # If checking an entire folder
        elif type(item) is FOLDER:

            self._logger.info(f"Checking folder {item.name} for updates")

            files = self._file_manager.get_files_in_folder(item)

            total_files = len(files)

            for checking, config_file in enumerate(files):
                try:
                    config_enum = LOCKING_CONFIG(config_file)
                    
                    self._logger.info(f"Checking {config_enum.name} for updates")
                    stringVar.set(f"({checking+1}/{total_files}) Checking")

                    update_available = self.compare_yaml_configs(config_enum)

                    if update_available:
                        self._logger.info(
                            f"{config_enum.name} configuration needs updating"
                        )
                        self._file_manager.update_file(item)
                    else:
                        self._logger.info(f"{config_enum.name} is up to date")
                        stringVar.set(f"({checking + 1}/{total_files}) Up to date")
                        
                except ValueError:
                    data = self._file_manager.get_config(config_file)
                    
                    if data.get("custom", False):
                        self._logger.info(f"Found custom config \"{data.get('title')}\", skipping")
                        continue
                    else:
                        self._logger.error(f"Failed to parse config file {config_file}")
                        stringVar.set(f"({checking + 1}/{total_files}) Error")
                        continue

    # region: YAML Config Versions

    def compare_yaml_configs(self, config_file: FILE | LOCKING_CONFIG) -> bool:
        """
        Compares the version of the current agent configuration with the latest version available.

        Args:
            config_file (constant.Files): The Enum of the configuration file to check.

        Returns:
            bool: True if the current version is older than the latest version, False otherwise.
        """
        self._logger.info(f"Comparing YAML config versions for {config_file.name}")
        current_version: str = self._file_manager.get_config(config_file).get(
            "version", None
        )

        latest_version: str = self._get_latest_config_version(config_file.value)

        self._logger.info(
            f"{config_file.name} : Current version: {current_version} | Latest version: {latest_version}"
        )

        return self.compare_versions(current_version, latest_version)

    # endregion

    def _get_latest_config_version(self, download_path: str, timeout: int = 2) -> str:
        """
        Retrieves the latest configuration version from the specified download path.

        Args:
            download_path (str): The path to the configuration file.
            timeout (int): The timeout value for the HTTP request in seconds. Default is 2 seconds.

        Returns:
            str: The latest configuration version, or None if an error occurred during the request.
        """
        config_url = f"{URL.DOWNLOAD_URL.value}/{FOLDER.DEFAULTS.value}/{download_path}"

        try:
            response = requests.get(config_url, timeout=timeout)
            response.raise_for_status()
            config_file: dict = self._file_manager.yaml.load(response.text)

        except requests.exceptions.RequestException as e:
            self._logger.error(
                f"Failed to retrieve configuration file from {config_url}, {e}"
            )
            return None
        return config_file.get("version", None)

    # region: Release Versions

    def compare_release_versions(self) -> Tuple[bool, str]:
        """
        Compares the version of the current agent with the latest version available.

        Returns:
            bool: True if the current version is older than the latest version, False otherwise.
        """
        latest_version = self._get_latest_release_version()

        self._logger.info(
            f"RELEASE: Current version: {self.release_version} | Latest version: {latest_version}"
        )

        return (
            self.compare_versions(self.release_version, latest_version),
            latest_version,
        )

    def _get_latest_release_version(self, timeout: int = 2) -> str:
        """
        Retrieves the latest release version from the API.

        Args:
            timeout (int): The timeout value for the HTTP request in seconds. Default is 2 seconds.

        Returns:
            str: The latest release version as a string, or None if an error occurred during the request.
        """
        try:
            release_info: requests.Response = requests.get(
                URL.API_RELEASE_URL.value, timeout=timeout
            )
            release_info.raise_for_status()

            release_yaml: dict = self._file_manager.yaml.load(release_info.text)
            release_number: str = release_yaml.get("tag_name", None)

            if release_number is None:
                self._logger.error(
                    f"tag_name not found in release info, web returned: {release_yaml}"
                )
                return None

            return release_number.replace("v", "")

        except requests.exceptions.RequestException as e:
            self._logger.error(
                f"Failed to retrieve release information from {URL.API_RELEASE_URL.value}, {e}"
            )
            return None

    # endregion

    def compare_versions(self, current_version: str, latest_version: str) -> bool:
        """
        Compare two version numbers and determine if an update is required.
        Both version should be in the format "v#.#.#" or "#.#.#".

        Args:
            current_version (str): The current version number.
            latest_version (str): The latest version number.

        Returns:
            bool: True if an update is available, False otherwise.
        """

        if current_version is None or latest_version is None:
            self._logger.warning(
                "Failed to retrieve version information, unable to compare versions"
            )
            return False

        current_version = current_version.replace("v", "").split(
            "."
        )  # Remove 'v' and split into parts
        latest_version = latest_version.replace("v", "").split(
            "."
        )  # Remove 'v' and split into parts

        for vers1, vers2 in zip(current_version, latest_version):
            vers1, vers2 = int(vers1), int(vers2)

            if vers1 < vers2:
                return True
            elif vers1 > vers2:
                return False

        return False

    def update_last_checked(self) -> None:
        """
        Updates the last checked time in the settings file.
        """
        settings = self._file_manager.get_config(FILE.SETTINGS)
        settings["lastChecked"] = int(time.time())
        self._file_manager.set_config(FILE.SETTINGS, settings)


if __name__ == "__main__":
    # Test Updater class
    file_manager = FileManager()
    file_manager.setup()
    updater = Updater("v1.0.0", file_manager)
    updater.check_for_config_update(FOLDER.LOCKING_CONFIGS)
    # updater.check_for_version_update()
    # updater.update_last_checked()
