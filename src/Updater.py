import requests
import time

# Custom imports
from Constants import URL, FOLDER, FILE
from CustomLogger import CustomLogger
from FileManager import FileManager


class Updater():
    _logger: CustomLogger = CustomLogger("Updater").get_logger()
    _file_manager: FileManager
    release_version: str
    check_frequency: int
    FILES_TO_CHECK: list[FILE]

    def __init__(
        self, release_version, file_manager: FileManager, check_frequency=3600
    ):
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
            compare_json_configs: Compares the version of the current agent configuration with the latest version available.
            compare_release_versions: Compares the version of the current agent with the latest version available.
            compare_versions: Compare two version numbers and determine if an update is required.
            update_last_checked: Updates the last checked time in the settings file.
        """
        self.release_version = release_version
        self.check_frequency = check_frequency
        self.FILES_TO_CHECK = [FILE.AGENT_CONFIG, FILE.SETTINGS]
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

    def check_for_version_update(self) -> bool:
        """
        Checks if an update is available for the agent.

        Returns:
            bool: True if an update is available, False otherwise.
        """
        if self.compare_release_versions():
            self._logger.info("New version available, release needs updating")
            return True

        return False

    def check_for_config_updates(self):
        """
        Checks for updates and updates the agent if necessary.
        """

        self._logger.info(
            f"Checking config files for updates: {', '.join([file.name for file in self.FILES_TO_CHECK])}"
        )

        for file in self.FILES_TO_CHECK:
            if self.compare_json_configs(file):
                self._logger.info(f"{file.name} configuration needs updating")
                self._file_manager.update_file(file)

        self._logger.info("Config files checked.")

    # region: JSON Config Versions

    def compare_json_configs(self, config_file: FILE) -> bool:
        """
        Compares the version of the current agent configuration with the latest version available.

        Args:
            config_file (constant.Files): The Enum of the configuration file to check.

        Returns:
            bool: True if the current version is older than the latest version, False otherwise.
        """
        self._logger.info(f"Comparing JSON config versions for {config_file.name}")
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
            config_file: dict = requests.get(config_url, timeout=timeout).json()

        except requests.exceptions.RequestException as e:
            self._logger.error(
                f"Failed to retrieve configuration file from {config_url}, {e}"
            )
            return None
        return config_file.get("version", None)

    # region: Release Versions

    def compare_release_versions(self) -> bool:
        """
        Compares the version of the current agent with the latest version available.

        Returns:
            bool: True if the current version is older than the latest version, False otherwise.
        """
        latest_version = self._get_latest_release_version()

        self._logger.info(
            f"RELEASE: Current version: {self.release_version} | Latest version: {latest_version}"
        )

        return self.compare_versions(self.release_version, latest_version)

    def _get_latest_release_version(self, timeout: int = 2) -> str:
        """
        Retrieves the latest release version from the API.

        Args:
            timeout (int): The timeout value for the HTTP request in seconds. Default is 2 seconds.

        Returns:
            str: The latest release version as a string, or None if an error occurred during the request.
        """
        try:
            release_info: requests.Response = requests.get(URL.API_RELEASE_URL.value, timeout=timeout)
            release_info.raise_for_status()

            release_json: dict = release_info.json()
            release_number: str = release_json.get("tag_name", None)

            if release_number is None:
                self._logger.error(
                    f"tag_name not found in release info, web returned: {release_json}"
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
    updater.check_for_config_updates()
    updater.check_for_version_update()
    updater.update_last_checked()
