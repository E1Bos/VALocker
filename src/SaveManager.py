import os
from ruamel.yaml import YAML

from typing import Optional

# Custom Imports
from CustomLogger import CustomLogger
from Constants import FOLDER, FILE, GET_WORKING_DIR
from FileManager import FileManager


class SaveManager:
    logger: CustomLogger = CustomLogger("Save Manager").get_logger()

    FOLDER_PATH: str = os.path.join(GET_WORKING_DIR(), FOLDER.SAVE_FILES.value)
    file_manager: FileManager
    current_save_file: str = str()
    save_data: dict[str, dict[str, list[bool] | str | None]]
    save_files: list[str] = list()

    def __init__(self, file_manager: FileManager) -> None:
        self.file_manager = file_manager

    def setup(self) -> None:
        """
        Sets up the SaveManager by populating the list of save files.

        This method iterates over the files in the specified folder path and adds
        any files with the ".yaml" extension to the list of save files.

        Returns:
            None
        """
        # Reads all save files in the save file folder
        for file in os.listdir(self.FOLDER_PATH):
            if file.endswith(".yaml"):
                self.save_files.append(file)

        # Logs Info
        number_of_save_files = len(self.save_files)
        self.logger.info(
            f"Found {number_of_save_files} save file{'s' if number_of_save_files > 1 else ''}"
        )

        # Ensures all save files have the correct agent data
        self.update_save_files()

    # region: Getters

    def get_all_save_files(self) -> list[str]:
        """
        Gets a list of all save files.

        Returns:
            list: A list of all save files.
        """
        return self.save_files

    def get_current_save_file(self) -> str:
        """
        Gets the current save file.

        Returns:
            str: The current save file.
        """
        return self.current_save_file

    def get_current_save_name(self) -> str:
        """
        Gets the name of the current save file.

        Returns:
            str: The name of the current save file.
        """
        return self.current_save_file.removesuffix(".yaml")

    def get_save_data(
        self,
    ) -> dict[str, str | dict[str, list[bool] | str | None]] | None:
        """
        Gets the save data.

        Returns:
            dict: The save data.
        """
        return self.save_data

    def get_current_agent(self) -> str:
        """
        Gets the name of the agent that is currently selected.

        Returns:
            str: The name of the agent that is currently selected.
        """
        return self.save_data.get("selectedAgent")

    def get_all_agent_names(self) -> list[str]:
        """
        Gets a list of agent names.

        Returns:
            list: A list of agent names.
        """
        return list(self.save_data.get("AGENTS").keys())

    def get_map_dict(self) -> dict[str, list[bool] | str | None] | None:
        """
        Gets a list of maps and their associated agents.

        Returns:
            dict: A dictionary of maps and their associated agents.
        """
        return self.save_data.get("mapSpecificAgents")

    def get_agent_status(self) -> dict[str, list[bool]]:
        """
        Gets the status of all agents.

        Returns:
            dict: A dictionary containing the status of all agents.
        """
        return self.save_data.get("agents")

    # endregion

    def load_save(self, file_name: str) -> None:
        try:
            with open(f"{self.FOLDER_PATH}/{file_name}", "r") as file:
                self.save_data = self.file_manager.yaml.load(file)
                
            self.current_save_file = file_name
            
            self.logger.info(f'Loaded file "{file_name}"')
        
        except FileNotFoundError:
            self.logger.error(f'File "{file_name}" not found')
            self.load_save(self.save_files[0])
            raise FileNotFoundError(f'File "{file_name}" not found')


    def save_file(self, save_data: Optional[dict] = None) -> None:
        """
        Saves the current save file to disk.

        Returns:
            None
        """
        if save_data is None:
            save_data = self.save_data

        with open(f"{self.FOLDER_PATH}/{self.current_save_file}", "w") as file:
            self.file_manager.yaml.dump(save_data, file)

        self.logger.info(f'Saved file "{self.current_save_file}"')

    def create_new_save(self, file_name: str) -> None:
        """
        Creates a new save file with the specified name.

        Returns:
            None
        """
        save_data = self.file_manager.get_config(FILE.DEFAULT_SAVE)

        default_agents = self.file_manager.get_value(FILE.AGENT_CONFIG, "defaultAgents")

        save_data["selectedAgent"] = default_agents[0]

        for agent in save_data.get("agents"):
            if agent in default_agents:
                save_data.get("agents")[agent] = (False,)
                continue
            
            save_data.get("agents")[agent] = (False, False)

        for map in save_data.get("mapSpecificAgents"):
            save_data.get("mapSpecificAgents")[map] = None

        with open(f"{self.FOLDER_PATH}/{file_name}", "w") as file:
            self.file_manager.yaml.dump(save_data, file)

        self.save_files.append(file_name)

        self.logger.info(f'Created new file "{file_name}"')

    def update_save_files(self) -> None:
        # List of all agent names
        roles = self.file_manager.get_value(FILE.AGENT_CONFIG, "roles")
        agent_names = sorted(
            [
                agent
                for role in roles
                for agent in self.file_manager.get_value(FILE.AGENT_CONFIG, role)
            ]
        )

        # List of all map names
        map_names = [
            map_name
            for map_name in self.file_manager.get_value(FILE.AGENT_CONFIG, "maps")
        ]

        # Iterates over all save files and update the agents and maps
        for save_file in self.save_files:
            with open(f"{self.FOLDER_PATH}/{save_file}", "r") as file:
                save_data: dict[str, dict] = self.file_manager.yaml.load(file)

            # Remove any agents that are not in the list of agents
            agents_to_remove = [
                agent for agent in save_data.get("agents") if agent not in agent_names
            ]
            for agent in agents_to_remove:
                save_data.get("agents").pop(agent)

            # Add any agents that are not in the list of agents
            for agent in agent_names:
                if agent not in save_data.get("agents"):
                    save_data.get("agents")[agent] = (False, False)

            save_data["agents"] = dict(sorted(save_data["agents"].items()))

            # Remove any maps that are not in the list of maps
            maps_to_remove = [
                map_name
                for map_name in save_data.get("mapSpecificAgents")
                if map_name not in map_names
            ]
            for map_name in maps_to_remove:
                save_data.get("mapSpecificAgents").pop(map_name)

            # Add any maps that are not in the list of maps
            for map_name in map_names:
                if map_name not in save_data.get("mapSpecificAgents"):
                    save_data.get("mapSpecificAgents")[map_name] = None

            save_data["mapSpecificAgents"] = dict(
                sorted(save_data.get("mapSpecificAgents").items())
            )

            # Replace the selected agent if it is not in the list of agents
            if save_data.get("selectedAgent") not in agent_names:
                available_agents = [
                    agent_name
                    for agent_name, values in save_data.get("agents").items()
                    if len(values) == 1 or values[0] is True
                ]

                save_data["selectedAgent"] = available_agents[0]

            # Saves the updated save file
            with open(f"{self.FOLDER_PATH}/{save_file}", "w") as file:
                self.file_manager.yaml.dump(save_data, file)

        self.logger.info(f"Updated all save files")


if __name__ == "__main__":
    file_manager = FileManager()
    file_manager.setup()
    save_manager = SaveManager(file_manager)
    save_manager.setup()
    save_manager.load_save("default.yaml")
