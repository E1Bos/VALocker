from CustomLogger import CustomLogger
from ProjectUtils import FOLDER, FILE, GET_WORKING_DIR
from FileManager import FileManager
import os
import json


class SaveManager:
    def __init__(self, file_manager: FileManager) -> None:
        self.logger = CustomLogger("Save Manager").get_logger()

        working_dir = GET_WORKING_DIR()
        self.FOLDER_PATH = os.path.join(working_dir, FOLDER.SAVE_FILES.value)
        self.file_manager = file_manager

        self.current_save = str()
        self.save_data = dict()
        self.save_files = list()

    def setup(self) -> None:
        """
        Sets up the SaveManager by populating the list of save files.

        This method iterates over the files in the specified folder path and adds
        any files with the ".json" extension to the list of save files.

        Returns:
            None
        """
        # Reads all save files in the save file folder
        for file in os.listdir(self.FOLDER_PATH):
            if file.endswith(".json"):
                self.save_files.append(file)

        # Logs Info
        number_of_save_files = len(self.save_files)
        self.logger.info(
            f"Found {number_of_save_files} save file{'s' if number_of_save_files > 1 else ''}."
        )

        # Ensures all save files have the correct agent data
        self.update_save_files()

    # region: Getters

    def get_all_save_files(self) -> list:
        """
        Gets a list of all save files.

        Returns:
            list: A list of all save files.
        """
        return self.save_files

    def get_current_save_name(self) -> str:
        """
        Gets the name of the current save file.

        Returns:
            str: The name of the current save file.
        """
        return self.current_save.removesuffix(".json")

    def get_current_agent(self) -> str:
        """
        Gets the name of the agent that is currently selected.

        Returns:
            str: The name of the agent that is currently selected.
        """
        return self.save_data.get("SELECTED_AGENT")

    def get_agent_names(self) -> list:
        """
        Gets a list of agent names.

        Returns:
            list: A list of agent names.
        """
        return list(self.save_data.get("AGENTS").keys())

    def get_agents_status(self) -> dict:
        """
        Gets a dict of all agents and their status.

        Returns:
            dict: A dict of all agents and their unlock status.
        """
        return {
            agent: value[0] for agent, value in self.save_data.get("AGENTS").items()
        }

    def get_random_dict(self) -> dict:
        """
        Gets a list of agents that have been unlocked.

        Returns:
            list: A list of agents that have been unlocked.
        """
        return {
            agent: value[1]
            for agent, value in self.save_data.get("AGENTS").items()
            if value
        }

    def get_map_dict(self) -> dict:
        """
        Gets a list of maps and their associated agents.

        Returns:
            list: A list of maps and their agent.
        """
        return self.save_data.get("MAP_SPECIFIC_AGENTS")

    def get_unlocked_agents(self) -> list:
        """
        Gets a list of agents that have been unlocked.

        Returns:
            list: A list of agents that have been unlocked.
        """
        return [agent for agent, value in self.get_agents_status().items() if value]

    def is_unlocked(self, agent_name: str) -> bool:
        """
        Checks if an agent has been unlocked.

        Args:
            agent_name (str): The name of the agent to check.

        Returns:
            bool: True if the agent has been unlocked, False otherwise.
        """
        return self.get_agents_status().get(agent_name)

    # endregion

    # region: Setters

    def set_current_agent(self, agent_name: str) -> None:
        """
        Sets the name of the agent that is currently selected.

        Args:
            agent_name (str): The name of the agent that is currently selected.

        Returns:
            None
        """
        self.save_data["SELECTED_AGENT"] = agent_name

    def set_agent_status(self, agent_name: str, status: bool, index: int = 0) -> None:
        """
        Sets the unlock status of an agent.

        Args:
            agent_name (str): The name of the agent to set the status of.
            status (bool): The status to set.
            index (int): The index of the agent to set the status of (0=Unlocked, 1=Random). 0 is the default.
        """
        self.save_data["AGENTS"][agent_name][index] = status

    def set_active(self, save_name: str) -> None:
        """
        Sets the active save file.

        Args:
            save_name (str): The name of the save file to set as active.

        Returns:
            None
        """

        if save_name.rfind(".json") == -1:
            save_name += ".json"

        if save_name not in self.save_files:
            error_file = save_name
            save_name = self.get_all_save_files()[0]
            self.logger.error(
                f"Save file {error_file} not found. Defaulting to {save_name}."
            )

        self.current_save = save_name
        self.file_manager.set_value(FILE.USER_SETTINGS, "ACTIVE_SAVE_FILE", save_name)
        self.logger.info(f"Save file set to {self.get_current_save_name()}.")

        with open(f"{self.FOLDER_PATH}/{self.current_save}", "r") as file:
            self.save_data = json.load(file)

        self.logger.info(f"Save file {self.current_save} loaded.")

    # endregion

    def save_file(self) -> None:
        """
        Saves the current save file to disk.

        Returns:
            None
        """
        with open(f"{self.FOLDER_PATH}/{self.current_save}", "w") as file:
            json.dump(self.save_data, file, indent=4)

        self.logger.info(f"Updated file {self.current_save}")

    def update_save_files(self) -> None:
        # List of all agent names
        agent_list = [
            agent
            for role in self.file_manager.get_value(
                FILE.AGENT_CONFIG, "ALL_AGENTS"
            ).values()
            for agent in role
        ]

        # List of all map names
        map_list = [
            map_name
            for map_name in self.file_manager.get_value(FILE.AGENT_CONFIG, "MAPS")
        ]

        for save_file in self.save_files:
            with open(f"{self.FOLDER_PATH}/{save_file}", "r") as file:
                save_data = json.load(file)

            # Ensures all save files have the correct agent data
            for agent in agent_list:
                if agent not in save_data.get("AGENTS"):
                    save_data["AGENTS"][agent] = [False, False]
                if agent in self.file_manager.get_value(FILE.AGENT_CONFIG, "DEFAULT_AGENTS"):
                    save_data["AGENTS"][agent][0] = True

            # Remove any agents that are not in the agent list
            save_data["AGENTS"] = {
                agent: value for agent, value in save_data.get("AGENTS").items() if agent in agent_list
            }

            # Sorts the agents by name
            save_data["AGENTS"] = {
                agent: value for agent, value in sorted(save_data.get("AGENTS").items())
            }

            # Ensures all save files have the correct map specific agent data
            for map_name in map_list:
                if map_name not in save_data.get("MAP_SPECIFIC_AGENTS"):
                    save_data["MAP_SPECIFIC_AGENTS"][map_name] = None

            # Remove any maps that are not in the map list
            save_data["MAP_SPECIFIC_AGENTS"] = {
                map_name: value
                for map_name, value in save_data.get("MAP_SPECIFIC_AGENTS").items()
                if map_name in map_list
            }

            # Sorts the map specific agents by map name
            save_data["MAP_SPECIFIC_AGENTS"] = {
                map_name: value
                for map_name, value in sorted(
                    save_data.get("MAP_SPECIFIC_AGENTS").items()
                )
            }

            # Saves the updated save file
            with open(f"{self.FOLDER_PATH}/{save_file}", "w") as file:
                json.dump(save_data, file, indent=4)


if __name__ == "__main__":
    file_manager = FileManager()
    file_manager.setup()
    save_manager = SaveManager(file_manager)
    save_manager.setup()
    save_manager.set_active("default.json")
    save_manager.update_save_files()
