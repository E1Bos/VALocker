from typing import Optional, Tuple
import requests
import time

from customtkinter import StringVar

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from VALocker import VALocker

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
    """
    Updater is used to update config files automatically and check for new versions of VALocker.
    @author: [E1Bos](https://www.github.com/E1Bos)
    """

    _logger: CustomLogger = CustomLogger.get_instance().get_logger("Updater")
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
            meets_required_version: Check if the current version of VALocker meets the required version required by a configuration file.
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
            self._file_manager.get_value(FILE.SETTINGS, "$lastChecked", 0)
        )

        time_since_last_check = int(time.time()) - last_checked_release

        if time_since_last_check < self.check_frequency:
            self._logger.info(
                f"Check frequency not met, checked {round(time_since_last_check / 60, 1)} minutes ago"
            )
            return False

        return True

    def check_for_version_update(
        self,
        main_window: "VALocker",
        stringVar: Optional[StringVar] = None,
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
        main_window.update_idletasks()

        update_available, latest_version = self.compare_release_versions()

        if update_available:
            self._logger.info("New version available, agent needs updating")
            stringVar.set(f"Update Available: {latest_version}")
            main_window.update_idletasks()
            return latest_version

        stringVar.set("Up to date")
        main_window.update_idletasks()
        return None

    def check_for_config_update(
        self,
        item: FILE | FOLDER | LOCKING_CONFIG,
        main_window: "VALocker",
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
            main_window.update()
            update_available = self.compare_yaml_configs(item)

            if update_available:
                self._logger.info(f"{item.name} configuration needs updating")
                innerStringVar.set("Downloading update...")
                main_window.update()
                self._file_manager.update_file(item)
                innerStringVar.set("Updated")
                main_window.update()
            else:
                self._logger.info(f"{item.name} is up to date")
                innerStringVar.set("Up to date")
                main_window.update()

        # If checking an entire folder
        elif type(item) is FOLDER:
            self._logger.info(f"Checking folder {item.name} for updates")

            files = self._file_manager.get_files_in_folder(item, contains_field="requiredVersion")

            total_files = len(files)

            for checking, config_file in enumerate(files):
                current_file_num = checking + 1

                try:
                    config_enum = LOCKING_CONFIG(config_file)

                    self._logger.info(f"Checking {config_enum.name} for updates")
                    stringVar.set(f"({current_file_num}/{total_files}) Checking")
                    main_window.update()

                    update_available = self.compare_yaml_configs(config_enum)

                    if update_available:
                        self._file_manager.update_file(config_enum)
                    else:
                        self._logger.info(f"{config_enum.name} is up to date")

                except ValueError:
                    data = self._file_manager.get_config(config_file)

                    if data.get("custom", False) or data.get("version", None) is None:
                        self._logger.info(
                            f"Found custom config \"{data.get('title')}\", skipping"
                        )
                    else:
                        self._logger.error(f"Failed to parse config file {config_file}")
                        stringVar.set(f"({current_file_num}/{total_files}) Error")
                        main_window.update()

                stringVar.set(f"({current_file_num}/{total_files}) Up to date")
                main_window.update()

    # region: YAML Config Versions

    def compare_yaml_configs(self, config_file: FILE | LOCKING_CONFIG) -> bool:
        """
        Compares the content of the current agent configuration with the latest version available.

        Args:
            config_file (constant.Files): The Enum of the configuration file to check.

        Returns:
            bool: True if the current version is different than the latest version, False otherwise.
        """
        self._logger.info(f"Comparing YAML config versions for {config_file.name}")
        current_config = self._file_manager.get_config(config_file)

        latest_config_str = self._get_latest_config(config_file.value)

        if latest_config_str is None:
            self._logger.error(f"Failed to retrieve YAML config for {config_file.name}")
            return False

        latest_config = self._file_manager.yaml.load(latest_config_str)

        # remove old fields that shouldnt exist
        for key in list(current_config.keys()):
            if key not in latest_config:
                del current_config[key]

        for key in latest_config:
            if not key.startswith("$"):
                if key not in current_config or current_config[key] != latest_config[key]:
                    self._logger.info(f"{config_file.name} configuration needs updating")
                    self._logger.info(
                        f"key: {key}, current: {current_config[key]}, latest: {latest_config[key]}"
                    )
                    return True

        self._logger.info(f"{config_file.name} is up to date")

        return False

    def _get_latest_config(self, download_path: str, timeout: int = 2) -> str:
        """
        Retrieves the latest configuration content from the specified download path.

        Args:
            download_path (str): The path to the configuration file.
            timeout (int): The timeout value for the HTTP request in seconds. Default is 2 seconds.

        Returns:
            str: The latest configuration content, or None if an error occurred during the request.
        """
        config_url = f"{URL.DOWNLOAD_URL.value}/{FOLDER.DEFAULTS.value}/{download_path}"

        try:
            response = requests.get(config_url, timeout=timeout)
            response.raise_for_status()
            return response.text

        except requests.exceptions.RequestException as e:
            self._logger.error(
                f"Failed to retrieve YAML config from {config_url}, {e}"
            )
            return None

    # endregion

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
        settings["$lastChecked"] = int(time.time())
        self._file_manager.set_config(FILE.SETTINGS, settings)

    def meets_required_version(self, config_file: FILE | LOCKING_CONFIG) -> bool:
        """
        Check if the current version of VALocker meets the required version required by a configuration file.

        If the configuration file does not have a required version, this method will return True.
        i.e. Updating will be required

        Args:
            config_file (FILE | LOCKING_CONFIG): The file.

        Returns:
            bool: True if the agent version meets the required version, False otherwise.
        """

        minimum_version = self._file_manager.get_config(config_file).get(
            "requiredVersion", "*.*.*"
        )

        release_version = self.release_version

        if any(
            release_vers_digit != minimum_version_digit
            and minimum_version_digit != "*"
            for release_vers_digit, minimum_version_digit in zip(
                release_version.split("."), minimum_version.split(".")
            )
        ):
            self._logger.error(
                "VALocker version does not meet the required version"
            )

            return False

        return True

if __name__ == "__main__":
    pass
