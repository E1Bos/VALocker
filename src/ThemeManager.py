import json

from Constants import FOLDER, GET_WORKING_DIR, BRIGHTEN_COLOR
from CustomLogger import CustomLogger


class ThemeManager:
    logger = CustomLogger("Theme Manager").get_logger()
    working_dir = GET_WORKING_DIR()
    theme: dict[str, str]

    """
    Manages the theme for the application and provides methods to set and retrieve the theme.
    """

    def get_theme(self, theme_name: str) -> dict[str, str]:
        """
        Sets the theme for the application, and brightens the colors for hover effects.

        Args:
            theme_name (str): The name of the theme to set.
        """
        with open(
            f"{self.working_dir}/{FOLDER.THEMES.value}/{theme_name}-theme.json", "r"
        ) as theme_file:
            self.theme = json.load(theme_file)

        for element_to_brighten in [
            "accent",
            "button-enabled",
            "button-disabled",
            "foreground",
            "foreground-highlight",
        ]:
            self.theme[f"{element_to_brighten}-hover"] = BRIGHTEN_COLOR(
                self.theme[element_to_brighten], 1.1
            )

        self.theme["label"] = (self.theme["font"], 16)
        self.theme["button"] = (self.theme["font"], 14)

        self.logger.info(f'Loaded Theme "{theme_name}"')

        return self.theme


if __name__ == "__main__":
    theme_manager = ThemeManager()
    theme_manager.set_theme("default")
