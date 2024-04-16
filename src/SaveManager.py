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
        for file in os.listdir(self.FOLDER_PATH):
            if file.endswith(".json"):
                self.save_files.append(file)
        
        number_of_save_files = len(self.save_files)
        self.logger.info(f"Found {number_of_save_files} save file{'s' if number_of_save_files > 1 else ''}.")

    def get_all_save_files(self) -> list:
        """
        Gets a list of all save files.

        Returns:
            list: A list of all save files.
        """
        return self.save_files

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
            self.logger.error(f"Save file {error_file} not found. Defaulting to {save_name}.")

        self.current_save = save_name
        self.file_manager.set_value(FILE.USER_SETTINGS, "ACTIVE_SAVE_FILE", save_name)
        self.logger.info(f"Save file set to {self.get_current_save_name()}.")
        self.load_save_file()

    def load_save_file(self) -> None:
        """
        Loads the current save file.

        Returns:
            None
        """
        with open(f"{self.FOLDER_PATH}/{self.current_save}", "r") as file:
            self.save_data = json.load(file)

        self.logger.info(f"Save file {self.current_save} loaded.")

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
    
    def set_current_agent(self, agent_name: str) -> None:
        """
        Sets the name of the agent that is currently selected.

        Args:
            agent_name (str): The name of the agent that is currently selected.

        Returns:
            None
        """
        self.save_data["SELECTED_AGENT"] = agent_name

    def get_unlocked_dict(self) -> dict:
        """
        Gets a list of agents that have been unlocked.

        Returns:
            list: A list of agents that have been unlocked.
        """
        return {agent: value[0] for agent, value in self.save_data.get("AGENTS").items() if value}

    def get_random_dict(self) -> dict:
        """
        Gets a list of agents that have been unlocked.

        Returns:
            list: A list of agents that have been unlocked.
        """
        return {agent: value[1] for agent, value in self.save_data.get("AGENTS").items() if value}

    def get_map_dict(self) -> dict:
        """
        Gets a list of agents that have been unlocked.

        Returns:
            list: A list of agents that have been unlocked.
        """
        return self.save_data.get("MAP_SPECIFIC_AGENTS")

    def is_unlocked(self, agent_name: str) -> bool:
        """
        Checks if an agent has been unlocked.

        Args:
            agent_name (str): The name of the agent to check.

        Returns:
            bool: True if the agent has been unlocked, False otherwise.
        """
        return self.get_unlocked_dict().get(agent_name)

    def get_unlocked_agents(self) -> list:
        """
        Gets a list of agents that have been unlocked.

        Returns:
            list: A list of agents that have been unlocked.
        """
        return [agent for agent, value in self.get_unlocked_dict().items() if value]

    def save_file(self) -> None:
        """
        Saves the current save file to disk.

        Returns:
            None
        """
        with open(f"{self.FOLDER_PATH}/{self.current_save}.json", "w") as file:
            file.write(self.save_data)

        self.logger.info(f"Save file {self.current_save_name} saved.")