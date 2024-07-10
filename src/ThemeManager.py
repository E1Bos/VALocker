from ruamel.yaml import YAML

from Constants import FOLDER, GET_WORKING_DIR, BRIGHTEN_COLOR
from CustomLogger import CustomLogger

"""
Idea for a theme that can be observed by other classes to update their appearance when the theme changes.
This would mean valocker would not need to be restarted to apply a new theme.

class ObservableTheme:
    def __init__(self):
        self._observers = []
        self._theme = {}

    def register_observer(self, observer):
        self._observers.append(observer)

    def notify_observers(self):
        for observer in self._observers:
            observer.update_theme(self._theme)

    def update_theme(self, key, value):
        self._theme[key] = value
        self.notify_observers()

    @property
    def theme(self):
        return self._theme
"""

class ThemeManager:
    """
    Manages the theme for the application and provides methods to set and retrieve the theme.
    @author: [E1Bos](https://www.github.com/E1Bos)
    """
    
    logger = CustomLogger("Theme Manager").get_logger()
    working_dir = GET_WORKING_DIR()
    theme: dict[str, str]

    def get_theme(self, theme_name: str) -> dict[str, str]:
        """
        Sets the theme for the application, and brightens the colors for hover effects.

        Args:
            theme_name (str): The name of the theme to set.
        """
        yaml = YAML(typ='rt')
        # yaml.indent(mapping=2, sequence=4, offset=2)
        
        with open(
            f"{self.working_dir}/{FOLDER.THEMES.value}/{theme_name}", "r"
        ) as theme_file:
            self.theme = yaml.load(theme_file)

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
    theme = theme_manager.get_theme("default-theme.yaml")
    print(theme)