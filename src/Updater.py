import requests
import constants
from CustomLogger import CustomLogger


class Updater:
    def __init__(self, release_version):
        """
        The Updater class is responsible for comparing versions and determining if an update is required.

        Args:
            release_version (str): The current release version of the agent.

        Attributes:
            release_version (str): The current release version of the agent.

        Methods:
            compare_json_configs: Compares the version of a JSON config with the latest version available.
            compare_release_versions: Compares the version of the current agent with the latest version available.
            compare_versions: Compare two version numbers and determine if an update is required.
        """
        self.release_version = release_version
        self.logger = CustomLogger("Updater").get_logger()

    #region: JSON Config Versions

    def compare_json_configs(self, current_config: dict, path_to_json_config: str) -> bool:
        """
        Compares the version of the current agent configuration with the latest version available.

        Args:
            current_config (dict): The current agent configuration.
            path_to_json_config (str): The path to the json config.

        Returns:
            bool: True if the current version is older than the latest version, False otherwise.
        """
        self.logger.info(f"Comparing JSON config versions for {path_to_json_config}")
        current_version = self._get_current_config_version(current_config)
        latest_version = self._get_latest_config_version(path_to_json_config)
        self.logger.info(f"Current version: {current_version}, Latest version: {latest_version}")

        return self.compare_versions(current_version, latest_version)

    #endregion

    def _get_current_config_version(self, current_config: dict) -> str:
        """
        Retrieves the current configuration version from a JSON file.

        Args:
            current_config (dict): The dictionary containing the current configuration.

        Returns:
            str: The current configuration version, or None if it is not found.
        """
        return current_config.get("CONFIG_VERSION", None)

    def _get_latest_config_version(self, download_path: str, timeout: int = 2) -> str:
        """
        Retrieves the latest configuration version from the specified download path.

        Args:
            download_path (str): The path to the configuration file.
            timeout (int): The timeout value for the HTTP request in seconds. Default is 2 seconds.

        Returns:
            str: The latest configuration version, or None if an error occurred during the request.
        """
        config_url = f"{constants.DOWNLOAD_URL}/{constants.TEMPLATE_FOLDER_NAME}/{download_path}"
        
        try:
            config_file = requests.get(config_url, timeout=timeout).json()
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to retrieve configuration file from {config_url}, {e}")
            return None

        return config_file.get("CONFIG_VERSION", None)

    #region: Release Versions

    def compare_release_versions(self) -> bool:
        """
        Compares the version of the current agent with the latest version available.

        Args:
            current_version (str): The current agent version.

        Returns:
            bool: True if the current version is older than the latest version, False otherwise.
        """
        latest_version = self._get_latest_release_version()

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
            release_info = requests.get(constants.API_RELEASE_URL, timeout=timeout)
            release_info.raise_for_status()
            
            return release_info.json().get("tag_name", None)
        
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to retrieve release information from {constants.API_RELEASE_URL}, {e}")
            return None

    #endregion

    def compare_versions(self, current_version: str, latest_version: str):
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

if __name__ == "__main__":
    updater = Updater("2.0.0")
